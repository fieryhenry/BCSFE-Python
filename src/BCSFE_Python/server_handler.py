"""Handler for server requests"""

import hashlib
import hmac
import random
import json
import time
from typing import Union
import requests
from . import serialise_save, helper, patcher


def get_current_time_stamp() -> int:
    """Returns the current time stamp in seconds"""

    return int(time.time())


def random_hex(length: int) -> str:
    """Returns a random hex string of length n"""

    return "".join(random.choice("0123456789abcdef") for i in range(length))


def random_digits(length: int) -> str:
    """Returns a random string of digits of length n"""

    return "".join(random.choice("0123456789") for i in range(length))


def get_nyanko_auth_url() -> str:
    """Returns the url for the nyanko auth server"""

    return "https://nyanko-auth.ponosgames.com"


def generate_nyanko_signature(inquiry_code: str, data: str) -> str:
    """Generates a signature for the given data with the given inquiry_code"""

    inquiry_code = inquiry_code.encode("utf-8")
    data = data.encode("utf-8")
    random_data = random_hex(64).encode("utf-8")
    input_rand = inquiry_code + random_data
    hmac_data = hmac.new(input_rand, data, hashlib.sha256).hexdigest()
    final_signature = random_data.decode("utf-8") + hmac_data
    return final_signature


def confirm_nyanko_signature(signature: str, json_data: str, inquiry_code: str) -> bool:
    """Checks to see if a given signature is valid"""

    random_data = signature[:64]
    hmac_data = signature[64:]
    input_rand = inquiry_code.encode("utf-8") + random_data.encode("utf-8")
    new_hmac = hmac.new(
        input_rand, json_data.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return new_hmac == hmac_data


def get_headers(inquiry_code: str, data: str) -> dict:
    """Returns the headers for the given inquiry_code and data"""

    headers = {
        "accept-encoding": "gzip",
        "connection": "keep-alive",
        "content-type": "application/json",
        "nyanko-signature": generate_nyanko_signature(inquiry_code, data),
        "nyanko-signature-algorithm": "HMACSHA256",
        "nyanko-signature-version": "1",
        "nyanko-timestamp": str(get_current_time_stamp()),
    }
    return headers


def get_password(inquiry_code: str) -> Union[dict, None]:
    """Returns the password for the given inquiry_code"""

    url = get_nyanko_auth_url() + "/v1/users"
    data = {
        "accountCode": inquiry_code,
        "accountCreatedAt": str(get_current_time_stamp() - 5),
        "nonce": random_hex(32),
    }
    data = json.dumps(data)
    data = data.replace(" ", "")
    headers = get_headers(inquiry_code, data)
    response = requests.post(url, data=data, headers=headers)
    data = response.json()
    if data["statusCode"] != 1:
        return None
    payload = data["payload"]
    return payload


def get_password_refresh(
    inquiry_code: str, password_refresh_token: str
) -> Union[dict, None]:
    """Returns the password for the given inquiry_code"""

    url = get_nyanko_auth_url() + "/v1/user/password"
    data = {
        "accountCode": inquiry_code,
        "nonce": random_hex(32),
        "passwordRefreshToken": password_refresh_token,
    }
    data = json.dumps(data)
    data = data.replace(" ", "")
    headers = get_headers(inquiry_code, data)
    try:
        response = requests.post(url, data=data, headers=headers)
    except requests.exceptions.RequestException:
        helper.colored_text(
            "Error couldn't get account password token.\nCheck your internet connection",
            helper.RED,
        )
        return False
    data = response.json()
    if data["statusCode"] != 1:
        return None
    payload = data["payload"]
    return payload


def get_client_info(country_code: str, game_version: str) -> dict:
    """Returns the client info for the given country_code and game_version"""

    data = {
        "clientInfo": {
            "client": {"countryCode": country_code, "version": game_version},
            "device": {"model": "SM-G973N"},
            "os": {"type": "android", "version": "7.1.2"},
        },
        "nonce": random_hex(32),
    }
    return data


def get_token(inquiry_code: str, password: str, save_stats: dict) -> Union[None, str]:
    """Returns the token for the given inquiry_code and password"""

    url = get_nyanko_auth_url() + "/v1/tokens"
    data = get_client_info(save_stats["version"], save_stats["game_version"])
    data["password"] = password
    data["accountCode"] = inquiry_code
    data = json.dumps(data)
    data = data.replace(" ", "")
    headers = get_headers(inquiry_code, data)
    response = requests.post(url, data=data, headers=headers)
    data = response.json()
    if data["statusCode"] != 1:
        return None
    payload = data["payload"]
    return payload["token"]


def download_save(
    country_code: str, transfer_code: str, confirmation_code: str, game_version: str
) -> Union[None, bytes]:
    """Downloads the save for the given country_code, transfer_code, confirmation_code and game_version"""

    if country_code == "jp":
        country_code = "ja"
    url = f"https://nyanko-save.ponosgames.com/v1/transfers/{transfer_code}/reception"
    data = get_client_info(country_code, game_version)
    data["pin"] = confirmation_code
    data = json.dumps(data)
    data = data.replace(" ", "")
    headers = headers = {"content-type": "application/json", "accept-encoding": "gzip"}
    try:
        response = requests.post(url, data=data, headers=headers)
    except requests.exceptions.RequestException:
        helper.colored_text(
            "Unable to download save data\nCheck your internet connection",
            base=helper.RED,
        )
        return
    return response.content


def download_save_handler() -> Union[None, str]:
    """Handler for the download_save function"""

    country_code = input("Enter your game version (en, ja, kr, tw):")
    if country_code == "jp":
        country_code = "ja"
    transfer_code = input("Enter transfer code:")
    confirmation_code = input("Enter confirmation code:")
    game_version = input("Enter current game version (e.g 11.3, 9.6, 10.4.0):")
    game_version = helper.str_to_gv(game_version)
    save_data = download_save(
        country_code, transfer_code, confirmation_code, game_version
    )
    if not save_data:
        return None
    try:
        save_data = json.loads(save_data)
    except (json.decoder.JSONDecodeError, UnicodeDecodeError):
        helper.colored_text("Successfully downloaded save data\n", base=helper.GREEN)
    else:
        helper.colored_text(
            "Incorrect transfer code / confirmation code / game version",
            base=helper.RED,
        )
        return None
    path = helper.save_file(
        "Save save data", helper.get_save_file_filetype(), "SAVE_DATA"
    )
    helper.write_file_bytes(path, save_data)
    return path


def upload_save_data(
    token: str, inquiry_code: str, save_data: bytes, save_stats: dict
) -> Union[None, dict]:
    """Uploads the save data for the given token, inquiry_code and save_data"""

    managed_item_details = {
        "managedItemDetails": [],
        "nonce": random_hex(32),
        "playTime": helper.time_to_frames(save_stats["play_time"]),
        "rank": 11,
        "receiptLogIds": [],
    }
    managed_item_details = json.dumps(managed_item_details)
    managed_item_details = managed_item_details.replace(" ", "")
    headers = get_headers(inquiry_code, managed_item_details)
    headers["authorization"] = "Bearer " + token
    boundary = f"__-----------------------{random_digits(9)}-2147483648".encode("utf-8")
    headers["content-type"] = "multipart/form-data; boundary=" + boundary.decode(
        "utf-8"
    )

    body = b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="saveData"; filename="data.sav"\r\n'
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += save_data + b"\r\n"
    body += b"--" + boundary + b"\r\n"
    body += b'Content-Disposition: form-data; name="metaData"\r\n\r\n'
    body += managed_item_details.encode("utf-8") + b"\r\n"
    body += b"--" + boundary + b"--\r\n"

    url = "https://nyanko-save.ponosgames.com/v1/transfers"
    response = requests.post(url, data=body, headers=headers)
    data = response.json()
    if data["statusCode"] != 1:
        print("Error: " + response.text)
        return None
    return data["payload"]


def get_inquiry_code() -> str:
    """Returns a new inquiry code"""

    url = "https://nyanko-backups.ponosgames.com/?action=createAccount&referenceId="
    response = requests.get(url)
    data = response.json()
    return data["accountId"]


def check_password(
    save_stats: dict, get_pass: bool = False
) -> Union[dict, tuple[dict, dict]]:
    """Checks the password for the given save_stats and generates new if stuff is invalid"""

    inquiry_code = save_stats["inquiry_code"]
    password_refresh_token = save_stats["token"]

    helper.colored_text("Getting your account password token...", helper.GREEN)
    password_refresh_data = get_password_refresh(inquiry_code, password_refresh_token)

    if password_refresh_data is False:
        return save_stats

    if password_refresh_data is None:
        helper.colored_text(
            "Error getting your account password token, Generating a new one...",
            helper.RED,
        )
        password_refresh_data = get_password(inquiry_code)

        if password_refresh_data is None:
            helper.colored_text(
                "Your inquiry code seems to be invalid. Generating a new one...",
                helper.RED,
            )
            inquiry_code = get_inquiry_code()

            save_stats["inquiry_code"] = inquiry_code
            helper.colored_text(
                f"A new account code has been generated for your account: &{inquiry_code}&",
                helper.GREEN,
                new=helper.WHITE,
            )

            return check_password(save_stats, get_pass)
        if "accountCode" in password_refresh_data:
            inquiry_code = password_refresh_data["accountCode"]
            save_stats["inquiry_code"] = inquiry_code

            helper.colored_text(
                f"A new account code has been generated for your account: &{inquiry_code}&",
                helper.GREEN,
                new=helper.WHITE,
            )

        password_refresh_token = password_refresh_data["passwordRefreshToken"]
        save_stats["token"] = password_refresh_token
        helper.colored_text(
            f"A new account password token has been generated for your account : &{password_refresh_token}&",
            helper.GREEN,
            helper.WHITE,
        )
    if get_pass:
        return save_stats, password_refresh_data
    return save_stats


def upload_handler(save_stats: dict, path: str) -> dict:
    """Handles the upload of the save data"""

    save_stats, password_refresh_data = check_password(save_stats, True)
    inquiry_code = save_stats["inquiry_code"]

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    save_data = helper.write_file_bytes(path, save_data)

    helper.colored_text("Getting account auth token...", helper.GREEN)
    token = get_token(inquiry_code, password_refresh_data["password"], save_stats)

    helper.colored_text("Uploading save data...", helper.GREEN)
    upload_data = upload_save_data(token, inquiry_code, save_data, save_stats)

    helper.colored_text(
        "After entering these codes in game, you may get a ban message when pressing play. If you do, just press play again and it should go away.\nPress enter to get your codes...",
        helper.DARK_YELLOW,
    )
    input()
    return upload_data
