import os
from typing import Optional
from . import helper


def get_data_path() -> str:
    """
    Get the data path

    Returns:
        str: The data path
    """
    return "/data/data/"


def get_installed_battlecats_versions() -> Optional[list[str]]:
    """
    Get a list of installed battle cats versions

    Returns:
        Optional[list[str]]: A list of installed battle cats versions
    """
    if not helper.is_android():
        return None
    path = get_data_path()
    if not os.path.exists(path):
        return None
    versions: list[str] = []
    for folder in os.listdir(path):
        if folder == "jp.co.ponos.battlecats":
            versions.append("jp")
        elif folder.startswith("jp.co.ponos.battlecats"):
            versions.append(folder.replace("jp.co.ponos.battlecats", ""))
    return versions


def pull_save_data(game_version: str) -> Optional[str]:
    """
    Pull save data from a game version

    Args:
        game_version (str): The game version to pull from

    Returns:
        Optional[str]: The path to the pulled save data
    """
    package_name = "jp.co.ponos.battlecats" + game_version.replace("jp", "")
    path = get_data_path() + package_name + "/files/SAVE_DATA"
    if not os.path.exists(path):
        return None
    return path

def is_ran_as_root() -> bool:
    """
    Check if the program is ran as root

    Returns:
        bool: If the program is ran as root
    """
    try:
        return os.geteuid() == 0 # type: ignore
    except AttributeError:
        return False