"""Module that runs when the module is run directly"""

import sys
from . import (
    helper,
    adb_handler,
    server_handler,
    updater,
    patcher,
    feature_handler,
    serialise_save,
    parse_save,
)


def main():
    """Main function"""

    helper.colored_text(
        "Welcome to the Battle Cats Save File Editor\nMade by fieryhenry\nhttps://github.com/fieryhenry/BCSFE-Python\n",
        base=helper.CYAN,
    )

    updater.check_update()
    normal_start_up()


def normal_start_up() -> None:
    """Display and handle options for downloading save data, pulling save data, selecting save data"""

    print()
    options = [
        "Download save data from the game using transfer and confirmation codes",
        "Select a save file from file",
        "Use adb to pull the save from a rooted device",
        "Load save data from json",
    ]
    helper.colored_list(options)
    option = input(f"Enter an option (1 to {len(options)}):")
    path = None
    if option == "1":
        path = server_handler.download_save_handler()
    elif option == "2":
        path = helper.select_file(
            "Select a save file:", helper.get_save_file_filetype()
        )
    elif option == "3":
        path = adb_handler.adb_pull_handler()
    elif option == "4":
        print("Select save data json file")
        js_path = helper.select_file("Select save data json file", [("Json", "*.json")])
        if js_path:
            path = helper.load_json_handler(js_path)
    else:
        print("Please enter a recognised option:")
        return normal_start_up()
    if not path:
        return normal_start_up()
    start(path)
    return None


def start(path: str) -> None:
    """Parse, patch, start the editor and serialise the save data"""
    data = helper.load_save_file(path)
    save_stats = data["save_stats"]
    save_data = data["save_data"]
    country_code = data["country_code"]

    if path.endswith(".json"):
        input(
            "Your save data seems to be in json format. Please use to import json option if you want to load json data.\nPress enter to continue...:"
        )
    while True:
        save_stats = parse_save.start_parse(save_data, country_code)
        save_data = patcher.patch_save_data(save_data, country_code)
        save_stats = feature_handler.menu(save_stats, path)
        save_data = serialise_save.start_serialize(save_stats)
        save_data = patcher.patch_save_data(save_data, country_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
