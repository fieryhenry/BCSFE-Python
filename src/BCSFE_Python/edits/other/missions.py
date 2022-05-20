import helper

def get_mission_conditions():
    mission_condition_path = helper.get_files_path("game_data/missions/Mission_Condition.csv")
    mission_conditions_list = helper.parse_csv_file(mission_condition_path, min_length=3, black_list=["\n"])
    mission_conditions = {}
    for line in mission_conditions_list[1:]:
        line = helper.ls_int(line)
        id = line[0]
        mission_conditions[id] = {"mission_type" : line[1], "conditions_type" : line[2], "progress_count" : line[3], "conditions_value" : line[4:]}
    return mission_conditions

def get_mission_names():
    mission_name = helper.open_file_s(helper.get_files_path("game_data/missions/Mission_Name.csv"))
    mission_name_list = mission_name.split("\n")
    mission_names = {}
    for mission_name in mission_name_list:
        line_data = mission_name.split("|")
        id = int(line_data[0])
        mission_names[id] = line_data[1]
    return mission_names

def get_mission_names_from_ids(ids, mission_names):
    names = []
    for id in ids:
        if id in mission_names:
            names.append(mission_names[id])
    return names

def edit_missions(save_stats):
    missions = save_stats["missions"]

    names = get_mission_names()
    conditions = get_mission_conditions()

    mission_ids_to_use = []
    for mission_id in missions["flags"]:
        if mission_id in conditions:
            mission_ids_to_use.append(mission_id)

    names_to_use = get_mission_names_from_ids(mission_ids_to_use, names)

    ids = helper.selection_list(names_to_use, "complete", True)
    re_claim = helper.valdiate_bool(helper.coloured_text("Do you want to re-complete already claimed missions &(1)& (Allows you to get the rewards again) or only complete non-claimed missions&(2)&:", is_input=True), "1")
    for id in ids:
        id = helper.validate_int(id)
        if id == None:
            continue
        id = helper.clamp(id, 1, len(mission_ids_to_use))
        id -= 1
        mission_id = mission_ids_to_use[id]
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