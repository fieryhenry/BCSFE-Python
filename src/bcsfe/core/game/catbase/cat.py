from typing import Any, Optional
from bcsfe.core.game.catbase import upgrade
from bcsfe.core import io, game_version


class Talent:
    def __init__(self, id: int, level: int):
        self.id = id
        self.level = level

    @staticmethod
    def read(stream: io.data.Data):
        return Talent(stream.read_int(), stream.read_int())

    def write(self, stream: io.data.Data):
        stream.write_int(self.id)
        stream.write_int(self.level)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Talent":
        return Talent(
            data["id"],
            data["level"],
        )

    def __repr__(self):
        return f"Talent({self.id}, {self.level})"

    def __str__(self):
        return self.__repr__()


class Cat:
    def __init__(self, id: int, unlocked: int):
        self.id = id
        self.unlocked = unlocked
        self.talents: Optional[list[Talent]] = None

    @staticmethod
    def read_unlocked(id: int, stream: io.data.Data):
        return Cat(id, stream.read_int())

    def write_unlocked(self, stream: io.data.Data):
        stream.write_int(self.unlocked)

    def read_upgrade(self, stream: io.data.Data):
        self.upgrade = upgrade.Upgrade.read(stream)

    def write_upgrade(self, stream: io.data.Data):
        self.upgrade.write(stream)

    def read_current_form(self, stream: io.data.Data):
        self.current_form = stream.read_int()

    def write_current_form(self, stream: io.data.Data):
        stream.write_int(self.current_form)

    def read_unlocked_forms(self, stream: io.data.Data):
        self.unlocked_forms = stream.read_int()

    def write_unlocked_forms(self, stream: io.data.Data):
        stream.write_int(self.unlocked_forms)

    def read_gatya_seen(self, stream: io.data.Data):
        self.gatya_seen = stream.read_int()

    def write_gatya_seen(self, stream: io.data.Data):
        stream.write_int(self.gatya_seen)

    def read_max_upgrade_level(self, stream: io.data.Data):
        level = upgrade.Upgrade.read(stream)
        self.max_upgrade_level = level

    def write_max_upgrade_level(self, stream: io.data.Data):
        self.max_upgrade_level.write(stream)

    def read_catguide_collected(self, stream: io.data.Data):
        self.catguide_collected = stream.read_bool()

    def write_catguide_collected(self, stream: io.data.Data):
        stream.write_bool(self.catguide_collected)

    def read_forth_form(self, stream: io.data.Data):
        self.forth_form = stream.read_int()

    def write_forth_form(self, stream: io.data.Data):
        stream.write_int(self.forth_form)

    def read_catseyes_used(self, stream: io.data.Data):
        self.catseyes_used = stream.read_int()

    def write_catseyes_used(self, stream: io.data.Data):
        stream.write_int(self.catseyes_used)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "unlocked": self.unlocked,
            "upgrade": self.upgrade.serialize(),
            "current_form": self.current_form,
            "unlocked_forms": self.unlocked_forms,
            "gatya_seen": self.gatya_seen,
            "max_upgrade_level": self.max_upgrade_level.serialize(),
            "catguide_collected": self.catguide_collected,
            "forth_form": self.forth_form,
            "catseyes_used": self.catseyes_used,
            "talents": [talent.serialize() for talent in self.talents]
            if self.talents is not None
            else None,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Cat":
        cat = Cat(data["id"], data["unlocked"])
        cat.upgrade = upgrade.Upgrade.deserialize(data["upgrade"])
        cat.current_form = data["current_form"]
        cat.unlocked_forms = data["unlocked_forms"]
        cat.gatya_seen = data["gatya_seen"]
        cat.max_upgrade_level = upgrade.Upgrade.deserialize(data["max_upgrade_level"])
        cat.catguide_collected = data["catguide_collected"]
        cat.forth_form = data["forth_form"]
        cat.catseyes_used = data["catseyes_used"]
        cat.talents = (
            [Talent.deserialize(talent) for talent in data["talents"]]
            if data["talents"] is not None
            else None
        )
        return cat

    def __repr__(self) -> str:
        return f"Cat(id={id}, unlocked={self.unlocked}, upgrade={self.upgrade}, current_form={self.current_form}, unlocked_forms={self.unlocked_forms}, gatya_seen={self.gatya_seen}, max_upgrade_level={self.max_upgrade_level}, catguide_collected={self.catguide_collected}, forth_form={self.forth_form}, catseyes_used={self.catseyes_used}, talents={self.talents})"

    def __str__(self) -> str:
        return self.__repr__()

    def read_talents(self, stream: io.data.Data):
        self.talents = []
        for _ in range(stream.read_int()):
            self.talents.append(Talent.read(stream))

    def write_talents(self, stream: io.data.Data):
        if self.talents is None:
            return
        stream.write_int(len(self.talents))
        for talent in self.talents:
            talent.write(stream)


class StorageItem:
    def __init__(self, item_id: int):
        self.item_id = item_id

    @staticmethod
    def read_item_id(stream: io.data.Data):
        return StorageItem(stream.read_int())

    def write_item_id(self, stream: io.data.Data):
        stream.write_int(self.item_id)

    def read_item_type(self, stream: io.data.Data):
        self.item_type = stream.read_int()

    def write_item_type(self, stream: io.data.Data):
        stream.write_int(self.item_type)

    def serialize(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "StorageItem":
        item = StorageItem(data.get("item_id", 0))
        item.item_type = data.get("item_type", 0)
        return item

    def __repr__(self) -> str:
        return f"StorageItem(item_id={self.item_id}, item_type={self.item_type})"

    def __str__(self) -> str:
        return f"StorageItem(item_id={self.item_id}, item_type={self.item_type})"


class Cats:
    def __init__(self, cats: list[Cat]):
        self.cats = cats

    @staticmethod
    def get_gv_cats(gv: game_version.GameVersion) -> Optional[int]:
        if gv == 20:
            total_cats = 203
        elif gv == 21:
            total_cats = 214
        elif gv == 22:
            total_cats = 231
        elif gv == 23:
            total_cats = 241
        elif gv == 24:
            total_cats = 249
        elif gv == 25:
            total_cats = 260
        else:
            total_cats = None
        return total_cats

    @staticmethod
    def read_unlocked(stream: io.data.Data, gv: game_version.GameVersion) -> "Cats":
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        cats_l: list[Cat] = []
        for i in range(total_cats):
            cats_l.append(Cat.read_unlocked(i, stream))
        return Cats(cats_l)

    def write_unlocked(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_unlocked(stream)

    def read_upgrade(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_upgrade(stream)

    def write_upgrade(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_upgrade(stream)

    def read_current_form(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_current_form(stream)

    def write_current_form(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_current_form(stream)

    def read_unlocked_forms(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_unlocked_forms(stream)

    def write_unlocked_forms(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_unlocked_forms(stream)

    def read_gatya_seen(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_gatya_seen(stream)

    def write_gatya_seen(self, stream: io.data.Data, gv: game_version.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_gatya_seen(stream)

    def read_max_upgrade_levels(
        self, stream: io.data.Data, gv: game_version.GameVersion
    ):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_max_upgrade_level(stream)

    def write_max_upgrade_levels(
        self, stream: io.data.Data, gv: game_version.GameVersion
    ):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_max_upgrade_level(stream)

    def read_storage(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv < 110100:
            total_storage = 100
        else:
            total_storage = stream.read_short()
        self.storage_items: list[StorageItem] = []
        for _ in range(total_storage):
            self.storage_items.append(StorageItem.read_item_id(stream))
        for item in self.storage_items:
            item.read_item_type(stream)

    def write_storage(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv >= 110100:
            stream.write_short(len(self.storage_items))
        for item in self.storage_items:
            item.write_item_id(stream)
        for item in self.storage_items:
            item.write_item_type(stream)

    def read_catguide_collected(self, stream: io.data.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_catguide_collected(stream)

    def write_catguide_collected(self, stream: io.data.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_catguide_collected(stream)

    def read_forth_forms(self, stream: io.data.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_forth_form(stream)

    def read_catseyes_used(self, stream: io.data.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_catseyes_used(stream)

    def write_catseyes_used(self, stream: io.data.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_catseyes_used(stream)

    def write_forth_forms(self, stream: io.data.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_forth_form(stream)

    def read_favorites(self, stream: io.data.Data):
        self.favourites: dict[int, bool] = {}
        total_cats = stream.read_int()
        for _ in range(total_cats):
            cat_id = stream.read_int()
            self.favourites[cat_id] = stream.read_bool()

    def write_favorites(self, stream: io.data.Data):
        stream.write_int(len(self.favourites))
        for cat_id, is_favourite in self.favourites.items():
            stream.write_int(cat_id)
            stream.write_bool(is_favourite)

    def read_chara_new_flags(self, stream: io.data.Data):
        self.chara_new_flags: dict[int, int] = {}
        total_cats = stream.read_int()
        for _ in range(total_cats):
            cat_id = stream.read_int()
            self.chara_new_flags[cat_id] = stream.read_int()

    def write_chara_new_flags(self, stream: io.data.Data):
        stream.write_int(len(self.chara_new_flags))
        for cat_id, new_flag in self.chara_new_flags.items():
            stream.write_int(cat_id)
            stream.write_int(new_flag)

    def read_talents(self, stream: io.data.Data):
        total_cats = stream.read_int()
        counter = 0
        for _ in range(total_cats):
            cat_id = stream.read_int()
            if self.cats[cat_id].talents is None:
                counter += 1
            self.cats[cat_id].read_talents(stream)

    def write_talents(self, stream: io.data.Data):
        total_talents = 0
        for cat in self.cats:
            total_talents += 1 if cat.talents is not None else 0
        stream.write_int(total_talents)
        for cat in self.cats:
            if not cat.talents:
                continue
            stream.write_int(cat.id)
            cat.write_talents(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "cats": [cat.serialize() for cat in self.cats],
            "storage_items": [item.serialize() for item in self.storage_items],
            "favorites": self.favourites,
            "chara_new_flags": self.chara_new_flags,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Cats":
        cats_l = [Cat.deserialize(cat) for cat in data.get("cats", [])]
        cats = Cats(cats_l)
        cats.storage_items = [
            StorageItem.deserialize(item) for item in data.get("storage_items", [])
        ]
        cats.favourites = data.get("favorites", {})
        cats.chara_new_flags = data.get("chara_new_flags", {})
        return cats

    def __repr__(self) -> str:
        return f"Cats(cats={self.cats}, storage_items={self.storage_items}, favourites={self.favourites}, chara_new_flags={self.chara_new_flags})"

    def __str__(self) -> str:
        return self.__repr__()
