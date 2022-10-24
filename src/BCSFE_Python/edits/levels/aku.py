"""Handler for editing the aku realm"""
from typing import Any
from . import story_level_id_selector, unlock_aku_realm
from ... import helper


def edit_aku(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear whole chapters"""

    save_stats = unlock_aku_realm.unlock_aku_realm(save_stats)

    aku = save_stats["aku"]["Value"]

    progress = story_level_id_selector.select_level_progress(None, total=49)
    progress = helper.clamp(progress, 0, 49)
    if progress == 0:
        aku["clear_progress"][0][0] = 0
        aku["clear_amount"][0][0] = [0] * len(aku["clear_amount"][0][0])

    else:
        stage_index = progress - 1
        aku["clear_progress"][0][0] = min(progress, 48)
        aku["clear_amount"][0][0][stage_index] = 1
        for i in range(stage_index):
            aku["clear_amount"][0][0][i] = 1
        for i in range(stage_index + 1, 49):
            aku["clear_amount"][0][0][i] = 0

    save_stats["aku"]["Value"] = aku
    helper.colored_text("Successfully set aku stages")
    return save_stats
