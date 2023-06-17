from typing import Any, Optional
from bcsfe.core import io, locale_handler


class ThemeHandler:
    def __init__(self, theme_code: Optional[str] = None):
        if theme_code is None:
            self.theme_code = io.config.Config().get(io.config.Key.THEME)
        else:
            self.theme_code = theme_code

    def get_theme_data(self) -> dict[str, Any]:
        file_path = io.path.Path("themes", True).add(self.theme_code + ".json")
        return io.json_file.JsonFile.from_data(file_path.read()).get_json()

    def get_theme_info(self) -> dict[str, Any]:
        return self.get_theme_data().get("info", {})

    def get_theme_name(self) -> str:
        return self.get_theme_info().get(
            "name", locale_handler.LocalManager().get_key("unknown_theme_name")
        )

    def get_theme_author(self) -> str:
        return self.get_theme_info().get(
            "author", locale_handler.LocalManager().get_key("unknown_theme_author")
        )

    def get_theme_version(self) -> str:
        return self.get_theme_info().get(
            "version", locale_handler.LocalManager().get_key("unknown_theme_version")
        )

    def get_theme_description(self) -> str:
        return self.get_theme_info().get(
            "description",
            locale_handler.LocalManager().get_key("unknown_theme_description"),
        )

    def get_theme_path(self) -> io.path.Path:
        return io.path.Path("themes", True).add(self.theme_code)

    def get_theme_colors(self) -> dict[str, Any]:
        return self.get_theme_data().get("colors", {})

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
