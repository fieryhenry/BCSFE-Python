"""Handler for server requests"""

import datetime
import hashlib
import hmac
import json
from random import randint
import time
from typing import Any, Optional, Union

import requests

from . import (
    helper,
    managed_item,
    serialise_save,
    patcher,
    config_manager,
    user_info,
    parse_save,
)


def get_current_time() -> int:
    """Get current time."""

    return int(time.time())


def random_hex_string(length: int) -> str:
    """Generate a random hex string."""

    return "".join([hex(randint(0, 15))[2:] for _ in range(length)])


def random_digit_string(length: int) -> str:
    """Generate a random digit string."""

    return "".join([str(randint(0, 9)) for _ in range(length)])


def get_nyanko_auth_url() -> str:
    """Get nyanko auth URL."""

    return "https://nyanko-auth.ponosgames.com"


def generate_nyanko_signature(inquiry_code: str, data: str) -> str:
    """Generate nyanko signature."""

    inquiry_code_bytes = inquiry_code.encode("utf-8")
    data_bytes = data.encode("utf-8")
    random_data = random_hex_string(64).encode("utf-8")
    input_rand = inquiry_code_bytes + random_data
    hmac_data = hmac.new(input_rand, data_bytes, digestmod=hashlib.sha256).hexdigest()

    final_signature = random_data.decode("utf-8") + hmac_data

    return final_signature


def generate_nyanko_signature_v1(inquiry_code: str, data: str) -> str:
    """Generate nyanko signature."""

    data += data

    inquiry_code_bytes = inquiry_code.encode("utf-8")
    data_bytes = data.encode("utf-8")
    random_data = random_hex_string(40).encode("utf-8")
    input_rand = inquiry_code_bytes + random_data
    hmac_data = hmac.new(input_rand, data_bytes, digestmod=hashlib.sha1).hexdigest()

    final_signature = random_data.decode("utf-8") + hmac_data

    return final_signature


def check_nyanko_signature(signature: str, data: str, inquiry_code: str) -> bool:
    """Check nyanko signature is correct"""

    curr_hmac_data = signature[64:]
    curr_random_data = signature[:64]
    curr_input_rand = inquiry_code.encode("utf-8") + curr_random_data.encode("utf-8")

    hmac_data = hmac.new(
        curr_input_rand, data.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()
    return hmac_data == curr_hmac_data


def create_backup_metadata(
    items: list[managed_item.ManagedItem],
    play_time: int,
    inquiry_code: str,
    user_rank: int,
    save_key: Optional[str],
) -> dict[str, Any]:
    """Create backup metadata."""
    managed_items: list[dict[str, Any]] = []
    for item in items:
        managed_items.append(item.to_dict())

    managed_items_s = json.dumps(managed_items)
    managed_items_s = managed_items_s.replace(" ", "")
    backup_metadata: dict[str, Any] = {
        "managedItemDetails": managed_items,
        "nonce": random_hex_string(32),
        "playTime": play_time,
        "rank": user_rank,
        "receiptLogIds": [],
        "signature_v1": generate_nyanko_signature_v1(inquiry_code, managed_items_s),
    }
    if save_key is not None:
        backup_metadata["saveKey"] = save_key
    return backup_metadata


def check_nyanko_signature_v1(signature: str, data: str, inquiry_code: str) -> bool:
    """Check nyanko signature is correct"""

    data += data

    curr_hmac_data = signature[40:]
    curr_random_data = signature[:40]
    curr_input_rand = inquiry_code.encode("utf-8") + curr_random_data.encode("utf-8")

    hmac_data = hmac.new(
        curr_input_rand, data.encode("utf-8"), digestmod=hashlib.sha1
    ).hexdigest()
    return hmac_data == curr_hmac_data


def get_headers(inquiry_code: str, data: str) -> dict[str, Any]:
    """Get headers for a request."""

    return {
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "content-type": "application/json",
        "nyanko-signature": generate_nyanko_signature(inquiry_code, data),
        "nyanko-timestamp": str(get_current_time()),
        "nyanko-signature-version": "1",
        "nyanko-signature-algorithm": "HMACSHA256",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
    }


def handle_request(
    url: str,
    data: Union[str, bytes, None],
    headers: dict[str, Any],
    is_get: bool = False,
) -> Union[dict[str, Any], None]:
    """Handle a request."""

    try:
        if is_get:
            response = requests.get(url, data=data, headers=headers)
        else:
            response = requests.post(url, data=data, headers=headers)
    except requests.exceptions.RequestException as err:
        raise Exception("Error getting password: " + str(err)) from err

    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError as err:
        raise Exception("Error getting password: " + str(err)) from err

    if "statusCode" in response_data:
        if response_data["statusCode"] != 1:
            return None
        else:
            return response_data["payload"]
    else:
        return None


def get_password(inquiry_code: str) -> Union[dict[str, Any], None]:
    """Returns the account password for the given inquiry code."""

    url = get_nyanko_auth_url() + "/v1/users"
    data = {
        "accountCode": inquiry_code,
        "accountCreatedAt": str(
            get_current_time() - datetime.timedelta(days=1).seconds
        ),
        "nonce": random_hex_string(32),
    }

    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    headers = get_headers(inquiry_code, data_s)

    return handle_request(url, data_s, headers)


def get_password_refresh(
    inquiry_code: str, password_refresh_token: str
) -> Union[dict[str, Any], None]:
    """Returns the password for the given inquiry code"""

    url = get_nyanko_auth_url() + "/v1/user/password"
    data = {
        "accountCode": inquiry_code,
        "passwordRefreshToken": password_refresh_token,
        "nonce": random_hex_string(32),
    }
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    headers = get_headers(inquiry_code, data_s)

    return handle_request(url, data_s, headers)


def get_client_info(country_code: str, game_version: str) -> dict[str, Any]:
    """Returns the client info for the given country_code and game_version"""

    country_code = country_code.replace("jp", "ja")

    data = {
        "clientInfo": {
            "client": {
                "countryCode": country_code,
                "version": game_version,
            },
            "device": {
                "model": "SM-G955F",
            },
            "os": {
                "type": "android",
                "version": "9",
            },
        },
        "nonce": random_hex_string(32),
    }
    return data


def get_token(
    inquiry_code: str, password: str, country_code: str, game_version: str
) -> Union[None, str]:
    """Returns the token for the given inquiry_code and password"""

    url = get_nyanko_auth_url() + "/v1/tokens"
    data = get_client_info(country_code, game_version)
    data["password"] = password
    data["accountCode"] = inquiry_code
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    headers = get_headers(inquiry_code, data_s)

    payload = handle_request(url, data_s, headers)
    if payload is not None:
        return payload["token"]
    return None


def get_nyanko_save_url() -> str:
    """Get nyanko save URL."""

    return "https://nyanko-save.ponosgames.com"


def download_save(
    country_code: str,
    transfer_code: str,
    confirmation_code: str,
    game_version: str,
) -> requests.Response:
    """Downloads the save for the given country_code, transfer_code, confirmation_code
    and game_version"""

    country_code = country_code.replace("jp", "ja")
    url = get_nyanko_save_url() + "/v2/transfers/" + transfer_code + "/reception"
    data = get_client_info(country_code, game_version)
    data["pin"] = confirmation_code
    # data["isPasswordRefresh"] = True
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")
    headers = {
        "content-type": "application/json",
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
    }
    try:
        response = requests.post(url, data=data_s, headers=headers)
    except requests.exceptions.RequestException as err:
        raise Exception("Error getting save: " + str(err)) from err
    return response


def upload_save_data_body_v2(
    save_data: bytes,
    save_key_data: dict[str, Any],
) -> tuple[bytes, bytes]:
    """Returns the body for the upload save data request

    Args:
        save_data (bytes): Save data
        save_key_data (dict[str, Any]): Save key data

    Returns:
        tuple[bytes, bytes]: Body and boundary
    """
    boundary = f"__-----------------------{random_digit_string(9)}-2147483648".encode(
        "utf-8"
    )
    body = b""
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="key"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["key"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="policy"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["policy"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="x-amz-signature"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["x-amz-signature"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="x-amz-credential"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["x-amz-credential"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="x-amz-algorithm"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["x-amz-algorithm"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="x-amz-date"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["x-amz-date"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="x-amz-security-token"\r\n'
    body += b"Content-Type: text/plain\r\n"
    body += b"\r\n"
    body += save_key_data["x-amz-security-token"].encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="file"; filename="file.sav"\r\n'
    body += b"Content-Type: application/octet-stream\r\n"
    body += b"\r\n"
    body += save_data + b"\r\n"
    body += b"--" + boundary + b"--\r\n"

    return body, boundary


def upload_save_data_body(
    managed_item_details: dict[str, Any],
    inquiry_code: str,
    token: str,
    save_data: bytes,
) -> tuple[bytes, dict[str, Any]]:
    """Gets the headers and body for uploading a save."""

    managed_item_details_str = json.dumps(managed_item_details)
    managed_item_details_str = managed_item_details_str.replace(" ", "")
    headers = get_headers(inquiry_code, managed_item_details_str)
    headers["authorization"] = "Bearer " + token

    boundary = f"__-----------------------{random_digit_string(9)}-2147483648".encode(
        "utf-8"
    )

    headers["content-type"] = "multipart/form-data; boundary=" + boundary.decode(
        "utf-8"
    )

    body = b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="saveData"; filename="data.sav"\r\n'
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += save_data + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="metaData"\r\n\r\n'
    body += managed_item_details_str.encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"--\r\n"

    return body, headers


def upload_save_data(
    token: str,
    inquiry_code: str,
    save_data: bytes,
    play_time: int,
    items: list[managed_item.ManagedItem],
    user_rank: int,
):
    """Uploads the save data for the given token, inquiry_code and save_data"""

    if not config_manager.get_config_value_category("SERVER", "UPLOAD_METADATA"):
        items = []
    save_key = get_save_key(token)
    metadata = create_backup_metadata(
        items, play_time, inquiry_code, user_rank, save_key
    )
    body, headers = upload_save_data_body(metadata, inquiry_code, token, save_data)

    url = get_nyanko_save_url() + "/v1/transfers"
    return handle_request(url, body, headers)


def upload_save_data_v2(
    token: str,
    inquiry_code: str,
    save_data: bytes,
    play_time: int,
    items: list[managed_item.ManagedItem],
    user_rank: int,
):
    """Uploads the save data for the given token, inquiry_code and save_data"""

    if not config_manager.get_config_value_category("SERVER", "UPLOAD_METADATA"):
        items = []
    save_key_data = get_save_key_data(token)
    if save_key_data is None:
        return None
    metadata = create_backup_metadata(
        items, play_time, inquiry_code, user_rank, save_key_data["key"]
    )
    body, boundary = upload_save_data_body_v2(save_data, save_key_data)

    url = "https://nyanko-service-data-prd.s3.amazonaws.com/"
    headers = {
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=" + boundary.decode("utf-8"),
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
    }

    response = requests.post(url, data=body, headers=headers)
    if response.status_code != 204:
        return None

    url_2 = get_nyanko_save_url() + "/v2/transfers"
    meta_data = json.dumps(metadata).replace(" ", "")
    headers_2 = get_headers(inquiry_code, meta_data)
    headers_2["authorization"] = "Bearer " + token

    return handle_request(url_2, meta_data, headers_2)


def upload_metadata_v2(
    token: str,
    inquiry_code: str,
    save_data: bytes,
    play_time: int,
    items: list[managed_item.ManagedItem],
    user_rank: int,
):
    """Uploads the save data for the given token, inquiry_code and save_data"""

    if not config_manager.get_config_value_category("SERVER", "UPLOAD_METADATA"):
        items = []
    save_key_data = get_save_key_data(token)
    if save_key_data is None:
        return None
    metadata = create_backup_metadata(
        items, play_time, inquiry_code, user_rank, save_key_data["key"]
    )
    body, boundary = upload_save_data_body_v2(save_data, save_key_data)

    url = "https://nyanko-service-data-prd.s3.amazonaws.com/"
    headers = {
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "content-type": "multipart/form-data; boundary=" + boundary.decode("utf-8"),
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
    }

    response = requests.post(url, data=body, headers=headers)
    if response.status_code != 204:
        return None

    url_2 = get_nyanko_save_url() + "/v2/backups"
    meta_data = json.dumps(metadata).replace(" ", "")
    headers_2 = get_headers(inquiry_code, meta_data)
    headers_2["authorization"] = "Bearer " + token

    return handle_request(url_2, meta_data, headers_2)


def get_save_key_data(token: str) -> Optional[dict[str, Any]]:
    """Gets the save key for the given token"""

    url = get_nyanko_save_url() + "/v2/save/key?nonce=" + random_hex_string(32)
    headers = {
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "authorization": "Bearer " + token,
        "nyanko-timestamp": str(get_current_time()),
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
    }
    payload = handle_request(url, None, headers, True)
    if payload is not None:
        return payload
    helper.colored_text("Error getting save key", helper.RED)
    return None


def get_save_key(token: str) -> Optional[str]:
    """Gets the save key for the given token

    Args:
        token (str): The token to get the save key for

    Returns:
        Optional[str]: The save key or None if it could not be retrieved
    """
    data = get_save_key_data(token)
    if data is not None:
        return data["key"]
    return None


def upload_metadata(
    token: str,
    inquiry_code: str,
    play_time: int,
    items: list[managed_item.ManagedItem],
    user_rank: int,
):
    """Uploads the metadata for the given token, inquiry_code and save_data"""
    save_key = get_save_key(token)
    metadata = create_backup_metadata(
        items, play_time, inquiry_code, user_rank, save_key
    )

    managed_item_details_str = json.dumps(metadata)
    managed_item_details_str = managed_item_details_str.replace(" ", "")
    headers = get_headers(inquiry_code, managed_item_details_str)
    headers["authorization"] = "Bearer " + token

    url = get_nyanko_save_url() + "/v2/backups"
    return handle_request(url, managed_item_details_str, headers)


def get_nyanko_backups_url() -> str:
    """Get nyanko backups URL."""

    return "https://nyanko-backups.ponosgames.com"


def get_nyanko_managed_items_url() -> str:
    """Get nyanko managed items URL."""

    return "https://nyanko-managed-item.ponosgames.com"


def get_inquiry_code() -> str:
    """Returns a new inquiry code"""

    url = get_nyanko_backups_url() + "/?action=createAccount&referenceId="
    response = requests.get(url)
    data = response.json()
    return data["accountId"]


def update_managed_items(
    inquiry_code: str, authorization: str, save_stats: dict[str, Any]
):
    """Updates the managed items"""
    # game should do this automatically, but eh why not just in case it doesn't

    data = {
        "catfoodAmount": save_stats["cat_food"]["Value"],
        "isPaid": False,
        "legendTicketAmount": save_stats["legend_tickets"]["Value"],
        "nonce": random_hex_string(32),
        "platinumTicketAmount": save_stats["platinum_tickets"]["Value"],
        "rareTicketAmount": save_stats["rare_tickets"]["Value"],
    }
    data_s = json.dumps(data)
    data_s = data_s.replace(" ", "")

    url = get_nyanko_managed_items_url() + "/v1/managed-items"
    headers = get_headers(inquiry_code, data_s)
    headers["authorization"] = "Bearer " + authorization
    return handle_request(url, data_s, headers)


def check_gen_token(
    save_stats: dict[str, Any], path: Optional[str] = None
) -> dict[str, Any]:
    """Gets the account auth token"""

    save_stats, password = check_gen_password(save_stats)
    inquiry_code = save_stats["inquiry_code"]

    save_data = None

    if path is not None:
        save_data = serialise_save.start_serialize(save_stats)
        save_data = patcher.patch_save_data(save_data, save_stats["version"])
        save_data = helper.write_file_bytes(path, save_data)

    # token = get_auth_token_from_file(inquiry_code)
    # if token is None:
    token = get_token(
        inquiry_code,
        password,
        save_stats["version"],
        save_stats["game_version"]["Value"],
    )

    info = user_info.UserInfo(inquiry_code)

    info.set_auth_token("" if token is None else token)

    return {
        "token": token,
        "save_data": save_data,
        "inquiry_code": inquiry_code,
        "save_stats": save_stats,
    }


def check_gen_password(save_stats: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """Checks the password for the given save_stats and generates new if stuff is invalid"""

    inquiry_code = save_stats["inquiry_code"]
    password_refresh_token = save_stats["token"]

    info = user_info.UserInfo(inquiry_code)

    password = info.get_password()
    if password:
        return save_stats, password

    password_refresh_data = get_password_refresh(inquiry_code, password_refresh_token)
    if password_refresh_data is not None:
        info.set_password(password_refresh_data["password"])
        save_stats["token"] = password_refresh_data["passwordRefreshToken"]
        return save_stats, password_refresh_data["password"]

    password_refresh_data = get_password(inquiry_code)
    if password_refresh_data is None:
        inquiry_code = get_inquiry_code()
        save_stats["inquiry_code"] = inquiry_code

        return check_gen_password(save_stats)

    if "accountCode" in password_refresh_data:
        save_stats["inquiry_code"] = password_refresh_data["accountCode"]
        info = user_info.UserInfo(password_refresh_data["accountCode"])

    password_refresh_token = password_refresh_data["passwordRefreshToken"]
    save_stats["token"] = password_refresh_token
    info.set_password(password_refresh_data["password"])
    return save_stats, password_refresh_data["password"]


def prepare_upload(
    save_stats: dict[str, Any],
    path: str,
    print_text: bool = True,
    managed_items: Optional[list[managed_item.ManagedItem]] = None,
) -> Optional[
    tuple[str, Any, bytes, int, list[managed_item.ManagedItem], dict[str, Any]]
]:
    """Handles the pre-upload of the save data"""

    original_iq = save_stats["inquiry_code"]
    if print_text:
        helper.colored_text("Getting account password...", helper.GREEN)
    data = check_gen_token(save_stats, path)
    token = data["token"]
    inquiry_code = data["inquiry_code"]
    save_data = data["save_data"]
    save_stats = data["save_stats"]
    info = user_info.UserInfo(inquiry_code)
    if token is None:
        token = info.get_auth_token()
        if not token:
            info.set_password("")
            if print_text:
                helper.colored_text(
                    "Error getting account auth token. Please try again. If this error persists, please report it on the discord server.",
                    helper.RED,
                )
            return None
    if original_iq != inquiry_code:
        info.clear_managed_items()
        update_managed_items(save_stats["inquiry_code"], token, save_stats)

    if print_text:
        helper.colored_text("Adding meta data...", helper.GREEN)
    if managed_items is None:
        managed_items = info.get_managed_items_lst()
    playtime = helper.time_to_frames(save_stats["play_time"])
    info.clear_managed_items()

    return token, inquiry_code, save_data, playtime, managed_items, save_stats


def upload_handler(
    save_stats: dict[str, Any], path: str
) -> Optional[tuple[Union[None, dict[str, Any]], dict[str, Any]]]:
    """Handles the upload of the save data"""

    data = prepare_upload(save_stats, path)
    if data is None:
        return None
    token, inquiry_code, save_data, playtime, managed_items, save_stats = data

    helper.colored_text("Uploading save data...", helper.GREEN)
    upload_data = upload_save_data_v2(
        token,
        inquiry_code,
        save_data,
        playtime,
        managed_items,
        helper.calculate_user_rank(save_stats),
    )
    # upload_data = upload_save_data(
    #    token,
    #    inquiry_code,
    #    save_data,
    #    playtime,
    #    managed_items,
    #    helper.calculate_user_rank(save_stats),
    # )

    helper.colored_text(
        "After entering these codes in game, you may get a ban message when pressing play. If you do, just press play again and it should go away.\nPress enter to get your codes...",
        helper.DARK_YELLOW,
    )
    input()
    return upload_data, save_stats


def meta_data_upload_handler(
    save_stats: dict[str, Any], path: str
) -> tuple[Union[None, dict[str, Any]], dict[str, Any]]:
    """Handles the upload of the meta data"""

    data = prepare_upload(save_stats, path)
    if data is None:
        return None, save_stats
    token, inquiry_code, save_data, playtime, managed_items, save_stats = data

    helper.colored_text("Uploading meta data...", helper.GREEN)
    upload_data = upload_metadata_v2(
        token,
        inquiry_code,
        save_data,
        playtime,
        managed_items,
        helper.calculate_user_rank(save_stats),
    )

    return upload_data, save_stats


def test_is_save_data(save_data: bytes) -> bool:
    """Test if the save data is a valid save data"""

    try:
        save_data = json.loads(save_data)
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        return True
    else:
        return False


def download_handler() -> Optional[str]:
    """Handles the download of the save data"""

    country_code = helper.ask_cc()
    if country_code == "jp":
        country_code = "ja"
    transfer_code = helper.check_hex(
        input("Enter transfer code:").lower().replace("o", "0")
    )
    if transfer_code is None:
        helper.colored_text(
            "Transfer code must only be made up of numbers 0-9 and letters a-f",
            helper.RED,
        )
        return None
    confirmation_code = helper.check_dec(
        input("Enter confirmation code:").lower().replace("o", "0")
    )
    if confirmation_code is None:
        helper.colored_text(
            "Confirmation code must only be made up of numbers 0-9",
            helper.RED,
        )
        return None
    game_version = input("Enter current game version (e.g 11.3, 9.6, 10.4.0):")
    game_version = helper.str_to_gv(game_version)
    response = download_save(
        country_code, transfer_code, confirmation_code, game_version
    )
    save_data = response.content
    if test_is_save_data(save_data):
        helper.colored_text("Successfully downloaded save data\n", base=helper.GREEN)
    else:
        helper.colored_text(
            "Incorrect transfer code / confirmation code / country code",
            base=helper.RED,
        )
        return None
    headers = response.headers
    save_stats = parse_save.start_parse(save_data, country_code)
    save_stats["token"] = headers["nyanko-password-refresh-token"]
    info = user_info.UserInfo(save_stats["inquiry_code"])
    info.set_password(headers["nyanko-password"])
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, country_code)
    path = helper.save_file(
        "Save save data",
        helper.get_save_file_filetype(),
        helper.get_save_path_home(),
    )
    if path is None:
        return None
    helper.write_file_bytes(path, save_data)
    return path
