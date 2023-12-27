"""Handler for editting zero legends"""
from typing import Any

from . import event_stages
from ... import user_input_handler

def edit_zl(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting zero legends"""
    stage_data = save_stats["zero_legends"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter stage ids (e.g &1& = Zero Field, &2& = The Edge of Spacetime)(You can enter &all& to get all, a range e.g &1&-&8&, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["zero_legends"] = event_stages.stage_handler(stage_data, ids, -1)

    return save_stats

def is_ancient_curse_clear(save_stats: dict[str, Any]) -> bool:
    """
    Check if the ancient curse is cleared

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        bool: If the ancient curse is cleared
    """
    return save_stats["uncanny"]["Value"]["clear_progress"][0][0] >= 1
