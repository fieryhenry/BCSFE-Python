"""Main class for the CLI."""

from bcsfe.cli import dialog_creator, file_dialog, server_cli, color, feature_handler
from bcsfe.core import io, country_code


class Main:
    """Main class for the CLI."""

    def __init__(self):
        self.save_file = None
        self.exit = False
        self.save_path = None
        self.fh = None

    def main(self):
        """Main function for the CLI."""
        self.print_start_text()
        while not self.exit:
            self.load_save_options()

    def print_start_text(self):
        color.ColoredText.localize(
            "welcome", config_path=io.config.Config.get_config_path()
        )
        print()

    def load_save_options(self):
        """Load save options."""

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
                devices = handler.get_connected_devices()
                device = dialog_creator.ChoiceInput(
                    devices, devices, [], {}, "select_device", True
                ).get_input_locale_while()
                if not device:
                    color.ColoredText.localize("no_device_error")
                    return
                device = device[0]

                handler.set_device(devices[device - 1])

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
        except Exception as e:
            color.ColoredText.localize("parse_save_error", error=e)
            return

        self.feature_handler()

    def feature_handler(self):
        """Run the feature handler."""
        if self.save_file is None:
            return
        self.fh = feature_handler.FeatureHandler(self.save_file)
        self.fh.select_features_run()

    def save_save_dialog(self, save_file: "io.save.SaveFile") -> io.path.Path:
        """Save save file dialog.

        Args:
            save_file (io.save.SaveFile): Save file to save.

        Returns:
            io.path.Path: Path to save file.
        """
        path = save_file.get_default_path()
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=path.parent().to_str(),
            initialfile=path.basename(),
        )
        path = io.path.Path(path)
        path.parent().generate_dirs()
        return path

    def load_save_file(self) -> io.path.Path:
        """Load save file from file dialog.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file("select_save_file")
        path = io.path.Path(path)
        return path

    def load_save_data_json(self) -> io.path.Path:
        """Load save data from json file.

        Returns:
            io.path.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file("load_save_data_json")
        path = io.path.Path(path)
        json_data = io.json_file.JsonFile.from_data(path.read()).get_json()
        save_file = io.save.SaveFile.from_dict(json_data)
        path = self.save_save_dialog(save_file)
        save_file.to_file(path)
        return path
