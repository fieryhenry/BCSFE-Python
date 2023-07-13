from typing import Any
from bcsfe import core


class TalentOrb:
    def __init__(self, id: int, value: int):
        self.id = id
        self.value = value

    @staticmethod
    def init() -> "TalentOrb":
        return TalentOrb(
            0,
            0,
        )

    @staticmethod
    def read(stream: "core.Data", gv: "core.GameVersion") -> "TalentOrb":
        id = stream.read_short()
        if gv < 110400:
            value = stream.read_byte()
        else:
            value = stream.read_short()
        return TalentOrb(id, value)

    def write(self, stream: "core.Data", gv: "core.GameVersion"):
        stream.write_short(self.id)
        if gv < 110400:
            stream.write_byte(self.value)
        else:
            stream.write_short(self.value)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "value": self.value,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "TalentOrb":
        return TalentOrb(data.get("id", 0), data.get("value", 0))

    def __repr__(self):
        return f"Orb({self.id}, {self.value})"

    def __str__(self):
        return self.__repr__()


class TalentOrbs:
    def __init__(self, orbs: dict[int, TalentOrb]):
        self.orbs = orbs

    @staticmethod
    def init() -> "TalentOrbs":
        return TalentOrbs({})

    @staticmethod
    def read(stream: "core.Data", gv: "core.GameVersion") -> "TalentOrbs":
        length = stream.read_short()
        orbs = {}
        for _ in range(length):
            orb = TalentOrb.read(stream, gv)
            orbs[orb.id] = orb
        return TalentOrbs(orbs)

    def write(self, stream: "core.Data", gv: "core.GameVersion"):
        stream.write_short(len(self.orbs))
        for orb in self.orbs.values():
            orb.write(stream, gv)

    def serialize(self) -> list[dict[str, Any]]:
        return [orb.serialize() for orb in self.orbs.values()]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "TalentOrbs":
        return TalentOrbs(
            {orb.get("id", 0): TalentOrb.deserialize(orb) for orb in data}
        )

    def __repr__(self):
        return f"TalentOrbs({self.orbs})"

    def __str__(self):
        return self.__repr__()
