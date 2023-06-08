from typing import Any
from bcsfe.core import io


class BattleItem:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read_amount(stream: io.data.Data) -> "BattleItem":
        return BattleItem(stream.read_int())

    def write_amount(self, stream: io.data.Data):
        stream.write_int(self.amount)

    def read_locked(self, stream: io.data.Data):
        self.locked = stream.read_bool()

    def write_locked(self, stream: io.data.Data):
        stream.write_bool(self.locked)

    def serialize(self) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "locked": self.locked,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "BattleItem":
        battle_item = BattleItem(data.get("amount", 0))
        battle_item.locked = data.get("locked", False)
        return battle_item

    def __repr__(self):
        try:
            return f"BattleItem({self.amount}, {self.locked})"
        except AttributeError:
            return f"BattleItem({self.amount})"

    def __str__(self):
        return self.__repr__()


class BattleItems:
    def __init__(self, items: list[BattleItem]):
        self.items = items
        self.lock_item = False

    @staticmethod
    def read_items(stream: io.data.Data) -> "BattleItems":
        total_items = 6
        items = [BattleItem.read_amount(stream) for _ in range(total_items)]
        return BattleItems(items)

    def write_items(self, stream: io.data.Data):
        for item in self.items:
            item.write_amount(stream)

    def read_locked_items(self, stream: io.data.Data):
        self.lock_item = stream.read_bool()
        for item in self.items:
            item.read_locked(stream)

    def write_locked_items(self, stream: io.data.Data):
        stream.write_bool(self.lock_item)
        for item in self.items:
            item.write_locked(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "items": [item.serialize() for item in self.items],
            "lock_item": self.lock_item,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "BattleItems":
        battle_items = BattleItems(
            [BattleItem.deserialize(item) for item in data.get("items", [])]
        )
        battle_items.lock_item = data.get("lock_item", False)
        return battle_items

    def __repr__(self):
        return f"BattleItems({self.items})"

    def __str__(self):
        return f"BattleItems({self.items})"
