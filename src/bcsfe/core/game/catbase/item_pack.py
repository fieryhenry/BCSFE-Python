from __future__ import annotations
from typing import Any
from bcsfe import core


class PurchasedPack:
    def __init__(self, purchased: bool):
        self.purchased = purchased

    @staticmethod
    def init() -> PurchasedPack:
        return PurchasedPack(False)

    @staticmethod
    def read(stream: core.Data) -> PurchasedPack:
        purchased = stream.read_bool()
        return PurchasedPack(purchased)

    def write(self, stream: core.Data):
        stream.write_bool(self.purchased)

    def serialize(self) -> bool:
        return self.purchased

    @staticmethod
    def deserialize(data: bool) -> PurchasedPack:
        return PurchasedPack(data)

    def __repr__(self) -> str:
        return f"PurchasedPack(purchased={self.purchased!r})"

    def __str__(self) -> str:
        return self.__repr__()


class PurchaseSet:
    def __init__(self, purchases: dict[str, PurchasedPack]):
        self.purchases = purchases

    @staticmethod
    def init() -> PurchaseSet:
        return PurchaseSet({})

    @staticmethod
    def read(stream: core.Data) -> PurchaseSet:
        total = stream.read_int()
        purchases: dict[str, PurchasedPack] = {}
        for _ in range(total):
            key = stream.read_string()
            purchases[key] = PurchasedPack.read(stream)
        return PurchaseSet(purchases)

    def write(self, stream: core.Data):
        stream.write_int(len(self.purchases))
        for key, purchase in self.purchases.items():
            stream.write_string(key)
            purchase.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            key: purchase.serialize()
            for key, purchase in self.purchases.items()
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> PurchaseSet:
        return PurchaseSet(
            {
                key: PurchasedPack.deserialize(purchase)
                for key, purchase in data.items()
            },
        )

    def __repr__(self) -> str:
        return f"PurchaseSet(purchases={self.purchases!r})"

    def __str__(self) -> str:
        return self.__repr__()


class Purchases:
    def __init__(self, purchases: dict[int, PurchaseSet]):
        self.purchases = purchases

    @staticmethod
    def init() -> Purchases:
        return Purchases({})

    @staticmethod
    def read(stream: core.Data) -> Purchases:
        total = stream.read_int()
        purchases: dict[int, PurchaseSet] = {}
        for _ in range(total):
            key = stream.read_int()
            purchases[key] = PurchaseSet.read(stream)

        return Purchases(purchases)

    def write(self, stream: core.Data):
        stream.write_int(len(self.purchases))
        for key, purchase in self.purchases.items():
            stream.write_int(key)
            purchase.write(stream)

    def serialize(self) -> dict[int, Any]:
        return {
            key: purchase.serialize()
            for key, purchase in self.purchases.items()
        }

    @staticmethod
    def deserialize(data: dict[int, Any]) -> Purchases:
        return Purchases(
            {
                key: PurchaseSet.deserialize(purchase)
                for key, purchase in data.items()
            },
        )

    def __repr__(self) -> str:
        return f"Purchases(purchases={self.purchases!r})"

    def __str__(self) -> str:
        return self.__repr__()


class ItemPack:
    def __init__(self, purchases: Purchases):
        self.purchases = purchases
        self.displayed_packs: dict[int, bool] = {}
        self.three_days_started: bool = False
        self.three_days_end_timestamp: float = 0.0

    @staticmethod
    def init() -> ItemPack:
        return ItemPack(Purchases.init())

    @staticmethod
    def read(stream: core.Data) -> ItemPack:
        return ItemPack(Purchases.read(stream))

    def write(self, stream: core.Data):
        self.purchases.write(stream)

    def read_displayed_packs(self, stream: core.Data) -> None:
        total = stream.read_int()
        displayed_packs: dict[int, bool] = {}
        for _ in range(total):
            key = stream.read_int()
            displayed_packs[key] = stream.read_bool()

        self.displayed_packs = displayed_packs

    def write_displayed_packs(self, stream: core.Data) -> None:
        stream.write_int(len(self.displayed_packs))
        for key, displayed in self.displayed_packs.items():
            stream.write_int(key)
            stream.write_bool(displayed)

    def read_three_days(self, stream: core.Data) -> None:
        self.three_days_started = stream.read_bool()
        self.three_days_end_timestamp = stream.read_double()

    def write_three_days(self, stream: core.Data) -> None:
        stream.write_bool(self.three_days_started)
        stream.write_double(self.three_days_end_timestamp)

    def serialize(self) -> dict[str, Any]:
        return {
            "purchases": self.purchases.serialize(),
            "displayed_packs": self.displayed_packs,
            "three_days_started": self.three_days_started,
            "three_days_end_timestamp": self.three_days_end_timestamp,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> ItemPack:
        item_pack = ItemPack(Purchases.deserialize(data.get("purchases", {})))
        item_pack.displayed_packs = data.get("displayed_packs", {})
        item_pack.three_days_started = data.get("three_days_started", False)
        item_pack.three_days_end_timestamp = data.get(
            "three_days_end_timestamp", 0.0
        )
        return item_pack

    def __repr__(self) -> str:
        return f"ItemPack(purchases={self.purchases!r}, displayed_packs={self.displayed_packs!r}, three_days_started={self.three_days_started!r}, three_days_end_timestamp={self.three_days_end_timestamp!r})"

    def __str__(self) -> str:
        return self.__repr__()
