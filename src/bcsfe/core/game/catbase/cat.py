from typing import Any, Optional
from bcsfe.core.game.catbase import upgrade
from bcsfe.core import io, game_version, server, game


class Talent:
    def __init__(self, id: int, level: int):
        self.id = id
        self.level = level

    @staticmethod
    def init() -> "Talent":
        return Talent(0, 0)

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


class NyankoPictureBookCatData:
    def __init__(
        self,
        cat_id: int,
        is_displayed_in_catguide: bool,
        limited: bool,
        total_forms: int,
        hint_display_type: int,
        scale_0: int,
        scale_1: int,
        scale_2: int,
        scale_3: int,
    ):
        self.cat_id = cat_id
        self.is_displayed_in_catguide = is_displayed_in_catguide
        self.limited = limited
        self.total_forms = total_forms
        self.hint_display_type = hint_display_type
        self.scale_0 = scale_0
        self.scale_1 = scale_1
        self.scale_2 = scale_2
        self.scale_3 = scale_3


class NyankoPictureBook:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file
        self.cats = self.get_cats()

    def get_cats(self) -> list[NyankoPictureBookCatData]:
        gdg = server.game_data_getter.GameDataGetter(self.save_file)
        data = gdg.download("DataLocal", "nyankoPictureBookData.csv")
        if data is None:
            return []
        csv = io.bc_csv.CSV(data)
        cats: list[NyankoPictureBookCatData] = []
        for i, line in enumerate(csv):
            cat = NyankoPictureBookCatData(
                i,
                line[0].to_bool(),
                line[1].to_bool(),
                line[2].to_int(),
                line[3].to_int(),
                line[4].to_int(),
                line[5].to_int(),
                line[6].to_int(),
                line[7].to_int(),
            )
            cats.append(cat)
        return cats

    def get_cat(self, cat_id: int) -> Optional[NyankoPictureBookCatData]:
        for cat in self.cats:
            if cat.cat_id == cat_id:
                return cat
        return None

    def get_obtainable_cats(self) -> list[NyankoPictureBookCatData]:
        return [cat for cat in self.cats if cat.is_displayed_in_catguide]


class EvolveItem:
    """Represents an item used to evolve a unit."""

    def __init__(
        self,
        item_id: int,
        amount: int,
    ):
        """Initializes a new EvolveItem object.

        Args:
            item_id (int): The ID of the item.
            amount (int): The amount of the item.
        """
        self.item_id = item_id
        self.amount = amount

    def __str__(self) -> str:
        """Gets a string representation of the EvolveItem object.

        Returns:
            str: The string representation of the EvolveItem object.
        """
        return f"{self.item_id}:{self.amount}"

    def __repr__(self) -> str:
        """Gets a string representation of the EvolveItem object.

        Returns:
            str: The string representation of the EvolveItem object.
        """
        return str(self)


class EvolveItems:
    """Represents the items used to evolve a unit."""

    def __init__(self, evolve_items: list[EvolveItem]):
        """Initializes a new EvolveItems object.

        Args:
            evolve_items (list[EvolveItem]): The items used to evolve a unit.
        """
        self.evolve_items = evolve_items

    @staticmethod
    def from_unit_buy_list(
        raw_data: "io.bc_csv.Row", start_index: int
    ) -> "EvolveItems":
        """Creates a new EvolveItems object from a row from unitbuy.csv.

        Args:
            raw_data (io.bc_csv.Row): The row from unitbuy.csv.

        Returns:
            EvolveItems: The EvolveItems object.
        """
        items: list[EvolveItem] = []
        for i in range(5):
            item_id = raw_data[start_index + i * 2].to_int()
            amount = raw_data[start_index + 1 + i * 2].to_int()
            items.append(EvolveItem(item_id, amount))
        return EvolveItems(items)


class UnitBuyCatData:
    def __init__(self, id: int, raw_data: "io.bc_csv.Row"):
        self.id = id
        self.assign(raw_data)

    def assign(self, raw_data: "io.bc_csv.Row"):
        self.stage_unlock = raw_data[0].to_int()
        self.purchase_cost = raw_data[1].to_int()
        self.upgrade_costs = [cost.to_int() for cost in raw_data[2:12]]
        self.unlock_source = raw_data[12].to_int()
        self.rarity = raw_data[13].to_int()
        self.position_order = raw_data[14].to_int()
        self.chapter_unlock = raw_data[15].to_int()
        self.sell_price = raw_data[16].to_int()
        self.gatya_rarity = raw_data[17].to_int()
        self.original_max_levels = raw_data[18].to_int(), raw_data[19].to_int()
        self.force_true_form_level = raw_data[20].to_int()
        self.second_form_unlock_level = raw_data[21].to_int()
        self.unknown_22 = raw_data[22].to_int()
        self.tf_id = raw_data[23].to_int()
        self.ff_id = raw_data[24].to_int()
        self.evolve_level_tf = raw_data[25].to_int()
        self.evolve_level_ff = raw_data[26].to_int()
        self.evolve_cost_tf = raw_data[27].to_int()
        self.evolve_items_tf = EvolveItems.from_unit_buy_list(raw_data, 28)
        self.evolve_cost_ff = raw_data[38].to_int()
        self.evolve_items_ff = EvolveItems.from_unit_buy_list(raw_data, 39)
        self.max_upgrade_level_no_catseye = raw_data[49].to_int()
        self.max_upgrade_level_catseye = raw_data[50].to_int()
        self.max_plus_upgrade_level = raw_data[51].to_int()
        self.unknown_52 = raw_data[52].to_int()
        self.unknown_53 = raw_data[53].to_int()
        self.unknown_54 = raw_data[54].to_int()
        self.unknown_55 = raw_data[55].to_int()
        self.catseye_usage_pattern = raw_data[56].to_int()
        self.game_version = raw_data[57].to_int()
        self.np_sell_price = raw_data[58].to_int()
        self.unknwon_59 = raw_data[59].to_int()
        self.unknown_60 = raw_data[60].to_int()
        self.egg_value = raw_data[61].to_int()
        self.egg_id = raw_data[62].to_int()


class UnitBuy:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file
        self.unit_buy = self.read_unit_buy()

    def read_unit_buy(self) -> list[UnitBuyCatData]:
        unit_buy: list[UnitBuyCatData] = []
        gdg = server.game_data_getter.GameDataGetter(self.save_file)
        data = gdg.download("DataLocal", "unitbuy.csv")
        if data is None:
            return unit_buy
        csv = io.bc_csv.CSV(data)
        for i, line in enumerate(csv):
            unit_buy.append(UnitBuyCatData(i, line))
        return unit_buy

    def get_unit_buy(self, id: int) -> Optional[UnitBuyCatData]:
        try:
            return self.unit_buy[id]
        except IndexError:
            return None

    def get_cat_rarity(self, id: int) -> int:
        unit_buy = self.get_unit_buy(id)
        if unit_buy is None:
            return -1
        return unit_buy.rarity


class Cat:
    def __init__(self, id: int, unlocked: int):
        self.id = id
        self.unlocked = unlocked
        self.talents: Optional[list[Talent]] = None
        self.upgrade: upgrade.Upgrade = upgrade.Upgrade.init()
        self.current_form: int = 0
        self.unlocked_forms: int = 0
        self.gatya_seen: int = 0
        self.max_upgrade_level: upgrade.Upgrade = upgrade.Upgrade.init()
        self.catguide_collected: bool = False
        self.forth_form: int = 0
        self.catseyes_used: int = 0

        self.names: Optional[list[str]] = None

    @staticmethod
    def init(id: int) -> "Cat":
        return Cat(id, 0)

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

    def get_names_cls(
        self, save_file: "io.save.SaveFile", localizable: "game.localizable.Localizable"
    ) -> list[str]:
        if self.names is None:
            self.names = Cat.get_names(self.id, save_file, localizable)
        return self.names

    @staticmethod
    def get_names(
        id: int,
        save_file: "io.save.SaveFile",
        localizable: "game.localizable.Localizable",
    ) -> list[str]:
        file_name = f"Unit_Explanation{id+1}_{localizable.get_lang()}.csv"
        data = server.game_data_getter.GameDataGetter(save_file).download(
            "resLocal", file_name
        )
        if data is None:
            return []
        csv = io.bc_csv.CSV(
            data,
            io.bc_csv.Delimeter.from_country_code_res(save_file.cc),
            remove_empty=False,
        )
        names: list[str] = []
        for line in csv.lines:
            names.append(line[0].to_str())

        return names


class StorageItem:
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.item_type = 0

    @staticmethod
    def init() -> "StorageItem":
        return StorageItem(0)

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
    def __init__(self, cats: list[Cat], total_storage_items: int = 0):
        self.cats = cats
        self.storage_items = [StorageItem.init() for _ in range(total_storage_items)]
        self.favourites: dict[int, bool] = {}
        self.chara_new_flags: dict[int, int] = {}
        self.unit_buy: Optional[UnitBuy] = None
        self.nyanko_picture_book: Optional[NyankoPictureBook] = None
        self.bulk_downloaded = False

    @staticmethod
    def init(gv: game_version.GameVersion) -> "Cats":
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = 0
        cats_l: list[Cat] = []
        for i in range(total_cats):
            cats_l.append(Cat.init(i))

        if gv < 110100:
            total_storage_items = 100
        else:
            total_storage_items = 0
        return Cats(cats_l, total_storage_items)

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

    def get_unlocked_cats(self) -> list[Cat]:
        return [cat for cat in self.cats if cat.unlocked]

    def read_unitbuy(self, save_file: "io.save.SaveFile") -> UnitBuy:
        if self.unit_buy is None:
            self.unit_buy = UnitBuy(save_file)
        return self.unit_buy

    def read_nyanko_picture_book(
        self, save_file: "io.save.SaveFile"
    ) -> NyankoPictureBook:
        if self.nyanko_picture_book is None:
            self.nyanko_picture_book = NyankoPictureBook(save_file)
        return self.nyanko_picture_book

    def get_cats_rarity(self, save_file: "io.save.SaveFile", rarity: int) -> list[Cat]:
        unit_buy = self.read_unitbuy(save_file)
        return [cat for cat in self.cats if unit_buy.get_cat_rarity(cat.id) == rarity]

    def get_cats_name(
        self,
        save_file: "io.save.SaveFile",
        search_name: str,
    ) -> list[Cat]:
        self.bulk_download_names(save_file)
        localizable = save_file.get_localizable()
        cats: list[Cat] = []
        for cat in self.cats:
            names = cat.get_names_cls(save_file, localizable)
            for name in names:
                if search_name.lower() in name.lower():
                    cats.append(cat)
                    break
        return cats

    def bulk_download_names(self, save_file: "io.save.SaveFile"):
        if self.bulk_downloaded:
            return
        localizable = save_file.get_localizable()
        file_names: list[str] = []
        gdg = server.game_data_getter.GameDataGetter(save_file)
        for cat in self.cats:
            if cat.names is None:
                file_name = f"Unit_Explanation{cat.id+1}_{localizable.get_lang()}.csv"
                if gdg.is_downloaded("resLocal", file_name):
                    continue
                file_names.append(file_name)
                cat.names = []

        server.game_data_getter.GameDataGetter(save_file).download_all(
            "resLocal", file_names
        )
        self.bulk_downloaded = True

    def get_cats_obtainable(self, save_file: "io.save.SaveFile") -> list[Cat]:
        nyanko_picture_book = self.read_nyanko_picture_book(save_file)
        ny_cats = [cat.cat_id for cat in nyanko_picture_book.get_obtainable_cats()]
        cats: list[Cat] = []
        for cat in self.cats:
            if cat.id in ny_cats:
                cats.append(cat)
        return cats

    def get_cats_by_ids(self, ids: list[int]) -> list[Cat]:
        cats: list[Cat] = []
        for cat in self.cats:
            if cat.id in ids:
                cats.append(cat)
        return cats

    @staticmethod
    def get_rarity_names(save_file: "io.save.SaveFile") -> list[str]:
        localizable = save_file.get_localizable()
        rarity_names: list[str] = []
        rarity_index = 1
        while True:
            rarity_name = localizable.get_optional(f"rarity_name_{rarity_index}")
            if rarity_name is None:
                break
            rarity_names.append(rarity_name)
            rarity_index += 1
        return rarity_names

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
