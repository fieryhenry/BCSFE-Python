import sys
from bcsfe.core import io, server, country_code
from bcsfe.cli import main, color, dialog_creator, server_cli
from typing import Optional


class SaveManagement:
    def __init__(self):
        pass

    @staticmethod
    def save_save(save_file: "io.save.SaveFile"):
        """Save the save file."""
        if save_file.save_path is None:
            save_file.save_path = main.Main.save_save_dialog(save_file)

        if save_file.save_path is None:
            return

        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_dialog(save_file: "io.save.SaveFile"):
        """Save the save file."""
        save_file.save_path = main.Main.save_save_dialog(save_file)
        if save_file.save_path is None:
            return

        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_upload(save_file: "io.save.SaveFile"):
        """Upload the save file."""
        result = server.server_handler.ServerHandler(save_file).get_codes()
        SaveManagement.save_save(save_file)
        if result is not None:
            transfer_code, confirmation_code = result
            color.ColoredText.localize(
                "upload_result",
                transfer_code=transfer_code,
                confirmation_code=confirmation_code,
            )
        else:
            color.ColoredText.localize("upload_fail")

    @staticmethod
    def unban_account(save_file: "io.save.SaveFile"):
        server_handler = server.server_handler.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.ColoredText.localize("unban_success")
        else:
            color.ColoredText.localize("unban_fail")

    @staticmethod
    def adb_push(save_file: "io.save.SaveFile") -> "io.adb_handler.AdbHandler":
        """Push the save file to the device.

        Args:
            save_file (io.save.SaveFile): The save file to push.

        Returns:
            io.adb_handler.AdbHandler: The AdbHandler instance.
        """
        SaveManagement.save_save(save_file)
        adb_handler = io.adb_handler.AdbHandler()
        adb_handler.select_device()
        adb_handler.set_cc(save_file.cc)
        if save_file.save_path is None:
            return adb_handler
        result = adb_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("adb_push_success")
        else:
            color.ColoredText.localize("adb_push_fail", error=result.result)

        return adb_handler

    @staticmethod
    def adb_push_rerun(save_file: "io.save.SaveFile"):
        """Push the save file and rerun the game."""
        adb_handler = SaveManagement.adb_push(save_file)
        result = adb_handler.rerun_game()
        if result.success:
            color.ColoredText.localize("adb_rerun_success")
        else:
            color.ColoredText.localize("adb_rerun_fail", error=result.result)

    @staticmethod
    def export_save(save_file: "io.save.SaveFile"):
        """Export the save file to a json file."""
        data = save_file.to_dict()
        path = main.Main.save_json_dialog(data)
        if path is None:
            return
        data = io.json_file.JsonFile.from_object(data).to_data()
        data.to_file(path)
        color.ColoredText.localize("export_success", path=path)

    @staticmethod
    def init_save(save_file: "io.save.SaveFile"):
        """Create a new save file."""
        confirm = dialog_creator.YesNoInput().get_input_once("init_save_confirm")
        if not confirm:
            return
        save_file.init_save(save_file.game_version)
        color.ColoredText.localize("init_save_success")

    @staticmethod
    def upload_items(save_file: "io.save.SaveFile"):
        """Upload the items."""
        server_handler = server.server_handler.ServerHandler(save_file)
        success = server_handler.upload_meta_data()
        if success:
            color.ColoredText.localize("upload_items_success")
        else:
            color.ColoredText.localize("upload_items_fail")

    @staticmethod
    def select_save(exit_option: bool = False) -> Optional["io.save.SaveFile"]:
        """Select a save file.

        Returns:
            Optional[io.save.SaveFile]: The save file.
        """
        options = [
            "download_save",
            "select_save_file",
            "adb_pull_save",
            "load_save_data_json",
        ]
        if exit_option:
            options.append("exit")

        root_handler = io.root_handler.RootHandler()

        if root_handler.is_android():
            options[2] = "root_storage_pull_save"

        choice = (
            dialog_creator.ChoiceInput(
                options, options, [], {}, "save_load_option", True
            ).get_input_locale_while()[0]
            - 1
        )

        save_path = None

        if choice == 0:
            save_path = server_cli.ServerCLI().download_save()
        elif choice == 1:
            save_path = main.Main.load_save_file()
        elif choice == 2:
            handler = root_handler
            if not root_handler.is_android():
                handler = io.adb_handler.AdbHandler()
                if not handler.select_device():
                    return None

            ccs = handler.get_battlecats_ccs()
            cc = country_code.CountryCode.select_from_ccs(ccs)
            if cc is None:
                color.ColoredText.localize("no_cc_error")
                return None
            handler.set_cc(cc)
            if root_handler.is_android():
                key = "storage_pulling"
            else:
                key = "adb_pulling"
            color.ColoredText.localize(key, cc=cc)
            save_path, result = handler.save_locally()
            if save_path is None:
                if root_handler.is_android():
                    color.ColoredText.localize(
                        "storage_pull_fail", cc=cc, error=result.result
                    )
                else:
                    color.ColoredText.localize(
                        "adb_pull_fail", cc=cc, error=result.result
                    )
        elif choice == 3:
            save_path = main.Main.load_save_data_json()
        elif choice == 4 and exit_option:
            sys.exit(0)

        if save_path is None:
            return None

        try:
            save_file = io.save.SaveFile(save_path.read())
            save_file.save_path = save_path
        except Exception as e:
            color.ColoredText.localize("parse_save_error", error=e)
            return None

        return save_file

    @staticmethod
    def load_save(save_file: "io.save.SaveFile"):
        """Load the save file."""
        new_save_file = SaveManagement.select_save()
        if new_save_file is None:
            return
        save_file.load_save_file(new_save_file)
        color.ColoredText.localize("load_save_success")
