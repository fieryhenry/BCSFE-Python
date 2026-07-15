from __future__ import annotations
from typing import Optional
from bcsfe import core
import bcsfe
from bcsfe.core import io
from bcsfe.cli import main, color, dialog_creator, server_cli
from bcsfe.core.country_code import CountryCode


class SaveManagement:
    def __init__(self):
        pass

    @staticmethod
    def save_save(save_file: core.SaveFile, check_strict: bool = True):
        """Save the save file without a dialog.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file, check_strict)

        if save_file.save_path is None:
            save_file.save_path = main.Main.save_save_dialog(save_file)

        if save_file.save_path is None:
            return

        try:
            save_file.to_file(save_file.save_path)
        except OSError as e:
            print(e)
            return

        color.color_print_key("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_dialog(save_file: core.SaveFile):
        """Save the save file with a dialog.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file)
        save_file.save_path = main.Main.save_save_dialog(save_file)
        if save_file.save_path is None:
            return

        save_file.to_file(save_file.save_path)

        color.color_print_key("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_data_dir(save_file: core.SaveFile):
        """Save the save file to the data folder.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file)
        save_file.save_path = core.SaveFile.get_save_path()
        save_file.to_file(save_file.save_path)
        color.color_print_key("save_success", path=save_file.save_path)

    @staticmethod
    def save_upload(save_file: core.SaveFile):
        """Save the save file and upload it to the server.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        if core.core_data.config.get_bool(core.ConfigKey.STRICT_BAN_PREVENTION):
            color.color_print_key("strict_ban_prevention_enabled")
            SaveManagement.create_new_account(save_file)

        result = core.ServerHandler(save_file).get_codes()
        if result is not None:
            SaveManagement.save_save(save_file, check_strict=False)
            transfer_code, confirmation_code = result
            color.color_print_key(
                "upload_result",
                transfer_code=transfer_code,
                confirmation_code=confirmation_code,
            )
        else:
            color.color_print_key("upload_fail")
            SaveManagement.save_save(save_file, check_strict=False)

    @staticmethod
    def unban_account(save_file: core.SaveFile):
        """Unban the account.

        Args:
            save_file (core.SaveFile): The save file to unban.
        """
        server_handler = core.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.color_print_key("unban_success")
        else:
            color.color_print_key("unban_fail")

    @staticmethod
    def create_new_account(save_file: core.SaveFile):
        """Create a new account.

        Args:
            save_file (core.SaveFile): The save file to create a new account.
        """
        server_handler = core.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.color_print_key("create_new_account_success")
        else:
            color.color_print_key("create_new_account_fail")

    @staticmethod
    def adb_push(
        save_file: core.SaveFile,
    ) -> core.AdbHandler | core.WayDroidHandler | None:
        """Push the save file to the device.

        Args:
            save_file (core.SaveFile): The save file to push.

        Returns:
            core.AdbHandler: The AdbHandler instance.
        """
        SaveManagement.save_save(save_file)
        try:
            adb_handler = core.AdbHandler()
        except core.AdbNotInstalled as e:
            core.AdbHandler.display_no_adb_error(e)
            return None
        success = adb_handler.select_device()
        if not success:
            return adb_handler
        device_id = adb_handler.get_device()
        if core.WayDroidHandler.is_waydroid(device_id):
            adb_handler = core.WayDroidHandler()
            adb_handler.adb_handler.set_device(device_id)
        if save_file.package_name is not None:
            adb_handler.set_package_name(save_file.package_name)
        else:
            packages = adb_handler.get_battlecats_packages()
            package_name = SaveManagement.select_package_name(packages)
            if package_name is None:
                color.color_print_key("no_package_name_error")
                return adb_handler
            adb_handler.set_package_name(package_name)
        if save_file.save_path is None:
            return adb_handler
        result = adb_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.color_print_key("adb_push_success")
        else:
            color.color_print_key("adb_push_fail", error=result.result)

        return adb_handler

    @staticmethod
    def root_push(save_file: core.SaveFile) -> core.RootHandler | None:
        """Push the save file to the device.

        Args:
            save_file (core.SaveFile): The save file to push.

        Returns:
            core.AdbHandler: The AdbHandler instance.
        """
        SaveManagement.save_save(save_file)
        root_handler = core.RootHandler()
        if not root_handler.is_android():
            color.color_print_key("root_push_not_android_error")
            return None
        if not root_handler.is_rooted():
            color.color_print_key("not_rooted_error")
            return None
        if save_file.package_name is not None:
            root_handler.set_package_name(save_file.package_name)
        else:
            packages = root_handler.get_battlecats_packages()
            package_name = SaveManagement.select_package_name(packages)
            if package_name is None:
                color.color_print_key("no_package_name_error")
                return root_handler
            root_handler.set_package_name(package_name)
        if save_file.save_path is None:
            return root_handler
        result = root_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.color_print_key("root_push_success")
        else:
            color.color_print_key("root_push_fail", error=result.result)

        return root_handler

    @staticmethod
    def adb_push_rerun(save_file: core.SaveFile):
        """Push the save file to the device and rerun the game.

        Args:
            save_file (core.SaveFile): The save file to push.
        """
        adb_handler = SaveManagement.adb_push(save_file)
        if not adb_handler:
            return
        if adb_handler.package_name is None:
            return
        result = adb_handler.rerun_game()
        if result.success:
            color.color_print_key("adb_rerun_success")
        else:
            color.color_print_key("adb_rerun_fail", error=result.result)

    @staticmethod
    def root_push_rerun(save_file: core.SaveFile):
        """Push the save file to the device and rerun the game.

        Args:
            save_file (core.SaveFile): The save file to push.
        """
        root_handler = SaveManagement.root_push(save_file)
        if not root_handler:
            return
        if root_handler.package_name is None:
            return
        result = root_handler.rerun_game()
        if result.success:
            color.color_print_key("root_rerun_success")
        else:
            color.color_print_key("root_rerun_fail", error=result.result)

    @staticmethod
    def export_save(save_file: core.SaveFile):
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
        color.color_print_key("export_success", path=path)

    @staticmethod
    def upload_items(save_file: core.SaveFile, check_strict: bool = True):
        """Upload the items to the server.

        Args:
            save_file (core.SaveFile): The save file to upload.
        """
        if (
            core.core_data.config.get_bool(core.ConfigKey.STRICT_BAN_PREVENTION)
            and check_strict
        ):
            color.color_print_key("strict_ban_prevention_enabled")
            SaveManagement.create_new_account(save_file)

        server_handler = core.ServerHandler(save_file)
        success = server_handler.upload_meta_data()
        if success:
            color.color_print_key("upload_items_success")
        else:
            color.color_print_key("upload_items_fail")

    @staticmethod
    def upload_items_checker(save_file: core.SaveFile, check_strict: bool = True):
        managed_items = core.BackupMetaData(save_file).get_managed_items()
        if not managed_items:
            return
        should_upload = dialog_creator.yes_no_key("upload_items_checker_confirm")
        if not should_upload:
            return

        SaveManagement.upload_items(save_file, check_strict)

    @staticmethod
    def pull_android(root_handler: core.RootHandler):
        if not root_handler.is_rooted():
            color.color_print_key("not_rooted_error")
            return None

        return SaveManagement.pull_root(root_handler)

    @staticmethod
    def pull_adb():
        try:
            handler = core.AdbHandler()
        except core.AdbNotInstalled as e:
            core.AdbHandler.display_no_adb_error(e)
            return None
        if not handler.select_device():
            return None

        device_id = handler.get_device()

        if core.WayDroidHandler.is_waydroid(device_id):
            handler = core.WayDroidHandler()
            handler.adb_handler.set_device(device_id)

        return SaveManagement.pull_root(handler)

    @staticmethod
    def pull_root(handler: core.RootHandler):
        package_names = handler.get_battlecats_packages()

        package_name = SaveManagement.select_package_name(package_names)
        if package_name is None:
            color.color_print_key("no_package_name_error")
            return None
        handler.set_package_name(package_name)
        if handler.is_android():
            key = "storage_pulling"
        else:
            key = "adb_pulling"
        color.color_print_key(key, package_name=package_name)
        save_path, result = handler.save_locally()
        if save_path is None:
            if handler.is_android():
                key = "storage_pull_fail"
            else:
                key = "adb_pull_fail"
            color.color_print_key(
                key,
                package_name=package_name,
                error=result.result,
            )
            return
        return SaveManagement.load_save_file_path(
            save_path, package_name=handler.get_package_name()
        )

    @staticmethod
    def select_save(
        starting_options: bool = False, input_file: str | None = None
    ) -> tuple[core.SaveFile | None, bool]:
        """Select a new save file.

        Args:
            starting_options (bool, optional): Whether to add the starting specific options. Defaults to False.


        Returns:
            core.SaveFile | None: The save file.
        """
        if input_file is not None:
            file = SaveManagement.load_save_file_path(core.Path(input_file), None, None)
            if file is None:
                return (None, True)
            return (file[0], False)

        root_handler = io.root_handler.RootHandler()

        root_action = dialog_creator.Action[
            Optional[tuple[core.SaveFile, core.Path]]
        ].new_key(
            "adb_pull_save",
            lambda _: SaveManagement.pull_adb(),
        )
        if root_handler.is_android():
            root_action = dialog_creator.Action[
                Optional[tuple[core.SaveFile, core.Path]]
            ].new_key(
                "root_storage_pull",
                lambda _: SaveManagement.pull_android(root_handler),
            )

        actions = (
            dialog_creator.Actions[Optional[tuple[core.SaveFile, core.Path]]]
            .new()
            .add_new_key(
                "download_save",
                lambda _: core.map_opt(
                    server_cli.ServerCLI().download_save(),
                    lambda vaaa: SaveManagement.load_save_file_path(vaaa[0], vaaa[1]),
                ),
            )
            .add_new_key(
                "select_save_file",
                lambda _: core.map_opt(
                    main.Main.load_save_file(), SaveManagement.load_save_file_path
                ),
            )
        )
        if core.SaveFile.get_save_path().exists():
            actions.add_new_key(
                "load_from_documents",
                lambda _: core.map_opt(
                    core.SaveFile.get_save_path(), SaveManagement.load_save_file_path
                ),
                path=core.SaveFile.get_save_path(),
            )

        actions.add(root_action).add_new_key(
            "load_save_data_json",
            lambda _: core.map_opt(
                main.Main.load_save_data_json(),
                lambda v: SaveManagement.load_save_file_path(v[0], v[1]),
            ),
        )
        if starting_options:
            actions = (
                actions.add_new_key(
                    "edit_config", lambda _: core.core_data.config.edit_config()
                )
                .add_new_key(
                    "update_external", lambda _: core.update_external_content()
                )
                .add_new_key("manage_game_data", lambda _: core.manage_game_data())
                .add_new_key("exit", lambda _: main.Main.exit_editor(check_temp=False))
            )

        res = dialog_creator.single_select_key(
            actions,
            "save_load_option",
        )
        if res is None:
            return None, False

        save_data, _ = res

        return (
            save_data,
            False,
        )

    @staticmethod
    def load_save_file_path(
        save_path: core.Path,
        cc: CountryCode | None = None,
        package_name: str | None = None,
    ) -> tuple[core.SaveFile, core.Path] | None:
        color.color_print_key("save_file_found", path=save_path)

        data = save_path.read()
        try:
            save_file = core.SaveFile(data, cc, package_name=package_name)
        except core.CantDetectSaveCCError:
            color.color_print_key("cant_detect_cc")
            cc = core.CountryCode.select()
            if cc is None:
                return None
            try:
                save_file = core.SaveFile(data, cc)
            except Exception:
                tb = core.core_data.logger.get_traceback()
                data.reset_pos()
                color.color_print_key(
                    "parse_save_error",
                    error=tb,
                    version=bcsfe.__version__,
                    game_version=data.read_int(),
                    country_code=cc.get_code(),
                )
                return None

        except Exception:
            tb = core.core_data.logger.get_traceback()
            save_file2 = core.SaveFile(data, cc, load=False)
            data.reset_pos()
            color.color_print_key(
                "parse_save_error",
                error=tb,
                version=bcsfe.__version__,
                game_version=data.read_int(),
                country_code=save_file2.cc,
            )
            return None

        save_file.save_path = save_path
        backup_path = save_file.get_default_path()
        try:
            save_file.save_path.copy_thread(backup_path)
        except Exception as e:
            print(e)

        return save_file, backup_path

    @staticmethod
    def select_package_name(package_names: list[str]) -> str | None:
        return dialog_creator.basic_pick_key(package_names, "select_package_name")

    @staticmethod
    def load_save(save_file: core.SaveFile):
        """Load a new save file.

        Args:
            save_file (core.SaveFile): The current save file.
        """
        SaveManagement.upload_items_checker(save_file)
        new_save_file, stop = SaveManagement.select_save()
        if new_save_file is None:
            return stop
        save_file.load_save_file(new_save_file)
        core.core_data.init_data()
        color.color_print_key("load_save_success")
        return False

    @staticmethod
    def convert_save_cc(save_file: core.SaveFile):
        color.color_print_key("cc_warning", current=save_file.cc)
        ccs_to_select = core.CountryCode.get_all()
        cc = core.CountryCode.select_from_ccs(ccs_to_select)
        if cc is None:
            return
        save_file.set_cc(cc)
        core.ServerHandler(save_file).create_new_account()
        core.core_data.init_data()
        color.color_print_key("country_code_set", cc=cc)

    @staticmethod
    def convert_save_gv(save_file: core.SaveFile):
        color.color_print_key("gv_warning", current=save_file.game_version.to_string())
        try:
            gv = core.GameVersion.from_string(
                color.color_input_key("game_version_dialog").strip()
            )
        except ValueError:
            color.color_print_key("invalid_game_version")
            return
        save_file.set_gv(gv)
        core.core_data.init_data()
        color.color_print_key("game_version_set", version=gv.to_string())
