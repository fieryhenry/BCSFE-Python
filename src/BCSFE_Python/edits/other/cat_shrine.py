"""Handler for editing cata shrine xp and level"""
from typing import Any, Optional

from ... import game_data_getter, helper, item, user_input_handler


def get_boundaries(is_jp: bool) -> Optional[list[int]]:
    """
    Returns the xp requirements for each level

    Args:
        is_jp (bool): If the save file is japanese

    Returns:
        list[int]: The xp requirements for each level
    """
    file_data = game_data_getter.get_file_latest("resLocal", "jinja_level.csv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get jinja level data")
        return None
    boundaries = file_data.decode("utf-8").splitlines()
    xp_requirements: list[int] = []
    counter = 0
    for line in boundaries:
        requirement = int(line.split(helper.get_text_splitter(is_jp))[0])
        counter += requirement
        xp_requirements.append(counter)
    return xp_requirements


def get_level_from_xp(shrine_xp: int, is_jp: bool) -> Optional[dict[str, Any]]:
    """
    Returns the level, max level and max xp from the given xp

    Args:
        shrine_xp (int): The xp of the shrine
        is_jp (bool): If the save file is japanese

    Returns:
        dict[str, Any]: The level, max level, and max xp
    """
    xp_requirements = get_boundaries(is_jp)
    if xp_requirements is None:
        return None
    level = 1
    for requirement in xp_requirements:
        if shrine_xp >= requirement:
            level += 1
    if level > len(xp_requirements):
        level = len(xp_requirements)
    return {
        "level": level,
        "max_level": len(xp_requirements),
        "max_xp": xp_requirements[-2],
    }


def get_xp_from_level(level: int, is_jp: bool) -> Optional[int]:
    """
    Returns the xp required to reach the given level

    Returns:
        _type_: int
    """
    xp_requirements = get_boundaries(is_jp)
    if xp_requirements is None:
        return None
    if level <= 1:
        shrine_xp = 0
    else:
        shrine_xp = xp_requirements[level - 2]
    return shrine_xp


def edit_shrine_xp(save_stats: dict[str, Any]) -> dict[str, Any]:
    """
    Edit the shrine xp of the save file

    Args:
        save_stats (dict[str, Any]): The save file stats

    Returns:
        dict[str, Any]: The edited save file stats
    """

    shrine_xp = save_stats["cat_shrine"]["xp_offering"]

    data = get_level_from_xp(shrine_xp, helper.check_data_is_jp(save_stats))
    if data is None:
        return save_stats
    level = data["level"]

    helper.colored_text(f"Shrine XP: &{shrine_xp}&\nLevel: &{level}&")
    raw = (
        user_input_handler.colored_input(
            "Do you want to edit raw xp(&1&) or the level(&2&)?:"
        )
        == "1"
    )

    if raw:
        cat_shrine_xp = item.IntItem(
            name="Shrine XP",
            value=item.Int(shrine_xp),
            max_value=None,
        )
        cat_shrine_xp.edit()
        shrine_xp = int(cat_shrine_xp.get_value())
    else:
        shrine_level = item.IntItem(
            name="Shrine Level",
            value=item.Int(level),
            max_value=data["max_level"],
        )
        shrine_level.edit()
        shrine_xp = get_xp_from_level(
            int(shrine_level.get_value()), helper.check_data_is_jp(save_stats)
        )
    if shrine_xp is None:
        return save_stats
    shrine_data = get_level_from_xp(shrine_xp, helper.check_data_is_jp(save_stats))
    if shrine_data is None:
        return save_stats
    shrine_level = shrine_data["level"]
    if shrine_level > data["max_level"]:
        shrine_level = data["max_level"]
    save_stats["shrine_dialogs"]["Value"] = shrine_level - 1  # Level up dialog
    save_stats["shrine_gone"] = 0
    save_stats["cat_shrine"]["stamp_1"] = 0
    save_stats["cat_shrine"]["stamp_2"] = 0

    save_stats["cat_shrine"]["xp_offering"] = shrine_xp
    return save_stats
