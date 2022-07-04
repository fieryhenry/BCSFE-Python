"""Handler for evolving cats"""

from ... import helper, user_input_handler, csv_file_handler
from ..cats import upgrade_cats


def get_evolve(save_stats: dict) -> dict:
    """Handler for evolving cats"""

    return evolve_handler(save_stats, 2, "set", False)


def get_evolve_forced(save_stats: dict) -> dict:
    """Handler for evolving cats without the form check"""

    return evolve_handler(save_stats, 2, "set", True)


def remove_evolve(save_stats: dict) -> dict:
    """Handler for de-evolving cats"""

    return evolve_handler(save_stats, 0, "removed", True)


def get_evolve_current(save_stats: dict) -> dict:
    """Evolve current cats"""

    cats = save_stats["cats"]
    current_cats = []
    for i, cat_flag in enumerate(cats):
        if cat_flag == 1:
            current_cats.append(i)

    return evolve_handler_ids(
        save_stats=save_stats,
        val=2,
        string="set",
        ids=current_cats,
        forced=False,
    )


def evolve_cat_rarity(save_stats: dict) -> dict:
    """Evolve all cats of a certain rarity"""

    ids = user_input_handler.select_options(
        options=upgrade_cats.types,
        mode="true form",
    )
    cat_ids = upgrade_cats.get_rarity(ids)

    save_stats = evolve_handler_ids(
        save_stats=save_stats,
        val=2,
        string="set",
        ids=cat_ids,
        forced=False,
    )
    return save_stats


def get_evolve_data() -> list:
    """Get max form of cats"""

    data = csv_file_handler.parse_csv(
        helper.get_file("game_data/true_forms/nyankoPictureBookData.csv")
    )
    forms = helper.copy_first_n(data, 2)
    forms = helper.offset_list(forms, -1)
    return forms


def evolve_handler(save_stats: dict, val: int, string: str, forced: bool) -> dict:
    """Evolve specific cats"""

    evolves = save_stats["unlocked_forms"]
    flags = evolves
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        len(flags),
    )
    return evolve_handler_ids(save_stats, val, string, ids, forced)


def evolve_handler_ids(
    save_stats: dict, val: int, string: str, ids: list, forced: bool
) -> dict:
    """Evolve specific cats by ids"""
    ids = helper.check_cat_ids(ids, save_stats)
    evolves = save_stats["unlocked_forms"]
    if not forced:
        form_data = get_evolve_data()
        length = min([len(ids), len(form_data)])
        for i in range(length):
            evolves[ids[i]] = form_data[i]
    else:
        for cat_id in ids:
            evolves[cat_id] = val
    save_stats["current_forms"] = evolves

    flags_evolved = [0 if form == 1 else form for form in evolves]
    save_stats["unlocked_forms"] = flags_evolved

    print(f"Successfully {string} true forms of cats")
    return save_stats
