from __future__ import annotations
from bcsfe import core
from typing import Any


class CatSlot:
    def __init__(self, cat_id: int, form: int):
        self.cat_id = cat_id
        self.form = form

    @staticmethod
    def init() -> CatSlot:
        return CatSlot(0, 0)

    @staticmethod
    def read(stream: core.Data) -> CatSlot:
        cat_id = stream.read_short()
        form = stream.read_byte()
        return CatSlot(cat_id, form)

    def write(self, stream: core.Data):
        stream.write_short(self.cat_id)
        stream.write_byte(self.form)

    def serialize(self) -> dict[str, Any]:
        return {
            "cat_id": self.cat_id,
            "form": self.form,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> CatSlot:
        return CatSlot(data.get("cat_id", 0), data.get("form", 0))

    def __repr__(self):
        return f"CatSlot({self.cat_id}, {self.form})"

    def __str__(self):
        return self.__repr__()


class LineupCat:
    def __init__(
        self,
        index: int,
        cats: list[CatSlot],
        u1: int,
        u2: int,
        u3: int,
    ):
        self.index = index
        self.cats = cats
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3

    @staticmethod
    def init() -> LineupCat:
        cats = [CatSlot.init() for _ in range(10)]
        return LineupCat(0, cats, 0, 0, 0)

    @staticmethod
    def read(stream: core.Data) -> LineupCat:
        index = stream.read_short()
        length = 10

        cats = [CatSlot.read(stream) for _ in range(length)]
        u1 = stream.read_byte()
        u2 = stream.read_byte()
        u3 = stream.read_byte()
        return LineupCat(index, cats, u1, u2, u3)

    def write(self, stream: core.Data):
        stream.write_short(self.index)
        for cat in self.cats:
            cat.write(stream)
        stream.write_byte(self.u1)
        stream.write_byte(self.u2)
        stream.write_byte(self.u3)

    def serialize(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "cats": [cat.serialize() for cat in self.cats],
            "u1": self.u1,
            "u2": self.u2,
            "u3": self.u3,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> LineupCat:
        return LineupCat(
            data.get("index", 0),
            [CatSlot.deserialize(cat) for cat in data.get("cats", [])],
            data.get("u1", 0),
            data.get("u2", 0),
            data.get("u3", 0),
        )

    def __repr__(self):
        return f"LineupCat({self.index}, {self.cats}, {self.u1}, {self.u2}, {self.u3})"

    def __str__(self):
        return self.__repr__()


class ClearedSlotsCat:
    def __init__(self, lineups: list[LineupCat]):
        self.lineups = lineups

    @staticmethod
    def init() -> ClearedSlotsCat:
        return ClearedSlotsCat([])

    @staticmethod
    def read(stream: core.Data) -> ClearedSlotsCat:
        total = stream.read_short()
        lineups = [LineupCat.read(stream) for _ in range(total)]
        return ClearedSlotsCat(lineups)

    def write(self, stream: core.Data):
        stream.write_short(len(self.lineups))
        for lineup in self.lineups:
            lineup.write(stream)

    def serialize(self) -> list[dict[str, Any]]:
        return [lineup.serialize() for lineup in self.lineups]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> ClearedSlotsCat:
        return ClearedSlotsCat(
            [LineupCat.deserialize(lineup) for lineup in data],
        )

    def __repr__(self):
        return f"ClearedSlotsCat({self.lineups})"

    def __str__(self):
        return self.__repr__()


class StageSlot:
    def __init__(self, stage_id: int):
        self.stage_id = stage_id

    @staticmethod
    def init() -> StageSlot:
        return StageSlot(0)

    @staticmethod
    def read(stream: core.Data) -> StageSlot:
        stage_id = stream.read_int()
        return StageSlot(stage_id)

    def write(self, stream: core.Data):
        stream.write_int(self.stage_id)

    def serialize(self) -> int:
        return self.stage_id

    @staticmethod
    def deserialize(data: int) -> StageSlot:
        return StageSlot(data)

    def __repr__(self):
        return f"StageSlot({self.stage_id})"

    def __str__(self):
        return self.__repr__()


class StageLineups:
    def __init__(self, index: int, slots: list[StageSlot]):
        self.index = index
        self.slots = slots

    @staticmethod
    def init() -> StageLineups:
        return StageLineups(0, [])

    @staticmethod
    def read(stream: core.Data) -> StageLineups:
        index = stream.read_short()
        total = stream.read_short()
        slots = [StageSlot.read(stream) for _ in range(total)]
        return StageLineups(index, slots)

    def write(self, stream: core.Data):
        stream.write_short(self.index)
        stream.write_short(len(self.slots))
        for slot in self.slots:
            slot.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "slots": [slot.serialize() for slot in self.slots],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> StageLineups:
        return StageLineups(
            data.get("index", 0),
            [StageSlot.deserialize(slot) for slot in data.get("slots", [])],
        )

    def __repr__(self):
        return f"StageLineups({self.index}, {self.slots})"

    def __str__(self):
        return self.__repr__()


class ClearedStageSlots:
    def __init__(self, lineups: list[StageLineups]):
        self.lineups = lineups

    @staticmethod
    def init() -> ClearedStageSlots:
        return ClearedStageSlots([])

    @staticmethod
    def read(stream: core.Data) -> ClearedStageSlots:
        total = stream.read_short()
        lineups = [StageLineups.read(stream) for _ in range(total)]
        return ClearedStageSlots(lineups)

    def write(self, stream: core.Data):
        stream.write_short(len(self.lineups))
        for lineup in self.lineups:
            lineup.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "lineups": [lineup.serialize() for lineup in self.lineups],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> ClearedStageSlots:
        return ClearedStageSlots(
            [
                StageLineups.deserialize(lineup)
                for lineup in data.get("lineups", [])
            ],
        )

    def __repr__(self):
        return f"ClearedStageSlots({self.lineups})"

    def __str__(self):
        return self.__repr__()


class ClearedSlots:
    def __init__(
        self,
        cleared_slots: ClearedSlotsCat,
        cleared_stage_slots: ClearedStageSlots,
        unknown: dict[int, bool],
    ):
        self.cleared_slots = cleared_slots
        self.cleared_stage_slots = cleared_stage_slots
        self.unknown = unknown

    @staticmethod
    def init() -> ClearedSlots:
        return ClearedSlots(
            ClearedSlotsCat.init(),
            ClearedStageSlots.init(),
            {},
        )

    @staticmethod
    def read(stream: core.Data) -> ClearedSlots:
        cleared_slots = ClearedSlotsCat.read(stream)
        cleared_stage_slots = ClearedStageSlots.read(stream)
        length = stream.read_short()
        unknown = stream.read_short_bool_dict(length)
        return ClearedSlots(cleared_slots, cleared_stage_slots, unknown)

    def write(self, stream: core.Data):
        self.cleared_slots.write(stream)
        self.cleared_stage_slots.write(stream)
        stream.write_short(len(self.unknown))
        stream.write_short_bool_dict(self.unknown, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "cleared_slots": self.cleared_slots.serialize(),
            "cleared_stage_slots": self.cleared_stage_slots.serialize(),
            "unknown": self.unknown,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> ClearedSlots:
        return ClearedSlots(
            ClearedSlotsCat.deserialize(data.get("cleared_slots", [])),
            ClearedStageSlots.deserialize(data.get("cleared_stage_slots", {})),
            data.get("unknown", {}),
        )

    def __repr__(self):
        return f"ClearedSlots({self.cleared_slots}, {self.cleared_stage_slots}, {self.unknown})"

    def __str__(self):
        return self.__repr__()
