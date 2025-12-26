from __future__ import annotations
import time
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator, color


class Stage:
    def __init__(
        self,
        level: int,
        stage_id: int,
        decoding_satus: int,
        start_time: float,
    ):
        self.level = level
        self.stage_id = stage_id
        self.decoding_satus = decoding_satus
        self.start_time = start_time

    @staticmethod
    def init() -> Stage:
        return Stage(0, 0, 0, 0.0)

    @staticmethod
    def read(data: core.Data) -> Stage:
        level = data.read_int()
        stage_id = data.read_int()
        decoding_satus = data.read_byte()
        start_time = data.read_double()

        return Stage(level, stage_id, decoding_satus, start_time)

    def write(self, data: core.Data):
        data.write_int(self.level)
        data.write_int(self.stage_id)
        data.write_byte(self.decoding_satus)
        data.write_double(self.start_time)

    def serialize(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "stage_id": self.stage_id,
            "decoding_satus": self.decoding_satus,
            "start_time": self.start_time,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Stage:
        return Stage(
            data.get("level", 0),
            data.get("stage_id", 0),
            data.get("decoding_satus", 0),
            data.get("start_time", 0.0),
        )

    def __repr__(self):
        return f"Stage({self.level}, {self.stage_id}, {self.decoding_satus}, {self.start_time})"

    def __str__(self):
        return self.__repr__()


class Enigma:
    def __init__(
        self,
        energy_since_1: int,
        energy_since_2: int,
        enigma_level: int,
        unknown_1: int,
        unknown_2: bool,
        stages: list[Stage],
        extra: tuple[int, int, int, float] | None,
    ):
        self.energy_since_1 = energy_since_1
        self.energy_since_2 = energy_since_2
        self.enigma_level = enigma_level
        self.unknown_1 = unknown_1
        self.unknown_2 = unknown_2
        self.stages = stages
        self.extra = extra

    @staticmethod
    def init() -> Enigma:
        return Enigma(0, 0, 0, 0, False, [], None)

    @staticmethod
    def read(data: core.Data, game_version: core.GameVersion) -> Enigma:
        energy_since_1 = data.read_int()
        energy_since_2 = data.read_int()
        enigma_level = data.read_byte()
        unknown_1 = data.read_byte()
        unknown_2 = data.read_bool()

        total_stages = data.read_byte()

        stages = [Stage.read(data) for _ in range(total_stages)]

        extra_data = None

        if game_version >= 140500:
            has_extra = data.read_bool()
            if has_extra:
                extra_data = (
                    data.read_int(),
                    data.read_int(),
                    data.read_byte(),
                    data.read_double(),
                )
        return Enigma(
            energy_since_1,
            energy_since_2,
            enigma_level,
            unknown_1,
            unknown_2,
            stages,
            extra_data,
        )

    def write(self, data: core.Data, game_version: core.GameVersion):
        data.write_int(self.energy_since_1)
        data.write_int(self.energy_since_2)
        data.write_byte(self.enigma_level)
        data.write_byte(self.unknown_1)
        data.write_bool(self.unknown_2)
        data.write_byte(len(self.stages))
        for stage in self.stages:
            stage.write(data)

        if game_version >= 140500:
            data.write_bool(self.extra is not None)
            if self.extra is not None:
                data.write_int(self.extra[0])
                data.write_int(self.extra[1])
                data.write_byte(self.extra[2])
                data.write_double(self.extra[3])

    def serialize(self) -> dict[str, Any]:
        return {
            "energy_since_1": self.energy_since_1,
            "energy_since_2": self.energy_since_2,
            "enigma_level": self.enigma_level,
            "unknown_1": self.unknown_1,
            "unknown_2": self.unknown_2,
            "stages": [stage.serialize() for stage in self.stages],
            "extra": self.extra,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Enigma:
        return Enigma(
            data.get("energy_since_1", 0),
            data.get("energy_since_2", 0),
            data.get("enigma_level", 0),
            data.get("unknown_1", 0),
            data.get("unknown_2", False),
            [Stage.deserialize(stage) for stage in data.get("stages", [])],
            data.get("extra", None),
        )

    def __repr__(self):
        return f"Enigma({self.energy_since_1}, {self.energy_since_2}, {self.enigma_level}, {self.unknown_1}, {self.unknown_2}, {self.stages}, {self.extra})"

    def __str__(self):
        return self.__repr__()

    def edit_enigma(self, save_file: core.SaveFile):
        names = core.MapNames(save_file, "H", base_index=25000).map_names
        names_list: list[str] = []
        keys = list(names.keys())
        keys.sort()
        for id in keys:
            name = names[id]
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_enigma_name", id=id
                )
            names_list.append(name)

        base_level = 25000

        color.ColoredText.localize("current_enigma_stages")
        for stage in self.stages:
            name = names[stage.stage_id - base_level]
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_enigma_name", id=stage.stage_id
                )
            color.ColoredText.localize(
                "enigma_stage", name=name, id=stage.stage_id - base_level
            )

        if self.stages:
            wipe = dialog_creator.YesNoInput().get_input_once("wipe_enigma")
            if wipe is None:
                return
            if wipe:
                for stage in self.stages:
                    id = stage.stage_id
                    save_file.event_stages.chapter_completion_count[id] = 0
                self.stages = []

        ids, _ = dialog_creator.ChoiceInput(
            names_list,
            names_list,
            [],
            {},
            "enigma_select",
        ).multiple_choice()
        if ids is None:
            return

        for enigma_id in ids:
            abs_id = enigma_id + base_level
            save_file.event_stages.chapter_completion_count[abs_id] = 0
            # TODO: level? they can go much higher than 3... not sure it really matters though
            stage = Stage(3, abs_id, 2, int(time.time()))
            self.stages.append(stage)

        color.ColoredText.localize("enigma_success")


def edit_enigma(save_file: core.SaveFile):
    save_file.enigma.edit_enigma(save_file)
