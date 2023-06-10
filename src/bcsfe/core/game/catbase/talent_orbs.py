from typing import Any
from bcsfe.core import io, game_version


class Orb:
    def __init__(self, id: int, value: int):
        self.id = id
        self.value = value

    @staticmethod
    def init() -> "Orb":
        return Orb(
            0,
            0,
        )

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "Orb":
        id = stream.read_short()
        if gv < 110400:
            value = stream.read_byte()
        else:
            value = stream.read_short()
        return Orb(id, value)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
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
    def deserialize(data: dict[str, Any]) -> "Orb":
        return Orb(data.get("id", 0), data.get("value", 0))

    def __repr__(self):
        return f"Orb({self.id}, {self.value})"

    def __str__(self):
        return self.__repr__()


class TalentOrbs:
    def __init__(self, orbs: dict[int, Orb]):
        self.orbs = orbs

    @staticmethod
    def init() -> "TalentOrbs":
        return TalentOrbs({})

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "TalentOrbs":
        length = stream.read_short()
        orbs = {}
        for _ in range(length):
            orb = Orb.read(stream, gv)
            orbs[orb.id] = orb
        return TalentOrbs(orbs)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        stream.write_short(len(self.orbs))
        for orb in self.orbs.values():
            orb.write(stream, gv)

    def serialize(self) -> list[dict[str, Any]]:
        return [orb.serialize() for orb in self.orbs.values()]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "TalentOrbs":
        return TalentOrbs({orb.get("id", 0): Orb.deserialize(orb) for orb in data})

    def __repr__(self):
        return f"TalentOrbs({self.orbs})"

    def __str__(self):
        return self.__repr__()
