"""Handler for removing all unlock popups"""

from typing import Any
from ... import helper

def remove_popups(save_stats: dict[str, Any], text: bool = True) -> dict[str, Any]:
    """Remove all unlock popups."""

    total_popups = 124
    for i in range(total_popups):
        save_stats["unlock_popups"][i] = 1
    if text:
        helper.colored_text("Successfully removed all unlock popups.", helper.GREEN)
    return save_stats