"""Handler for unlocking the enemy guide"""
from typing import Any

from ... import user_input_handler


def enemy_guide(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for unlocking the enemy guide"""

    enemy_guide_stats = save_stats["enemy_guide"]
    total = len(enemy_guide_stats)
    unlock = (
        user_input_handler.colored_input(
            "Do you want to remove enemy guide entries &(1)& or unlock them &(2)&:"
        )
        == "2"
    )
    set_val = 1
    if not unlock:
        set_val = 0
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter enemy ids (Look up enemy release order battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        total,
    )

    for enemy_id in ids:
        if enemy_id >= 2:
            enemy_id -= 2
        if enemy_id >= len(enemy_guide_stats):
            print(f"Invalid enemy id: {enemy_id+2}")
            continue
        enemy_guide_stats[enemy_id] = set_val
    save_stats["enemy_guide"] = enemy_guide_stats
    if not unlock:
        print("Successfully removed enemy guide entries")
    else:
        print("Successfully unlocked enemy guide entries")
    return save_stats
