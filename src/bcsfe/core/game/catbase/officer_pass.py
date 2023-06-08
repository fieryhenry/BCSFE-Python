from typing import Any
from bcsfe.core import game_version, io, game


class OfficerPass:
    def __init__(self, play_time: int):
        self.play_time = play_time

    @staticmethod
    def read(data: io.data.Data) -> "OfficerPass":
        play_time = data.read_int()
        return OfficerPass(play_time)

    def write(self, data: io.data.Data):
        data.write_int(self.play_time)

    def read_gold_pass(self, data: io.data.Data, gv: game_version.GameVersion):
        self.gold_pass = game.catbase.nyanko_club.NyankoClub.read(data, gv)

    def write_gold_pass(self, data: io.data.Data, gv: game_version.GameVersion):
        self.gold_pass.write(data, gv)

    def read_cat_data(self, data: io.data.Data):
        self.cat_id = data.read_short()
        self.cat_form = data.read_short()

    def write_cat_data(self, data: io.data.Data):
        data.write_short(self.cat_id)
        data.write_short(self.cat_form)

    def serialize(self) -> dict[str, Any]:
        return {
            "play_time": self.play_time,
            "gold_pass": self.gold_pass.serialize(),
            "cat_id": self.cat_id,
            "cat_form": self.cat_form,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "OfficerPass":
        officer_pass = OfficerPass(
            data.get("play_time", 0),
        )
        officer_pass.gold_pass = game.catbase.nyanko_club.NyankoClub.deserialize(
            data.get("gold_pass", {})
        )
        officer_pass.cat_id = data.get("cat_id", 0)
        officer_pass.cat_form = data.get("cat_form", 0)
        return officer_pass

    def __repr__(self):
        return f"OfficerPass({self.play_time}, {self.gold_pass}, {self.cat_id}, {self.cat_form})"

    def __str__(self):
        return self.__repr__()
