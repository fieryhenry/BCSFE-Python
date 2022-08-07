"""Handler for editing main story treasures"""
from typing import Any

from ... import helper, user_input_handler, item, csv_handler, game_data_getter
from . import story_level_id_selector, main_story

def get_stages(is_jp: bool) -> list[list[list[int]]]:
    """Get what stages belong to which treasure group"""

    treasures_values: list[list[list[int]]] = []
    eoc_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest("DataLocal", "treasureData0.csv", is_jp).decode("utf-8"),
        )
    )[11:22]
    itf_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest("DataLocal", "treasureData1.csv", is_jp).decode("utf-8"),
        )
    )[11:22]
    cotc_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest("DataLocal", "treasureData2_0.csv", is_jp).decode("utf-8"),
        )
    )[11:22]

    treasures_values.append(remove_negative_1(eoc_treasures))
    treasures_values.append(remove_negative_1(itf_treasures))
    treasures_values.append(remove_negative_1(cotc_treasures))
    return treasures_values


def remove_negative_1(data: list[list[int]]) -> list[list[int]]:
    """Remove items from a list that have a negative value of 1"""

    new_data = data.copy()
    for i, val in enumerate(data):
        if -1 in val:
            new_data[i] = new_data[i][:-1]
    return new_data


def get_names(is_jp: bool) -> list[list[list[str]]]:
    """Get the names of all of the treasure groups"""

    names: list[list[list[str]]] = []
    eoc_names = csv_handler.parse_csv(
        game_data_getter.get_file_latest("resLocal", "Treasure3_0_en.csv", is_jp).decode("utf-8"),
        delimeter="|"
    )[:11]
    itf_names = csv_handler.parse_csv(
        game_data_getter.get_file_latest("resLocal", "Treasure3_1_AfterFirstEncounter_en.csv", is_jp).decode("utf-8"),
        delimeter="|",
    )[:11]
    cotc_names = csv_handler.parse_csv(
        game_data_getter.get_file_latest("resLocal", "Treasure3_2_0_en.csv", is_jp).decode("utf-8"),
        delimeter="|"
    )[:11]

    names.append(helper.copy_first_n(eoc_names, 0))
    names.append(helper.copy_first_n(itf_names, 0))
    names.append(helper.copy_first_n(cotc_names, 0))

    return names


def get_treasure_groups(is_jp: bool) -> dict[str, Any]:
    """Get the names and stages of all of the treasure groups"""

    treasure_stages = get_stages(is_jp)
    treasure_names = get_names(is_jp)
    return {"names": treasure_names, "stages": treasure_stages}


def set_treasures(
    treasure_stats: list[list[int]], user_levels: list[int]
) -> list[list[int]]:
    """Set the treasure stats of a set of levels"""

    for i, level in enumerate(user_levels):
        if level == -1:
            continue
        if i > 2:
            i += 1
        treasure_stats[i] = [level] * 48 + [0]
    return treasure_stats


def set_specific_treasures(
    treasure_stats: list[list[int]], treasure_data: list[int], chapter_id: int
) -> list[list[int]]:
    """Set the treasure stats of specific treasures"""

    for i, stage in enumerate(treasure_data):
        if stage == -1:
            continue
        if i > 45:
            stage_id = i
        else:
            stage_id = 45 - i
        treasure_stats[chapter_id][stage_id] = stage
    return treasure_stats


def set_treasure_groups(
    treasures_stats: list[list[int]],
    treasure_grps: dict[str, Any],
    treasure_levels: list[int],
    type_id: int,
    chapter_id: int,
) -> list[list[int]]:
    """Set the treasure stats of a group of treasures"""
    
    for i, treasure_level in enumerate(treasure_levels):
        if treasure_level is None:
            continue
        stages = treasure_grps["stages"][type_id][i]
        for stage in stages:
            treasures_stats[chapter_id][stage] = treasure_level
    return treasures_stats


def treasure_groups(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing treasure groups"""

    treasure_grps = get_treasure_groups(helper.is_jp(save_stats))
    treasures_stats = save_stats["treasures"]

    helper.colored_list(main_story.CHAPTERS)
    ids = user_input_handler.colored_input(
        "Enter a number from 1 to 9 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")

    ids = helper.check_clamp(ids, 9, 1, -1)

    for chapter_id in ids:
        print(f"Chapter: {main_story.CHAPTERS[chapter_id]}")
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

        treasures_stats = set_treasure_groups(
            treasures_stats, treasure_grps, treasure_levels.values, type_id, chapter_id
        )
    save_stats["treasures"] = treasures_stats

    return save_stats


def specific_treasures(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing treasure levels"""

    individual = (
        user_input_handler.colored_input(
            "Do you want to edit the treasures for individual levels &(1)&, or groups of treasures (e.g energy drink, aqua crystal) &(2)&?:"
        )
        == "1"
    )
    if not individual:
        return treasure_groups(save_stats)

    chapter_ids = story_level_id_selector.select_specific_chapters()

    treasure_stats = save_stats["treasures"]

    if len(chapter_ids) > 1:
        individual_chapter = (
            user_input_handler.colored_input(
                "Do you want to set the treasure level for each stage in each chapter individually, or do you want to select a single treasure level to applly to all chapters at once? (&1&=individual, &2&=all at once):"
            )
            == "1"
        )
    else:
        individual_chapter = False

    if individual_chapter:
        choice = story_level_id_selector.get_option()
        for chapter_id in chapter_ids:
            chapter_id = main_story.format_story_id(chapter_id)
            stage_ids = story_level_id_selector.select_levels(chapter_id, choice)
            treasure_data = [-1] * 48
            treasure_data = user_input_handler.handle_all_at_once(
                stage_ids,
                False,
                treasure_data,
                list(range(1, 49)),
                "treasure level",
                "stage",
                "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)",
            )
            treasure_stats = set_specific_treasures(
                treasure_stats, treasure_data, chapter_id
            )
    else:
        stage_ids = story_level_id_selector.select_levels(None)
        treasure_data = [-1] * 48
        for i, chapter_id in enumerate(chapter_ids):
            chapter_id = main_story.format_story_id(chapter_id)
            if i == 0:
                treasure_data = user_input_handler.handle_all_at_once(
                    stage_ids,
                    True,
                    treasure_data,
                    list(range(0, 48)),
                    "treasure level",
                    "stage",
                    "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)",
                )
            treasure_stats = set_specific_treasures(
                treasure_stats, treasure_data, chapter_id
            )
    save_stats["treasures"] = treasure_stats
    print("Successfully set treasures")
    return save_stats
