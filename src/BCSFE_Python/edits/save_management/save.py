"""Handler for saving and exiting the editor"""

from typing import Any

from ... import helper, serialise_save, patcher, adb_handler, root_handler


def save(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialise the save data and exit"""

    save_data = serialise_save.start_serialize(save_stats)
    helper.write_save_data(
        save_data, save_stats["version"], helper.get_save_path(), True
    )

    helper.check_managed_items(save_stats, helper.get_save_path())

    return save_stats


def save_save(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialise the save data"""

    save_data = serialise_save.start_serialize(save_stats)
    helper.write_save_data(
        save_data, save_stats["version"], helper.get_save_path(), False
    )

    helper.check_managed_items(save_stats, helper.get_save_path())

    return save_stats


def save_and_push(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialise the save data and and push it to the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(helper.get_save_path(), save_data)

    helper.check_managed_items(save_stats, helper.get_save_path())

    if not helper.is_android():
        adb_handler.adb_push_save_data(save_stats["version"], helper.get_save_path())

    return save_stats


def save_and_push_rerun(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialise the save data and push it to the game and restart the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(helper.get_save_path(), save_data)

    helper.check_managed_items(save_stats, helper.get_save_path())

    if not helper.is_android():
        adb_handler.adb_push_save_data(save_stats["version"], helper.get_save_path())
        adb_handler.rerun_game(save_stats["version"])
    else:
        root_handler.rerun_game(save_stats["version"])

    return save_stats
