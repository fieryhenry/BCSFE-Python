"""Handler for clearing behemoth culling stages"""
from typing import Any

from . import event_stages
from ... import user_input_handler


def edit_behemoth_culling(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for clearing behemoth culling stages"""

    stage_data = save_stats["behemoth_culling"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter behemoth culling ids (e.g &0& = &Hidden Forest of Gapra&, &1& = &Ashvini Desert&) (You can enter &all& to get all, a range e.g 1-49, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["behemoth_culling"] = event_stages.stage_handler(stage_data, ids, 0)
    return save_stats
