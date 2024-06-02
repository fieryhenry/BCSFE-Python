from __future__ import annotations
from bcsfe import core


class Catamin:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(stream: core.Data) -> Catamin:
        amount = stream.read_int()
        return Catamin(amount)

    def write(self, stream: core.Data):
        stream.write_int(self.amount)

    def serialize(self) -> int:
        return self.amount

    @staticmethod
    def deserialize(data: int) -> Catamin:
        return Catamin(data)

    def __repr__(self):
        return f"Catamin({self.amount})"

    def __str__(self):
        return f"Catamin({self.amount})"


class Catamins:
    def __init__(self, catamins: list[Catamin]):
        self.catamins = catamins

    @staticmethod
    def read(stream: core.Data) -> Catamins:
        total = stream.read_int()
        catamins: list[Catamin] = []
        for _ in range(total):
            catamins.append(Catamin.read(stream))
        return Catamins(catamins)

    def write(self, stream: core.Data):
        stream.write_int(len(self.catamins))
        for catamin in self.catamins:
            catamin.write(stream)

    def serialize(self) -> list[int]:
        return [catamin.serialize() for catamin in self.catamins]

    @staticmethod
    def deserialize(data: list[int]) -> Catamins:
        return Catamins([Catamin.deserialize(catamin) for catamin in data])

    def __repr__(self):
        return f"Catamins({self.catamins})"

    def __str__(self):
        return f"Catamins({self.catamins})"
