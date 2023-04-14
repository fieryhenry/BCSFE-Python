"""Handler for server save management functions"""
from typing import Any

from ... import helper, serialise_save, server_handler, user_info


def upload_metadata(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Upload the metadata to the game server"""

    _, save_stats = server_handler.meta_data_upload_handler(
        save_stats, helper.get_save_path()
    )
    return save_stats


def set_managed_items(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Set the managed items for the save stats"""

    data = server_handler.check_gen_token(save_stats)
    token = data["token"]
    save_stats = data["save_stats"]
    if token is None:
        helper.colored_text("Error generating token")
        return save_stats
    server_handler.update_managed_items(save_stats["inquiry_code"], token, save_stats)
    return save_stats


def handle_upload_error(inquiry_code: str):
    """Show an error message"""
    info = user_info.UserInfo(inquiry_code)
    info.set_auth_token("")
    info.set_password("")
    helper.colored_text(
        "Error uploading save data\nPlease try again. If error persists, please report this in #bug-reports"
    )


def save_and_upload(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Serialise the save data, and upload it to the game server"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = helper.write_save_data(
        save_data, save_stats["version"], helper.get_save_path(), False
    )
    upload_data = server_handler.upload_handler(save_stats, helper.get_save_path())
    if upload_data is None:
        handle_upload_error(save_stats["inquiry_code"])
        return save_stats
    upload_data, save_stats = upload_data
    inquiry_code = save_stats["inquiry_code"]
    if upload_data is None:
        handle_upload_error(inquiry_code)
        return save_stats
    if "transferCode" not in upload_data:
        handle_upload_error(inquiry_code)
        return save_stats
    else:
        helper.colored_text(f"Transfer code : &{upload_data['transferCode']}&")
        helper.colored_text(f"Confirmation Code : &{upload_data['pin']}&")

    return save_stats
