from typing import Any, Optional
from bcsfe import core
from bcsfe.cli import dialog_creator


class Cannon:
    def __init__(self, levels: list[int]):
        self.levels = levels

    @staticmethod
    def init() -> "Cannon":
        return Cannon([])

    @staticmethod
    def read(stream: "core.Data") -> "Cannon":
        total = stream.read_int()
        levels: list[int] = []
        for _ in range(total):
            levels.append(stream.read_int())
        return Cannon(levels)

    def write(self, stream: "core.Data"):
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
    def init(gv: "core.GameVersion") -> "Cannons":
        cannnons = {}
        if gv < 80200:
            selected_parts = [[0, 0, 0]]
        else:
            if gv > 90699:
                total_selected_parts = 0
            else:
                total_selected_parts = 10

            selected_parts = [[0, 0, 0] for _ in range(total_selected_parts)]
        return Cannons(cannnons, selected_parts)

    @staticmethod
    def read(stream: "core.Data", gv: "core.GameVersion") -> "Cannons":
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

    def write(self, stream: "core.Data", gv: "core.GameVersion"):
        stream.write_int(len(self.cannons))
        for cannon_id, cannon in self.cannons.items():
            stream.write_int(cannon_id)
            cannon.write(stream)
        if gv < 80200:
            stream.write_int_list(self.selected_parts[0], write_length=False, length=3)
        else:
            if gv > 90699:
                stream.write_byte(len(self.selected_parts))

            for part in self.selected_parts:
                stream.write_byte_list(part, write_length=False, length=3)

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
                for cannon_id, cannon in data.get("cannons", {}).items()
            },
            data.get("selected_parts", []),
        )

    def __repr__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"

    def __str__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"


class Ototo:
    def __init__(
        self,
        base_materials: "core.BaseMaterials",
        game_version: Optional["core.GameVersion"] = None,
    ):
        self.base_materials = base_materials
        self.remaining_seconds = 0.0
        self.return_flag = False
        self.improve_id = 0
        self.engineers = 0
        self.cannons = Cannons.init(game_version) if game_version else None

    @staticmethod
    def init(game_version: "core.GameVersion") -> "Ototo":
        return Ototo(core.BaseMaterials.init(), game_version)

    @staticmethod
    def read(stream: "core.Data") -> "Ototo":
        bm = core.BaseMaterials.read(stream)
        return Ototo(bm)

    def write(self, stream: "core.Data"):
        self.base_materials.write(stream)

    def read_2(self, stream: "core.Data", gv: "core.GameVersion"):
        self.remaining_seconds = stream.read_double()
        self.return_flag = stream.read_bool()
        self.improve_id = stream.read_int()
        self.engineers = stream.read_int()
        self.cannons = Cannons.read(stream, gv)

    def write_2(self, stream: "core.Data", gv: "core.GameVersion"):
        stream.write_double(self.remaining_seconds)
        stream.write_bool(self.return_flag)
        stream.write_int(self.improve_id)
        stream.write_int(self.engineers)
        if self.cannons is None:
            Cannons.init(gv).write(stream, gv)
        else:
            self.cannons.write(stream, gv)

    def serialize(self) -> dict[str, Any]:
        return {
            "base_materials": self.base_materials.serialize(),
            "remaining_seconds": self.remaining_seconds,
            "return_flag": self.return_flag,
            "improve_id": self.improve_id,
            "engineers": self.engineers,
            "cannons": self.cannons.serialize() if self.cannons else None,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Ototo":
        ototo = Ototo(core.BaseMaterials.deserialize(data.get("base_materials", [])))
        ototo.remaining_seconds = data.get("remaining_seconds", 0.0)
        ototo.return_flag = data.get("return_flag", False)
        ototo.improve_id = data.get("improve_id", 0)
        ototo.engineers = data.get("engineers", 0)
        ototo.cannons = Cannons.deserialize(data.get("cannons", {}))
        return ototo

    def __repr__(self):
        return f"Ototo({self.base_materials}, {self.remaining_seconds}, {self.return_flag}, {self.improve_id}, {self.engineers}, {self.cannons})"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def get_max_engineers(save_file: "core.SaveFile") -> int:
        file = core.GameDataGetter(save_file).download(
            "DataLocal", "CastleCustomLimit.csv"
        )
        if file is None:
            return 5
        csv = core.CSV(file)
        return csv.lines[0][0].to_int()

    def edit_engineers(self, save_file: "core.SaveFile"):
        name = core.GatyaItemNames(save_file).get_name(92)
        self.engineers = dialog_creator.SingleEditor(
            name, self.engineers, Ototo.get_max_engineers(save_file)
        ).edit()
