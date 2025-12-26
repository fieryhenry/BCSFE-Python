from __future__ import annotations
from bcsfe import core


class Popup:
    def __init__(self, seen: bool):
        self.seen = seen

    @staticmethod
    def init() -> Popup:
        return Popup(False)

    @staticmethod
    def read(stream: core.Data) -> Popup:
        seen = stream.read_bool()
        return Popup(seen)

    def write(self, stream: core.Data):
        stream.write_bool(self.seen)

    def serialize(self) -> bool:
        return self.seen

    @staticmethod
    def deserialize(data: bool) -> Popup:
        return Popup(data)

    def __repr__(self) -> str:
        return f"Popup(seen={self.seen!r})"

    def __str__(self) -> str:
        return self.__repr__()


class UnlockPopups:
    def __init__(self, popups: dict[int, Popup]):
        self.popups = popups

    @staticmethod
    def init() -> UnlockPopups:
        return UnlockPopups({})

    @staticmethod
    def read(stream: core.Data) -> UnlockPopups:
        total = stream.read_int()
        popups: dict[int, Popup] = {}
        for _ in range(total):
            key = stream.read_int()
            popups[key] = Popup.read(stream)
        return UnlockPopups(popups)

    def write(self, stream: core.Data):
        stream.write_int(len(self.popups))
        for key, popup in self.popups.items():
            stream.write_int(key)
            popup.write(stream)

    def serialize(self) -> dict[int, bool]:
        return {key: popup.serialize() for key, popup in self.popups.items()}

    @staticmethod
    def deserialize(data: dict[int, bool]) -> UnlockPopups:
        return UnlockPopups(
            {int(key): Popup.deserialize(popup) for key, popup in data.items()}
        )

    def __repr__(self) -> str:
        return f"Popups(popups={self.popups!r})"

    def __str__(self) -> str:
        return self.__repr__()


class UnlockPopupLine:
    def __init__(
        self,
        popup_id: int,
        enabled: bool,
        conditions: int,
        stage: int,
        map_conditions: int,
        user_rank: int,
        get_char_id1: int,
        get_char_id2: int,
        os_id: int,
        unlock_eye_1_id: int,
        add_level1: int,
        unlock_eye_2_id: int,
        add_level2: int,
        unlock_plus_id: int,
        add_level: int,
        skill_id: int,
        item_id: int,
        num: int,
        help_enabled: bool,
    ):
        self.popup_id = popup_id
        self.enabled = enabled
        self.conditions = conditions
        self.stage = stage
        self.map_conditions = map_conditions
        self.user_rank = user_rank
        self.get_char_id1 = get_char_id1
        self.get_char_id2 = get_char_id2
        self.os_id = os_id
        self.unlock_eye_1_id = unlock_eye_1_id
        self.add_level1 = add_level1
        self.unlock_eye_2_id = unlock_eye_2_id
        self.add_level2 = add_level2
        self.unlock_plus_id = unlock_plus_id
        self.add_level = add_level
        self.skill_id = skill_id
        self.item_id = item_id
        self.num = num
        self.help_enabled = help_enabled

    @staticmethod
    def from_csv_row(row: core.Row) -> UnlockPopupLine:
        return UnlockPopupLine(
            row.next_int(),
            row.next_bool(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_bool(),
        )


class UnlockPopupData:
    def __init__(self, popups: list[UnlockPopupLine]):
        self.popups = popups

    @staticmethod
    def from_csv(csv: core.CSV) -> UnlockPopupData:
        popups: list[UnlockPopupLine] = []
        for line in csv.lines[1:]:
            popups.append(UnlockPopupLine.from_csv_row(line))

        return UnlockPopupData(popups)

    @staticmethod
    def from_save(save_file: core.SaveFile) -> UnlockPopupData | None:
        gdg = core.core_data.get_game_data_getter(save_file)
        data = gdg.download("DataLocal", "unlockPopup.tsv")
        if data is None:
            return None

        csv = core.CSV(data, "\t")

        return UnlockPopupData.from_csv(csv)
