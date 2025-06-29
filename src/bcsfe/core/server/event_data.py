from __future__ import annotations
from collections.abc import Callable
from typing import Type, TypeVar

from bcsfe import core


class FilterDate:
    def __init__(self, start_mmdd: int, start_hhmm: int, end_mmdd: int, end_hhmm: int):
        self.start_mmdd = start_mmdd
        self.start_hhmm = start_hhmm
        self.end_mmdd = end_mmdd
        self.end_hhmm = end_hhmm

    @staticmethod
    def from_csv_row(row: core.Row) -> FilterDate:
        return FilterDate(
            row.next_int(), row.next_int(), row.next_int(), row.next_int()
        )


class FilterItem:
    def __init__(
        self,
        filter_date: FilterDate | None,
        filter_day_flags: list[bool],  # 31 item array
        filter_week: int,
        filter_times_start_end_hhmm: list[tuple[int, int]],
    ):
        self.filter_date = filter_date
        self.filter_day_flags = filter_day_flags
        self.filter_week = filter_week
        self.filter_times_start_end_hhmm = filter_times_start_end_hhmm

    @staticmethod
    def from_csv_row(row: core.Row) -> FilterItem:
        filter_date_enabled = row.next_bool()

        filter_date = None
        if filter_date_enabled:
            filter_date = FilterDate.from_csv_row(row)

        filter_day_count = row.next_int()

        filter_day_flags: list[bool] = [False] * 31

        for _ in range(filter_day_count):
            day_ind = row.next_int() - 1
            if day_ind >= 0 and day_ind < len(filter_day_flags):
                filter_day_flags[day_ind] = True

        filter_week = row.next_int()
        filter_time_count = row.next_int()

        filter_times_start_end_hhmm: list[tuple[int, int]] = []

        for _ in range(filter_time_count):
            start_hhmm = row.next_int()
            end_hhmm = row.next_int()

            filter_times_start_end_hhmm.append((start_hhmm, end_hhmm))

        return FilterItem(
            filter_date, filter_day_flags, filter_week, filter_times_start_end_hhmm
        )


def split_yyyymmdd(yyyymmdd: int) -> tuple[int, int, int]:
    year = yyyymmdd // 10_000
    month = (yyyymmdd % 10_000) // 100
    day = yyyymmdd % 100

    return year, month, day


def split_hhmm(hhmm: int) -> tuple[int, int]:
    hour = hhmm // 100
    minute = hhmm % 100

    return hour, minute


class FilterData:
    def __init__(
        self,
        start_yyyymmdd: int,
        start_hhmm: int,
        end_yyyymmdd: int,
        end_hhmm: int,
        min_game_version: int,
        max_game_version: int,
        platform_flag: int,
        filter_items: list[FilterItem],
    ):
        self.start_yyyymmdd = start_yyyymmdd
        self.start_hhmm = start_hhmm
        self.end_yyyymmdd = end_yyyymmdd
        self.end_hhmm = end_hhmm
        self.min_game_version = min_game_version
        self.max_game_version = max_game_version
        self.platform_flag = platform_flag
        self.filter_items = filter_items

    @staticmethod
    def from_csv_row(row: core.Row) -> FilterData:
        start_yyyymmdd = row.next_int()
        start_hhmm = row.next_int()
        end_yyyymmdd = row.next_int()
        end_hhmm = row.next_int()
        min_game_version = row.next_int()
        max_game_version = row.next_int()
        platform_flag = row.next_int()
        total_items = row.next_int()

        filter_items: list[FilterItem] = []

        for _ in range(total_items):
            filter_items.append(FilterItem.from_csv_row(row))

        return FilterData(
            start_yyyymmdd,
            start_hhmm,
            end_yyyymmdd,
            end_hhmm,
            min_game_version,
            max_game_version,
            platform_flag,
            filter_items,
        )


class Localization:
    def __init__(self, lang: str, title: str, message: str):
        self.lang = lang
        self.title = title
        self.message = message

    @staticmethod
    def from_csv_row(row: core.Row) -> Localization:
        return Localization(row.next_str(), row.next_str(), row.next_str())


class RarityGatya:
    def __init__(self, prob: int, guaranteed: int):
        self.prob = prob
        self.guaranteed = guaranteed

    @staticmethod
    def from_csv_row(row: core.Row) -> RarityGatya:
        return RarityGatya(row.next_int(), row.next_int())


class ServerGatyaDataSet:
    def __init__(
        self,
        number: int,
        catfood: int,
        stage_progress: int,
        flags: int,
        rarity_info: list[RarityGatya],
        message: str,
        collab_message: tuple[str, str] | None,
    ):
        self.number = number
        self.catfood = catfood
        self.stage_progress = stage_progress
        self.flags = flags
        self.rarity_info = rarity_info
        self.message = message
        self.other_event_message = collab_message

    @staticmethod
    def from_csv_row(row: core.Row, flag: int) -> ServerGatyaDataSet:
        number = row.next_int()
        catfood = row.next_int()
        stage_progress = row.next_int()
        flags = row.next_int()
        rarity_info: list[RarityGatya] = []

        for _ in range(5):
            rarity_info.append(RarityGatya.from_csv_row(row))

        message = row.next_str()

        collab_message = None
        if flag == 4:
            collab_message = (row.next_str(), row.next_str())

        return ServerGatyaDataSet(
            number,
            catfood,
            stage_progress,
            flags,
            rarity_info,
            message,
            collab_message,
        )

    def is_visible_silhouette(self) -> bool:
        return (self.flags & 1) != 0

    def is_required_user_rank_1600(self) -> bool:
        return (self.flags & 2) != 0

    def has_stepup_gatya(self) -> bool:
        return (self.flags & 4) != 0


class ServerGatyaDataItem:
    def __init__(self, filter: FilterData, flags: int, sets: list[ServerGatyaDataSet]):
        self.filter = filter
        self.flags = flags
        self.sets = sets

    @staticmethod
    def from_csv_row(row: core.Row) -> ServerGatyaDataItem:
        filter = FilterData.from_csv_row(row)
        flag = row.next_int()
        count = row.next_int()

        sets: list[ServerGatyaDataSet] = []

        for _ in range(count):
            sets.append(ServerGatyaDataSet.from_csv_row(row, flag))

        return ServerGatyaDataItem(filter, flag, sets)

    def get_normal_flag(self) -> bool:
        return self.flags == 0

    def get_rare_flag(self) -> bool:
        return 1 <= self.flags <= 3

    def get_collab_flag(self) -> bool:
        return self.flags == 4

    def get_first_rare_flag(self) -> bool:
        return self.flags == 2

    def get_first_rare_10_flag(self) -> bool:
        return self.flags == 3


class ServerItemDataItem:
    def __init__(
        self,
        filter: FilterData,
        event_number: int,  # server item id
        item_number: int,
        item_unit: int,  # base quanity, not cat unit (e.g 2 XP+1000s)
        title: str,
        message: str,
        stage_progress: int,
        stage_progress_flag: int,
        flags: int,
        locales: list[Localization] | None,
    ):
        self.filter = filter
        self.event_number = event_number
        self.item_number = item_number
        self.item_unit = item_unit
        self.title = title
        self.message = message
        self.stage_progress = stage_progress
        self.stage_progress_flag = stage_progress_flag
        self.flags = flags
        self.locales = locales

    def is_every_day(self) -> bool:
        return (self.flags & 1) != 0

    def is_required_user_rank_1600(self) -> bool:
        return (self.flags & 2) != 0

    @staticmethod
    def from_csv_row(row: core.Row) -> ServerItemDataItem:
        filter = FilterData.from_csv_row(row)

        event_number = row.next_int()
        item_number = row.next_int()
        item_unit = row.next_int()
        title = row.next_str()
        message = row.next_str()
        stage_progress = row.next_int()
        stage_progress_flag = row.next_bool()
        flags = row.next_int()

        locales: list[Localization] | None = None

        if not row.done():
            locales = []
            total_locales = row.next_int()

            for _ in range(total_locales):
                locales.append(Localization.from_csv_row(row))

        return ServerItemDataItem(
            filter,
            event_number,
            item_number,
            item_unit,
            title,
            message,
            stage_progress,
            stage_progress_flag,
            flags,
            locales,
        )


Item = TypeVar("Item")
T = TypeVar("T")


def read_event_data(
    csv: core.CSV,
    read_func: Callable[[core.Row], Item],
    init_func: Callable[[list[Item]], T],
) -> T | None:
    start = csv.read_line()
    if start is None:
        return None

    if start.next_str() != "[start]":
        return None

    if not start.done():
        return None

    items: list[Item] = []

    while True:
        row = csv.read_line()
        if row is None:
            return None

        if len(row) == 0:
            return None

        if row[0].to_str() == "[end]":
            break

        item = read_func(row)

        items.append(item)

    return init_func(items)


class ServerItemData:
    def __init__(self, items: list[ServerItemDataItem]):
        self.items = items

    @staticmethod
    def from_csv(csv: core.CSV) -> ServerItemData | None:
        return read_event_data(csv, ServerItemDataItem.from_csv_row, ServerItemData)

    @staticmethod
    def from_data(data: core.Data) -> ServerItemData | None:
        csv = core.CSV(data, delimiter="\t", remove_comments=False, remove_empty=False)

        return ServerItemData.from_csv(csv)


class ServerGatyaData:
    def __init__(self, items: list[ServerGatyaDataItem]):
        self.items = items

    @staticmethod
    def from_csv(csv: core.CSV) -> ServerGatyaData | None:
        return read_event_data(csv, ServerGatyaDataItem.from_csv_row, ServerGatyaData)

    @staticmethod
    def from_data(data: core.Data) -> ServerGatyaData | None:
        csv = core.CSV(data, delimiter="\t", remove_comments=False, remove_empty=False)

        return ServerGatyaData.from_csv(csv)
