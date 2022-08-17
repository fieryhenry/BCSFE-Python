"""Handler for clearing the cat guide"""

from typing import Any

from ... import helper
from . import cat_id_selector


def collect_cat_guide(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Collect cat guide for cats"""

    ids = cat_id_selector.select_cats(save_stats)

    save_stats = cat_guide_ids(save_stats, ids, 1, "collected")
    return save_stats


def remove_cat_guide(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Remove cat guide for cats"""

    ids = cat_id_selector.select_cats(save_stats)

    save_stats = cat_guide_ids(save_stats, ids, 0, "removed")
    return save_stats


def cat_guide_ids(
    save_stats: dict[str, Any], ids: list[int], val: int, string: str
) -> dict[str, Any]:
    """Clear cat guide for a set of cat ids"""
    ids = helper.check_cat_ids(ids, save_stats)
    cat_guide_collected = save_stats["cat_guide_collected"]
    for cat_id in ids:
        cat_guide_collected[cat_id] = val

    save_stats["cat_guide_collected"] = cat_guide_collected
    print(f"Successfully {string} cat guide")
    return save_stats
