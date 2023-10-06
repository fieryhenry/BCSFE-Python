from typing import Any, Optional
from bcsfe import core


class ThemeHandler:
    def __init__(self, theme_code: Optional[str] = None):
        if theme_code is None:
            self.theme_code = core.config.get_str(core.ConfigKey.THEME)
        else:
            self.theme_code = theme_code

        self.theme_data = self.get_theme_data()

    def get_theme_data(self) -> dict[str, Any]:
        file_path = core.Path("themes", True).add(self.theme_code + ".json")
        if not file_path.exists():
            return {}
        try:
            return core.JsonFile.from_data(file_path.read()).to_object()
        except core.JSONDecodeError:
            return {}

    def get_theme_info(self) -> dict[str, Any]:
        return self.theme_data.get("info", {})

    def get_theme_name(self) -> str:
        return self.get_theme_info().get(
            "name", core.local_manager.get_key("unknown_theme_name")
        )

    def get_theme_author(self) -> str:
        return self.get_theme_info().get(
            "author", core.local_manager.get_key("unknown_theme_author")
        )

    def get_theme_path(self) -> "core.Path":
        return core.Path("themes", True).add(self.theme_code + ".json")

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
