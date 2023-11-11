from typing import Any

from bcsfe import core
from bcsfe import scripting


class LoadSaveParser:
    def __init__(self, load_action: dict[str, Any]):
        self.data = load_action

    def load(self) -> "core.SaveFile":
        method = scripting.handle_string_field(self.data, "method")
        if method is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key("s!_missing_method_load")
            )
        if method == "adb-pull":
            return AdbPullSave(self.data).load()
        raise scripting.ParsingError(
            core.core_data.local_manager.get_key(
                "s!_unknown_method", method=method, valid_methods=["adb-pull"]
            )
        )


class LoadSaveParserBase:
    def __init__(self, data: dict[str, Any]):
        self.data = data

    def load(self) -> "core.SaveFile":
        ...


class AdbPullSave(LoadSaveParserBase):
    def load(self) -> "core.SaveFile":
        adb_handler = core.AdbHandler()
        device = scripting.handle_string_field(self.data, "device")
        if device is None:
            connected_devices = adb_handler.get_connected_devices()
            if len(connected_devices) == 0:
                raise scripting.ParsingError(
                    core.core_data.local_manager.get_key("s!_no_connected_devices")
                )
            device = connected_devices[0]

        cc = scripting.handle_string_field(self.data, "cc")
        if cc is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key("s!_missing_cc_pull")
            )
        cc = core.CountryCode.from_code(cc)

        adb_handler.set_device(device)
        adb_handler.set_cc(cc)
        save_path, result = adb_handler.save_locally()
        if save_path is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key("s!_failed_to_pull", error=result)
            )
        return core.SaveFile(save_path.read(), cc)
