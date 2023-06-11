from typing import Any
from bcsfe.core import io, game_version
from bcsfe.cli import dialog_creator


class Gatya:
    def __init__(self, rare_seed: int, normal_seed: int):
        self.rare_seed = rare_seed
        self.normal_seed = normal_seed
        self.event_seed = 0
        self.stepup_stage_3_cooldown = 0
        self.previous_normal_roll = 0
        self.previous_normal_roll_type = 0
        self.previous_rare_roll = 0
        self.previous_rare_roll_type = 0
        self.unknown1 = False
        self.roll_single = False
        self.roll_multi = False
        self.trade_progress = 0
        self.step_up_stages: dict[int, int] = {}
        self.stepup_durations: dict[int, float] = {}

    @staticmethod
    def init() -> "Gatya":
        return Gatya(0, 0)

    @staticmethod
    def read_rare_normal_seed(
        data: io.data.Data, gv: "game_version.GameVersion"
    ) -> "Gatya":
        if gv < 33:
            return Gatya(data.read_long(), data.read_long())
        return Gatya(data.read_int(), data.read_int())

    def read_event_seed(self, data: io.data.Data, gv: "game_version.GameVersion"):
        if gv < 33:
            self.event_seed = data.read_long()
        else:
            self.event_seed = data.read_int()

    def write_rare_normal_seed(self, data: io.data.Data):
        data.write_int(self.rare_seed)
        data.write_int(self.normal_seed)

    def write_event_seed(self, data: io.data.Data):
        data.write_int(self.event_seed)

    def read2(self, data: io.data.Data):
        self.stepup_stage_3_cooldown = data.read_int()
        self.previous_normal_roll = data.read_int()
        self.previous_normal_roll_type = data.read_int()
        self.previous_rare_roll = data.read_int()
        self.previous_rare_roll_type = data.read_int()
        self.unknown1 = data.read_bool()
        self.roll_single = data.read_bool()
        self.roll_multi = data.read_bool()

    def write2(self, data: io.data.Data):
        data.write_int(self.stepup_stage_3_cooldown)
        data.write_int(self.previous_normal_roll)
        data.write_int(self.previous_normal_roll_type)
        data.write_int(self.previous_rare_roll)
        data.write_int(self.previous_rare_roll_type)
        data.write_bool(self.unknown1)
        data.write_bool(self.roll_single)
        data.write_bool(self.roll_multi)

    def read_trade_progress(self, data: io.data.Data):
        self.trade_progress = data.read_int()

    def write_trade_progress(self, data: io.data.Data):
        data.write_int(self.trade_progress)

    def read_stepup(self, data: io.data.Data):
        self.step_up_stages: dict[int, int] = {}
        total = data.read_int()
        for _ in range(total):
            key = data.read_int()
            self.step_up_stages[key] = data.read_int()

        self.stepup_durations: dict[int, float] = {}
        total = data.read_int()
        for _ in range(total):
            key = data.read_int()
            self.stepup_durations[key] = data.read_double()

    def write_stepup(self, data: io.data.Data):
        data.write_int(len(self.step_up_stages))
        for id, stage in self.step_up_stages.items():
            data.write_int(id)
            data.write_int(stage)

        data.write_int(len(self.stepup_durations))
        for id, duration in self.stepup_durations.items():
            data.write_int(id)
            data.write_double(duration)

    def serialize(self) -> dict[str, Any]:
        return {
            "rare_seed": self.rare_seed,
            "normal_seed": self.normal_seed,
            "stepup_stage_3_cooldown": self.stepup_stage_3_cooldown,
            "previous_normal_roll": self.previous_normal_roll,
            "previous_normal_roll_type": self.previous_normal_roll_type,
            "previous_rare_roll": self.previous_rare_roll,
            "previous_rare_roll_type": self.previous_rare_roll_type,
            "unknown1": self.unknown1,
            "roll_single": self.roll_single,
            "roll_multi": self.roll_multi,
            "trade_progress": self.trade_progress,
            "event_seed": self.event_seed,
            "step_up_stages": self.step_up_stages,
            "stepup_durations": self.stepup_durations,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Gatya":
        gatya = Gatya(data.get("rare_seed", 0), data.get("normal_seed", 0))
        gatya.stepup_stage_3_cooldown = data.get("stepup_stage_3_cooldown", 0)
        gatya.previous_normal_roll = data.get("previous_normal_roll", 0)
        gatya.previous_normal_roll_type = data.get("previous_normal_roll_type", 0)
        gatya.previous_rare_roll = data.get("previous_rare_roll", 0)
        gatya.previous_rare_roll_type = data.get("previous_rare_roll_type", 0)
        gatya.unknown1 = data.get("unknown1", False)
        gatya.roll_single = data.get("roll_single", False)
        gatya.roll_multi = data.get("roll_multi", False)
        gatya.trade_progress = data.get("trade_progress", 0)
        gatya.event_seed = data.get("event_seed", 0)
        gatya.step_up_stages = data.get("step_up_stages", {})
        gatya.stepup_durations = data.get("stepup_durations", {})
        return gatya

    def __repr__(self) -> str:
        return f"Gatya({self.serialize()})"

    def __str__(self) -> str:
        return f"Gatya({self.serialize()})"

    def edit_rare_gatya_seed(self):
        self.rare_seed = dialog_creator.SingleEditor(
            "rare_gatya_seed",
            self.rare_seed,
            None,
            localized_item=True,
        ).edit()

    def edit_normal_gatya_seed(self):
        self.normal_seed = dialog_creator.SingleEditor(
            "normal_gatya_seed",
            self.normal_seed,
            None,
            localized_item=True,
        ).edit()

    def edit_event_gatya_seed(self):
        self.event_seed = dialog_creator.SingleEditor(
            "event_gatya_seed",
            self.event_seed,
            None,
            localized_item=True,
        ).edit()
