"""Handler for miscalanous save management functions"""

from typing import Any

from ... import adb_handler, helper


def export(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Export the save stats to a json file"""

    helper.export_json(save_stats, helper.get_save_path() + ".json")

    return save_stats


def clear_data(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear data wrapper for the clear_data function"""

    confirm = input("Do want to clear your data (y/n)?:").lower()
    if confirm == "y":
        adb_handler.adb_clear_save_data(save_stats["version"])
        print("Data cleared")

    return save_stats
