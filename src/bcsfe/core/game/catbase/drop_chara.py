from __future__ import annotations
from dataclasses import dataclass

from bcsfe import core


@dataclass
class Drop:
    stage_id: int
    save_id: int
    chara_id: int


class CharaDrop:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.drops = self.get_drops()

    def get_drops(self) -> list[Drop] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "drop_chara.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        drops: list[Drop] = []
        for line in csv.lines[1:]:
            drops.append(
                Drop(
                    stage_id=line[0].to_int(),
                    save_id=line[1].to_int(),
                    chara_id=line[2].to_int(),
                )
            )

        return drops

    def get_drop(self, stage_id: int) -> Drop | None:
        if self.drops is None:
            return None
        for drop in self.drops:
            if drop.stage_id == stage_id:
                return drop

        return None

    def get_drops_from_chara_id(self, chara_id: int) -> list[Drop] | None:
        if self.drops is None:
            return None
        drops: list[Drop] = []
        for drop in self.drops:
            if drop.chara_id == chara_id:
                drops.append(drop)

        return drops

    def unlock_drops_from_cat_id(self, cat_id: int) -> None:
        drops = self.get_drops_from_chara_id(cat_id)
        if drops is None:
            return
        for drop in drops:
            try:
                self.save_file.unit_drops[drop.save_id] = 1
            except IndexError:
                pass

    def remove_drops_from_cat_id(self, cat_id: int) -> None:
        drops = self.get_drops_from_chara_id(cat_id)
        if drops is None:
            return
        for drop in drops:
            try:
                self.save_file.unit_drops[drop.save_id] = 0
            except IndexError:
                pass
