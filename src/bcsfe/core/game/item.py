from typing import Any, Optional
from bcsfe import core


class Item:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(strream: "core.Data") -> "Item":
        return Item(strream.read_int())

    def write(self, stream: "core.Data"):
        stream.write_int(self.amount)

    def serialize(self) -> dict[str, Any]:
        return {"amount": self.amount}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Item":
        return Item(data["amount"])

    def __repr__(self) -> str:
        return f"Item(amount={self.amount})"

    def __str__(self) -> str:
        return f"Item(amount={self.amount})"


class Items:
    def __init__(self, items: list[Item]):
        self.items = items

    @staticmethod
    def read(stream: "core.Data", length: Optional[int] = None) -> "Items":
        if length is None:
            length = stream.read_int()

        items = [Item.read(stream) for _ in range(length)]
        return Items(items)

    def write(self, stream: "core.Data", write_length: bool = True):
        if write_length:
            stream.write_int(len(self.items))

        for item in self.items:
            item.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {"items": [item.serialize() for item in self.items]}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Items":
        return Items([Item.deserialize(item) for item in data["items"]])

    def __repr__(self) -> str:
        return f"Items(items={self.items})"

    def __str__(self) -> str:
        return f"Items(items={self.items})"
