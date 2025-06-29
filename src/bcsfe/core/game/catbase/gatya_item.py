from __future__ import annotations
import enum
from bcsfe import core


class GatyaItemNames:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.names = self.__get_names()

    def __get_names(self) -> list[str] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", "GatyaitemName.csv")
        if data is None:
            return None
        csv = core.CSV(
            data, core.Delimeter.from_country_code_res(self.save_file.cc)
        )
        names: list[str] = []
        for line in csv:
            names.append(line[0].to_str())

        return names

    def get_name(self, index: int) -> str | None:
        if self.names is None:
            return None
        try:
            return self.names[index]
        except IndexError:
            return core.core_data.local_manager.get_key(
                "gatya_item_unknown_name", index=index
            )


class GatyaItemBuyItem:
    def __init__(
        self,
        id: int,
        rarity: int,
        reflect_or_storage: bool,
        price: int,
        stage_drop_id: int,
        quantity: int,
        server_id: int,
        category: int,
        index: int,
        src_item_id: int,
        main_menu_type: int,
        gatya_ticket_id: int,
        comment: str,
    ):
        self.id = id
        self.rarity = rarity
        self.reflect_or_storage = reflect_or_storage
        self.price = price
        self.stage_drop_id = stage_drop_id
        self.quantity = quantity
        self.server_id = server_id
        self.category = category
        self.index = index
        self.src_item_id = src_item_id
        self.main_menu_type = main_menu_type
        self.gatya_ticket_id = gatya_ticket_id
        self.comment = comment

class GatyaItemCategory(enum.Enum):
    MISC = 0
    EVENT_TICKETS = 1
    SPECIAL_SKILLS = 2
    BATTLE_ITEMS = 3
    EVOLVE_ITEMS = 4
    CATSEYES = 5
    CATAMINS = 6
    BASE_MATERIALS = 7
    LUCKY_TICKETS_1 = 8
    ENDLESS_ITEMS = 9
    LUCKY_TICKETS_2 = 10
    LABYRINTH_MEDALS = 11
    TREASURE_CHESTS = 12

class GatyaItemBuy:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.buy = self.get_buy()

    def get_buy(self) -> list[GatyaItemBuyItem] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "Gatyaitembuy.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        buy: list[GatyaItemBuyItem] = []
        for i, line in enumerate(csv.lines[1:]):
            try:
                buy.append(
                    GatyaItemBuyItem(
                        i,
                        line[0].to_int(),
                        line[1].to_bool(),
                        line[2].to_int(),
                        line[3].to_int(),
                        line[4].to_int(),
                        line[5].to_int(),
                        line[6].to_int(),
                        line[7].to_int(),
                        line[8].to_int(),
                        line[9].to_int(),
                        line[10].to_int(),
                        line[11].to_str(),
                    )
                )
            except IndexError:
                pass

        return buy

    def sort_by_index(self, items: list[GatyaItemBuyItem]):
        items.sort(key=lambda x: x.index)
        return items

    def get_by_category(self, category: int | GatyaItemCategory) -> list[GatyaItemBuyItem] | None:
        if self.buy is None:
            return None
        if isinstance(category, GatyaItemCategory):
            category = category.value
        return self.sort_by_index(
            [item for item in self.buy if item.category == category]
        )

    def get_names_by_category(self, category: int | GatyaItemCategory) -> list[tuple[GatyaItemBuyItem, str | None]] | None:
        items = self.get_by_category(category)
        if items is None:
            return None

        names = GatyaItemNames(self.save_file)

        return [(item, names.get_name(item.id)) for item in items]

    def get(self, item_id: int) -> GatyaItemBuyItem | None:
        if self.buy is None:
            return None
        if item_id < 0 or item_id >= len(self.buy):
            return None

        return self.buy[item_id]

    def get_by_server_id(self, server_id: int) -> GatyaItemBuyItem | None:
        if self.buy is None:
            return None
        for item in self.buy:
            if item.server_id == server_id:
                return item

        return None
