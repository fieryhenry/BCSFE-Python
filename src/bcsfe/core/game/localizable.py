from typing import Optional
from bcsfe import core


class Localizable:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file
        self.localizable = self.get_localizable()

    def get_localizable(self) -> Optional[dict[str, str]]:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", "localizable.tsv")
        if data is None:
            return None
        csv = core.CSV(data, "\t")
        keys: dict[str, str] = {}
        for line in csv:
            try:
                keys[line[0].to_str()] = line[1].to_str()
            except IndexError:
                pass

        return keys

    def get(self, key: str) -> Optional[str]:
        if self.localizable is None:
            return None
        return self.localizable.get(key)

    def get_lang(self) -> Optional[str]:
        return self.get("lang")
