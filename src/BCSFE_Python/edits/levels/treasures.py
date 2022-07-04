"""Handler for editing main story treasures"""

from ..levels import main_story
from ... import helper, csv_file_handler, user_input_handler, item


def get_stages() -> list:
    """Get what stages belong to which treasure group"""

    treasures_values = []
    eoc_treasures = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/treasureData0.csv")
    )[11:22]
    itf_treasures = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/treasureData1.csv")
    )[11:22]
    cotc_treasures = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/treasureData2_0.csv")
    )[11:22]

    treasures_values.append(remove_negative_1(eoc_treasures))
    treasures_values.append(remove_negative_1(itf_treasures))
    treasures_values.append(remove_negative_1(cotc_treasures))
    return treasures_values


def get_treasure_groups() -> dict:
    """Get the names and stages of all of the treasure groups"""

    treasure_stages = get_stages()
    treasure_names = get_names()
    return {"names": treasure_names, "stages": treasure_stages}


def get_names() -> list:
    """Get the names of all of the treasure groups"""

    names = []
    eoc_names = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/Treasure3_0_en.csv"), delimiter="|"
    )[:11]
    itf_names = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/Treasure3_1_AfterFirstEncounter_en.csv"),
        delimiter="|",
    )[:11]
    cotc_names = csv_file_handler.parse_csv(
        helper.get_file("game_data/treasures/Treasure3_2_0_en.csv"), delimiter="|"
    )[:11]

    names.append(helper.copy_first_n(eoc_names, 0))
    names.append(helper.copy_first_n(itf_names, 0))
    names.append(helper.copy_first_n(cotc_names, 0))

    return names


def remove_negative_1(data: list) -> list:
    """Remove items from a list that have a negative value of 1"""

    new_data = data.copy()
    for i, val in enumerate(data):
        if -1 in val:
            new_data[i] = new_data[i][:-1]
    return new_data


def treasure_groups(save_stats: dict) -> dict:
    """Handler for editing treasure groups"""

    treasure_grps = get_treasure_groups()
    treasures_stats = save_stats["treasures"]

    helper.colored_list(main_story.chapters)
    ids = user_input_handler.colored_input(
        "Enter a number from 1 to 9 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")

    ids = helper.check_clamp(ids, 9, 1, -1)

    for chapter_id in ids:
        print(f"Chapter: {main_story.chapters[chapter_id]}")
        type_id = chapter_id // 3
        if chapter_id > 2:
            chapter_id += 1
        names = treasure_grps["names"][type_id]
        treasure_levels = [-1] * len(names)
        print("0 = None, 1 = Inferior, 2 = Normal, 3 = Superior")
        treasure_levels = item.create_item_group(
            names=names,
            values=None,
            maxes=None,
            edit_name="treasure level",
            group_name="Treasures",
        )
        treasure_levels.edit()

        for i, treasure_level in enumerate(treasure_levels.values):
            if treasure_level is None:
                continue
            stages = treasure_grps["stages"][type_id][i]
            for stage in stages:
                treasures_stats[chapter_id][stage] = treasure_level
    save_stats["treasures"] = treasures_stats

    return save_stats


def specific_treasures(save_stats: dict) -> dict:
    """Handler for editing treasure levels"""

    individual = (
        user_input_handler.colored_input(
            "Do you want to edit the treasures for individual levels &(1)&, or groups of treasures (e.g energy drink, aqua crystal) &(2)&?:"
        )
        == "1"
    )
    if not individual:
        return treasure_groups(save_stats)
    treasure_stats = save_stats["treasures"]

    helper.colored_list(main_story.chapters)
    ids = user_input_handler.colored_input(
        "Enter a number from 1 to 9 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")

    ids = user_input_handler.create_all_list(ids, 9)
    ids = helper.check_clamp(ids, 9, 1, -1)

    for chapter_id in ids:
        stage_ids = user_input_handler.get_range(
            user_input_handler.colored_input(
                f"Enter stage ids for chapter {main_story.chapters[chapter_id]}(e.g 1=korea, 2=mongolia)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
            ),
            48,
        )
        stage_ids = helper.check_clamp(stage_ids, 48, 1, -1)
        all_at_once = len(stage_ids) == 48
        treasure_data = [-1] * 49
        treasure_data = user_input_handler.handle_all_at_once(
            stage_ids,
            all_at_once,
            treasure_data,
            range(1, 50),
            "treasure level",
            "stage",
            "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)",
        )
        if chapter_id > 2:
            chapter_id += 1
        for i, stage in enumerate(treasure_data):
            if stage == -1:
                continue
            if i > 45:
                stage_id = i
            else:
                stage_id = 45 - i
            treasure_stats[chapter_id][stage_id] = stage

    save_stats["treasures"] = treasure_stats
    print("Successfully set treasures")
    return save_stats


def treasures(save_stats: dict) -> dict:
    """Handler for editing treasure chapters"""

    treasure_stats = save_stats["treasures"]

    helper.colored_list(main_story.chapters)
    ids = user_input_handler.colored_input(
        "10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")

    data = user_input_handler.create_all_list(ids, 10, True)
    ids = data["ids"]
    ids = helper.check_clamp(ids, 10, 1, -1)
    all_at_once = data["at_once"]
    usr_levels = [-1] * 9
    usr_levels = user_input_handler.handle_all_at_once(
        ids,
        all_at_once,
        usr_levels,
        main_story.chapters,
        "treasure level",
        "chapter",
        "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)",
    )
    for i, level in enumerate(usr_levels):
        if level == -1:
            continue
        if i > 2:
            i += 1
        treasure_stats[i] = [level] * 48 + [0]

    save_stats["treasures"] = treasure_stats
    print("Successfully set treasures")
    return save_stats
