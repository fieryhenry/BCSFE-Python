"""Handler for fixing time issues"""
from typing import Any
from ... import helper


def fix_time_issues(save_stats: dict[str, Any]) -> dict[str, Any]:
    """
    Fix time issues

    Args:
        save_stats (dict[str, Any]): Save stats

    Returns:
        dict[str, Any]: Save stats
    """
    save_stats["third_time"] = helper.get_iso_time()

    save_stats["time_stamp"] = helper.get_time()
    save_stats["time_stamp_4"] = helper.get_time()

    helper.colored_text(
        "Successfully fixed time issues &(Your device time on both devices must be correct for this to work!)&",
        helper.GREEN,
        helper.RED,
    )
    return save_stats
