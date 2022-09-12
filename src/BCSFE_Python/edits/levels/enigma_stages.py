"""Handler for editing enigma stages"""
import time
from typing import Any

from ... import helper, user_input_handler


def edit_enigma_stages(save_stats: dict[str, Any]) -> dict[str, Any]:
    """
    Edit enigma stages

    Args:
        save_stats (dict[str, Any]): Save stats

    Returns:
        dict[str, Any]: save stats
    """
    enigma_stages = save_stats["enigma_data"]

    enigma_names = helper.read_file_string(helper.get_file("enigma_names.txt")).splitlines()
    ids = user_input_handler.select_not_inc(enigma_names, "select")
    level = user_input_handler.get_int(
        "Enter engima level (&1&=inferior, &2&=normal, &3&=superior):"
    )

    base_level = 25000
    for enigma_id in ids:
        abs_id = enigma_id + base_level
        data: dict[str, int] = {}
        data["level"] = level
        data["stage_id"] = abs_id
        data["decoding_status"] = 2
        data["start_time"] = int(time.time())
        enigma_stages["stages"].append(data)

    save_stats["enigma_data"] = enigma_stages

    print("Successfully edited enigma stages")
    return save_stats
