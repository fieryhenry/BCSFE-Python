"""Handler for editing catnip missions"""
from ... import helper, user_input_handler, csv_file_handler


def get_mission_conditions() -> dict:
    """Get the mission data and what you need to do to complete it"""

    mission_condition_path = helper.get_file("game_data/missions/Mission_Condition.csv")
    mission_conditions_list = csv_file_handler.parse_csv(mission_condition_path)
    mission_conditions = {}
    for line in mission_conditions_list[1:]:
        mission_id = line[0]
        mission_conditions[mission_id] = {
            "mission_type": line[1],
            "conditions_type": line[2],
            "progress_count": line[3],
            "conditions_value": line[4:],
        }
    return mission_conditions


def get_mission_names() -> dict:
    """Get all mission names"""

    mission_name = helper.read_file_string(
        helper.get_file("game_data/missions/Mission_Name.csv")
    )
    mission_name_list = mission_name.split("\n")
    mission_names = {}
    for mission_name in mission_name_list:
        line_data = mission_name.split("|")
        mission_id = int(line_data[0])
        mission_names[mission_id] = line_data[1]
    return mission_names


def get_mission_names_from_ids(ids: list, mission_names: dict) -> list:
    """Get the mission names from the ids"""

    names = []
    for mission_id in ids:
        if mission_id in mission_names:
            names.append(mission_names[mission_id])
    return names


def edit_missions(save_stats: dict) -> dict:
    """Handler for editting catnip missions"""

    missions = save_stats["missions"]

    names = get_mission_names()
    conditions = get_mission_conditions()

    mission_ids_to_use = []
    for mission_id in missions["flags"]:
        if mission_id in conditions:
            mission_ids_to_use.append(mission_id)

    names_to_use = get_mission_names_from_ids(mission_ids_to_use, names)

    ids = user_input_handler.select_options(
        options=names_to_use,
        mode="complete",
    )
    re_claim = (
        user_input_handler.colored_input(
            "Do you want to re-complete already claimed missions &(1)& (Allows you to get the rewards again) or only complete non-claimed missions&(2)&:"
        )
        == "1"
    )
    for mission_id in ids:
        mission_id = helper.clamp(mission_id, 1, len(mission_ids_to_use))
        mission_id -= 1
        mission_id = mission_ids_to_use[mission_id]
        if re_claim:
            claim = True
        elif not re_claim and missions["flags"][mission_id] != 4:
            claim = True
        else:
            claim = False
        if claim:
            missions["flags"][mission_id] = 2
            missions["values"][mission_id] = conditions[mission_id]["progress_count"]

    save_stats["missions"] = missions
    print("Successfully completed missions")
    return save_stats
