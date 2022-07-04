"""Handler for clearing gauntlets"""

from ..levels import event_stages
from ... import user_input_handler


def edit_gauntlet(save_stats: dict) -> dict:
    """Handler for clearing gauntlets"""

    stage_data = save_stats["gauntlets"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter gauntlet ids (Look up &Event Release Order battle cats& and scroll past the &events& to find &gauntlet& ids) (You can enter &all& to get all, a range e.g 1-49, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"],
    )
    save_stats["gauntlets"] = event_stages.stage_handler(stage_data, ids, 0)
    return save_stats
