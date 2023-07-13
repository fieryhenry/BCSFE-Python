from typing import Optional
from bcsfe import core


class Localizable:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file
        self.localizable = self.get_localizable()

    def get_localizable(self):
        gdg = core.GameDataGetter(self.save_file)
        data = gdg.download("resLocal", "localizable.tsv")
        csv = core.CSV(data, "\t")
        keys: dict[str, str] = {}
        for line in csv:
            try:
                keys[line[0].to_str()] = line[1].to_str()
            except IndexError:
                pass

        return keys

    def get(self, key: str):
        return self.localizable.get(key, key)

    def get_optional(self, key: str) -> Optional[str]:
        return self.localizable.get(key)

    def get_lang(self) -> str:
        return self.get("lang")
