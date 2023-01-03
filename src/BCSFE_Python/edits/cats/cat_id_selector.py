"""Handler for selecting cat ids"""

import os
from multiprocessing import Process
from typing import Any, Callable, Optional


from ... import (
    csv_handler,
    game_data_getter,
    helper,
    user_input_handler,
)
from ..levels import treasures
from . import cat_helper


def select_cats(save_stats: dict[str, Any], current: bool = True) -> list[int]:
    """Select cats"""

    options: dict[str, Callable[[dict[str, Any]], list[int]]] = {
        "Select currently unlocked cats": select_current_cats,
        "Select cats of a certain rarity": select_cats_rarity,
        "Select specific cat ids": select_cats_range,
        "Select cats of a specific gacha banner": select_cats_gatya_banner,
        "Select all cats": get_all_cats,
        "Search by cat name": select_cat_names,
        "Select all obtainable cats": select_cats_obtainable,
    }
    if not current:
        del options["Select currently unlocked cats"]

    choice_index = (
        user_input_handler.select_single(list(options.keys()), title="Select cats:") - 1
    )
    cat_ids = options[list(options)[choice_index]](save_stats)
    return cat_ids


def select_cats_obtainable(save_stats: dict[str, Any]) -> list[int]:
    """
    Select cats that can be obtained

    Args:
        save_stats (dict[str, Any]): Save stats

    Returns:
        list[int]: Cat ids
    """
    return filter_obtainable_cats(save_stats, get_all_cats(save_stats))


def select_current_cats(save_stats: dict[str, Any]) -> list[int]:
    """Select current cats"""

    cats = save_stats["cats"]
    cat_ids: list[int] = []
    for i, cat_val in enumerate(cats):
        if cat_val == 1:
            cat_ids.append(i)
    return cat_ids


def select_cats_rarity(save_stats: dict[str, Any]) -> list[int]:
    """Select cats of a certain rarity"""

    ids = user_input_handler.select_not_inc(
        options=cat_helper.TYPES,
        mode="select",
    )
    is_jp = helper.is_jp(save_stats)

    cat_ids = cat_helper.get_rarity(ids, is_jp)
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


def select_cats_gatya_banner(save_stats: dict[str, Any]) -> list[int]:
    """Select cats for a specific gacha banner"""
    is_jp = helper.is_jp(save_stats)
    file_data = game_data_getter.get_file_latest(
        "DataLocal", "GatyaDataSetR1.csv", is_jp
    )
    if file_data is None:
        helper.colored_text("Failed to get gatya banners")
        return []
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter gacha banner id (Look up the gacha banners you want, then click on the image at the top, and look for the last digits of the file name (e.g royal fest = 602))(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
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


def select_cat_names(save_stats: dict[str, Any]) -> list[int]:
    """
    select_cat_names

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        list[int]: cat ids
    """
    all_names = get_cat_names(save_stats)
    if all_names is None:
        return []
    name = user_input_handler.colored_input("Enter cat name:")
    found_names = search_cat_names(name, all_names)
    found_names = filter_cat_names(found_names)
    if not found_names:
        print("No cats with that name found")
        return []

    cat_ids: list[int] = []
    cat_ids_str: list[str] = []
    cat_names: list[str] = []
    for cat_name, cat_id, _ in found_names:
        cat_ids.append(cat_id)
        cat_name = cat_name.replace("&", "\\&")
        cat_names.append(cat_name)
        cat_ids_str.append(f"Cat id: &{cat_id}&")

    print("Select indexes of cats to select (Not the cat id itself):")
    indexes = user_input_handler.select_not_inc(
        cat_names, mode="select", extra_data=cat_ids_str
    )
    selected_ids: list[int] = []
    for index in indexes:
        try:
            selected_ids.append(cat_ids[index])
        except IndexError:
            helper.colored_text(
                f"Option is too high: {index} - Make sure to select the index on the left rather than the cat id",
                helper.RED,
            )
    return selected_ids


def get_cat_by_form_and_id(
    all_names: list[tuple[str, int, int]], cat_id: int, form_id: int
) -> Optional[tuple[str, int, int]]:
    """
    Get cat by form and id

    Args:
        all_names (list[tuple[str, int, int]]): all names
        cat_id (int): cat id
        form_id (int): form id

    Returns:
        Optional[tuple[str, int, int]]: cat data
    """
    for cat in all_names:
        if cat[1] == cat_id and cat[2] == form_id:
            return cat
    return None


def get_cat_by_id(
    cat_names: list[tuple[str, int, int]], cat_id_to_search: int
) -> list[tuple[str, int, int]]:
    """
    Get cat by id

    Args:
        cat_names (list[tuple[str, int, int]]): list of cat names
        cat_id_to_search (int): cat id to search for

    Returns:
        Optional[tuple[str, int, int]]: cat name, cat id, cat form
    """
    cats: list[tuple[str, int, int]] = []
    for cat_name, cat_id, cat_form in cat_names:
        if cat_id == cat_id_to_search:
            cats.append((cat_name, cat_id, cat_form))
    return cats


def filter_cat_names(
    cat_names: list[tuple[str, int, int]]
) -> list[tuple[str, int, int]]:
    """
    Filter cat names by only selecting one of the forms

    Args:
        cat_names (list[tuple[str, int, int]]): list of cat names

    Returns:
        list[tuple[str, int, int]]: filtered cat names
    """
    filtered_cat_ids: list[int] = []
    cat_data: list[tuple[str, int, int]] = []
    for cat_name, cat_id, cat_form in cat_names:
        if cat_id not in filtered_cat_ids:
            filtered_cat_ids.append(cat_id)
            cat_data.append((cat_name, cat_id, cat_form))

    return cat_data


def search_cat_names(
    name: str, cat_names: list[tuple[str, int, int]]
) -> list[tuple[str, int, int]]:
    """
    Search cat names

    Args:
        name (str): name to search for
        cat_names (list[tuple[str, int, int]]): list of cat names

    Returns:
        list[tuple[str, int, int]]: list of cat names that match the search
    """

    found_names: list[tuple[str, int, int]] = []

    for cat_name, cat_id, form_id in cat_names:
        if name.lower().replace(" ", "") in cat_name.lower().replace(" ", ""):
            found_names.append((cat_name, cat_id, form_id))
    return found_names


def download_10_files(game_version: str, file_names: list[str]) -> None:
    """
    Download 10 files

    Args:
        game_version (str): game version
        file_names (list[str]): file names
    """
    for file_name in file_names:
        game_data_getter.download_file(game_version, "resLocal", file_name, False)


def get_cat_names(save_stats: dict[str, Any]) -> Optional[list[tuple[str, int, int]]]:
    """
    Get cat names and ids

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        Optional[list[tuple[str, int, int]]]: cat names and ids
    """

    is_jp = helper.is_jp(save_stats)

    path = game_data_getter.get_path("resLocal", "", is_jp)
    if path is None:
        helper.colored_text("Failed to get cat names", helper.RED)
        return None
    file_path_dir = os.path.dirname(helper.get_file(path))
    helper.create_dirs(file_path_dir)
    if len(helper.find_files_in_dir(file_path_dir, "Unit_Explanation")) < len(
        save_stats["cats"]
    ):
        helper.colored_text(
            "Downloading cat names for the first time... (This may take some time, but next time it will be much faster)",
            helper.GREEN,
        )
        funcs: list[Process] = []
        version = game_data_getter.get_latest_version(is_jp)
        if version is None:
            helper.colored_text("Failed to get cat names", helper.RED)
            return None
        all_file_names: list[str] = []
        for cat_id, _ in enumerate(save_stats["cats"]):
            file_name = f"Unit_Explanation{cat_id+1}_{helper.get_lang(is_jp)}.csv"
            all_file_names.append(file_name)
        file_names_split = helper.chunks(all_file_names, 10)
        for file_names in file_names_split:
            funcs.append(
                Process(
                    target=download_10_files,
                    args=(version, file_names),
                )
            )
        helper.run_in_parallel(funcs)

    names: list[tuple[str, int, int]] = []
    for cat_id, _ in enumerate(save_stats["cats"]):
        file_path = os.path.join(
            file_path_dir, f"Unit_Explanation{cat_id+1}_{helper.get_lang(is_jp)}.csv"
        )
        data = csv_handler.parse_csv(
            helper.read_file_string(file_path),
            delimeter=helper.get_text_splitter(is_jp),
        )
        for form_id, form in enumerate(data):
            name = form[0]
            names.append((name, cat_id, form_id))
    return names


def get_obtainability(save_stats: dict[str, Any]) -> list[int]:
    """
    Get obtainability of cats

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        list[int]: obtainability of cats (0 = not obtainable, 1 = obtainable)
    """
    file_data = game_data_getter.get_file_latest(
        "DataLocal", "nyankoPictureBookData.csv", helper.is_jp(save_stats)
    )
    if file_data is None:
        helper.colored_text("Failed to get obtainability", helper.RED)
        return []
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    is_obtainable = helper.copy_first_n(data, 0)
    return is_obtainable


def get_obtainable_cats(save_stats: dict[str, Any]) -> list[int]:
    """
    Get obtainable cats

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        list[int]: obtainable cats
    """
    obtainability = get_obtainability(save_stats)
    return [i for i, x in enumerate(obtainability) if x == 1]


def filter_obtainable_cats(save_stats: dict[str, Any], cat_ids: list[int]) -> list[int]:
    """
    Filter obtainable cats in a list of cat ids

    Args:
        save_stats (dict[str, Any]): save stats
        cat_ids (list[int]): cat ids

    Returns:
        list[int]: obtainable cats
    """
    obtainable_cats = get_obtainable_cats(save_stats)
    return [i for i in cat_ids if i in obtainable_cats]
