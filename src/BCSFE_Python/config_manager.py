"""
Manager for config settings
"""
import os
from typing import Any, Optional

import yaml

from . import helper, user_input_handler, locale_handler


def get_config_value_category(category: str, key: str) -> Any:
    """
    Returns the value of the given key in the config file.
    """
    config = get_config_file()
    category_data: Optional[dict[str, Any]] = config.get(category)
    if category_data is None:
        create_config_file()
        return get_config_value_category(category, key)
    key_data = category_data.get(key)
    if key_data is None:
        create_config_file()
        return get_config_value_category(category, key)
    return key_data


def get_config_file() -> dict[str, Any]:
    """
    Get the config file

    Returns:
        dict: Config file
    """
    config_file = get_config_path()
    with open(config_file, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


def get_config_path() -> str:
    """
    Get the path to the config file

    Returns:
        str: Path to config file
    """
    config_path_path = helper.get_file("config_path.txt")
    helper.create_dirs(os.path.dirname(config_path_path))
    if not os.path.exists(config_path_path):
        helper.write_file_string(config_path_path, "")

    config_path = helper.read_file_string(config_path_path)
    if config_path == "":
        config_path = os.path.join(get_app_data_folder(), "config.yaml")
    if not os.path.exists(config_path):
        create_config_file(config_path)
    return config_path


def set_config_path(path: str):
    """
    Set the path to the config file

    Args:
        path (str): Path to config file
    """
    helper.write_file_string(helper.get_file("config_path.txt"), path)
    if not os.path.exists(path):
        create_config_file()


def get_config_value(setting: str) -> Any:
    """
    Get a config setting

    Args:
        setting (str): Setting to get

    Returns:
        Any: Value of setting
    """
    config = get_config_file()
    setting_data = config.get(setting)
    if setting_data is None:
        create_config_file()
        return get_config_value(setting)
    return setting_data


def set_config_setting_category(category: str, key: str, value: Any) -> None:
    """
    Set a config setting

    Args:
        setting (str): Setting to set
        value (Any): Value to set setting to
    """
    config = get_config_file()
    config[category][key] = value
    with open(get_config_path(), "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file)


def set_config_setting(setting: str, value: Any) -> None:
    """
    Set a config setting

    Args:
        setting (str): Setting to set
        value (Any): Value to set setting to
    """
    config = get_config_file()
    config[setting] = value
    with open(get_config_path(), "w", encoding="utf-8") as file:
        yaml.safe_dump(config, file)


def create_config_file(config_path: Optional[str] = None) -> None:
    """
    Create the config file if it doesn't exist
    """
    if config_path is None:
        config_file = get_config_path()
    else:
        config_file = config_path
    file_data = "# Configuration file for BCSFE\n"
    file_data += "# This file is automatically created when the program is run for the first time\n"
    file_data += "# You can edit this file to change the settings\n"
    file_data += "# You can also edit the settings in the program\n#\n"
    file_data += "# The following settings are available:\n#\n"
    file_data += """DEFAULT_COUNTRY_CODE: "" # The default game version when downloading / pulling / loading save data. E.g en, jp, kr, tw. Empty means the game version is not specified and will be asked for when needed.
DEFAULT_SAVE_FILE_PATH: "SAVE_DATA" # The default file path for your save data when saving changes / downloading save data / pulling etc
FIXED_SAVE_PATH: False # If True, the save path will be from your user's folder / home folder. If False, the save path will be where the program is run from
LOCALE: "en" # The locale to use for the program.
EDITOR:
  DISABLE_MAXES: False # Allows you to edit the level / amount of items past the max amount.
  SHOW_BAN_WARNING: True # Show a warning when editing bannable items.
  SHOW_CATEGORIES: True # Show the categories in the feature list, instead of a long list.
  SHOW_FEATURE_SELECT_EXPLANATION: True # Show an explanation of how to select a feature.
  ONLY_GET_EN_DATA: False # Only get the en version of the game data even if the save is jp, use if you can't read japanese

START_UP:
  CHECK_FOR_UPDATES: True # Check for updates on startup
  UPDATE_TO_BETAS: False # Check for beta versions of the editor and update to them if found
  HIDE_START_TEXT: False # Hide the start up text - the credits, version info, other links, etc.
  DEFAULT_START_OPTION: -1 # The default save selection option when the editor starts, -1 gives you the option to do any option.
  CREATE_BACKUP: True # Create a backup of the save file when you start the editor.

SAVE_CHANGES:
  SAVE_CHANGES_ON_EDIT: False # Automatically save changes to your save data after using a feature.
  ALWAYS_EXPORT_JSON: False # Always export your save data as json when saving changes.

SERVER:
  UPLOAD_METADATA: True # Upload metadata (catfood, rare ticket, platinum ticket, and legend ticket changes) to the ponos servers when uploading and saving your save data - prevents bans.
  WIPE_TRACKED_ITEMS_ON_START: True # Wipe all tracked items stored when the editor starts up - if disabled, it allows you to upload metadata changes after you exit and re-enter the editor.
"""

    helper.write_file_string(config_file, file_data)


def get_app_data_folder() -> str:
    """
    Get the path to the app data folder cross platform

    Returns:
        str: Path to app data folder
    """
    app_name = "BCSFE_Python"
    os_name = os.name
    if os_name == "nt":
        path = os.path.join(os.environ["APPDATA"], app_name)
    elif os_name == "mac":
        path = os.path.join(
            os.environ["HOME"], "Library", "Application Support", app_name
        )
    elif os_name == "posix":
        path = os.path.join(os.environ["HOME"], "Documents", app_name)
    else:
        raise Exception("Unknown OS: %s" % os_name)
    helper.create_dirs(path)
    return path


def edit_default_gv(_: Any) -> None:
    """
    Edit the default game version
    """
    locale_manager = locale_handler.LocalManager.from_config()
    default_gv = get_config_value("DEFAULT_COUNTRY_CODE")
    default_gv = user_input_handler.colored_input(
        locale_manager.search_key("enter_default_gv") % default_gv
    )
    set_config_setting("DEFAULT_COUNTRY_CODE", default_gv)


def edit_default_save_file_path(_: Any) -> None:
    """
    Edit the default save file path
    """
    locale_manager = locale_handler.LocalManager.from_config()
    default_save_file_path = get_config_value("DEFAULT_SAVE_FILE_PATH")
    default_save_file_path = helper.select_dir(
        locale_manager.search_key("select_default_save_path"),
        default_save_file_path,
    )
    set_config_setting(
        "DEFAULT_SAVE_FILE_PATH", os.path.join(default_save_file_path, "SAVE_DATA")
    )


def edit_fixed_save_path(_: Any) -> None:
    """
    Edit the fixed save path
    """
    locale_manager = locale_handler.LocalManager.from_config()

    fixed_save_path = get_config_value("FIXED_SAVE_PATH")
    if fixed_save_path:
        fixed_save_path = locale_manager.search_key("enabled")
    else:
        fixed_save_path = locale_manager.search_key("disabled")
    fixed_save_path = user_input_handler.colored_input(
        locale_manager.search_key("flag_set_config")
        % (locale_manager.search_key("fixed_save_path"), fixed_save_path)
    )
    if fixed_save_path == "1":
        fixed_save_path = True
    else:
        fixed_save_path = False
    set_config_setting("FIXED_SAVE_PATH", fixed_save_path)


def edit_locale(_: Any) -> None:
    """
    Edit the locale
    """
    all_locales = locale_handler.LocalManager.get_locales()
    locale_manager = locale_handler.LocalManager.from_config()
    locale = get_config_value("LOCALE")
    locale = all_locales[
        user_input_handler.select_single(
            all_locales,
            locale_manager.search_key("select_l"),
            locale_manager.search_key("select_locale") % locale,
        )
        - 1
    ]
    set_config_setting("LOCALE", locale)


def edit_editor_settings(_: Any) -> None:
    """
    Edit the editor settings
    """
    locale_manager = locale_handler.LocalManager.from_config()
    options = [
        "DISABLE_MAXES",
        "SHOW_BAN_WARNING",
        "SHOW_CATEGORIES",
        "SHOW_FEATURE_SELECT_EXPLANATION",
        "ONLY_GET_EN_DATA",
    ]
    option_values = [get_config_value_category("EDITOR", option) for option in options]
    ids = user_input_handler.select_not_inc(options, "select", option_values)
    for option_id in ids:
        option_name = options[option_id]
        current_value = option_values[option_id]
        if current_value:
            current_value = locale_manager.search_key("enabled")
        else:
            current_value = locale_manager.search_key("disabled")
        enable = (
            user_input_handler.colored_input(
                locale_manager.search_key("flag_set_config")
                % (option_name, current_value)
            )
            == "1"
        )
        set_config_setting_category("EDITOR", option_name, enable)


def edit_start_up_settings(_: Any) -> None:
    """
    Edit the start up settings

    Raises:
        Exception: If the option type is not int or bool
    """
    locale_manager = locale_handler.LocalManager.from_config()
    options = {
        "CHECK_FOR_UPDATES": bool,
        "UPDATE_TO_BETAS": bool,
        "HIDE_START_TEXT": bool,
        "DEFAULT_START_OPTION": int,
        "CREATE_BACKUP": bool,
    }
    option_values = [
        get_config_value_category("START_UP", option) for option in options
    ]
    ids = user_input_handler.select_not_inc(
        list(options.keys()), locale_manager.search_key("select_l"), option_values
    )
    for option_id in ids:
        option_name = list(options.keys())[option_id]
        option_type = options[option_name]
        current_value = option_values[option_id]
        if option_type == bool:
            if current_value:
                current_value = locale_manager.search_key("enabled")
            else:
                current_value = locale_manager.search_key("disabled")
            enable = (
                user_input_handler.colored_input(
                    locale_manager.search_key("flag_set_config")
                    % (option_name, current_value)
                )
                == "1"
            )
            set_config_setting_category("START_UP", option_name, enable)
        elif option_type == int:
            option_value = user_input_handler.get_int(
                locale_manager.search_key("enter_new_val_config")
                % (option_name, current_value)
            )
            set_config_setting_category("START_UP", option_name, option_value)
        else:
            raise Exception(f"Unsupported option type {option_type}")


def edit_save_changes_settings(_: Any) -> None:
    """
    Edit the save changes settings
    """
    locale_manager = locale_handler.LocalManager.from_config()
    options = [
        "SAVE_CHANGES_ON_EDIT",
        "ALWAYS_EXPORT_JSON",
    ]
    option_values = [
        get_config_value_category("SAVE_CHANGES", option) for option in options
    ]
    ids = user_input_handler.select_not_inc(
        options, locale_manager.search_key("select_l"), option_values
    )
    for option_id in ids:
        option_name = options[option_id]
        current_value = option_values[option_id]
        if current_value:
            current_value = locale_manager.search_key("enabled")
        else:
            current_value = locale_manager.search_key("disabled")
        enable = (
            user_input_handler.colored_input(
                locale_manager.search_key("flag_set_config")
                % (option_name, current_value)
            )
            == "1"
        )
        set_config_setting_category("SAVE_CHANGES", option_name, enable)


def edit_server_settings(_: Any) -> None:
    """
    Edit the server settings
    """
    locale_manager = locale_handler.LocalManager.from_config()
    options = [
        "UPLOAD_METADATA",
        "WIPE_TRACKED_ITEMS_ON_START",
    ]
    option_values = [get_config_value_category("SERVER", option) for option in options]
    ids = user_input_handler.select_not_inc(
        options, locale_manager.search_key("select_l"), option_values
    )
    for option_id in ids:
        option_name = options[option_id]
        current_value = option_values[option_id]
        if current_value:
            current_value = locale_manager.search_key("enabled")
        else:
            current_value = locale_manager.search_key("disabled")
        enable = (
            user_input_handler.colored_input(
                locale_manager.search_key("flag_set_config")
                % (option_name, current_value)
            )
            == "1"
        )
        set_config_setting_category("SERVER", option_name, enable)


def edit_config_path(_: Any) -> None:
    """
    Edit the config path
    """
    locale_manager = locale_handler.LocalManager.from_config()
    config_path = os.path.dirname(get_config_path())
    config_path = helper.select_dir(
        locale_manager.search_key("select_config_path"), config_path
    )
    config_path = os.path.join(config_path, "config.yaml")
    set_config_path(config_path)
