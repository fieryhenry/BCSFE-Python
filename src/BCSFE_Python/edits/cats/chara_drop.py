"""Handler for editing character drops"""

from typing import Any

from ... import helper, user_input_handler, csv_handler, game_data_getter
from . import cat_id_selector


def set_t_ids(save_stats: dict[str, Any]) -> dict[str, Any]:
    """handler for editing treasure ids"""

    unit_drops_stats = save_stats["unit_drops"]
    data = get_data(helper.check_data_is_jp(save_stats))

    usr_t_ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter treasures ids (Look up item drop cats battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        all_ids=data["t_ids"],
    )

    unit_drops_stats = set_t_ids_val(unit_drops_stats, data, usr_t_ids)

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats


def set_c_ids(save_stats: dict[str, Any]) -> dict[str, Any]:
    """handler for editing cat ids"""

    unit_drops_stats = save_stats["unit_drops"]
    data = get_data(helper.check_data_is_jp(save_stats))

    ids = cat_id_selector.select_cats(save_stats)

    usr_c_ids = helper.check_cat_ids(ids, save_stats)
    unit_drops_stats = set_c_ids_val(unit_drops_stats, data, usr_c_ids)

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats


def get_character_drops(save_stats: dict[str, Any]) -> dict[str, Any]:
    """handler for getting character drops"""

    flag_t_ids = (
        user_input_handler.colored_input(
            "Do you want to select treasure ids &(1)&, or cat ids? &(2)&:"
        )
        == "1"
    )

    if flag_t_ids:
        save_stats = set_t_ids(save_stats)
    else:
        save_stats = set_c_ids(save_stats)
    print("Successfully set unit drops")

    return save_stats


def get_data(is_jp: bool) -> dict[str, Any]:
    """gets all of the cat ids and treasure ids that can be dropped"""

    file_data = game_data_getter.get_file_latest("DataLocal", "drop_chara.csv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get drop_chara.csv")
        return {"t_ids": [], "c_ids": [], "indexes": []}
    character_data = helper.parse_int_list_list(
        csv_handler.parse_csv(file_data.decode("utf-8"))[1:]
    )

    treasure_ids = helper.copy_first_n(character_data, 0)
    indexes = helper.copy_first_n(character_data, 1)
    cat_ids = helper.copy_first_n(character_data, 2)

    return {"t_ids": treasure_ids, "indexes": indexes, "c_ids": cat_ids}


def set_t_ids_val(
    unit_drops_stats: list[int], data: dict[str, Any], user_t_ids: list[int]
) -> list[int]:
    """sets the treasure ids of the unit drops"""

    for t_id in user_t_ids:
        if t_id in data["t_ids"]:
            index = data["t_ids"].index(t_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1
    return unit_drops_stats


def set_c_ids_val(
    unit_drops_stats: list[int], data: dict[str, Any], user_t_ids: list[int]
) -> list[int]:
    """sets the cat ids of the unit drops"""

    for c_id in user_t_ids:
        if c_id in data["c_ids"]:
            index = data["c_ids"].index(c_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1
    return unit_drops_stats
