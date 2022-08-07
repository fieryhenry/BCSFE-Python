"""Handler for evolving cats"""
from typing import Any

from ... import user_input_handler, helper, csv_handler, game_data_getter
from . import cat_id_selector


def get_evolve(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for evolving cats"""

    cat_ids = cat_id_selector.select_cats(save_stats)
    return evolve_handler_ids(
        save_stats=save_stats,
        val=2,
        string="set",
        ids=cat_ids,
        forced=False,
    )


def get_evolve_forced(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for evolving cats without the form check"""

    cat_ids = cat_id_selector.select_cats(save_stats)
    return evolve_handler_ids(
        save_stats=save_stats,
        val=2,
        string="set",
        ids=cat_ids,
        forced=True,
    )


def remove_evolve(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for de-evolving cats"""

    cat_ids = cat_id_selector.select_cats(save_stats)
    return evolve_handler_ids(
        save_stats=save_stats,
        val=0,
        string="removed",
        ids=cat_ids,
        forced=True,
    )


def evolve_handler(
    save_stats: dict[str, Any], val: int, string: str, forced: bool
) -> dict[str, Any]:
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

def get_evolve_data(is_jp: bool) -> list[int]:
    """Get max form of cats"""

    data = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest(
                "DataLocal", "nyankoPictureBookData.csv", is_jp
            ).decode("utf-8")
        )
    )
    forms = helper.copy_first_n(data, 2)
    forms = helper.offset_list(forms, -1)
    return forms


def evolve_handler_ids(
    save_stats: dict[str, Any], val: int, string: str, ids: list[int], forced: bool
) -> dict[str, Any]:
    """Evolve specific cats by ids"""
    ids = helper.check_cat_ids(ids, save_stats)
    evolves = save_stats["unlocked_forms"]
    if not forced:
        form_data = get_evolve_data(helper.is_jp(save_stats))
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
