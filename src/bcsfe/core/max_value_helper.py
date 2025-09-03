from __future__ import annotations
import enum
from typing import Any
from bcsfe import core


class MaxValueType(enum.Enum):
    CATFOOD = "catfood"
    XP = "xp"
    NORMAL_TICKETS = "normal_tickets"
    HUNDRED_MILLION_TICKETS = "100_million_tickets"
    RARE_TICKETS = "rare_tickets"
    PLATINUM_TICKETS = "platinum_tickets"
    LEGEND_TICKETS = "legend_tickets"
    NP = "np"
    LEADERSHIP = "leadership"
    BATTLE_ITEMS = "battle_items"
    CATAMINS = "catamins"
    CATSEYES = "catseyes"
    CATFRUIT = "catfruit"
    BASE_MATERIALS = "base_materials"
    LABYRINTH_MEDALS = "labyrinth_medals"
    TALENT_ORBS = "talent_orbs"
    TREASURE_LEVEL = "treasure_level"
    STAGE_CLEAR_COUNT = "stage_clear_count"
    ITF_TIMED_SCORE = "itf_timed_score"
    EVENT_TICKETS = "event_tickets"
    TREASURE_CHESTS = "treasure_chests"


class MaxValueHelper:
    def __init__(self):
        self.max_value_data = self.get_max_value_data()

    @staticmethod
    def convert_val_code(value_code: MaxValueType | str) -> str:
        if isinstance(value_code, MaxValueType):
            value_code = value_code.value
        return value_code

    def get_max_value_data(self) -> dict[str, Any]:
        file_path = core.Path("max_values.json", True)
        if not file_path.exists():
            return {}
        try:
            return core.JsonFile.from_data(file_path.read()).to_object()
        except core.JSONDecodeError:
            return {}

    def get(self, value_code: str | MaxValueType) -> int:
        try:
            return int(self.max_value_data.get(self.convert_val_code(value_code), 0))
        except ValueError:
            return 0

    def get_property(self, value_code: str | MaxValueType, property: str) -> int:
        try:
            return int(
                self.max_value_data.get(self.convert_val_code(value_code), {}).get(
                    property, 0
                )
            )
        except ValueError:
            return 0

    def get_old(self, value_code: str | MaxValueType) -> int:
        return self.get_property(value_code, "old")

    def get_new(self, value_code: str | MaxValueType) -> int:
        return self.get_property(value_code, "new")
