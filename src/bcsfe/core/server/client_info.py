from typing import Any
from bcsfe.core import io, crypto, country_code, game_version


class ClientInfo:
    def __init__(
        self, cc: country_code.CountryCode, game_version: game_version.GameVersion
    ):
        self.cc = cc
        self.game_version = game_version

    @staticmethod
    def from_save_file(save_file: io.save.SaveFile):
        return ClientInfo(save_file.cc, save_file.game_version)

    def get_client_info(self) -> dict[str, Any]:
        country_code = self.cc.get_client_info_code()

        data = {
            "clientInfo": {
                "client": {
                    "countryCode": country_code,
                    "version": self.game_version.game_version,
                },
                "device": {
                    "model": "SM-G955F",
                },
                "os": {
                    "type": "android",
                    "version": "9",
                },
            },
            "nonce": crypto.Random.get_hex_string(32),
        }
        return data
