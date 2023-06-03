from typing import Any
from bcsfe.core import io


class Material:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(stream: io.data.Data) -> "Material":
        amount = stream.read_int()
        return Material(amount)

    def write(self, stream: io.data.Data):
        stream.write_int(self.amount)

    def serialize(self) -> dict[str, Any]:
        return {"amount": self.amount}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Material":
        return Material(data["amount"])

    def __repr__(self) -> str:
        return f"Material(amount={self.amount!r})"

    def __str__(self) -> str:
        return self.__repr__()


class Materials:
    def __init__(self, materials: list[Material]):
        self.materials = materials

    @staticmethod
    def read(stream: io.data.Data) -> "Materials":
        total = stream.read_int()
        materials: list[Material] = []
        for _ in range(total):
            materials.append(Material.read(stream))
        return Materials(materials)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.materials))
        for material in self.materials:
            material.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {"materials": [material.serialize() for material in self.materials]}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Materials":
        return Materials(
            [Material.deserialize(material) for material in data["materials"]]
        )

    def __repr__(self) -> str:
        return f"Materials(materials={self.materials!r})"

    def __str__(self) -> str:
        return self.__repr__()
