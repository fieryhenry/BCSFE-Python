"""Handler for cat upgrades"""
from typing import Any, Union

from ... import helper, user_input_handler, game_data_getter, csv_handler
from . import cat_id_selector

def get_rarities(is_jp: bool) -> list[int]:
    """Get all cat ids of each rarity"""

    file_data = game_data_getter.get_file_latest("DataLocal", "unitbuy.csv", is_jp).decode("utf-8")
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data))
    rarity_ids = helper.copy_first_n(data, 13)
    return rarity_ids


def get_rarity(rarity_ids: list[int], is_jp: bool) -> list[int]:
    """Get all cat ids of a certain rarity"""

    rarities = get_rarities(is_jp)
    cat_ids: list[int] = []
    for rarity_id in rarity_ids:
        for i, rarity_val in enumerate(rarities):
            if int(rarity_val) == rarity_id:
                cat_ids.append(i)
    return cat_ids


TYPES = [
    "Normal",
    "Special",
    "Rare",
    "Super Rare",
    "Uber Super Rare",
    "Legend Rare",
]


def set_user_popups(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Set user popups, stops the user rank popups from spamming up the screen"""

    save_stats["user_rank_popups"]["Value"] = 0xFFFFFF
    return save_stats


def get_plus_base(usr_input: str) -> tuple[Union[int, None], Union[int, None]]:
    """Get the base and plus level of an input"""

    split = usr_input.split("+")
    base = None
    plus = None
    if split[0]:
        base = helper.check_int(split[0])
    if len(split) == 2 and split[1]:
        plus = helper.check_int(split[1])
    if len(split) == 1:
        plus = 0
    return base, plus


def upgrade_cats(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Upgrade specific cats"""

    ids = cat_id_selector.select_cats(save_stats)

    return upgrade_cats_ids(save_stats, ids)


def upgrade_handler(
    data: dict[str, Any], ids: list[int], item_name: str, save_stats: dict[str, Any]
) -> dict[str, Any]:
    """Handler for cat upgrades"""

    ids = helper.check_cat_ids(ids, save_stats)

    base = data["Base"]
    plus = data["Plus"]
    individual = True
    if len(ids) > 1:
        individual = (
            user_input_handler.colored_input(
                f"Do you want to upgrade each {item_name} individually(&1&), or all at once(&2&):"
            )
            == "1"
        )
    first = True
    base_lvl = None
    plus_lvl = None
    for cat_id in ids:
        if not individual and first:
            levels = get_plus_base(
                user_input_handler.colored_input(
                    'Enter the base level followed by a "&+&" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n'
                )
            )
            base_lvl = levels[0]
            plus_lvl = levels[1]
            first = False
        elif individual:
            helper.colored_text(
                f"The current upgrade level of id &{cat_id}& is &{base[cat_id]+1}&+&{plus[cat_id]}&"
            )
            levels = get_plus_base(
                user_input_handler.colored_input(
                    f'Enter the base level for {item_name}: &{cat_id}& followed by a "&+&" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n'
                )
            )
            base_lvl = levels[0]
            plus_lvl = levels[1]
        if base_lvl is not None:
            base[cat_id] = base_lvl - 1
        if plus_lvl is not None:
            plus[cat_id] = plus_lvl
    data["Base"] = base
    data["Plus"] = plus

    return data


def upgrade_cats_ids(save_stats: dict[str, Any], ids: list[int]) -> dict[str, Any]:
    """Upgrade cats by ids"""

    save_stats["cat_upgrades"] = upgrade_handler(
        data=save_stats["cat_upgrades"],
        ids=ids,
        item_name="cat",
        save_stats=save_stats,
    )
    save_stats = set_user_popups(save_stats)
    print("Successfully set cat levels")
    return save_stats
