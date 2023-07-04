from typing import Any
from bcsfe.core import io


class Upgrade:
    def __init__(self, plus: int, base: int):
        self.plus = plus
        self.base = base

    def get_base(self) -> int:
        return self.base + 1

    def get_plus(self) -> int:
        return self.plus

    @staticmethod
    def read(stream: io.data.Data) -> "Upgrade":
        plus = stream.read_short()
        base = stream.read_short()

        return Upgrade(plus, base)

    def write(self, stream: io.data.Data):
        stream.write_short(self.plus)
        stream.write_short(self.base)

    def serialize(self) -> dict[str, Any]:
        return {
            "plus": self.plus,
            "base": self.base,
        }

    @staticmethod
    def init() -> "Upgrade":
        return Upgrade(0, 1)

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Upgrade":
        return Upgrade(data.get("plus", 0), data.get("base", 0))

    def __repr__(self) -> str:
        return f"Upgrade(plus={self.plus}, base={self.base})"

    def __str__(self) -> str:
        return f"Upgrade(plus={self.plus}, base={self.base})"
