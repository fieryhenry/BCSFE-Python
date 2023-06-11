from bcsfe.cli import dialog_creator, file_dialog, server_cli
from bcsfe.core import io


class Main:
    def __init__(self):
        pass

    def main(self):
        self.load_save_options()

    def load_save_options(self):
        options = [
            "download_save",
            "select_save_file",
            "adb_pull_save",
            "load_save_data_json",
        ]

        if io.root_handler.RootHandler().is_android():
            options[2] = "root_storage_pull_save"

        choice = (
            dialog_creator.ChoiceInput(
                options, options, [], {}, "save_load_option", True
            ).get_input_locale_while()[0]
            - 1
        )

        if choice == 0:
            server_cli.ServerCLI().download_save()

    def save_save_dialog(self, save_file: "io.save.SaveFile") -> io.path.Path:
        path = save_file.get_default_path()
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=path.parent().to_str(),
            initialfile=path.basename(),
        )
        path = io.path.Path(path)
        path.parent().generate_dirs()
        return path
