from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color


class OfficerPass:
    def __init__(self, play_time: int):
        self.play_time = play_time
        self.gold_pass = core.NyankoClub.init()
        self.cat_id = 0
        self.cat_form = 0

    @staticmethod
    def init() -> OfficerPass:
        return OfficerPass(0)

    @staticmethod
    def read(data: core.Data) -> OfficerPass:
        play_time = data.read_int()
        return OfficerPass(play_time)

    def write(self, data: core.Data):
        if self.play_time > 2**31 - 1:
            self.play_time = 2**31 - 1
        data.write_int(self.play_time)

    def read_gold_pass(self, data: core.Data, gv: core.GameVersion):
        self.gold_pass = core.NyankoClub.read(data, gv)

    def write_gold_pass(self, data: core.Data, gv: core.GameVersion):
        self.gold_pass.write(data, gv)

    def read_cat_data(self, data: core.Data):
        self.cat_id = data.read_short()
        self.cat_form = data.read_short()

    def write_cat_data(self, data: core.Data):
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
    def deserialize(data: dict[str, Any]) -> OfficerPass:
        officer_pass = OfficerPass(
            data.get("play_time", 0),
        )
        officer_pass.gold_pass = core.NyankoClub.deserialize(
            data.get("gold_pass", {})
        )
        officer_pass.cat_id = data.get("cat_id", 0)
        officer_pass.cat_form = data.get("cat_form", 0)
        return officer_pass

    def __repr__(self):
        return f"OfficerPass({self.play_time}, {self.gold_pass}, {self.cat_id}, {self.cat_form})"

    def __str__(self):
        return self.__repr__()

    def reset(self, save_file: core.SaveFile):
        self.cat_id = 0
        self.cat_form = 0
        self.play_time = 0
        self.gold_pass.remove_gold_pass(save_file)

    @staticmethod
    def fix_crash(save_file: core.SaveFile):
        officer_pass = save_file.officer_pass
        officer_pass.reset(save_file)

        color.ColoredText.localize("officer_pass_fixed")
