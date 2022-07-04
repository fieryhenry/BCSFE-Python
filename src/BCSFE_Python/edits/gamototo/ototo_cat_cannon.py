"""Handler for editing the ototo cat cannon"""

from ... import user_input_handler, item

types = [
    "Base",
    "Slow Beam",
    "Iron Wall",
    "Thunderbolt",
    "Waterblast",
    "Holy Blast",
    "Breakerblast",
    "Curseblast",
]


def set_level(save_stats: dict, levels: list) -> dict:
    """Set the upgrade level of the cannon"""

    cannons = save_stats["ototo_cannon"]

    ot_levels = item.create_item_group(
        names=types,
        values=levels,
        maxes=[19, 29, 29, 29, 29, 29, 29, 29],
        edit_name="level",
        group_name="Cannon Level",
        offset=1,
    )
    ot_levels.edit()

    for i, level in enumerate(ot_levels.values):
        if level > 0:
            cannons[i]["unlock_flag"] = 3
        cannons[i]["level"] = level
    save_stats["ototo_cannon"] = cannons
    return save_stats


def set_stage(save_stats: dict, stages: list) -> dict:
    """Set the stage of the cannon development"""

    cannons = save_stats["ototo_cannon"]

    ot_stages = item.create_item_group(
        names=types[1:],
        values=stages[1:],
        maxes=3,
        edit_name="stage",
        group_name="Ototo Cat Cannon Stage",
    )
    ot_stages.edit()
    for i in range(len(cannons) - 1):
        cannons[i + 1]["unlock_flag"] = ot_stages.values[i]

    save_stats["ototo_cannon"] = cannons
    return save_stats


def edit_cat_cannon(save_stats: dict) -> dict:
    """Handler for ototo cat cannon upgrades"""

    cannons = save_stats["ototo_cannon"]
    levels = []
    stages = []
    for cannon in cannons:
        level = cannons[cannon]["level"]
        stage = cannons[cannon]["unlock_flag"]
        levels.append(level)
        stages.append(stage)
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
