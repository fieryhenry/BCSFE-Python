from bcsfe import core
from bcsfe.core import io
from bcsfe.cli import main, color, dialog_creator, server_cli
from typing import Optional


class SaveManagement:
    def __init__(self):
        pass

    @staticmethod
    def save_save(save_file: "core.SaveFile", check_strict: bool = True):
        """Save the save file without a dialog.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file, check_strict)

        if save_file.save_path is None:
            save_file.save_path = main.Main.save_save_dialog(save_file)

        if save_file.save_path is None:
            return

        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_dialog(save_file: "core.SaveFile"):
        """Save the save file with a dialog.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file)
        save_file.save_path = main.Main.save_save_dialog(save_file)
        if save_file.save_path is None:
            return

        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_upload(save_file: "core.SaveFile"):
        """Save the save file and upload it to the server.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        if core.core_data.config.get_bool(core.ConfigKey.STRICT_BAN_PREVENTION):
            color.ColoredText.localize("strict_ban_prevention_enabled")
            SaveManagement.create_new_account(save_file)

        result = core.ServerHandler(save_file).get_codes()
        if result is not None:
            SaveManagement.save_save(save_file, check_strict=False)
            transfer_code, confirmation_code = result
            color.ColoredText.localize(
                "upload_result",
                transfer_code=transfer_code,
                confirmation_code=confirmation_code,
            )
        else:
            color.ColoredText.localize("upload_fail")
            SaveManagement.save_save(save_file, check_strict=False)

    @staticmethod
    def unban_account(save_file: "core.SaveFile"):
        """Unban the account.

        Args:
            save_file (core.SaveFile): The save file to unban.
        """
        server_handler = core.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.ColoredText.localize("unban_success")
        else:
            color.ColoredText.localize("unban_fail")

    @staticmethod
    def create_new_account(save_file: "core.SaveFile"):
        """Create a new account.

        Args:
            save_file (core.SaveFile): The save file to create a new account.
        """
        server_handler = core.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.ColoredText.localize("create_new_account_success")
        else:
            color.ColoredText.localize("create_new_account_fail")

    @staticmethod
    def adb_push(save_file: "core.SaveFile") -> "core.AdbHandler":
        """Push the save file to the device.

        Args:
            save_file (core.SaveFile): The save file to push.

        Returns:
            core.AdbHandler: The AdbHandler instance.
        """
        SaveManagement.save_save(save_file)
        adb_handler = core.AdbHandler()
        adb_handler.select_device()
        if save_file.used_storage:
            adb_handler.set_cc(save_file.real_cc)
        else:
            ccs = adb_handler.get_battlecats_ccs()
            cc = core.CountryCode.select_from_ccs(ccs)
            if cc is None:
                color.ColoredText.localize("no_cc_error")
                return adb_handler
            adb_handler.set_cc(cc)
        if save_file.save_path is None:
            return adb_handler
        result = adb_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("adb_push_success")
        else:
            color.ColoredText.localize("adb_push_fail", error=result.result)

        return adb_handler

    @staticmethod
    def adb_push_rerun(save_file: "core.SaveFile"):
        """Push the save file to the device and rerun the game.

        Args:
            save_file (core.SaveFile): The save file to push.
        """
        adb_handler = SaveManagement.adb_push(save_file)
        if adb_handler.cc is None:
            return
        result = adb_handler.rerun_game()
        if result.success:
            color.ColoredText.localize("adb_rerun_success")
        else:
            color.ColoredText.localize("adb_rerun_fail", error=result.result)

    @staticmethod
    def export_save(save_file: "core.SaveFile"):
        """Export the save file to a json file.

        Args:
            save_file (core.SaveFile): The save file to export.
        """
        data = save_file.to_dict()
        path = main.Main.save_json_dialog(data)
        if path is None:
            return
        data = core.JsonFile.from_object(data).to_data()
        data.to_file(path)
        color.ColoredText.localize("export_success", path=path)

    @staticmethod
    def init_save(save_file: "core.SaveFile"):
        """Initialize the save file to a new save file.

        Args:
            save_file (core.SaveFile): The save file to initialize.
        """
        confirm = dialog_creator.YesNoInput().get_input_once("init_save_confirm")
        if not confirm:
            return
        save_file.init_save(save_file.game_version)
        color.ColoredText.localize("init_save_success")

    @staticmethod
    def upload_items(save_file: "core.SaveFile", check_strict: bool = True):
        """Upload the items to the server.

        Args:
            save_file (core.SaveFile): The save file to upload.
        """
        if (
            core.core_data.config.get_bool(core.ConfigKey.STRICT_BAN_PREVENTION)
            and check_strict
        ):
            color.ColoredText.localize("strict_ban_prevention_enabled")
            SaveManagement.create_new_account(save_file)

        server_handler = core.ServerHandler(save_file)
        success = server_handler.upload_meta_data()
        if success:
            color.ColoredText.localize("upload_items_success")
        else:
            color.ColoredText.localize("upload_items_fail")

    @staticmethod
    def upload_items_checker(save_file: "core.SaveFile", check_strict: bool = True):
        managed_items = core.BackupMetaData(save_file).get_managed_items()
        if not managed_items:
            return
        should_upload = dialog_creator.YesNoInput().get_input_once(
            "upload_items_checker_confirm"
        )
        if not should_upload:
            return
        SaveManagement.upload_items(save_file, check_strict)

    @staticmethod
    def select_save(starting_options: bool = False) -> Optional["core.SaveFile"]:
        """Select a new save file.

        Args:
            starting_options (bool, optional): Whether to add the starting specific options. Defaults to False.


        Returns:
            Optional[core.SaveFile]: The save file.
        """
        options = [
            "download_save",
            "select_save_file",
            "adb_pull_save",
            "load_save_data_json",
        ]
        if starting_options:
            options.append("edit_config")
            options.append("update_external")
            options.append("exit")

        root_handler = io.root_handler.RootHandler()

        if root_handler.is_android():
            options[2] = "root_storage_pull_save"

        choice = dialog_creator.ChoiceInput(
            options, options, [], {}, "save_load_option", True
        ).get_input_locale_while()
        if choice is None:
            return None
        choice = choice[0] - 1

        save_path = None
        cc: Optional[core.CountryCode] = None
        used_storage = False

        if choice == 0:
            data = server_cli.ServerCLI().download_save()
            if data is not None:
                save_path, cc = data
            else:
                save_path = None
        elif choice == 1:
            save_path = main.Main.load_save_file()
        elif choice == 2:
            handler = root_handler
            if not root_handler.is_android():
                handler = core.AdbHandler()
                if not handler.select_device():
                    return None

            ccs = handler.get_battlecats_ccs()
            cc = core.CountryCode.select_from_ccs(ccs)
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
            else:
                used_storage = True
        elif choice == 3:
            data = main.Main.load_save_data_json()
            if data is not None:
                save_path, cc = data
            else:
                save_path = None
        elif choice == 4 and starting_options:
            core.core_data.config.edit_config()
        elif choice == 5 and starting_options:
            core.update_external_content()
        elif choice == 6 and starting_options:
            main.Main.exit_editor(check_temp=False)

        if save_path is None or not save_path.exists():
            return None

        try:
            save_file = core.SaveFile(save_path.read(), cc)
        except core.CantDetectSaveCCError:
            color.ColoredText.localize("cant_detect_cc")
            cc = core.CountryCode.select()
            if cc is None:
                return None
            try:
                save_file = core.SaveFile(save_path.read(), cc)
            except Exception:
                tb = core.core_data.logger.get_traceback()
                color.ColoredText.localize("parse_save_error", error=tb)
                return None

        except Exception:
            tb = core.core_data.logger.get_traceback()
            color.ColoredText.localize("parse_save_error", error=tb)
            return None

        save_file.save_path = save_path
        save_file.save_path.copy_thread(save_file.get_default_path())
        save_file.used_storage = used_storage

        return save_file

    @staticmethod
    def load_save(save_file: "core.SaveFile"):
        """Load a new save file.

        Args:
            save_file (core.SaveFile): The current save file.
        """
        SaveManagement.upload_items_checker(save_file)
        new_save_file = SaveManagement.select_save()
        if new_save_file is None:
            return
        save_file.load_save_file(new_save_file)
        color.ColoredText.localize("load_save_success")

    @staticmethod
    def convert_save_cc(save_file: "core.SaveFile"):
        color.ColoredText.localize("cc_warning", current=save_file.cc)
        ccs_to_select = core.CountryCode.get_all()
        cc = core.CountryCode.select_from_ccs(ccs_to_select)
        if cc is None:
            return
        save_file.set_cc(cc)
        core.ServerHandler(save_file).create_new_account()
        color.ColoredText.localize("country_code_set", cc=cc)

    @staticmethod
    def convert_save_gv(save_file: "core.SaveFile"):
        color.ColoredText.localize(
            "gv_warning", current=save_file.game_version.to_string()
        )
        try:
            gv = core.GameVersion.from_string(
                color.ColoredInput().localize("game_version_dialog")
            )
        except ValueError:
            color.ColoredText.localize("invalid_game_version")
            return
        save_file.set_gv(gv)
        color.ColoredText.localize("game_version_set", version=gv.to_string())
