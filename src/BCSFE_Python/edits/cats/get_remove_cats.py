"""Handler to add and remove cats"""
from typing import Any

from ... import helper
from . import cat_id_selector


def get_cat(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler to get cats"""

    cat_ids = cat_id_selector.select_cats(save_stats, False)

    save_stats = get_cat_ids(
        save_stats=save_stats,
        val=1,
        string="gave",
        ids=cat_ids,
    )
    return save_stats


def remove_cats(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler to remove cats"""

    cat_ids = cat_id_selector.select_cats(save_stats, False)

    save_stats = get_cat_ids(
        save_stats=save_stats,
        val=0,
        string="removed",
        ids=cat_ids,
    )
    return save_stats


def get_cat_ids(
    save_stats: dict[str, Any], val: int, string: str, ids: list[int]
) -> dict[str, Any]:
    """Get specific cats by ids"""

    ids = helper.check_cat_ids(ids, save_stats)

    cats = save_stats["cats"]
    seen_cats = save_stats["gatya_seen_cats"]

    for cat_id in ids:
        cats[cat_id] = val
        seen_cats[cat_id] = val

    save_stats["cats"] = cats
    save_stats["gatya_seen_cats"] = seen_cats
    save_stats["menu_unlocks"][2] = 1
    print(f"Successfully {string} cats")
    return save_stats
