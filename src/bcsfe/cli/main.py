"""Main class for the CLI."""

import sys
from typing import Any, Optional
from bcsfe.cli import dialog_creator, file_dialog, server_cli, color, feature_handler
from bcsfe.core import io, country_code, server


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

        if local_version < latest_version:
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
        color.ColoredText.localize(
            "welcome", config_path=io.config.Config.get_config_path()
        )
        print()

    def select_save(self):
        options = [
            "download_save",
            "select_save_file",
            "adb_pull_save",
            "load_save_data_json",
            "exit",
        ]

        root_handler = io.root_handler.RootHandler()

        if root_handler.is_android():
            options[2] = "root_storage_pull_save"

        choice = (
            dialog_creator.ChoiceInput(
                options, options, [], {}, "save_load_option", True
            ).get_input_locale_while()[0]
            - 1
        )

        if choice == 0:
            self.save_path = server_cli.ServerCLI().download_save()
        elif choice == 1:
            self.save_path = self.load_save_file()
        elif choice == 2:
            handler = root_handler
            if not root_handler.is_android():
                handler = io.adb_handler.AdbHandler()
                if not handler.select_device():
                    return

            ccs = handler.get_battlecats_ccs()
            cc = country_code.CountryCode.select_from_ccs(ccs)
            if cc is None:
                color.ColoredText.localize("no_cc_error")
                return
            handler.set_cc(cc)
            self.save_path = handler.save_locally()
        elif choice == 3:
            self.save_path = self.load_save_data_json()
        elif choice == 4:
            self.exit = True
            return

        if self.save_path is None:
            return

        try:
            self.save_file = io.save.SaveFile(self.save_path.read())
            self.save_file.save_path = self.save_path
        except Exception as e:
            color.ColoredText.localize("parse_save_error", error=e)
            return

    def load_save_options(self):
        """Load save options."""
        self.select_save()
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
        main_path = save_file.get_default_path()
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=save_file.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
        )
        if path is None:
            return None
        path = io.path.Path(path)
        path.parent().generate_dirs()
        save_file.save_path = path
        save_file.to_file(path)
        save_file.to_file(main_path)
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

    def load_save_file(self) -> Optional[io.path.Path]:
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

    def load_save_data_json(self) -> Optional[io.path.Path]:
        """Load save data from json file.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file("load_save_data_json")
        if path is None:
            return None
        path = io.path.Path(path)
        json_data = io.json_file.JsonFile.from_data(path.read()).get_json()
        save_file = io.save.SaveFile.from_dict(json_data)
        path = self.save_save_dialog(save_file)
        if path is None:
            return None
        save_file.to_file(path)
        return path
