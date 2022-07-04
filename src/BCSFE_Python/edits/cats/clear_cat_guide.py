"""Handler for clearing the cat guide"""

from ..cats import upgrade_cats
from ... import user_input_handler, helper


def clear_cat_guide(save_stats: dict) -> dict:
    """clear cat guide for specific cats"""

    cat_guide_collected = save_stats["cat_guide_collected"]

    total = len(cat_guide_collected)
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        total,
    )
    save_stats = cat_guide_ids(save_stats, ids)
    return save_stats


def clear_cat_guide_rarity(save_stats: dict) -> dict:
    """Clear cat guide for all cats of a certain rarity"""

    ids = user_input_handler.select_options(
        options=upgrade_cats.types,
        mode="collect",
    )
    cat_ids = upgrade_cats.get_rarity(ids)
    save_stats = cat_guide_ids(save_stats, cat_ids)
    return save_stats


def cat_guide_ids(save_stats: dict, ids: list) -> dict:
    """Clear cat guide for a set of cat ids"""
    ids = helper.check_cat_ids(ids, save_stats)
    cat_guide_collected = save_stats["cat_guide_collected"]
    for cat_id in ids:
        cat_guide_collected[cat_id] = 1

    save_stats["cat_guide_collected"] = cat_guide_collected
    print("Successfully collected cat guide")
    return save_stats
