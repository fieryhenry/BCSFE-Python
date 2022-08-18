"""Get game data from the BCData GitHub repository."""
import os
import requests

from . import helper

URL = "https://raw.githubusercontent.com/fieryhenry/BCData/master/"


def download_file(
    game_version: str,
    pack_name: str,
    file_name: str,
    get_data: bool = True,
    print_progress: bool = True,
) -> bytes:
    """
    Downloads the file.

    Args:
        game_version (str): The game version to download from.
        pack_name (str): The pack name to download from.
        file_name (str): The file name to download.
        get_data (bool, optional): Whether to return the data. Defaults to True.
        print_progress (bool, optional): Whether to print the progress. Defaults to True.

    Returns:
        bytes: The data of the file.
    """

    path = helper.get_file(os.path.join("game_data", game_version, pack_name))
    file_path = os.path.join(path, file_name)
    if os.path.exists(file_path):
        if get_data:
            return helper.read_file_bytes(file_path)
        return b""

    if print_progress:
        helper.colored_text(
            f"Downloading game data file &{file_name}& from &{pack_name}& with game version &{game_version}&",
            helper.GREEN,
            helper.WHITE,
        )
    url = URL + game_version + "/" + pack_name + "/" + file_name
    response = requests.get(url)

    helper.create_dirs(path)
    helper.write_file_bytes(file_path, response.content)
    return response.content


def get_latest_versions() -> list[str]:
    """
    Gets the latest versions of the game data.

    Returns:
        list[str]: The latest versions of the game data.
    """
    response = requests.get(URL + "latest.txt")
    versions = response.text.splitlines()
    return versions


def get_latest_version(is_jp: bool) -> str:
    """
    Gets the latest version of the game data.

    Args:
        is_jp (bool): Whether to get the japanese version.

    Returns:
        str: The latest version of the game data.
    """
    if is_jp:
        return get_latest_versions()[1]
    else:
        return get_latest_versions()[0]


def get_file_latest(pack_name: str, file_name: str, is_jp: bool) -> bytes:
    """
    Gets the latest version of the file.

    Args:
        pack_name (str): The pack name to find.
        file_name (str): The file name to find.
        is_jp (bool): Whether to get the japanese version.

    Returns:
        bytes: The data of the file.
    """    
    version = get_latest_version(is_jp)
    return download_file(version, pack_name, file_name)


def get_path(pack_name: str, file_name: str, is_jp: bool):
    """
    Gets the path of the file.

    Args:
        pack_name (str): The pack name to find.
        file_name (str): The file name to find.
        is_jp (bool): Whether to get the japanese version.

    Returns:
        _type_: The path of the file.
    """
    version = get_latest_version(is_jp)
    return os.path.join("game_data", version, pack_name, file_name)


def check_remove(new_version: str, is_jp: bool):
    """
    Checks if older game data is downloaded, and deletes if out of date.

    Args:
        new_version (str): The new version.
        is_jp (bool): Whether to get the japanese version.
    """    
    all_versions = helper.get_dirs(helper.get_file("game_data"))
    for version in all_versions:
        if is_jp:
            if "jp" not in version:
                continue
            if version != new_version:
                helper.delete_dir(helper.get_file(os.path.join("game_data", version)))
        else:
            if "jp" in version:
                continue
            if version != new_version:
                helper.delete_dir(helper.get_file(os.path.join("game_data", version)))


def check_remove_handler():
    """
    Checks if older game data is downloaded, and deletes if out of date.
    """    

    versions = get_latest_versions()
    check_remove(versions[0], is_jp=False)
    check_remove(versions[1], is_jp=True)
