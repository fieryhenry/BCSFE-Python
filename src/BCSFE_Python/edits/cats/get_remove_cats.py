"""Handler to add and remove cats"""

from ..cats import upgrade_cats
from ... import user_input_handler, helper


def get_cat(save_stats: dict) -> dict:
    """Handler to get cats"""

    return cat_handler(save_stats, 1, "gave")


def remove_cats(save_stats: dict) -> dict:
    """Handler to remove cats"""

    return cat_handler(save_stats, 0, "removed")


def get_cat_rarity(save_stats: dict) -> dict:
    """Get all cats of a certain rarity"""

    ids = user_input_handler.select_options(
        options=upgrade_cats.types,
        mode="get",
    )
    cat_ids = upgrade_cats.get_rarity(ids)

    save_stats = get_cat_ids(
        save_stats=save_stats,
        val=1,
        string="gave",
        ids=cat_ids,
    )
    return save_stats


def cat_handler(save_stats: dict, val: int, string: str) -> dict:
    """Get specific cats"""

    cats = save_stats["cats"]
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        len(cats),
    )

    save_stats = get_cat_ids(
        save_stats=save_stats,
        val=val,
        string=string,
        ids=ids,
    )

    return save_stats


def get_cat_ids(save_stats: dict, val: int, string: str, ids: list) -> dict:
    """Get specific cats by ids"""

    ids = helper.check_cat_ids(ids, save_stats)

    cats = save_stats["cats"]

    for cat_id in ids:
        cats[cat_id] = val

    save_stats["cats"] = cats
    print(f"Successfully {string} cats")
    return save_stats
