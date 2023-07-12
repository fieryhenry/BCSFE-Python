"""Main class for the CLI."""

import sys
from typing import Any, Optional
from bcsfe.cli import (
    file_dialog,
    color,
    feature_handler,
    theme_handler,
    save_management,
)
from bcsfe.core import country_code, io, server


class Main:
    """Main class for the CLI."""

    def __init__(self):
        self.save_file = None
        self.exit = False
        self.save_path = None
        self.fh = None

    def main(self):
        """Main function for the CLI."""
        self.check_update()
        print()
        self.print_start_text()
        while not self.exit:
            self.load_save_options()

    def check_update(self):
        updater = server.updater.Updater()
        has_pre_release = updater.has_enabled_pre_release()
        local_version = updater.get_local_version()
        latest_version = updater.get_latest_version(has_pre_release)

        color.ColoredText.localize(
            "version_line",
            local_version=local_version,
            latest_version=latest_version,
        )

        if local_version.split("b")[0] == latest_version:
            update_needed = True
            if local_version == latest_version:
                update_needed = False
        elif local_version < latest_version:
            update_needed = True
        else:
            update_needed = False

        if update_needed:
            update = (
                color.ColoredInput().localize(
                    "update_available", latest_version=latest_version
                )
                == "y"
            )
            if update:
                if updater.update(latest_version):
                    color.ColoredText.localize("update_success")
                else:
                    color.ColoredText.localize("update_fail")
                sys.exit()

    def print_start_text(self):
        theme_manager = theme_handler.ThemeHandler()
        color.ColoredText.localize(
            "welcome",
            config_path=io.config.Config.get_config_path(),
            theme_name=theme_manager.get_theme_name(),
            theme_version=theme_manager.get_theme_version(),
            theme_author=theme_manager.get_theme_author(),
            theme_path=theme_manager.get_theme_path(),
        )
        print()

    def load_save_options(self):
        """Load save options."""
        save_file = save_management.SaveManagement.select_save(True)
        if save_file is None:
            return
        self.save_file = save_file

        self.feature_handler()

    def feature_handler(self):
        """Run the feature handler."""
        if self.save_file is None:
            return
        self.fh = feature_handler.FeatureHandler(self.save_file)
        self.fh.select_features_run()

    @staticmethod
    def save_save_dialog(save_file: "io.save.SaveFile") -> Optional[io.path.Path]:
        """Save save file dialog.

        Args:
            save_file (io.save.SaveFile): Save file to save.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=io.save.SaveFile.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
        )
        if path is None:
            return None
        path = io.path.Path(path)
        path.parent().generate_dirs()
        save_file.save_path = path
        return path

    @staticmethod
    def save_json_dialog(json_data: dict[str, Any]) -> Optional[io.path.Path]:
        """Save json file dialog.

        Args:
            json_data (dict): Json data to save.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file("save_json_dialog")
        if path is None:
            return None
        path = io.path.Path(path)
        path.parent().generate_dirs()
        io.json_file.JsonFile.from_object(json_data).to_data().to_file(path)
        return path

    @staticmethod
    def load_save_file() -> Optional[io.path.Path]:
        """Load save file from file dialog.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file(
            "select_save_file", initialdir=io.save.SaveFile.get_saves_path().to_str()
        )
        if path is None:
            return None
        path = io.path.Path(path)
        return path

    @staticmethod
    def load_save_data_json() -> (
        Optional[tuple[io.path.Path, "country_code.CountryCode"]]
    ):
        """Load save data from json file.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file("load_save_data_json")
        if path is None:
            return None
        path = io.path.Path(path)
        if not path.exists():
            return None
        json_data = io.json_file.JsonFile.from_data(path.read()).get_json()
        save_file = io.save.SaveFile.from_dict(json_data)
        path = Main.save_save_dialog(save_file)
        if path is None:
            return None
        save_file.to_file(path)
        return path, save_file.cc
