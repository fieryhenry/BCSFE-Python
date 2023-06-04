from typing import Any
from bcsfe.core import game_version, io
from bcsfe.core.game.gamoto import base_materials


class Cannon:
    def __init__(self, levels: list[int]):
        self.levels = levels

    @staticmethod
    def read(stream: io.data.Data) -> "Cannon":
        total = stream.read_int()
        levels: list[int] = []
        for _ in range(total):
            levels.append(stream.read_int())
        return Cannon(levels)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.levels))
        for level in self.levels:
            stream.write_int(level)

    def serialize(self) -> list[int]:
        return self.levels

    @staticmethod
    def deserialize(data: list[int]) -> "Cannon":
        return Cannon(data)

    def __repr__(self):
        return f"Cannon({self.levels})"

    def __str__(self):
        return f"Cannon({self.levels})"


class Cannons:
    def __init__(self, cannons: dict[int, Cannon], selected_parts: list[list[int]]):
        self.cannons = cannons
        self.selected_parts = selected_parts

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "Cannons":
        total = stream.read_int()
        cannons: dict[int, Cannon] = {}
        for _ in range(total):
            cannon_id = stream.read_int()
            cannon = Cannon.read(stream)
            cannons[cannon_id] = cannon
        if gv < 80200:
            selected_parts = [stream.read_int_list(length=3)]
        else:
            if gv > 90699:
                total_selected_parts = stream.read_byte()
            else:
                total_selected_parts = 10

            selected_parts: list[list[int]] = []
            for _ in range(total_selected_parts):
                selected_parts.append(stream.read_byte_list(length=3))

        return Cannons(cannons, selected_parts)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        stream.write_int(len(self.cannons))
        for cannon_id, cannon in self.cannons.items():
            stream.write_int(cannon_id)
            cannon.write(stream)
        if gv < 80200:
            stream.write_int_list(self.selected_parts[0], write_length=False)
        else:
            if gv > 90699:
                stream.write_byte(len(self.selected_parts))
            else:
                stream.write_byte(10)

            for part in self.selected_parts:
                stream.write_byte_list(part, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "cannons": {
                cannon_id: cannon.serialize()
                for cannon_id, cannon in self.cannons.items()
            },
            "selected_parts": self.selected_parts,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Cannons":
        return Cannons(
            {
                cannon_id: Cannon.deserialize(cannon)
                for cannon_id, cannon in data["cannons"].items()
            },
            data["selected_parts"],
        )

    def __repr__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"

    def __str__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"


class Ototo:
    def __init__(self, base_materials: base_materials.Materials):
        self.base_materials = base_materials

    @staticmethod
    def read(stream: io.data.Data) -> "Ototo":
        bm = base_materials.Materials.read(stream)
        return Ototo(bm)

    def write(self, stream: io.data.Data):
        self.base_materials.write(stream)

    def read_2(self, stream: io.data.Data, gv: game_version.GameVersion):
        self.remaining_seconds = stream.read_double()
        self.return_flag = stream.read_bool()
        self.improve_id = stream.read_int()
        self.engineers = stream.read_int()
        self.cannons = Cannons.read(stream, gv)

    def write_2(self, stream: io.data.Data, gv: game_version.GameVersion):
        stream.write_double(self.remaining_seconds)
        stream.write_bool(self.return_flag)
        stream.write_int(self.improve_id)
        stream.write_int(self.engineers)
        self.cannons.write(stream, gv)

    def serialize(self) -> dict[str, Any]:
        return {
            "base_materials": self.base_materials.serialize(),
            "remaining_seconds": self.remaining_seconds,
            "return_flag": self.return_flag,
            "improve_id": self.improve_id,
            "engineers": self.engineers,
            "cannons": self.cannons.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Ototo":
        ototo = Ototo(base_materials.Materials.deserialize(data["base_materials"]))
        ototo.remaining_seconds = data["remaining_seconds"]
        ototo.return_flag = data["return_flag"]
        ototo.improve_id = data["improve_id"]
        ototo.engineers = data["engineers"]
        ototo.cannons = Cannons.deserialize(data["cannons"])
        return ototo

    def __repr__(self):
        return f"Ototo({self.base_materials}, {self.remaining_seconds}, {self.return_flag}, {self.improve_id}, {self.engineers}, {self.cannons})"

    def __str__(self):
        return self.__repr__()
