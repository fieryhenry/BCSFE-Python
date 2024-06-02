from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class Medals:
    def __init__(
        self,
        u1: int,
        u2: int,
        u3: int,
        medal_data_1: list[int],
        medal_data_2: dict[int, int],
        ub: bool,
    ):
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.medal_data_1 = medal_data_1
        self.medal_data_2 = medal_data_2
        self.ub = ub

    @staticmethod
    def init() -> Medals:
        return Medals(0, 0, 0, [], {}, False)

    @staticmethod
    def read(data: core.Data) -> Medals:
        u1 = data.read_int()
        u2 = data.read_int()
        u3 = data.read_int()
        total_medals = data.read_short()
        medal_data_1 = data.read_short_list(total_medals)
        total_medals = data.read_short()
        medal_data_2: dict[int, int] = {}
        for _ in range(total_medals):
            key = data.read_short()
            value = data.read_byte()
            medal_data_2[key] = value
        ub = data.read_bool()
        return Medals(u1, u2, u3, medal_data_1, medal_data_2, ub)

    def write(self, data: core.Data) -> None:
        data.write_int(self.u1)
        data.write_int(self.u2)
        data.write_int(self.u3)
        data.write_short(len(self.medal_data_1))
        data.write_short_list(self.medal_data_1, write_length=False)
        data.write_short(len(self.medal_data_2))
        for key, value in self.medal_data_2.items():
            data.write_short(key)
            data.write_byte(value)
        data.write_bool(self.ub)

    def serialize(self) -> dict[str, Any]:
        return {
            "u1": self.u1,
            "u2": self.u2,
            "u3": self.u3,
            "medal_data_1": self.medal_data_1,
            "medal_data_2": self.medal_data_2,
            "ub": self.ub,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Medals:
        return Medals(
            data.get("u1", 0),
            data.get("u2", 0),
            data.get("u3", 0),
            data.get("medal_data_1", []),
            data.get("medal_data_2", {}),
            data.get("ub", False),
        )

    def __repr__(self) -> str:
        return (
            f"Medals(u1={self.u1}, u2={self.u2}, u3={self.u3}, "
            f"medal_data_1={self.medal_data_1}, medal_data_2={self.medal_data_2}, "
            f"ub={self.ub})"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def has_medal(self, medal_id: int) -> bool:
        return medal_id in self.medal_data_1

    @staticmethod
    def edit_medals(save_file: core.SaveFile):
        medals = save_file.medals
        medal_names = core.core_data.get_medal_names(save_file)
        if medal_names.medal_names is None:
            return
        options = ["add_medals", "remove_medals"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="medal_add_remove_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        add_medals = choice == 0

        medals_to_choose_from: list[tuple[int, str]] = []
        for i, medal in enumerate(medal_names.medal_names):
            if len(medal) == 0:
                continue
            if medals.has_medal(i) == add_medals:
                continue
            key = "medal_string"
            string = core.core_data.local_manager.get_key(
                key, medal_name=medal[0], medal_req=medal[1]
            )
            medals_to_choose_from.append((i, string))
        if len(medals_to_choose_from) == 0:
            return
        options = [medal[1] for medal in medals_to_choose_from]
        choices, _ = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="select_medals"
        ).multiple_choice()
        if choices is None:
            return
        for choice in choices:
            medal_id = medals_to_choose_from[choice][0]
            if add_medals:
                medals.add_medal(medal_id)
            else:
                medals.remove_medal(medal_id)

        if add_medals:
            color.ColoredText.localize("medals_added")
        else:
            color.ColoredText.localize("medals_removed")

    def add_medal(self, medal_id: int) -> None:
        if self.has_medal(medal_id):
            return
        self.medal_data_1.append(medal_id)
        self.medal_data_2[medal_id] = 0

    def remove_medal(self, medal_id: int) -> None:
        if medal_id in self.medal_data_2:
            del self.medal_data_2[medal_id]
        if medal_id in self.medal_data_1:
            self.medal_data_1.remove(medal_id)


class MedalNames:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.medal_names = self.get_medal_names()

    def get_medal_names(self) -> list[list[str]] | None:
        file_name = "medalname.tsv"
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", file_name)
        if data is None:
            return None
        csv = core.CSV(data, delimiter="\t")
        names: list[list[str]] = []
        for row in csv:
            names.append(row.to_str_list())
        return names

    def get_medal_name(self, medal_id: int) -> list[str] | None:
        if self.medal_names is None:
            return None
        if medal_id < 0 or medal_id >= len(self.medal_names):
            return []
        return self.medal_names[medal_id]
