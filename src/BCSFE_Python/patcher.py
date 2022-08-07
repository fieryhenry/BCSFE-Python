"""Handler for patching save data"""

import hashlib
from typing import Union


def get_md5_sum(data: bytes) -> str:
    """Get MD5 sum of data."""

    return hashlib.md5(data).hexdigest()


def get_save_data_sum(save_data: bytes, game_version: str) -> str:
    """Get MD5 sum of save data."""

    if game_version in ("jp", "ja"):
        game_version = ""

    salt = f"battlecats{game_version}".encode("utf-8")
    data_to_hash = salt + save_data[:-32]

    return get_md5_sum(data_to_hash)


def detect_game_version(save_data: bytes) -> Union[str, None]:
    """Detect the game version of the save file"""

    if not save_data:
        return None

    game_versions = [
        "jp",
        "en",
        "kr",
        "tw",
    ]
    try:
        curr_hash = save_data[-32:].decode("utf-8")
    except UnicodeDecodeError as err:
        raise Exception("Invalid save hash") from err

    for game_version in game_versions:
        if curr_hash == get_save_data_sum(save_data, game_version):
            return game_version
    return None


def patch_save_data(save_data: bytes, game_version: str) -> bytes:
    """Set the md5 sum of the save data"""

    save_hash = get_save_data_sum(save_data, game_version)
    save_data = save_data[:-32] + save_hash.encode("utf-8")
    return save_data
