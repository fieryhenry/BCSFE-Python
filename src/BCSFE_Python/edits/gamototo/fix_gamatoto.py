"""Fix gamatoto from crashing the game"""
from typing import Any


def fix_gamatoto(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Fix gamatoto from crashing the game"""

    save_stats["gamatoto_skin"]["Value"] = 2
    print("Successfully fixed gamatoto from crashing the game")
    return save_stats
