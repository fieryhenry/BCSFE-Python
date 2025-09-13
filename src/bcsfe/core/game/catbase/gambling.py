from __future__ import annotations
from bcsfe import core
from typing import Any

from bcsfe.cli import color


class GamblingEvent:
    def __init__(
        self,
        completed: dict[int, bool],
        values: dict[int, dict[int, int]],
        start_times: dict[int, int | float],
    ):
        self.completed = completed
        self.values = values
        self.start_times = start_times

    @staticmethod
    def init() -> GamblingEvent:
        return GamblingEvent({}, {}, {})

    @staticmethod
    def read(data: core.Data, game_version: core.GameVersion) -> GamblingEvent:
        total = data.read_short()
        completed: dict[int, bool] = {}

        for _ in range(total):
            key = data.read_short()
            completed[key] = data.read_bool()

        total = data.read_short()
        values: dict[int, dict[int, int]] = {}

        for _ in range(total):
            key = data.read_short()
            if key not in values:
                values[key] = {}

            total2 = data.read_short()
            for _ in range(total2):
                key2 = data.read_short()

                values[key][key2] = data.read_short()

        total = data.read_short()
        start_times: dict[int, int | float] = {}

        for _ in range(total):
            key = data.read_short()

            if game_version < 90100:
                value = data.read_double()
            else:
                value = data.read_int()

            start_times[key] = value

        return GamblingEvent(completed, values, start_times)

    def write(self, data: core.Data, game_version: core.GameVersion):
        data.write_short(len(self.completed))
        data.write_short_bool_dict(self.completed, write_length=False)

        data.write_short(len(self.values))

        for key, value in self.values.items():
            data.write_short(key)
            data.write_short(len(value))

            for key2, value2 in value.items():
                data.write_short(key2)
                data.write_short(value2)

        data.write_short(len(self.start_times))
        for key, value in self.start_times.items():
            data.write_short(key)

            # this is a bad conversion, since float is timestamp i assume and int as the date as YYYMMDD. FIXME
            if game_version < 90100:
                data.write_double(float(value))
            else:
                data.write_int(int(value))

    def serialize(self) -> dict[str, Any]:
        return {
            "completed": self.completed,
            "values": self.values,
            "start_times": self.start_times,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> GamblingEvent:
        return GamblingEvent(
            data.get("completed", {}),
            data.get("values", {}),
            data.get("start_times", {}),
        )

    def reset(self):
        self.completed = {}
        self.values = {}
        # TODO: check start times
        self.start_times = {}

    @staticmethod
    def reset_events(save_file: core.SaveFile):
        save_file.wildcat_slots.reset()
        color.ColoredText.localize("reset_wildcat_slots")
        save_file.cat_scratcher.reset()
        color.ColoredText.localize("reset_cat_scratcher")
