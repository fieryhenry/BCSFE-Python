from typing import Optional
from bcsfe import core


class Fruit:
    def __init__(
        self,
        id: int,
        seed: bool,
        group: int,
        sort: int,
        require: Optional[int] = None,
        text: Optional[str] = None,
        grow_up: Optional[list[int]] = None,
    ):
        self.id = id
        self.seed = seed
        self.group = group
        self.sort = sort
        self.require = require
        self.text = text
        self.grow_up = grow_up


class Matatabi:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file
        self.matatabi = self.__get_matatabi()
        self.gatya_item_names = core.GatyaItemNames(self.save_file)

    def __get_matatabi(self) -> list[Fruit]:
        gdg = core.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "Matatabi.tsv")
        if data is None:
            return []
        csv = core.CSV(data, "\t")
        matatabi: list[Fruit] = []
        for line in csv.lines[1:]:
            id = line[0].to_int()
            seed = line[1].to_bool()
            group = line[2].to_int()
            sort = line[3].to_int()
            if len(line) > 4:
                require = line[4].to_int()
            else:
                require = None
            if len(line) > 5:
                text = line[5].to_str()
            else:
                text = None
            if len(line) > 6:
                grow_up = [item.to_int() for item in line[6:]]
            else:
                grow_up = None
            matatabi.append(Fruit(id, seed, group, sort, require, text, grow_up))

        return matatabi

    def get_names(self):
        ids = [fruit.id for fruit in self.matatabi]
        names = [self.gatya_item_names.get_name(id) for id in ids]
        return names
