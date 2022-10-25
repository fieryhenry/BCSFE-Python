"""Handler for clearing gauntlets"""
from typing import Any

from . import event_stages
from ... import user_input_handler, helper
from ..other import meow_medals


def edit_gauntlet(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for clearing gauntlets"""

    stage_data = save_stats["gauntlets"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter gauntlet ids (Look up &Event Release Order battle cats& and scroll past the &events& to find &gauntlet& ids) (You can enter &all& to get all, a range e.g 1-49, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["gauntlets"] = event_stages.stage_handler(stage_data, ids, 0)
    base_addr = meow_medals.BaseMapIds.GAUNTLETS.value
    save_stats["gauntlets"], save_stats["medals"] = event_stages.set_medals(
        save_stats["gauntlets"],
        save_stats["medals"],
        (base_addr, base_addr + len(save_stats["gauntlets"]["Value"]["unlock_next"])),
        -base_addr,
        helper.check_data_is_jp(save_stats),
    )
    return save_stats


def edit_collab_gauntlet(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for clearing collab gauntlets"""

    stage_data = save_stats["collab_gauntlets"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter collab gauntlet ids (Look up &Event Release Order battle cats& and scroll past the &events& and past &gauntlet& to find &Collaboration Gauntlet& ids) (You can enter &all& to get all, a range e.g 1-49, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["collab_gauntlets"] = event_stages.stage_handler(stage_data, ids, 0)
    return save_stats
