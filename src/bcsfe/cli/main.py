"""Main class for the CLI."""

import sys
import traceback
from typing import Any, Optional
from bcsfe.cli import (
    file_dialog,
    color,
    feature_handler,
    save_management,
)
from bcsfe import core


class Main:
    """Main class for the CLI."""

    def __init__(self):
        self.save_file = None
        self.exit = False
        self.save_path = None
        self.fh = None

    def wipe_temp_save(self):
        """Wipe the temp save."""
        core.SaveFile.get_temp_path().remove()

    def main(self):
        """Main function for the CLI."""
        self.wipe_temp_save()
        core.GameDataGetter.delete_old_versions()
        self.check_update()
        print()
        self.print_start_text()
        while not self.exit:
            self.load_save_options()

    def check_update(self):
        updater = core.Updater()
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
        theme_manager = core.theme_manager
        color.ColoredText.localize(
            "welcome",
            config_path=core.Config.get_config_path(),
            theme_name=theme_manager.get_theme_name(),
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
    def save_save_dialog(save_file: "core.SaveFile") -> Optional["core.Path"]:
        """Save save file dialog.

        Args:
            save_file (core.SaveFile): Save file to save.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=core.SaveFile.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
        )
        if path is None:
            return None
        path = core.Path(path)
        path.parent().generate_dirs()
        save_file.save_path = path
        return path

    @staticmethod
    def save_json_dialog(json_data: dict[str, Any]) -> Optional["core.Path"]:
        """Save json file dialog.

        Args:
            json_data (dict): Json data to save.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file("save_json_dialog")
        if path is None:
            return None
        path = core.Path(path)
        path.parent().generate_dirs()
        core.JsonFile.from_object(json_data).to_data().to_file(path)
        return path

    @staticmethod
    def load_save_file() -> Optional["core.Path"]:
        """Load save file from file dialog.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file(
            "select_save_file", initialdir=core.SaveFile.get_saves_path().to_str()
        )
        if path is None:
            return None
        path = core.Path(path)
        return path

    @staticmethod
    def load_save_data_json() -> Optional[tuple["core.Path", "core.CountryCode"]]:
        """Load save data from json file.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file("load_save_data_json")
        if path is None:
            return None
        path = core.Path(path)
        if not path.exists():
            return None
        try:
            json_data = core.JsonFile.from_data(path.read()).get_json()
        except core.JSONDecodeError:
            color.ColoredText.localize(
                "load_json_fail", error=core.logger.get_traceback()
            )
            return None
        try:
            save_file = core.SaveFile.from_dict(json_data)
        except core.SaveError:
            color.ColoredText.localize(
                "load_json_fail", error=core.logger.get_traceback()
            )
            return None
        path = Main.save_save_dialog(save_file)
        if path is None:
            return None
        save_file.to_file(path)
        return path, save_file.cc

    @staticmethod
    def exit_editor(
        save_file: Optional["core.SaveFile"] = None, check_temp: bool = True
    ):
        """Exit the editor."""
        print()
        if save_file is None and check_temp:
            temp_path = core.SaveFile.get_temp_path()
            if temp_path.exists():
                try:
                    save_file = core.SaveFile(temp_path.read())
                except core.SaveError as e:
                    tb = traceback.format_exc()
                    color.ColoredText.localize(
                        "save_temp_fail", error=str(e), traceback=tb
                    )
                    sys.exit()
                color.ColoredText.localize("save_temp_success")
            else:
                color.ColoredText.localize("save_temp_not_found")

        if save_file is None:
            sys.exit()
        save = color.ColoredInput().localize("save_before_exit") == "y"

        if save:
            save_management.SaveManagement.save_save(save_file)

        sys.exit()
