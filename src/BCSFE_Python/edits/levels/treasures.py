"""Handler for editing main story treasures"""
from typing import Any, Optional

from ... import helper, user_input_handler, item, csv_handler, game_data_getter
from . import story_level_id_selector, main_story


def get_stages(is_jp: bool) -> Optional[list[list[list[int]]]]:
    """Get what stages belong to which treasure group"""

    treasures_values: list[list[list[int]]] = []
    file_data = game_data_getter.get_file_latest(
        "DataLocal", "treasureData0.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Failed to get treasureData0.csv")
        return None
    eoc_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            file_data.decode("utf-8"),
        )
    )[11:22]
    file_data = game_data_getter.get_file_latest(
        "DataLocal", "treasureData1.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Failed to get treasureData1.csv")
        return None
    itf_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            file_data.decode("utf-8"),
        )
    )[11:22]
    file_data = game_data_getter.get_file_latest(
        "DataLocal", "treasureData2_0.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Failed to get treasureData2_0.csv")
        return None
    cotc_treasures = helper.parse_int_list_list(
        csv_handler.parse_csv(
            file_data.decode("utf-8"),
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


def get_names(is_jp: bool) -> Optional[list[list[list[str]]]]:
    """Get the names of all of the treasure groups"""

    names: list[list[list[str]]] = []
    if is_jp:
        country_code = "ja"
    else:
        country_code = "en"

    file_data = game_data_getter.get_file_latest(
        "resLocal", f"Treasure3_0_{country_code}.csv", is_jp
    )
    if file_data is None:
        helper.error_text(f"Failed to get Treasure3_0_{country_code}.csv")
        return None
    eoc_names = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )[:11]

    file_data = game_data_getter.get_file_latest(
        "resLocal", f"Treasure3_1_AfterFirstEncounter_{country_code}.csv", is_jp
    )
    if file_data is None:
        helper.error_text(
            f"Failed to get Treasure3_1_AfterFirstEncounter_{country_code}.csv"
        )
        return None
    itf_names = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )[:11]

    file_data = game_data_getter.get_file_latest(
        "resLocal", f"Treasure3_2_0_{country_code}.csv", is_jp
    )
    if file_data is None:
        helper.error_text(f"Failed to get Treasure3_2_0_{country_code}.csv")
        return None
    cotc_names = csv_handler.parse_csv(
        file_data.decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )[:11]

    names.append(helper.copy_first_n(eoc_names, 0))
    names.append(helper.copy_first_n(itf_names, 0))
    names.append(helper.copy_first_n(cotc_names, 0))

    return names


def get_treasure_groups(is_jp: bool) -> Optional[dict[str, Any]]:
    """Get the names and stages of all of the treasure groups"""

    treasure_stages = get_stages(is_jp)
    treasure_names = get_names(is_jp)
    if treasure_stages is None or treasure_names is None:
        return None
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
    treasure_levels: list[Optional[int]],
    type_id: int,
    chapter_id: int,
) -> list[list[int]]:
    """Set the treasure stats of a group of treasures"""

    for i, treasure_level in enumerate(treasure_levels):
        stages = treasure_grps["stages"][type_id][i]
        for stage in stages:
            if treasure_level is not None:
                treasures_stats[chapter_id][stage] = treasure_level
    return treasures_stats


def treasure_groups(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing treasure groups"""

    treasure_grps = get_treasure_groups(helper.check_data_is_jp(save_stats))
    if treasure_grps is None:
        return save_stats
    treasures_stats = save_stats["treasures"]

    ids = user_input_handler.select_not_inc(main_story.CHAPTERS, "select")

    for chapter_id in ids:
        helper.colored_text(f"Chapter: &{main_story.CHAPTERS[chapter_id]}&")
        type_id = chapter_id // 3
        if chapter_id > 2:
            chapter_id += 1
        names = treasure_grps["names"][type_id]
        treasure_levels = [-1] * len(names)
        helper.colored_text("&0& = None, &1& = Inferior, &2& = Normal, &3& = Superior")
        treasure_levels = item.IntItemGroup.from_lists(
            names=names,
            values=None,
            maxes=None,
            group_name="Treasures",
        )
        treasure_levels.edit()

        treasures_stats = set_treasure_groups(
            treasures_stats,
            treasure_grps,
            treasure_levels.get_values_none(),
            type_id,
            chapter_id,
        )
    save_stats["treasures"] = treasures_stats

    return save_stats


def specific_stages(save_stats: dict[str, Any]):
    """Handler for editing specific stages"""

    treasure_stats = save_stats["treasures"]
    chapter_ids = story_level_id_selector.select_specific_chapters()

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
    save_stats["treasures"] = treasure_stats
    print("Successfully set treasures")
    return save_stats


def specific_stages_all_chapters(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing treasure levels"""

    chapter_ids = story_level_id_selector.select_specific_chapters()

    treasure_stats = save_stats["treasures"]

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
