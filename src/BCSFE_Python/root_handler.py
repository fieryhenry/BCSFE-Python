import os
import subprocess
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
    if not is_ran_as_root():
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
    if not is_ran_as_root():
        return None
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
    if not helper.is_android():
        return False
    try:
        os.listdir(get_data_path())
    except PermissionError:
        helper.colored_text(
            "Root access is required to get installed game versions. Try adding sudo before the run command",
            base=helper.RED,
        )
        return False
    return True


def rerun_game(version: str) -> None:
    """
    Rerun the game on the device without adb

    Args:
        version (str): The game version to rerun
    """
    if not is_ran_as_root():
        return
    package_name = "jp.co.ponos.battlecats" + version.replace("jp", "")
    subprocess.run(
        f"sudo pkill -f {package_name}", capture_output=True, check=False, shell=True
    )
    subprocess.run(
        f"sudo monkey -p {package_name} -c android.intent.category.LAUNCHER 1",
        capture_output=True,
        check=False,
        shell=True,
    )
