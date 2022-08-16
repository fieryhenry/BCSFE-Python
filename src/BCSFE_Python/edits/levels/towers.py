"""Handler for editing tower stages"""
from typing import Any

from . import event_stages
from ... import user_input_handler

def edit_tower(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing tower stages"""

    stage_data = save_stats["tower"]["progress"]
    stage_data = {
        "Value": stage_data,
        "Lengths": {"stars": stage_data["stars"], "stages": stage_data["stages"]},
    }

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter tower ids (Look up &Event Release Order battle cats& and scroll past the &events& and &gauntlets& to find &tower& ids) (You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):"
        ),
        stage_data["Value"]["total"],
    )
    save_stats["tower"]["progress"] = event_stages.stage_handler(
        stage_data, ids, 0, False
    )["Value"]
    save_stats["tower"]["progress"]["total"] = stage_data["Value"]["total"]
    save_stats["tower"]["progress"]["stars"] = stage_data["Lengths"]["stars"]
    save_stats["tower"]["progress"]["stages"] = stage_data["Lengths"]["stages"]

    return save_stats
