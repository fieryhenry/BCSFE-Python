"""Fix the elsewhere issue and unban an account"""

import json
import os

from ... import adb_handler, helper, server_handler


def edit_cache(password: str, token: str, save_stats: str):
    """Edit the cache file in /data/data/jp.co.ponos.battlecats/files/cache/ to add the token and password"""

    data = {"password": password, "token": token}
    data = json.dumps(data)
    data = data.replace(" ", "")
    inquiry_code = save_stats["inquiry_code"]
    local_path = os.path.abspath(inquiry_code + ".json")

    helper.write_file_string(local_path, data)
    game_v = save_stats["version"]
    if game_v == "jp":
        game_v = ""
    success = (
        adb_handler.adb_cmd_handler(
            f'adb shell mv "{local_path}" "/data/data/jp.co.ponos.battlecats{game_v}/cache/{inquiry_code}.json"'
        )
        is not None
    )
    os.remove(local_path)
    return success


def fix_elsewhere(save_stats: dict) -> dict:
    """Handler for fixing the elsewhere issue and unban an account"""

    save_stats, password_refresh_data = server_handler.check_password(save_stats, True)
    inquiry_code = save_stats["inquiry_code"]
    helper.colored_text("Getting account auth token...", helper.GREEN)
    token = server_handler.get_token(
        inquiry_code, password_refresh_data["password"], save_stats
    )
    if edit_cache(password_refresh_data["password"], token, save_stats):
        helper.colored_text(
            "Done!\nYou may get a ban message when pressing play. If you do, just press play again and it should go away\nPress enter to continue...",
            helper.DARK_YELLOW,
        )
        input()
    return save_stats
