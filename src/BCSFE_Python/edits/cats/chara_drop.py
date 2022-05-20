import helper


def get_data():
    character_data = helper.parse_csv_file(helper.get_files_path("game_data/drops/drop_chara.csv"), black_list=["\n"], min_length=2, parse=True)[1:]

    treasure_ids = helper.copy_first_n(character_data, 0)
    indexes = helper.copy_first_n(character_data, 1)
    cat_ids = helper.copy_first_n(character_data, 2)

    return {"t_ids": treasure_ids, "indexes": indexes, "c_ids": cat_ids}


def set_t_ids(save_stats):
    unit_drops_stats = save_stats["unit_drops"]
    data = get_data()

    usr_t_ids = helper.get_range_input(helper.coloured_text("Enter treasures ids (Look up item drop cats battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), all_ids=data["t_ids"])
    for t_id in usr_t_ids:
        if t_id in data["t_ids"]:
            index = data["t_ids"].index(t_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats


def set_c_ids(save_stats):
    unit_drops_stats = save_stats["unit_drops"]
    data = get_data()

    usr_c_ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), all_ids=data["c_ids"])
    for c_id in usr_c_ids:
        if c_id in data["c_ids"]:
            index = data["c_ids"].index(c_id)
            save_index = data["indexes"][index]
            unit_drops_stats[save_index] = 1

    save_stats["unit_drops"] = unit_drops_stats
    return save_stats


def get_character_drops(save_stats):
    flag_t_ids = helper.valdiate_bool(helper.coloured_text(f"Do you want to select treasure ids &(1)&, or cat ids? &(2)&:", is_input=True), "1")

    if flag_t_ids:
        save_stats = set_t_ids(save_stats)
    else:
        save_stats = set_c_ids(save_stats)
    print("Successfully set unit drops")

    return save_stats
