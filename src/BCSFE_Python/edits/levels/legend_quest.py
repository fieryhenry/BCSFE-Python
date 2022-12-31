"""Handler for clearing the legend quest"""
from typing import Any
from . import story_level_id_selector
from ... import helper


def edit_legend_quest(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for clearing the legend quest"""
    stage_data = save_stats["legend_quest"]
    lengths = stage_data["Lengths"]
    total = lengths["stages"]
    progress = story_level_id_selector.select_level_progress(None, total=total, examples=["LEVEL 1", "LEVEL 2"])

    if progress == 0:
        stage_data["Value"]["clear_progress"][0][0] = 0
        stage_data["Value"]["clear_amount"][0][0] = [0] * len(stage_data["Value"]["clear_amount"][0][0])
    else:
        stage_id = progress - 1
        stage_data["Value"]["clear_progress"][0][0] = min(progress, total)
        stage_data["Value"]["clear_amount"][0][0][stage_id] = 1
        stage_data["Value"]["tries"][0][0][stage_id] = 1
        for i in range(stage_id):
            stage_data["Value"]["clear_amount"][0][0][i] = 1
            stage_data["Value"]["tries"][0][0][i] = 1
        for i in range(stage_id + 1, total):
            stage_data["Value"]["clear_amount"][0][0][i] = 0
            stage_data["Value"]["tries"][0][0][i] = 0
    
    if stage_data["Value"]["clear_progress"][0][0] == total:
        stage_data["Value"]["unlock_next"][0][1] = lengths["stars"] - 1

    save_stats["legend_quest"] = stage_data
    helper.colored_text("Successfully set legend quest stages")
    return save_stats