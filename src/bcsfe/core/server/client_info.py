from __future__ import annotations
from typing import Any
from bcsfe import core


class ClientInfo:
    def __init__(self, cc: core.CountryCode, gv: core.GameVersion):
        self.cc = cc
        self.gv = gv

    @staticmethod
    def from_save_file(save_file: core.SaveFile):
        return ClientInfo(save_file.cc, save_file.game_version)

    def get_client_info(self) -> dict[str, Any]:
        cc = self.cc.get_client_info_code()

        data = {
            "clientInfo": {
                "client": {
                    "countryCode": cc,
                    "version": self.gv.game_version,
                },
                "device": {
                    "model": "SM-G955F",
                },
                "os": {
                    "type": "android",
                    "version": "9",
                },
            },
            "nonce": core.Random.get_hex_string(32),
        }
        return data
