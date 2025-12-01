from __future__ import annotations

from bcsfe import core


class MapOptionLine:
    def __init__(
        self,
        map_id: int,
        crown_count: int,
        crown_mults: list[int],
        guerrilla_set: int,
        reset_type: int,
        one_time_display: bool,
        display_order: int,
        interval: int,
        challenge_flag: bool,
        difficulty_mask: int,
        hide_after_clear: bool,
        name: str,
    ):
        self.map_id = map_id
        self.crown_count = crown_count
        self.crown_mults = crown_mults
        self.guerrilla_set = guerrilla_set
        self.reset_type = reset_type
        self.one_time_display = one_time_display
        self.display_order = display_order
        self.interval = interval
        self.challenge_flag = challenge_flag
        self.difficulty_mask = difficulty_mask
        self.hide_after_clear = hide_after_clear
        self.name = name

    @staticmethod
    def from_line(line: core.Row) -> MapOptionLine:
        return MapOptionLine(
            line.next_int(),
            line.next_int(),
            [line.next_int() for _ in range(4)],
            line.next_int(),
            line.next_int(),
            line.next_bool(),
            line.next_int(),
            line.next_int(),
            line.next_bool(),
            line.next_int(),
            line.next_bool(),
            line.next_str(),
        )


class MapOption:
    def __init__(self, maps: dict[int, MapOptionLine]):
        self.maps = maps

    @staticmethod
    def from_csv(csv: core.CSV) -> MapOption:
        data: dict[int, MapOptionLine] = {}

        for line in csv.lines[1:]:  # skip headers
            item = MapOptionLine.from_line(line)
            data[item.map_id] = item

        return MapOption(data)

    @staticmethod
    def from_save(save_file: core.SaveFile) -> MapOption | None:
        gdg = core.core_data.get_game_data_getter(save_file)
        data = gdg.download("DataLocal", "Map_option.csv")
        if data is None:
            return None

        csv = core.CSV(data)

        return MapOption.from_csv(csv)

    def get_map(self, map_id: int) -> MapOptionLine | None:
        return self.maps.get(map_id)
