from typing import Any, Optional
from ... import user_input_handler, server_handler, helper, adb_handler
from ..levels import clear_tutorial


def select(save_stats: dict[str, Any]) -> dict[str, Any]:
    helper.check_changes(None)
    options = [
        "Download save data from the game using transfer and confirmation codes",
        "Select a save file from file",
        "Use adb to pull the save from a rooted device",
        "Load save data from json",
    ]
    index = (
        user_input_handler.select_single(
            options, title="Select an option to get save data:"
        )
        - 1
    )
    save_path = handle_index(index)
    if not save_path:
        return save_stats
    helper.set_save_path(save_path)
    data = helper.load_save_file(save_path)
    save_stats = data["save_stats"]
    if save_path.endswith(".json"):
        input(
            "Your save data seems to be in json format. Please use to import json option if you want to load json data.\nPress enter to continue...:"
        )
    if not clear_tutorial.is_tutorial_cleared(save_stats):
        save_stats = clear_tutorial.clear_tutorial(save_stats)
    return save_stats
def handle_index(index: int) -> Optional[str]:
    path = None
    if index == 0:
        print("Enter details for data transfer:")
        path = server_handler.download_handler()
    elif index == 1:
        print("Select save file:")
        path = helper.select_file(
            "Select a save file:",
            helper.get_save_file_filetype(),
            initial_file=helper.get_save_path_home(),
        )
    elif index == 2:
        print("Enter details for save pulling:")
        game_versions = adb_handler.find_game_versions()
        if not game_versions:
            game_version = helper.ask_cc()
        else:
            index = (
                user_input_handler.select_single(
                    game_versions, "Select", "Select a game version to pull from:", True
                )
                - 1
            )
            game_version = game_versions[index]
        path = adb_handler.adb_pull_save_data(game_version)
    elif index == 3:
        print("Select save data json file")
        js_path = helper.select_file(
            "Select save data json file",
            [("Json", "*.json")],
            initial_file=helper.get_save_path_home() + ".json",
        )
        if js_path:
            path = helper.load_json_handler(js_path)
    else:
        helper.colored_text("Please enter a recognised option", base=helper.RED)
        return None
    return path