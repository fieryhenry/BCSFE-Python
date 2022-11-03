"""Helper for cats"""
from typing import Any, Optional

from ... import csv_handler, game_data_getter, helper
from ..levels import main_story, uncanny

TYPES = [
    "Normal",
    "Special",
    "Rare",
    "Super Rare",
    "Uber Super Rare",
    "Legend Rare",
]


def get_level_cap_increase_amount(cat_base_level: int) -> int:
    """
    Get the amount of levels to increase the level cap by

    Args:
        cat_base_level (int): The base level of the cat (30 = 29)

    Returns:
        int: The amount of levels to increase the level cap by
    """
    return max(0, cat_base_level - 29)


def get_unit_max_levels(is_jp: bool) -> Optional[tuple[list[int], list[int]]]:
    """
    Get the max base and plus levels for all cats

    Args:
        is_jp (bool): If the game is in Japanese

    Returns:
        tuple[list[int], list[int]]: The max base and plus levels for all cats
    """
    file_data = game_data_getter.get_file_latest("DataLocal", "unitbuy.csv", is_jp)
    if file_data is None:
        helper.error_text("Could not get unitbuy.csv")
        return None
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    max_base_level = helper.copy_first_n(data, 50)
    max_plus_level = helper.copy_first_n(data, 51)
    return max_base_level, max_plus_level


def get_unit_max_level(
    data: tuple[list[int], list[int]], cat_id: int
) -> tuple[int, int]:
    """
    Get the max base and plus levels for a cat

    Args:
        data (tuple[list[int], list[int]]): The max base and plus levels for all cats
        cat_id (int): The id of the cat

    Returns:
        tuple[int, int]: The max base and plus levels for a cat
    """
    try:
        return data[0][cat_id], data[1][cat_id]
    except IndexError:
        return 0, 0


def get_rarities(is_jp: bool) -> list[int]:
    """Get all cat ids of each rarity"""

    file_data = game_data_getter.get_file_latest(
        "DataLocal", "unitbuy.csv", is_jp
    )
    if file_data is None:
        helper.error_text("Could not get unitbuy.csv")
        return []
    data = helper.parse_int_list_list(csv_handler.parse_csv(file_data.decode("utf-8")))
    rarity_ids = helper.copy_first_n(data, 13)
    return rarity_ids


def get_rarity(rarity_ids: list[int], is_jp: bool) -> list[int]:
    """Get all cat ids of a certain rarity"""

    rarities = get_rarities(is_jp)
    cat_ids: list[int] = []
    for rarity_id in rarity_ids:
        for i, rarity_val in enumerate(rarities):
            if int(rarity_val) == rarity_id:
                cat_ids.append(i)
    return cat_ids


def is_legend(cat_id: int) -> bool:
    """
    Check if a cat is a legend

    Args:
        cat_id (int): The id of the cat

    Returns:
        bool: If the cat is a legend
    """
    legends = [
        24,
        25,
        130,
        172,
        268,
        323,
        352,
        383,
        426,
        437,
        462,
        464,
        532,
        554,
        568,
        613,
        622,
        653,
    ]
    if cat_id in legends:
        return True
    return False


def is_crazed(cat_id: int) -> bool:
    """
    Check if a cat is crazed

    Args:
        cat_id (int): The id of the cat

    Returns:
        bool: If the cat is crazed
    """
    crazed = [
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
    ]
    if cat_id in crazed:
        return True
    return False


def get_max_cat_level_normal(save_stats: dict[str, Any]) -> int:
    """
    Get the max level a normal cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        int: The max level of a normal cat
    """
    if main_story.has_cleared_chapter(save_stats, 1):
        return 20
    return 10


def catseyes_unlocked(save_stats: dict[str, Any]) -> bool:
    """
    Check if catseyes are unlocked

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        bool: If catseyes are unlocked
    """
    return helper.calculate_user_rank(save_stats) >= 1600


def get_max_cat_level_special(save_stats: dict[str, Any], cat_id: int) -> int:
    """
    Get the max level a special cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats
        cat_id (int): The id of the cat

    Returns:
        int: The max level of a special cat
    """
    legend = is_legend(cat_id)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    user_rank = helper.calculate_user_rank(save_stats)
    catseyes = catseyes_unlocked(save_stats)
    eoc_cleared_2 = main_story.has_cleared_chapter(save_stats, 1)

    if not eoc_cleared_2:
        return 10
    if user_rank < 1600:
        return 20
    if not catseyes:
        return 30
    if not acient_curse_clear and not legend:
        return 40
    if not acient_curse_clear and legend:
        return 30
    if acient_curse_clear and legend:
        return 40
    return 50


def get_max_cat_level_rare(save_stats: dict[str, Any]) -> int:
    """
    Get the max level a cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        int: The max level of a cat
    """
    user_rank = helper.calculate_user_rank(save_stats)
    catseyes = catseyes_unlocked(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 900:
        return 20
    if user_rank < 1200:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_super_rare(save_stats: dict[str, Any], cat_id: int) -> int:
    """
    Get the max level a super rare cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats
        cat_id (int): The id of the cat

    Returns:
        int: The max level of a super rare cat
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    crazed = is_crazed(cat_id)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if crazed and user_rank < 3600:
        return 20
    if not crazed and user_rank < 1000:
        return 20
    if crazed and user_rank < 3650:
        return 25
    if not crazed and user_rank < 1300:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_uber_rare(save_stats: dict[str, Any]) -> int:
    """
    Get the max level a uber rare cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        int: The max level of a uber rare cat
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 1100:
        return 20
    if user_rank < 1400:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level_legend_rare(save_stats: dict[str, Any]) -> int:
    """
    Get the max level a legend rare cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        int: The max level of a legend rare cat
    """
    user_rank = helper.calculate_user_rank(save_stats)
    cleared_eoc_2 = main_story.has_cleared_chapter(save_stats, 1)
    acient_curse_clear = uncanny.is_ancient_curse_clear(save_stats)
    catseyes = catseyes_unlocked(save_stats)

    if not cleared_eoc_2:
        return 10
    if user_rank < 1110:
        return 20
    if user_rank < 1410:
        return 25
    if not catseyes:
        return 30
    if not acient_curse_clear:
        return 40
    return 50


def get_max_level(save_stats: dict[str, Any], rarity_index: int, cat_id: int) -> int:
    """
    Get the max level a cat can be upgraded to

    Args:
        save_stats (dict[str, Any]): The save stats
        rarity_index (int): The rarity index of the cat
        cat_id (int): The id of the cat

    Returns:
        int: The max level of a cat
    """
    if rarity_index == 0:
        return get_max_cat_level_normal(save_stats)
    if rarity_index == 1:
        return get_max_cat_level_special(save_stats, cat_id)
    if rarity_index == 2:
        return get_max_cat_level_rare(save_stats)
    if rarity_index == 3:
        return get_max_level_super_rare(save_stats, cat_id)
    if rarity_index == 4:
        return get_max_level_uber_rare(save_stats)
    if rarity_index == 5:
        return get_max_level_legend_rare(save_stats)
    return 0
