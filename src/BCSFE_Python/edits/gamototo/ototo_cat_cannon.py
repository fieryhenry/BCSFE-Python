"""Handler for editing the ototo cat cannon"""
from typing import Any

from ... import user_input_handler, item, game_data_getter, csv_handler, helper


def get_canon_types(is_jp: bool):
    """Get the cannon types"""

    data = csv_handler.parse_csv(
        game_data_getter.get_file_latest(
            "resLocal", "CastleRecipeDescriptions.csv", is_jp
        ).decode("utf-8"),
        delimeter=helper.get_text_splitter(is_jp),
    )
    types: list[str] = []
    for cannon in data:
        types.append(cannon[1])
    return types


def get_cannon_maxes(is_jp: bool) -> list[int]:
    """Get the cannon maxes"""

    data = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest(
                "DataLocal", "CastleRecipeUnlock.csv", is_jp
            ).decode("utf-8")
        )
    )
    maxes: list[int] = []
    for cannon in data:
        cannon_id = cannon[0]
        max_val = cannon[3] - 1
        if cannon_id == len(maxes):
            maxes.append(max_val)
        else:
            if maxes[cannon_id] < max_val:
                maxes[cannon_id] = max_val
    return maxes


def set_level_val(
    cannons: list[dict[str, Any]], levels: list[int]
) -> list[dict[str, Any]]:
    """Set the upgrade level of the cannon"""

    for i, level in enumerate(levels):
        if level > 0:
            cannons[i]["unlock_flag"] = 3
        cannons[i]["level"] = level
    return cannons


def set_stage_val(
    cannons: list[dict[str, Any]], stages: list[int]
) -> list[dict[str, Any]]:
    """Set the stage of the cannon development"""

    for i, stage in enumerate(stages):
        cannons[i + 1]["unlock_flag"] = stage
    return cannons


def get_data(cannons: dict[int, dict[str, int]]) -> tuple[list[int], list[int]]:
    """Get the data of the cannon"""

    levels: list[int] = []
    stages: list[int] = []
    for cannon in cannons.values():
        level = cannon["level"]
        stage = cannon["unlock_flag"]
        levels.append(level)
        stages.append(stage)
    return levels, stages


def set_level(save_stats: dict[str, Any], levels: list[int]) -> dict[str, Any]:
    """Set the upgrade level of the cannon"""

    cannons = save_stats["ototo_cannon"]

    ot_levels = item.create_item_group(
        names=get_canon_types(helper.is_jp(save_stats)),
        values=levels,
        maxes=get_cannon_maxes(helper.is_jp(save_stats)),
        edit_name="level",
        group_name="Cannon Level",
        offset=1,
    )
    ot_levels.edit()

    save_stats["ototo_cannon"] = set_level_val(cannons, ot_levels.values)
    return save_stats


def set_stage(save_stats: dict[str, Any], stages: list[int]) -> dict[str, Any]:
    """Set the stage of the cannon development"""

    cannons = save_stats["ototo_cannon"]

    ot_stages = item.create_item_group(
        names=get_canon_types(helper.is_jp(save_stats))[1:],
        values=stages[1:],
        maxes=3,
        edit_name="stage",
        group_name="Ototo Cat Cannon Stage",
    )
    ot_stages.edit()
    save_stats["ototo_cannon"] = set_stage_val(cannons, ot_stages.values)
    return save_stats


def edit_cat_cannon(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for ototo cat cannon upgrades"""

    cannons = save_stats["ototo_cannon"]
    levels, stages = get_data(cannons)
    stage = (
        user_input_handler.colored_input(
            "Do you want to set the level of the cannon &(1)& or the level of construction &(2)& (e.g foundation, style, cannon):"
        )
        == "2"
    )
    if stage:
        save_stats = set_stage(save_stats, stages)
    else:
        save_stats = set_level(save_stats, levels)
    return save_stats
