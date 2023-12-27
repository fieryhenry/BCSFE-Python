"""Handler for editting zero legends"""
from typing import Any

from . import event_stages
from ... import user_input_handler

def count_chapters(save_stats) -> int:
    data1 = save_stats.get("zero_legends", {})
    count = len(data1)
    return count
    
def set_zl(stage_data, ids, lengths):
    

def edit_zl(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting zero legends"""
    stage_data = save_stats["zero_legends"]
    lengths = count_chapters(save_stats)
    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter stage ids (e.g &1& = Zero Field, &2& = The Edge of Spacetime)(You can enter &all& to get all, a range e.g &1&-&8&, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths,
    )
    stage_data = set_zl(stage_data, ids, lengths)

    return save_stats
