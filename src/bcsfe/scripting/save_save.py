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
        if method == "adb-push":
            AdbPushSave(self.data).save()
            return
        raise scripting.ParsingError(f"Unknown method: {method}")


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

        adb_handler = core.AdbHandler()
        adb_handler.set_device(device)
        adb_handler.set_cc(cc)
        result = adb_handler.load_save(scripting.context.get_save())
        if not result.success:
            raise scripting.ParsingError(f"Failed to save locally: {result.result}")
