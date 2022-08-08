"""Get game data from the BCData GitHub repository."""
import os
import requests

from . import helper

URL = "https://raw.githubusercontent.com/fieryhenry/BCData/master/"


def download_file(
    game_version: str,
    pack_name: str,
    file_name: str,
) -> bytes:
    """
    Downloads a file from the BCData GitHub repository.
    :param game_version: The game version to download the file from.
    :param pack_name: The pack name to download the file from.
    :param file_name: The file name to download.
    :param is_jp: Whether the game data should be from the jp version of the game.
    :return: The file contents.
    """

    path = helper.get_file(os.path.join("game_data", game_version, pack_name))
    file_path = os.path.join(path, file_name)
    if os.path.exists(file_path):
        return helper.read_file_bytes(file_path)

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
    Gets the latest version of the game data.
    :return: The latest version of the game data.
    """
    response = requests.get(URL + "latest.txt")
    versions = response.text.splitlines()
    return versions

def get_latest_version(is_jp: bool) -> str:
    """
    Gets the latest version of the game data.
    :return: The latest version of the game data.
    """
    if is_jp:
        return get_latest_versions()[1]
    else:
        return get_latest_versions()[0]

def get_file_latest(pack_name: str, file_name: str, is_jp: bool) -> bytes:
    """
    Gets the latest version of the file.
    :return: The latest version of the file.
    """
    version = get_latest_version(is_jp)
    return download_file(version, pack_name, file_name)


def check_remove(new_version: str, is_jp: bool):
    """Checks if older game data is downloaded, and deletes if out of date."""
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
    """Checks if older game data is downloaded, and deletes if out of date."""

    versions = get_latest_versions()
    check_remove(versions[0], is_jp=False)
    check_remove(versions[1], is_jp=True)
