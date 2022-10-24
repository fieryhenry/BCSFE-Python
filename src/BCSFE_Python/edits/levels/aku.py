"""Handler for editing the aku realm"""
from typing import Any
from . import story_level_id_selector, unlock_aku_realm
from ... import helper, user_input_handler


def edit_aku(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear whole chapters"""

    save_stats = unlock_aku_realm.unlock_aku_realm(save_stats)
    options = ["Clear aku stages", "Wipe aku data"]
    option = user_input_handler.select_single(options, "select")
    if option == 2:
        return wipe_aku(save_stats)

    aku = save_stats["aku"]["Value"]

    ids = story_level_id_selector.select_levels(None, total=49)
    aku["clear_progress"][0][0] = max(ids)

    for level_id in ids:
        aku["clear_amount"][0][0][level_id] = 1
    save_stats["aku"]["Value"] = aku
    helper.colored_text("Successfully cleared aku stages")
    return save_stats


def wipe_aku(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Reset aku data"""

    aku = save_stats["aku"]["Value"]
    aku["clear_progress"][0][0] = 0
    aku["clear_amount"][0][0] = [0] * len(aku["clear_amount"][0][0])
    save_stats["aku"]["Value"] = aku
    helper.colored_text("Successfully wiped aku data")
    return save_stats
