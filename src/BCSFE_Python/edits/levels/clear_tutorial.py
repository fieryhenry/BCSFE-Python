"""Handler for clearing the tutorial"""
from typing import Any
from ..other import remove_popups

def clear_tutorial(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for clearing the tutorial"""

    save_stats["tutorial_cleared"]["Value"] = 1
    if save_stats["story_chapters"]["Chapter Progress"][0] == 0:
        save_stats["story_chapters"]["Chapter Progress"][0] = 1
    save_stats["story_chapters"]["Times Cleared"][0][0] = 1
    print("Successfully cleared the tutorial")

    save_stats = remove_popups.remove_popups(save_stats, False)
    return save_stats
