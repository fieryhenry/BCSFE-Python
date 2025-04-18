from __future__ import annotations
import dataclasses
import tempfile
from typing import Any
from bcsfe import core
from bcsfe.cli import color


class ThemeHandler:
    def __init__(self, theme_code: str | None = None):
        if theme_code is None:
            self.theme_code = core.core_data.config.get_str(
                core.ConfigKey.THEME
            )
        else:
            self.theme_code = theme_code

        self.theme_data = self.get_theme_data()

    @staticmethod
    def get_themes_folder() -> core.Path:
        return core.Path("themes", True).generate_dirs()

    @staticmethod
    def get_external_themes_folder() -> core.Path:
        return (
            core.Path.get_documents_folder()
            .add("external_themes")
            .generate_dirs()
        )

    @staticmethod
    def get_theme_path(theme_code: str) -> core.Path:
        if theme_code.startswith("ext-"):
            return ThemeHandler.get_external_themes_folder().add(
                theme_code + ".json"
            )
        return ThemeHandler.get_themes_folder().add(theme_code + ".json")

    def get_theme_data(self) -> dict[str, Any]:
        file_path = self.get_theme_path(self.theme_code)
        if not file_path.exists():
            return {}
        try:
            return core.JsonFile.from_data(file_path.read()).to_object()
        except core.JSONDecodeError:
            return {}

    def get_short_name(self) -> str:
        return self.theme_data.get("short_name", "")

    def get_name(self) -> str:
        return self.theme_data.get("name", "")

    def get_description(self) -> str:
        return self.theme_data.get("description", "")

    def get_author(self) -> str:
        return self.theme_data.get("author", "")

    def get_version(self) -> str:
        return self.theme_data.get("version", "")

    def get_git_repo(self) -> str | None:
        return self.theme_data.get("git_repo", None)

    def get_theme_colors(self) -> dict[str, Any]:
        return self.theme_data.get("colors", {})

    def get_theme_color(self, color_code: str) -> str:
        return self.get_theme_colors().get(color_code, "")

    def get_primary_color(self) -> str:
        return self.get_theme_color("primary")

    def get_secondary_color(self) -> str:
        return self.get_theme_color("secondary")

    def get_tertiary_color(self) -> str:
        return self.get_theme_color("tertiary")

    def get_quaternary_color(self) -> str:
        return self.get_theme_color("quaternary")

    def get_error_color(self) -> str:
        return self.get_theme_color("error")

    def get_warning_color(self) -> str:
        return self.get_theme_color("warning")

    def get_success_color(self) -> str:
        return self.get_theme_color("success")

    @staticmethod
    def get_all_themes() -> list[str]:
        themes = [
            file.get_file_name_without_extension()
            for file in ThemeHandler.get_themes_folder().get_paths_dir(
                regex=r".*\.json"
            )
        ]
        themes += [
            folder.get_file_name_without_extension()
            for folder in ThemeHandler.get_external_themes_folder().get_paths_dir(
                regex=r".*\.json"
            )
        ]
        return themes

    @staticmethod
    def remove_theme(theme_code: str):
        extern = ExternalThemeManager.get_external_theme(theme_code)
        if extern is not None:
            ExternalThemeManager.delete_theme(extern)

        ThemeHandler.get_theme_path(theme_code).remove()
        if theme_code == core.core_data.config.get_str(core.ConfigKey.THEME):
            core.core_data.config.set_default(core.ConfigKey.THEME)


@dataclasses.dataclass
class ExternalTheme:
    short_name: str
    name: str
    description: str
    author: str
    version: str
    colors: dict[str, Any]
    git_repo: str | None = None

    def to_json(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_json(json_data: dict[str, Any]) -> ExternalTheme | None:
        try:
            return ExternalTheme(**json_data)
        except TypeError:
            return None

    @staticmethod
    def from_git_repo(git_repo: str) -> ExternalTheme | None:
        repo = core.GitHandler().get_repo(git_repo)
        if repo is None:
            return None
        theme_json = repo.get_file(core.Path("theme.json"))
        if theme_json is None:
            return None
        json_data = core.JsonFile.from_data(theme_json).to_object()
        json_data["git_repo"] = git_repo
        return ExternalTheme.from_json(json_data)

    def get_new_version(self) -> bool:
        if self.git_repo is None:
            return False
        repo = core.GitHandler().get_repo(self.git_repo)
        if repo is None:
            return False
        with tempfile.TemporaryDirectory() as tmp:
            temp_dir = core.Path(tmp)
            success = repo.clone_to_temp(temp_dir)
            if not success:
                return False
            external_theme = ExternalThemeManager.parse_external_theme(
                temp_dir.add("theme.json")
            )
            if external_theme is None:
                return False
            version = external_theme.version

            if version == self.version:
                return False

            self.name = external_theme.name
            self.short_name = external_theme.short_name
            self.description = external_theme.description
            self.author = external_theme.author
            self.colors = external_theme.colors
            self.version = version

        success = repo.pull()
        if not success:
            return False
        self.save()
        return True

    def save(self):
        ExternalThemeManager.save_theme(self)

    def get_full_name(self) -> str:
        return f"ext-{self.author}-{self.short_name}"


class ExternalThemeManager:
    @staticmethod
    def delete_theme(external_theme: ExternalTheme):
        if external_theme.git_repo is None:
            return
        folder = core.GitHandler.get_repo_folder().add(
            external_theme.git_repo.split("/")[-1]
        )
        folder.remove()

    @staticmethod
    def save_theme(
        external_theme: ExternalTheme,
    ):
        """Saves an external theme.

        Args:
            external_theme (ExternalTheme): External theme to save.
        """
        if external_theme.git_repo is None:
            return
        file = ThemeHandler.get_theme_path(external_theme.get_full_name())

        json_data = external_theme.to_json()
        file.write(core.JsonFile.from_object(json_data).to_data())

    @staticmethod
    def parse_external_theme(path: core.Path) -> ExternalTheme | None:
        """Parses an external theme.

        Args:
            path (core.Path): Path to the external theme.

        Returns:
            ExternalTheme: External theme.
        """
        json_data = core.JsonFile.from_data(path.read()).to_object()
        return ExternalTheme.from_json(json_data)

    @staticmethod
    def update_external_theme(external_theme: ExternalTheme):
        """Updates an external theme.

        Args:
            external_theme (ExternalTheme): External theme to update.
        """
        if external_theme.git_repo is None:
            return
        color.ColoredText.localize(
            "checking_for_theme_updates",
            theme_name=external_theme.name,
        )
        updated = external_theme.get_new_version()
        if updated:
            color.ColoredText.localize(
                "external_theme_updated",
                theme_name=external_theme.name,
                version=external_theme.version,
            )
        else:
            color.ColoredText.localize(
                "external_theme_no_update",
                theme_name=external_theme.name,
                version=external_theme.version,
            )
        print()

    @staticmethod
    def update_all_external_themes(_: Any = None):
        """Updates all external themes."""
        files = ThemeHandler.get_external_themes_folder().get_paths_dir()
        if not files:
            color.ColoredText.localize(
                "no_external_themes",
            )
            return
        if not core.GitHandler.is_git_installed():
            color.ColoredText.localize(
                "git_not_installed",
            )
            return
        for file in files:
            theme = ExternalThemeManager.parse_external_theme(file)
            if theme is None:
                continue
            ExternalThemeManager.update_external_theme(theme)

    @staticmethod
    def get_external_theme_config() -> ExternalTheme | None:
        """Gets the external theme from the config.

        Returns:
            ExternalTheme: External theme.
        """

        theme = core.core_data.config.get_str(core.ConfigKey.THEME)
        if not theme.startswith("ext-"):
            return None
        return ExternalThemeManager.parse_external_theme(
            ThemeHandler.get_theme_path(theme)
        )

    @staticmethod
    def get_external_theme(theme: str) -> ExternalTheme | None:
        """Gets the external theme from the theme code.

        Returns:
            ExternalTheme: External theme.
        """

        if not theme.startswith("ext-"):
            return None
        return ExternalThemeManager.parse_external_theme(
            ThemeHandler.get_theme_path(theme)
        )
