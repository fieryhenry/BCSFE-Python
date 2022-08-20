"""Handler for selecting cat ids"""

from multiprocessing import Process
import os
from typing import Any, Optional

from ... import user_input_handler, helper, game_data_getter, csv_handler
from . import upgrade_cats
from ..levels import treasures


def select_cats_not_current(save_stats: dict[str, Any]) -> list[int]:
    """Select cats not currently unlocked"""

    options = [
        "Select cats of a certain rarity",
        "Select specific cat ids",
        "Select cats of a specific gacha banner",
        "Select all cats",
        "Search by cat name",
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
    if choice == 5:
        return select_cat_names(save_stats)
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
        "Select all cats",
        "Search by cat name",
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
    if choice == 6:
        return select_cat_names(save_stats)
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


def select_cat_names(save_stats: dict[str, Any]) -> list[int]:
    """
    select_cat_names

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        list[int]: cat ids
    """
    all_names = get_cat_names(save_stats)
    name = user_input_handler.colored_input("Enter cat name:")
    found_names = search_cat_names(name, all_names)
    found_names = filter_cat_names(found_names)
    if not found_names:
        print("No cats with that name found")
        return []

    cat_ids: list[int] = []
    cat_names: list[str] = []
    for cat_name, cat_id, _ in found_names:
        cat_ids.append(cat_id)
        cat_name = cat_name.replace("&", "\\&")
        cat_names.append(cat_name)

    indexes = user_input_handler.select_not_inc(
        cat_names, mode="select", extra_data=cat_ids
    )
    cat_ids = [cat_ids[i] for i in indexes]
    return cat_ids

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

def get_cat_names(save_stats: dict[str, Any]) -> list[tuple[str, int, int]]:
    """
    Get cat names and ids

    Args:
        save_stats (dict[str, Any]): save stats

    Returns:
        list[tuple[str, int, int]]: cat names and ids
    """

    is_jp = helper.is_jp(save_stats)

    file_path_dir = os.path.dirname(
        helper.get_file(game_data_getter.get_path("resLocal", "", is_jp))
    )
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
        all_file_names: list[str] = []
        for cat_id, _ in enumerate(save_stats["cats"]):
            file_name = f"Unit_Explanation{cat_id+1}_{helper.get_cc(save_stats)}.csv"
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
            file_path_dir, f"Unit_Explanation{cat_id+1}_{helper.get_cc(save_stats)}.csv"
        )
        data = csv_handler.parse_csv(
            helper.read_file_string(file_path),
            delimeter=helper.get_text_splitter(is_jp),
        )
        for form_id, form in enumerate(data):
            name = form[0]
            names.append((name, cat_id, form_id))
    return names
