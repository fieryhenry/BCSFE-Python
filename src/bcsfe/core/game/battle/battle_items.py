from __future__ import annotations

from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator


class BattleItem:
    def __init__(self, amount: int):
        self.amount = amount
        self.locked = False

    @staticmethod
    def init() -> BattleItem:
        return BattleItem(0)

    @staticmethod
    def read_amount(stream: core.Data) -> BattleItem:
        return BattleItem(stream.read_int())

    def write_amount(self, stream: core.Data):
        stream.write_int(self.amount)

    def read_locked(self, stream: core.Data):
        self.locked = stream.read_bool()

    def write_locked(self, stream: core.Data):
        stream.write_bool(self.locked)

    def serialize(self) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "locked": self.locked,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> BattleItem:
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
    def init() -> BattleItems:
        return BattleItems([BattleItem.init() for _ in range(6)])

    @staticmethod
    def read_items(stream: core.Data) -> BattleItems:
        total_items = 6
        items = [BattleItem.read_amount(stream) for _ in range(total_items)]
        return BattleItems(items)

    def write_items(self, stream: core.Data):
        for item in self.items:
            item.write_amount(stream)

    def read_locked_items(self, stream: core.Data):
        self.lock_item = stream.read_bool()
        for item in self.items:
            item.read_locked(stream)

    def write_locked_items(self, stream: core.Data):
        stream.write_bool(self.lock_item)
        for item in self.items:
            item.write_locked(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "items": [item.serialize() for item in self.items],
            "lock_item": self.lock_item,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> BattleItems:
        battle_items = BattleItems(
            [BattleItem.deserialize(item) for item in data.get("items", [])]
        )
        battle_items.lock_item = data.get("lock_item", False)
        return battle_items

    def __repr__(self):
        return f"BattleItems({self.items})"

    def __str__(self):
        return f"BattleItems({self.items})"

    def get_names(self, save_file: core.SaveFile) -> list[str] | None:
        names = core.core_data.get_gatya_item_names(save_file).names
        if names is None:
            return None
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(3)
        if items is None:
            return None

        names = [names[item.id] for item in items]
        return names

    def edit(self, save_file: core.SaveFile):
        group_name = save_file.get_localizable().get("shop_category1")
        if group_name is None:
            group_name = core.core_data.local_manager.get_key("battle_items")
        item_names = self.get_names(save_file)
        if item_names is None:
            return
        current_values = [item.amount for item in self.items]
        values = dialog_creator.MultiEditor.from_reduced(
            group_name,
            item_names,
            current_values,
            core.core_data.max_value_manager.get("battle_items"),
        ).edit()
        for i, value in enumerate(values):
            self.items[i].amount = value
