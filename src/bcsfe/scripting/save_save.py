from typing import Any

from bcsfe import core
from bcsfe import scripting


class SaveSaveParser:
    def __init__(self, save_action: dict[str, Any]):
        self.data = save_action

    def save(self):
        method = scripting.handle_string_field(self.data, "method")
        if method is None:
            raise scripting.ParsingError("Missing method")

        managed_items = self.data.get("managed-items")
        if managed_items:
            self.handle_managed_items(managed_items)

        if method == "adb-push":
            AdbPushSave(self.data).save()
            return
        raise scripting.ParsingError(f"Unknown method: {method}")

    def handle_managed_items(self, managed_items: dict[str, Any]):
        enabled = scripting.handle_bool_field(managed_items, "enabled")
        if enabled is None:
            enabled = True
        should_print = scripting.handle_bool_field(managed_items, "print")
        if should_print is None:
            should_print = False
        allow_iq_change = scripting.handle_bool_field(managed_items, "allow-iq-change")
        if allow_iq_change is None:
            allow_iq_change = False

        if enabled:
            loop_count = 0
            while True:
                save_managed_items = core.BackupMetaData(
                    scripting.context.get_save()
                ).get_managed_items()
                if save_managed_items:
                    server_handler = core.ServerHandler(
                        scripting.context.get_save(), should_print
                    )
                    success = server_handler.upload_meta_data()
                    if not success:
                        if not allow_iq_change:
                            raise scripting.ParsingError(
                                core.core_data.local_manager.get_key(
                                    "s!_failed_to_upload_meta"
                                )
                            )
                        server_handler.create_new_account()
                        loop_count += 1
                        if loop_count > 1:
                            raise scripting.ParsingError(
                                core.core_data.local_manager.get_key(
                                    "s!_failed_to_upload_meta"
                                )
                            )
                        continue
                break


class SaveSaveParserBase:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def save(self):
        ...


class AdbPushSave(SaveSaveParserBase):
    def save(self):
        device = scripting.handle_string_field(self.data, "device")
        if device is None:
            raise scripting.ParsingError("Missing device")
        cc = scripting.handle_string_field(self.data, "cc")
        if cc is None:
            cc = scripting.context.get_save().real_cc
        else:
            cc = core.CountryCode.from_code(cc)

        rerun = scripting.handle_bool_field(self.data, "rerun")
        if rerun is None:
            rerun = False

        adb_handler = core.AdbHandler()
        adb_handler.set_device(device)
        adb_handler.set_cc(cc)
        result = adb_handler.load_save(scripting.context.get_save(), rerun)
        if not result.success:
            raise scripting.ParsingError(f"Failed to save locally: {result.result}")
