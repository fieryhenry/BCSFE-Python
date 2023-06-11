from bcsfe.core import io, server, country_code


class Localizable:
    def __init__(self, cc: country_code.CountryCode):
        self.cc = cc
        self.localizable = self.get_localizable()

    def get_localizable(self):
        gdg = server.game_data_getter.GameDataGetter(self.cc)
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
