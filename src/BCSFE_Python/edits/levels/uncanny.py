"""Handler for editting uncanny legends"""
from typing import Any

from ..levels import event_stages
from ... import user_input_handler

def edit_uncanny(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting uncanny legends"""
    stage_data = save_stats["uncanny"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter stage ids (e.g &1& = a new legend, &2& = here be dragons)(You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["uncanny"] = event_stages.stage_handler(stage_data, ids, -1)

    return save_stats
