from __future__ import annotations
from bcsfe import core
import bcsfe
from bcsfe.core import io
from bcsfe.cli import main, color, dialog_creator, server_cli
from bcsfe.core.country_code import CountryCode
from bcsfe.core.io.config import ConfigKey


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

        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

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

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_documents(save_file: core.SaveFile):
        """Save the save file to the documents folder.

        Args:
            save_file (core.SaveFile): The save file to save.
        """
        SaveManagement.upload_items_checker(save_file)
        save_file.save_path = core.SaveFile.get_saves_path().add("SAVE_DATA")
        save_file.to_file(save_file.save_path)
        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_upload(save_file: core.SaveFile):
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
    def unban_account(save_file: core.SaveFile):
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
    def create_new_account(save_file: core.SaveFile):
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
    def waydroid_push(save_file: core.SaveFile) -> core.WayDroidHandler | None:
        SaveManagement.save_save(save_file)
        try:
            waydroid_handler = core.WayDroidHandler()
        except core.AdbNotInstalled as e:
            core.AdbHandler.display_no_adb_error(e)
            return None
        except core.io.waydroid.WayDroidNotInstalledError as e:
            core.WayDroidHandler.display_waydroid_not_installed(e)
            return None

        if not waydroid_handler.adb_handler.select_device():
            return None

        if save_file.used_storage and save_file.package_name is not None:
            waydroid_handler.set_package_name(save_file.package_name)
        else:
            packages = waydroid_handler.get_battlecats_packages()
            package_name = SaveManagement.select_package_name(packages)
            if package_name is None:
                color.ColoredText.localize("no_package_name_error")
                return waydroid_handler
            waydroid_handler.set_package_name(package_name)

        if save_file.save_path is None:
            return waydroid_handler

        result = waydroid_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("waydroid_push_success")
        else:
            color.ColoredText.localize("waydroid_push_fail", error=result.result)

        return waydroid_handler

    @staticmethod
    def waydroid_push_rerun(save_file: core.SaveFile) -> core.AdbHandler | None:
        waydroid_handler = SaveManagement.waydroid_push(save_file)
        if not waydroid_handler:
            return
        if waydroid_handler.package_name is None:
            return
        result = waydroid_handler.rerun_game()
        if result.success:
            color.ColoredText.localize("waydroid_rerun_success")
        else:
            color.ColoredText.localize("waydroid_rerun_fail", error=result.result)

    @staticmethod
    def adb_push(save_file: core.SaveFile) -> core.AdbHandler | None:
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
        if save_file.used_storage and save_file.package_name is not None:
            adb_handler.set_package_name(save_file.package_name)
        else:
            packages = adb_handler.get_battlecats_packages()
            package_name = SaveManagement.select_package_name(packages)
            if package_name is None:
                color.ColoredText.localize("no_package_name_error")
                return adb_handler
            adb_handler.set_package_name(package_name)
        if save_file.save_path is None:
            return adb_handler
        result = adb_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("adb_push_success")
        else:
            color.ColoredText.localize("adb_push_fail", error=result.result)

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
            color.ColoredText.localize("root_push_not_android_error")
            return None
        if not root_handler.is_rooted():
            color.ColoredText.localize("not_rooted_error")
            return None
        if save_file.used_storage and save_file.package_name is not None:
            root_handler.set_package_name(save_file.package_name)
        else:
            packages = root_handler.get_battlecats_packages()
            package_name = SaveManagement.select_package_name(packages)
            if package_name is None:
                color.ColoredText.localize("no_package_name_error")
                return root_handler
            root_handler.set_package_name(package_name)
        if save_file.save_path is None:
            return root_handler
        result = root_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("root_push_success")
        else:
            color.ColoredText.localize("root_push_fail", error=result.result)

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
            color.ColoredText.localize("adb_rerun_success")
        else:
            color.ColoredText.localize("adb_rerun_fail", error=result.result)

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
            color.ColoredText.localize("root_rerun_success")
        else:
            color.ColoredText.localize("root_rerun_fail", error=result.result)

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
        color.ColoredText.localize("export_success", path=path)

    @staticmethod
    def init_save(save_file: core.SaveFile):
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
    def upload_items(save_file: core.SaveFile, check_strict: bool = True):
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
    def upload_items_checker(save_file: core.SaveFile, check_strict: bool = True):
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
            file = SaveManagement.load_save_file_path(
                core.Path(input_file), None, False, None
            )
            if file is None:
                return (None, True)
            return (file, False)

        options = [
            "download_save",
            "select_save_file",
            "load_from_documents",
            "adb_pull_save",
            "load_save_data_json",
            # "create_new_save",
        ]
        if starting_options:
            options.append("edit_config")
            options.append("update_external")
            options.append("exit")

        use_waydroid = core.core_data.config.get_bool(ConfigKey.USE_WAYDROID)
        if use_waydroid:
            options[3] = "waydroid_pull_save"

        root_handler = io.root_handler.RootHandler()

        if root_handler.is_android():
            options[3] = "root_storage_pull_save"

        choice = dialog_creator.ChoiceInput(
            options, options, [], {}, "save_load_option", True
        ).get_input_locale_while()
        if choice is None:
            return None, False
        choice = choice[0] - 1

        save_path = None
        cc: core.CountryCode | None = None
        used_storage = False
        package_name = None

        if choice == 0:
            data = server_cli.ServerCLI().download_save()
            if data is not None:
                save_path, cc = data
            else:
                save_path = None
        elif choice == 1:
            save_path = main.Main.load_save_file()
        elif choice == 2:
            save_path = core.SaveFile.get_saves_path().add("SAVE_DATA")
            if not save_path.exists():
                color.ColoredText.localize("save_file_not_found")
                return None, False
        elif choice == 3:
            handler = root_handler
            if not root_handler.is_android():
                if use_waydroid:
                    try:
                        handler = core.WayDroidHandler()
                    except core.AdbNotInstalled as e:
                        core.AdbHandler.display_no_adb_error(e)
                        return None, False
                    except core.io.waydroid.WayDroidNotInstalledError as e:
                        core.WayDroidHandler.display_waydroid_not_installed(e)
                        return None, False
                    if not handler.adb_handler.select_device():
                        return None, False
                else:
                    try:
                        handler = core.AdbHandler()
                    except core.AdbNotInstalled as e:
                        core.AdbHandler.display_no_adb_error(e)
                        return None, False
                    if not handler.select_device():
                        return None, False

            elif not root_handler.is_rooted():
                color.ColoredText.localize("not_rooted_error")
                return None, False

            package_names = handler.get_battlecats_packages()

            package_name = SaveManagement.select_package_name(package_names)
            if package_name is None:
                color.ColoredText.localize("no_package_name_error")
                return None, False
            handler.set_package_name(package_name)
            if root_handler.is_android():
                key = "storage_pulling"
            else:
                if use_waydroid:
                    key = "waydroid_pulling"
                else:
                    key = "adb_pulling"
            color.ColoredText.localize(key, package_name=package_name)
            save_path, result = handler.save_locally()
            if save_path is None:
                if root_handler.is_android():
                    key = "storage_pull_fail"
                else:
                    if use_waydroid:
                        key = "waydroid_pull_fail"
                    else:
                        key = "adb_pull_fail"
                color.ColoredText.localize(
                    key,
                    package_name=package_name,
                    error=result.result,
                )
            else:
                used_storage = True
        elif choice == 4:
            data = main.Main.load_save_data_json()
            if data is not None:
                save_path, cc = data
            else:
                save_path = None
        # elif choice == 5:
        #     color.ColoredText.localize("create_new_save_warning")
        #     cc = core.CountryCode.select()
        #     if cc is None:
        #         return None, False
        #     try:
        #         gv = core.GameVersion.from_string(
        #             color.ColoredInput().localize(
        #                 "game_version_dialog",
        #             )
        #         )
        #     except ValueError:
        #         color.ColoredText.localize("invalid_game_version")
        #         return None, False
        #     save = core.SaveFile(cc=cc, gv=gv, load=False)
        #     save_path = main.Main.save_save_dialog(save)
        #     if save_path is None:
        #         return None, False
        #     save.to_file(save_path)
        #     color.ColoredText.localize("create_new_save_success")

        elif choice == 5 and starting_options:
            core.core_data.config.edit_config()
        elif choice == 6 and starting_options:
            core.update_external_content()
        elif choice == 7 and starting_options:
            main.Main.exit_editor(check_temp=False)

        if save_path is None or not save_path.exists():
            return None, False

        return (
            SaveManagement.load_save_file_path(
                save_path, cc, used_storage, package_name
            ),
            False,
        )

    @staticmethod
    def load_save_file_path(
        save_path: core.Path,
        cc: CountryCode | None,
        used_storage: bool,
        package_name: str | None = None,
    ) -> core.SaveFile | None:
        color.ColoredText.localize("save_file_found", path=save_path)

        data = save_path.read()
        try:
            save_file = core.SaveFile(data, cc, package_name=package_name)
        except core.CantDetectSaveCCError:
            color.ColoredText.localize("cant_detect_cc")
            cc = core.CountryCode.select()
            if cc is None:
                return None
            try:
                save_file = core.SaveFile(data, cc)
            except Exception:
                tb = core.core_data.logger.get_traceback()
                data.reset_pos()
                color.ColoredText.localize(
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
            color.ColoredText.localize(
                "parse_save_error",
                error=tb,
                version=bcsfe.__version__,
                game_version=data.read_int(),
                country_code=save_file2.cc,
            )
            return None

        save_file.save_path = save_path
        save_file.save_path.copy_thread(save_file.get_default_path())
        save_file.used_storage = used_storage

        return save_file

    @staticmethod
    def select_package_name(package_names: list[str]) -> str | None:
        choice = dialog_creator.ChoiceInput.from_reduced(
            package_names,
            dialog="select_package_name",
            single_choice=True,
            localize_options=False,
        ).single_choice()
        if choice is None:
            return None
        return package_names[choice - 1]

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
        color.ColoredText.localize("load_save_success")
        return False

    @staticmethod
    def convert_save_cc(save_file: core.SaveFile):
        color.ColoredText.localize("cc_warning", current=save_file.cc)
        ccs_to_select = core.CountryCode.get_all()
        cc = core.CountryCode.select_from_ccs(ccs_to_select)
        if cc is None:
            return
        save_file.set_cc(cc)
        core.ServerHandler(save_file).create_new_account()
        core.core_data.init_data()
        color.ColoredText.localize("country_code_set", cc=cc)

    @staticmethod
    def convert_save_gv(save_file: core.SaveFile):
        color.ColoredText.localize(
            "gv_warning", current=save_file.game_version.to_string()
        )
        try:
            gv = core.GameVersion.from_string(
                color.ColoredInput().localize("game_version_dialog").strip()
            )
        except ValueError:
            color.ColoredText.localize("invalid_game_version")
            return
        save_file.set_gv(gv)
        core.core_data.init_data()
        color.ColoredText.localize("game_version_set", version=gv.to_string())
