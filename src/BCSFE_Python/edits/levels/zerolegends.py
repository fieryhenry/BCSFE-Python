"""Handler for editting zero legends"""
from typing import Any

from . import event_stages
from ... import user_input_handler

def count_chapters(save_stats) -> int:
    data1 = save_stats.get("zero_legends", {})
    count = len(data1)
    return count
    

def edit_zl(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting zero legends"""
    stage_data = save_stats["zero_legends"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter stage ids (e.g &1& = Zero Field, &2& = The Edge of Spacetime)(You can enter &all& to get all, a range e.g &1&-&8&, or ids separate by spaces e.g &5 4 7&):"
        ),
        count_chapters(save_stats),
    )
    save_stats["zero_legends"] = event_stages.stage_handler(stage_data, ids, -1)

    return save_stats
