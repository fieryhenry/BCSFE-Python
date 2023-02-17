"""Handler for editing catnip missions"""
from typing import Any, Optional

from ... import user_input_handler, game_data_getter, csv_handler, helper


def get_mission_conditions(is_jp: bool) -> Optional[dict[Any, Any]]:
    """Get the mission data and what you need to do to complete it"""

    file_data = game_data_getter.get_file_latest(
        "DataLocal", "Mission_Condition.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Failed to get mission conditions")
        return None
    mission_condition_data = file_data.decode("utf-8")
    mission_conditions_list = helper.parse_int_list_list(
        csv_handler.parse_csv(mission_condition_data)
    )
    mission_conditions: dict[Any, Any] = {}
    for line in mission_conditions_list[1:]:
        mission_id = line[0]
        mission_conditions[mission_id] = {
            "mission_type": line[1],
            "conditions_type": line[2],
            "progress_count": line[3],
            "conditions_value": line[4:],
        }
    return mission_conditions


def get_mission_names(is_jp: bool) -> Optional[dict[int, Any]]:
    """Get all mission names"""

    file_data = game_data_getter.get_file_latest("resLocal", "Mission_Name.csv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get mission names")
        return None
    mission_name = file_data.decode("utf-8")
    mission_name_list = mission_name.split("\n")
    mission_names: dict[int, Any] = {}
    for mission_name in mission_name_list:
        line_data = mission_name.split(helper.get_text_splitter(is_jp))
        if helper.check_int(line_data[0]) is None:
            continue
        mission_id = int(line_data[0])
        name = line_data[1]
        name = name.replace("&", "\\&")
        mission_names[mission_id] = name
    return mission_names


def get_mission_names_from_ids(
    ids: list[int], mission_names: dict[int, Any]
) -> list[str]:
    """Get the mission names from the ids"""

    names: list[str] = []
    for mission_id in ids:
        if mission_id in mission_names:
            names.append(mission_names[mission_id])
    return names


def get_mission_ids(
    missions: dict[str, Any], conditions: dict[int, Any], names: dict[int, Any]
) -> tuple[list[int], list[str]]:
    """Get the mission ids and names from the conditions"""

    mission_ids_to_use: list[int] = []
    for mission_id in missions["states"]:
        if mission_id in conditions:
            mission_ids_to_use.append(mission_id)

    names_to_use = get_mission_names_from_ids(mission_ids_to_use, names)
    return mission_ids_to_use, names_to_use


def set_missions(
    missions: dict[str, Any],
    ids: list[int],
    conditions: dict[Any, Any],
    mission_ids_to_use: list[int],
    re_claim: bool,
) -> dict[str, Any]:
    """Set the missions"""

    for mission_id in ids:
        mission_id = helper.clamp(mission_id, 1, len(mission_ids_to_use))
        mission_id = mission_ids_to_use[mission_id]
        if re_claim:
            claim = True
        elif not re_claim and missions["states"][mission_id] != 4:
            claim = True
        else:
            claim = False
        if claim:
            missions["states"][mission_id] = 2
            missions["requirements"][mission_id] = conditions[mission_id][
                "progress_count"
            ]
    return missions


def edit_missions(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting catnip missions"""

    missions = save_stats["missions"]

    names = get_mission_names(helper.check_data_is_jp(save_stats))
    conditions = get_mission_conditions(helper.check_data_is_jp(save_stats))

    if names is None or conditions is None:
        return save_stats

    mission_ids_to_use, names_to_use = get_mission_ids(missions, conditions, names)

    ids = user_input_handler.select_not_inc(
        options=names_to_use,
        mode="complete",
    )
    re_claim = (
        user_input_handler.colored_input(
            "Do you want to re-complete already claimed missions &(1)& (Allows you to get the rewards again) or only complete non-claimed missions&(2)&:"
        )
        == "1"
    )
    missions = set_missions(missions, ids, conditions, mission_ids_to_use, re_claim)
    save_stats["missions"] = missions
    print("Successfully completed missions")
    return save_stats
