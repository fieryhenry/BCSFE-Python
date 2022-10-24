"""Handler for unlocking the aku realm"""
from typing import Any
from ... import helper
from . import event_stages


def unlock_aku_realm(save_stats: dict[str, Any]) -> dict[str, Any]:
    """
    Unlock the aku realm

    Args:
        save_stats (dict[str, Any]): The save stats to edit

    Returns:
        dict[str, Any]: The edited save stats
    """
    stage_ids = [255, 256, 257, 258, 265, 266, 268]
    offset = 400
    for stage_id in stage_ids:
        save_stats["event_stages"] = event_stages.set_stage_data(
            save_stats["event_stages"],
            stage_id + offset,
            1,
            save_stats["event_stages"]["Lengths"],
            True,
        )
    helper.colored_text("&The Aku realm has successfully been unlocked.")
    return save_stats
