from __future__ import annotations

import datetime
from math import inf, isnan
import math
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator, color


class EndlessItem:
    def __init__(
        self, active: bool, unknown: bool, amount: int, start: float, end: float
    ):
        self.active = active
        self.unknown = unknown
        self.amount = amount
        self.start = start
        self.end = end

    @staticmethod
    def init() -> EndlessItem:
        return EndlessItem(False, False, 0, 0, 0)

    @staticmethod
    def read(stream: core.Data) -> EndlessItem:
        return EndlessItem(
            stream.read_bool(),
            stream.read_bool(),
            stream.read_byte(),
            stream.read_double(),
            stream.read_double(),
        )

    def write(self, stream: core.Data):
        stream.write_bool(self.active)
        stream.write_bool(self.unknown)
        stream.write_byte(self.amount)
        stream.write_double(self.start)
        stream.write_double(self.end)

    def serialize(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "unknown": self.unknown,
            "amount": self.amount,
            "start": self.start,
            "end": self.end,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EndlessItem:
        return EndlessItem(
            data.get("active", False),
            data.get("unknown", False),
            data.get("amount", 0),
            data.get("start", 0.0),
            data.get("end", 0.0),
        )

    def get_endless_duration(self) -> datetime.timedelta | None:
        if not self.active:
            return datetime.timedelta()

        if self.end == inf:
            return None
        if math.isnan(self.end) or math.isnan(self.start):
            return None

        return datetime.timedelta(
            seconds=self.end - self.start + (self.amount * 3 * 60 * 60)
        )

    def get_endless_duration_formatted(self) -> str:
        duration = self.get_endless_duration()

        if duration is None:
            return core.localize("infinity_duration")

        days = duration.days
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        return core.localize(
            "duration", days=days, hours=hours, minutes=minutes, seconds=seconds
        )

    def set_duration_mins(self, mins: float, amount: int):
        self.active = True
        self.unknown = True
        self.amount = amount
        self.start = datetime.datetime.now(datetime.timezone.utc).timestamp()
        self.end = self.start + mins * 60


class BattleItem:
    def __init__(self, amount: int):
        self.amount = amount
        self.locked = False

        self.endless_item = EndlessItem.init()

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

    def read_endless_items(self, stream: core.Data):
        self.endless_item = EndlessItem.read(stream)

    def write_endless_items(self, stream: core.Data):
        self.endless_item.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "amount": self.amount,
            "locked": self.locked,
            "endless": self.endless_item.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> BattleItem:
        battle_item = BattleItem(data.get("amount", 0))
        battle_item.locked = data.get("locked", False)
        battle_item.endless_item = EndlessItem.deserialize(data.get("endless", {}))
        return battle_item

    def __repr__(self):
        try:
            return f"BattleItem({self.amount}, {self.locked}, {self.endless_item})"
        except AttributeError:
            return f"BattleItem({self.amount}, {self.endless_item})"

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

    def read_endless_items(self, stream: core.Data):
        for i in range(6):
            if i >= len(self.items):
                _ = EndlessItem.read(stream)  # ensure we still read 6 items
            else:
                item = self.items[i]
                item.read_endless_items(stream)

    def write_endless_items(self, stream: core.Data):
        for i in range(6):
            if i >= len(self.items):
                EndlessItem.init().write(stream)  # ensure we still write 6 items
            else:
                item = self.items[i]
                item.write_endless_items(stream)

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

    def edit_endless_items(self, save_file: core.SaveFile):
        item_names = self.get_names(save_file)
        if item_names is None:
            return

        current_values = [
            item.endless_item.get_endless_duration_formatted() for item in self.items
        ]

        (options, all_at_once) = dialog_creator.ChoiceInput.from_reduced(
            [core.localize("endless_item_item", item=item) for item in item_names],
            current_values,
            localize_options=False,
            dialog="select_option",
        ).multiple_choice(False)

        if options is None:
            return

        infinity_str = core.localize("infinity")

        if all_at_once:
            val = dialog_creator.StringInput().get_input_locale_while(
                "enter_duration_minutes", {}
            )
            if val is None:
                return

            if val.lower() == infinity_str.lower():
                val = inf
            else:
                try:
                    val = float(val)
                except ValueError:
                    return

            for item in self.items:
                item.endless_item.set_duration_mins(val, 0)
        else:
            for opt in options:
                val = dialog_creator.StringInput().get_input_locale_while(
                    "enter_duration_minutes_item", {"item": item_names[opt]}
                )
                if val is None:
                    return

                if val.lower() == infinity_str.lower():
                    val = inf
                else:
                    try:
                        val = float(val)
                    except ValueError:
                        color.ColoredText.localize("invalid_minute_count")
                        continue

                self.items[opt].endless_item.set_duration_mins(val, 0)

        color.ColoredText.localize("endless_items_success")
