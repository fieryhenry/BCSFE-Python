from typing import Optional
from bcsfe.core import io, server


class Localizable:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file
        self.localizable = self.get_localizable()

    def get_localizable(self):
        gdg = server.game_data_getter.GameDataGetter(self.save_file)
        data = gdg.download("resLocal", "localizable.tsv")
        csv = io.bc_csv.CSV(data, "\t")
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
