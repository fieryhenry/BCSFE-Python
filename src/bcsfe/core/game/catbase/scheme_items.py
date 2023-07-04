from bcsfe.core import io, game, server
from bcsfe.cli import dialog_creator, color
from typing import Optional


class SchemeDataItem:
    def __init__(
        self,
        id: int,
        type: int,
        type_id: int,
        item_id: int,
        number: int,
        type_id2: Optional[int] = None,
        item_id2: Optional[int] = None,
        number2: Optional[int] = None,
        type_id3: Optional[int] = None,
        item_id3: Optional[int] = None,
        number3: Optional[int] = None,
    ):
        self.id = id
        self.type = type
        self.type_id = type_id
        self.item_id = item_id
        self.number = number
        self.type_id2 = type_id2
        self.item_id2 = item_id2
        self.number2 = number2
        self.type_id3 = type_id3
        self.item_id3 = item_id3
        self.number3 = number3

    def is_cat(self) -> bool:
        return self.type_id == 1

    def get_name(self, localizable: "game.localizable.Localizable"):
        key = f"scheme_popup_{self.id}"
        return localizable.get(key).replace("<flash>,", "").replace("<flash>", "")


class SchemeItems:
    def __init__(self, to_obtain: list[int], received: list[int]):
        self.to_obtain = to_obtain
        self.received = received

    @staticmethod
    def init() -> "SchemeItems":
        return SchemeItems([], [])

    @staticmethod
    def read(stream: io.data.Data) -> "SchemeItems":
        total = stream.read_int()
        to_obtain: list[int] = []
        for _ in range(total):
            to_obtain.append(stream.read_int())

        total = stream.read_int()
        received: list[int] = []
        for _ in range(total):
            received.append(stream.read_int())

        return SchemeItems(to_obtain, received)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.to_obtain))
        for item in self.to_obtain:
            stream.write_int(item)

        stream.write_int(len(self.received))
        for item in self.received:
            stream.write_int(item)

    def serialize(self) -> dict[str, list[int]]:
        return {"to_obtain": self.to_obtain, "received": self.received}

    @staticmethod
    def deserialize(data: dict[str, list[int]]) -> "SchemeItems":
        return SchemeItems(data.get("to_obtain", []), data.get("received", []))

    def __repr__(self) -> str:
        return f"SchemeItems(to_obtain={self.to_obtain!r}, received={self.received!r})"

    def __str__(self) -> str:
        return self.__repr__()

    def edit(self, save_file: "io.save.SaveFile"):
        item_names = game.catbase.gatya_item.GatyaItemNames(save_file)
        localizable = save_file.get_localizable()
        scheme_data = server.game_data_getter.GameDataGetter(save_file).download(
            "DataLocal", "schemeItemData.tsv"
        )
        if scheme_data is None:
            return
        csv = io.bc_csv.CSV(scheme_data, "\t")
        scheme_items: dict[int, SchemeDataItem] = {}
        for line in csv.lines[1:]:
            scheme_items[line[0].to_int()] = SchemeDataItem(
                line[0].to_int(),
                line[1].to_int(),
                line[2].to_int(),
                line[3].to_int(),
                line[4].to_int(),
                line[5].to_int(),
                line[6].to_int(),
                line[7].to_int(),
                line[8].to_int(),
                line[9].to_int(),
                line[10].to_int(),
            )

        options: list[str] = []
        for item in scheme_items.values():
            scheme_name = item.get_name(localizable)
            string = "\n\t"
            if item.is_cat():
                cat_names = game.catbase.cat.Cat.get_names(
                    item.item_id, save_file, localizable
                )
                if cat_names is None:
                    continue
                cat_name = cat_names[0]
                string += scheme_name.replace("%@", cat_name)
            else:
                item_name = item_names.get_name(item.item_id)
                string += scheme_name
                first_index = string.find("%@")
                second_index = string.find("%@", first_index + 1)
                string = (
                    string[:first_index]
                    + str(item.number)
                    + " "
                    + item_name
                    + string[second_index + 2 :]
                )
            string = string.replace("<br>", "\n\t")
            options.append(string)

        scheme_ids, _ = dialog_creator.ChoiceInput(
            options,
            options,
            [],
            {},
            "scheme_items_select",
        ).multiple_choice()
        for option_id in scheme_ids:
            scheme_id = list(scheme_items.keys())[option_id]
            if scheme_id not in self.to_obtain:
                self.to_obtain.append(scheme_id)
            if scheme_id in self.received:
                self.received.remove(scheme_id)

        color.ColoredText.localize("scheme_items_edit_success")