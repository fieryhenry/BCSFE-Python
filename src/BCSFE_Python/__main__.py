"""Module that runs when the module is run directly"""
import sys

from . import (
    adb_handler,
    config_manager,
    feature_handler,
    game_data_getter,
    helper,
    parse_save,
    patcher,
    serialise_save,
    server_handler,
    tracker,
    updater,
    user_input_handler,
)
from .edits.levels import clear_tutorial


def print_start_up():
    """Print start up message"""

    helper.colored_text(
        "Welcome to the &Battle Cats Save File Editor&\n"
        + "Made by &fieryhenry&\n\n"
        + "GitHub: &https://github.com/fieryhenry/BCSFE-Python&\n"
        + "Discord: &https://discord.gg/DvmMgvn5ZB& - Please report any bugs to &#bug-reports&, or any suggestions to &#suggestions&\n"
        + "Donate: &https://ko-fi.com/fieryhenry&\n"
        + f"Config file path: &{config_manager.get_config_path()}&",
        base=helper.CYAN,
        new=helper.WHITE,
    )
    local_version = updater.get_local_version()

    print()
    if "b" in local_version:
        helper.colored_text(
            "You are using a &beta& release, some things may be broken. Please report any bugs you find to &#bug-reports& on Discord and specify that you are using a beta version",
            base=helper.RED,
            new=helper.WHITE,
        )
    print()
    helper.colored_text(
        "Thanks To:\n"
        + "&Lethal's editor& for giving me inspiration to start the project and it helped me work out how to patch the save data and edit cf/xp: &https://www.reddit.com/r/BattleCatsCheats/comments/djehhn/editoren&\n"
        + "&Beeven& and &csehydrogen's& code, which helped me figure out how to patch save data: &https://github.com/beeven/battlecats& and &https://github.com/csehydrogen/BattleCatsHacker&\n"
        + "Anyone who has supported my work for giving me motivation to keep working on this project: &https://ko-fi.com/fieryhenry&\n"
        + "Everyone in the discord for giving me saves, reporting bugs, suggesting new features, and for being an amazing community: &https://discord.gg/DvmMgvn5ZB&",
        base=helper.GREEN,
        new=helper.WHITE,
    )


def check_update() -> None:
    """Check if there is an update available and if so, ask the user if they want to update"""
    version_info = updater.get_version_info()
    stable_ver, pre_release_ver = version_info

    local_version = updater.get_local_version()

    helper.colored_text(
        f"Local version: &{local_version} | &Latest stable version: &{stable_ver}",
        base=helper.CYAN,
        new=helper.WHITE,
        end="",
    )
    if pre_release_ver > stable_ver:
        helper.colored_text(
            f"& | &Latest pre-release version: &{pre_release_ver}&",
            base=helper.CYAN,
            new=helper.WHITE,
            end="",
        )
    print()
    update_data = updater.check_update(version_info)
    if update_data[0]:
        helper.colored_text(
            "\nAn update is available, would you like to update? (&y&/&n&):",
            base=helper.GREEN,
            new=helper.WHITE,
            end="",
        )
        if input().lower() == "y":
            updater.update(update_data[1])
            helper.colored_text("Update successful", base=helper.GREEN)
            helper.exit_editor()


def main():
    """Main function"""

    item_tracker = tracker.Tracker()

    if config_manager.get_config_value_category(
        "SERVER", "WIPE_TRACKED_ITEMS_ON_START"
    ):
        item_tracker.reset_tracker()
    game_data_getter.check_remove_handler()

    check_updates = config_manager.get_config_value_category(
        "START_UP", "CHECK_FOR_UPDATES"
    )
    show_start = not config_manager.get_config_value_category(
        "START_UP", "HIDE_START_TEXT"
    )

    if show_start or check_updates:
        print()
        helper.print_line_seperator(helper.CYAN, length=200)
    if check_updates:
        check_update()
    if show_start:
        print_start_up()
    if show_start or check_updates:
        helper.print_line_seperator(helper.CYAN, length=200)
    normal_start_up()


def normal_start_up(default_op: bool = True) -> None:
    """Display and handle options for downloading save data, pulling save data, selecting save data"""

    default_start_option = config_manager.get_config_value_category(
        "START_UP", "DEFAULT_START_OPTION"
    )

    if default_start_option != -1 and default_op:
        index = default_start_option - 1
    else:
        print()
        if not default_op:
            helper.print_line_seperator(helper.WHITE)
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
    path = None
    if index == 0:
        print("Enter details for data transfer:")
        path = server_handler.download_handler()
    elif index == 1:
        print("Select save file:")
        path = helper.select_file(
            "Select a save file:",
            helper.get_save_file_filetype(),
            initial_file=helper.get_default_save_name(),
        )
    elif index == 2:
        print("Enter details for save pulling:")
        game_version = helper.ask_cc()
        path = adb_handler.adb_pull_save_data(game_version)
    elif index == 3:
        print("Select save data json file")
        js_path = helper.select_file(
            "Select save data json file",
            [("Json", "*.json")],
            initial_file=helper.get_default_save_name() + ".json",
        )
        if js_path:
            path = helper.load_json_handler(js_path)
    else:
        helper.colored_text("Please enter a recognised option", base=helper.RED)
        return normal_start_up(False)
    if not path:
        return normal_start_up(False)
    start(path)
    return None


def start(path: str) -> None:
    """Parse, patch, start the editor and serialise the save data"""
    data = helper.load_save_file(path)
    save_stats = data["save_stats"]
    save_data: bytes = data["save_data"]
    country_code = data["country_code"]

    if path.endswith(".json"):
        input(
            "Your save data seems to be in json format. Please use to import json option if you want to load json data.\nPress enter to continue...:"
        )
    if not clear_tutorial.is_tutorial_cleared(save_stats):
        save_stats = clear_tutorial.clear_tutorial(save_stats)
        save_data = serialise_save.start_serialize(save_stats)
    while True:
        save_stats = parse_save.start_parse(save_data, country_code)
        save_data = patcher.patch_save_data(save_data, country_code)
        save_stats = feature_handler.menu(save_stats, path)
        save_data = serialise_save.start_serialize(save_stats)
        save_data = patcher.patch_save_data(save_data, country_code)
        if config_manager.get_config_value_category(
            "SAVE_CHANGES", "SAVE_CHANGES_ON_EDIT"
        ):
            helper.write_file_bytes(path, save_data)
            helper.colored_text(
                f"Save data saved to &{path}&", base=helper.GREEN, new=helper.WHITE
            )
        if config_manager.get_config_value_category(
            "SAVE_CHANGES", "ALWAYS_EXPORT_JSON"
        ):
            helper.export_json(save_stats, path + ".json")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
