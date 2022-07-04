"""Handler for editing character drops"""

from ... import helper, csv_file_handler, user_input_handler

def get_data() -> dict:
    """gets all of the cat ids and treasure ids that can be dropped"""

    character_data = csv_file_handler.parse_csv(helper.get_file("game_data/drops/drop_chara.csv"))[1:]

    treasure_ids = helper.copy_first_n(character_data, 0)
    indexes = helper.copy_first_n(character_data, 1)
    cat_ids = helper.copy_first_n(character_data, 2)

    return {"t_ids": treasure_ids, "indexes": indexes, "c_ids": cat_ids}


def set_t_ids(save_stats: dict) -> dict:
    """handler for editing treasure ids"""

    unit_drops_stats = save_stats["unit_drops"]
    data = get_data()

    usr_t_ids = user_input_handler.get_range(user_input_handler.colored_input("Enter treasures ids (Look up item drop cats battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"), all_ids=data["t_ids"])

    for t_id in usr_t_ids:
        if t_id in data["t_ids"]:
            index = data["t_ids"].index(t_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats

def set_c_ids(save_stats: dict) -> dict:
    """handler for editing cat ids"""

    unit_drops_stats = save_stats["unit_drops"]
    data = get_data()

    usr_c_ids = user_input_handler.get_range(user_input_handler.colored_input("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"), all_ids=data["c_ids"])
    usr_c_ids = helper.check_cat_ids(usr_c_ids, save_stats)
    for c_id in usr_c_ids:
        if c_id in data["c_ids"]:
            index = data["c_ids"].index(c_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats

def get_character_drops(save_stats: dict) -> dict:
    """handler for getting character drops"""

    flag_t_ids = user_input_handler.colored_input("Do you want to select treasure ids &(1)&, or cat ids? &(2)&:") == "1"

    if flag_t_ids:
        save_stats = set_t_ids(save_stats)
    else:
        save_stats = set_c_ids(save_stats)
    print("Successfully set unit drops")

    return save_stats
