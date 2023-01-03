"""Scheme item edit"""
from typing import Any

from ... import csv_handler, game_data_getter, helper, user_input_handler


def get_item_names(is_jp: bool) -> list[str]:
    """Get the item names

    Args:
        is_jp (bool): If the data is for jp

    Returns:
        list[str]: The item names
    """
    item_names = game_data_getter.get_file_latest(
        "resLocal", "GatyaitemName.csv", is_jp
    )
    if item_names is None:
        helper.error_text("Failed to get item names")
        return []

    item_names = csv_handler.parse_csv(
        item_names.decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )
    names: list[str] = []
    for item in item_names:
        names.append(item[0])
    return names


def get_scheme_data(is_jp: bool) -> list[list[int]]:
    """Get the scheme data

    Args:
        is_jp (bool): If the data is for jp

    Returns:
        list[list[int]]: The scheme data
    """
    scheme_data = game_data_getter.get_file_latest(
        "DataLocal", "schemeItemData.tsv", is_jp
    )
    if scheme_data is None:
        helper.error_text("Failed to get scheme data")
        return []

    scheme_data_data = helper.parse_int_list_list(
        csv_handler.parse_csv(
            scheme_data.decode("utf-8"),
            delimeter="\t",
        )
    )
    return scheme_data_data


def get_scheme_names(is_jp: bool, scheme_data: list[list[int]]) -> dict[int, str]:
    """Get the scheme names"""

    file_data = game_data_getter.get_file_latest("resLocal", "localizable.tsv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get scheme names")
        return {}

    localizable = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        delimeter="\t",
    )
    names: dict[int, str] = {}
    for scheme in scheme_data[1:]:
        scheme_id = scheme[0]
        for name in localizable:
            scheme_str = f"scheme_popup_{scheme_id}"
            if name[0] == scheme_str:
                scheme_name = name[1].replace("<flash>", "").replace("</flash>", "")
                names[scheme_id] = scheme_name
                break
    return names


def get_cat_name(cat_id: int, is_jp: bool, cc: str) -> str:
    """Get the cat name"""

    file_data = game_data_getter.get_file_latest(
        "resLocal", f"Unit_Explanation{cat_id+1}_{cc}.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Failed to get cat names")
        return ""

    cat_name = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )
    return cat_name[0][0]


def edit_scheme_data(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing scheme data"""

    is_jp = helper.check_data_is_jp(save_stats)
    data = get_scheme_data(is_jp)
    names = get_scheme_names(is_jp, data)
    item_names = get_item_names(is_jp)

    options: list[str] = []
    for scheme in data[1:]:
        scheme_id = scheme[0]
        is_cat = scheme[2] == 1
        item_id = scheme[3]
        amount = scheme[4]
        try:
            scheme_name = names[scheme_id]
        except KeyError:
            continue
        string = "\n\t"
        if is_cat:
            cat_name = get_cat_name(item_id, is_jp, helper.get_lang(is_jp))
            string += scheme_name.replace("%@", cat_name)
        else:
            try:
                item_name = item_names[item_id]
            except IndexError:
                continue
            string += scheme_name
            first_index = string.find("%@")
            second_index = string.find("%@", first_index + 1)
            string = (
                string[:first_index]
                + str(amount)
                + " "
                + item_name
                + string[second_index + 2 :]
            )

        string = string.replace("<br>", "\n\t")
        options.append(string)

    scheme_ids = user_input_handler.select_not_inc(options, "get")
    scheme_data = save_stats["item_schemes"]
    for scheme_index in scheme_ids:
        try:
            scheme_id = data[scheme_index + 1][0]
        except IndexError:
            continue
        obtain_ids: list[int] = scheme_data["to_obtain_ids"]
        obtain_ids.append(scheme_id)
        received_ids: list[int] = scheme_data["received_ids"]
        if scheme_id in received_ids:
            received_ids.remove(scheme_id)
        scheme_data["to_obtain_ids"] = obtain_ids
        scheme_data["received_ids"] = received_ids
    save_stats["item_schemes"] = scheme_data
    return save_stats
