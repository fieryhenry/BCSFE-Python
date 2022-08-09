"""Handler for selecting cat ids"""

from typing import Any

from ... import user_input_handler, helper, game_data_getter, csv_handler
from . import upgrade_cats
from ..levels import treasures

def select_cats_not_current(save_stats: dict[str, Any]) -> list[int]:
    """Select cats not currently unlocked"""

    options = [
        "Select cats of a certain rarity",
        "Select specific cat ids",
        "Select cats of a specific gacha banner",
        "Select all cats"
    ]
    choice = user_input_handler.select_single(options, "select")
    if choice == 1:
        return select_cats_rarity(helper.check_data_is_jp(save_stats))
    if choice == 2:
        return select_cats_range(save_stats)
    if choice == 3:
        return select_cats_gatya_banner(helper.check_data_is_jp(save_stats))
    if choice == 4:
        return get_all_cats(save_stats)
    return []

def select_cats(save_stats: dict[str, Any], current: bool = True) -> list[int]:
    """Select cats"""

    if not current:
        return select_cats_not_current(save_stats)

    options = [
        "Select currently unlocked cats",
        "Select cats of a certain rarity",
        "Select specific cat ids",
        "Select cats of a specific gacha banner",
        "Select all cats"
    ]
    choice = user_input_handler.select_single(options, "select")
    if choice == 1:
        return select_current_cats(save_stats)
    if choice == 2:
        return select_cats_rarity(helper.check_data_is_jp(save_stats))
    if choice == 3:
        return select_cats_range(save_stats)
    if choice == 4:
        return select_cats_gatya_banner(helper.check_data_is_jp(save_stats))
    if choice == 5:
        return get_all_cats(save_stats)
    return []


def select_current_cats(save_stats: dict[str, Any]) -> list[int]:
    """Select current cats"""

    cats = save_stats["cats"]
    cat_ids: list[int] = []
    for i, cat_val in enumerate(cats):
        if cat_val == 1:
            cat_ids.append(i)
    return cat_ids


def select_cats_rarity(is_jp: bool) -> list[int]:
    """Select cats of a certain rarity"""

    ids = user_input_handler.select_not_inc(
        options=upgrade_cats.TYPES,
        mode="upgrade",
    )

    cat_ids = upgrade_cats.get_rarity(ids, is_jp)
    return cat_ids


def select_cats_range(save_stats: dict[str, Any]) -> list[int]:
    """Select cats in a range"""

    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        length=len(save_stats["cats"]),
    )
    return ids


def select_cats_gatya_banner(is_jp: bool) -> list[int]:
    """Select cats for a specific gacha banner"""

    data = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest(
                "DataLocal", "GatyaDataSetR1.csv", is_jp
            ).decode("utf-8")
        )
    )
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter gacha banner id (Look up the gacha banners you want, then click on the image at the top, and look for the last digits of the file name (e.g royal fest = 602)):"
        ),
        length=len(data),
    )
    data = treasures.remove_negative_1(data)
    cat_ids: list[int] = []
    for c_id in ids:
        cat_ids.extend(data[c_id])
    return cat_ids

def get_all_cats(save_stats: dict[str, Any]) -> list[int]:
    """Get all cats"""

    return list(range(len(save_stats["cats"])))