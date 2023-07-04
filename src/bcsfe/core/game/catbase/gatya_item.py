from bcsfe.core import io, server


class GatyaItemNames:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file
        self.names = self.__get_names()

    def __get_names(self) -> list[str]:
        gdg = server.game_data_getter.GameDataGetter(self.save_file)
        data = gdg.download("resLocal", "GatyaitemName.csv")
        if data is None:
            return []
        csv = io.bc_csv.CSV(
            data, io.bc_csv.Delimeter.from_country_code_res(self.save_file.cc)
        )
        names: list[str] = []
        for line in csv:
            names.append(line[0].to_str())

        return names

    def get_name(self, index: int) -> str:
        try:
            return self.names[index]
        except IndexError:
            return ""


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


class GatyaItemBuy:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file
        self.buy = self.get_buy()

    def get_buy(self):
        gdg = server.game_data_getter.GameDataGetter(self.save_file)
        data = gdg.download("DataLocal", "Gatyaitembuy.csv")
        csv = io.bc_csv.CSV(data)
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

    def get_by_category(self, category: int) -> list[GatyaItemBuyItem]:
        return self.sort_by_index(
            [item for item in self.buy if item.category == category]
        )