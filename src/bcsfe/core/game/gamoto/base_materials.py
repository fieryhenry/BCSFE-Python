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

    def serialize(self) -> int:
        return self.amount

    @staticmethod
    def deserialize(data: int) -> "Material":
        return Material(data)

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

    def serialize(self) -> list[int]:
        return [material.serialize() for material in self.materials]

    @staticmethod
    def deserialize(data: list[int]) -> "Materials":
        return Materials([Material.deserialize(material) for material in data])

    def __repr__(self) -> str:
        return f"Materials(materials={self.materials!r})"

    def __str__(self) -> str:
        return self.__repr__()
