"""Module for editing catseyes"""
from typing import Any

from ... import csv_handler, game_data_getter, helper, item


def get_catseye_ids(is_jp: bool) -> list[int]:
    """Get the catseye ids"""

    file_data = game_data_getter.get_file_latest("DataLocal", "Gatyaitembuy.csv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get catseye ids")
        return []
    items = helper.parse_int_list_list(
        csv_handler.parse_csv(
            file_data.decode("utf-8"),
            ",",
        )[1:]
    )
    catseye_ids: dict[int, int] = {}
    for item_id, item_data in enumerate(items):
        category = item_data[6]
        if category == 5:
            index = item_data[7]
            catseye_ids[index] = item_id
    ids = sorted(catseye_ids.items(), key=lambda x: x[0])
    return [id[1] for id in ids]


def get_catseye_names(is_jp: bool) -> list[str]:
    """Get the catseye names"""

    file_data = game_data_getter.get_file_latest("resLocal", "GatyaitemName.csv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get catseye names")
        return []
    item_names = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        helper.get_text_splitter(is_jp),
    )
    catseye_names: list[str] = []
    for catseye_id in get_catseye_ids(is_jp):
        try:
            catseye_names.append(item_names[catseye_id][0])
        except IndexError:
            helper.error_text(f"Failed to get catseye name for {catseye_id}")
    return catseye_names


def edit_catseyes(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing catseyes"""

    catseyes = item.IntItemGroup.from_lists(
        names=get_catseye_names(helper.check_data_is_jp(save_stats)),
        values=save_stats["catseyes"],
        maxes=9999,
        group_name="Catseyes",
    )
    catseyes.edit()
    save_stats["catseyes"] = catseyes.get_values()
    return save_stats
