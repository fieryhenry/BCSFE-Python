"""Fix the elsewhere issue and unban an account"""
import json
import os
from typing import Any


from ... import helper, adb_handler, server_handler, user_info


def edit_cache(password: str, token: str, save_stats: dict[str, Any]) -> bool:
    """Edit the cache file in /data/data/jp.co.ponos.battlecats/files/cache/ to add the token and password"""

    data = {"password": password, "token": token}
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    inquiry_code = save_stats["inquiry_code"]
    local_path = os.path.abspath(inquiry_code + ".json")

    helper.write_file_string(local_path, data_s)
    game_v = save_stats["version"]
    if game_v == "jp":
        game_v = ""
    try:
        success = adb_handler.run_adb_command(
            f'shell mv "{local_path}" "/data/data/jp.co.ponos.battlecats{game_v}/cache/{inquiry_code}.json"'
        )
    except adb_handler.ADBException:
        success = False
    os.remove(local_path)
    return success


def fix_elsewhere(
    save_stats: dict[str, Any], force_mi: bool = False, text: bool = True
) -> dict[str, Any]:
    """Handler for fixing the elsewhere issue and unban an account"""

    helper.colored_text("Getting account password...", helper.GREEN)
    original_iq = save_stats["inquiry_code"]
    data = server_handler.check_gen_token(save_stats)
    token = data["token"]
    inquiry_code = data["inquiry_code"]
    if token is None:
        helper.colored_text("Failed to get auth token", helper.RED)
        return save_stats
    if original_iq != inquiry_code or force_mi:
        info = user_info.UserInfo(inquiry_code)
        info.clear_managed_items()
        server_handler.update_managed_items(
            save_stats["inquiry_code"], token, save_stats
        )
    if text:
        helper.colored_text(
            "Done!\nYou may get a ban message when pressing play. If you do, just press play again and it should go away\nPress enter to continue...(You still need to save your changes)",
            helper.DARK_YELLOW,
        )
        input()
    return save_stats
