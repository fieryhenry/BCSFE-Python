from __future__ import annotations
import base64
import time
from typing import Any

from bcsfe import core
import jwt

from bcsfe.cli import color


class RequestResult:
    def __init__(
        self,
        url: str,
        response: core.Response | None,
        headers: dict[str, str],
        data: str,
        payload: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ):
        self.url = url
        self.response = response
        self.headers = headers
        self.data = data
        self.payload = payload
        self.timestamp = timestamp


class ServerHandler:
    auth_url = "https://nyanko-auth.ponosgames.com"
    save_url = "https://nyanko-save.ponosgames.com"
    backups_url = "https://nyanko-backups.ponosgames.com"
    aws_url = "https://nyanko-service-data-prd.s3.amazonaws.com"
    managed_item_url = "https://nyanko-managed-item.ponosgames.com"
    events_url = "https://nyanko-events.ponosgames.com"

    def __init__(self, save_file: core.SaveFile, print: bool = True):
        self.save_file = save_file
        self.print = print
        self.counter = 0

    @staticmethod
    def get_password_key() -> str:
        return "password"

    @staticmethod
    def get_auth_token_key() -> str:
        return "auth_token"

    @staticmethod
    def get_save_key_key() -> str:
        return "save_key"

    def save_password(self, password: str):
        self.save_file.store_string(ServerHandler.get_password_key(), password)

    def get_stored_password(self) -> str | None:
        return self.save_file.get_string(ServerHandler.get_password_key())

    def remove_stored_password(self):
        self.save_file.remove_string(ServerHandler.get_password_key())

    def save_save_key_data(self, save_key: dict[str, Any]):
        self.save_file.store_dict(ServerHandler.get_save_key_key(), save_key)

    def get_stored_save_key_data(self) -> dict[str, Any] | None:
        save_key_data = self.save_file.get_dict(ServerHandler.get_save_key_key())
        if save_key_data is None:
            return None
        if not self.validate_save_key_data(save_key_data):
            self.remove_stored_save_key_data()
            return None
        return save_key_data

    def validate_save_key_data(self, save_key_data: dict[str, Any]) -> bool:
        key = save_key_data.get("key")
        if key is None:
            return False
        if key.split("/")[2] != self.save_file.inquiry_code:
            return False
        policy = save_key_data.get("policy")
        if policy is None:
            return False
        policy = base64.b64decode(policy)
        json_policy = core.JsonFile.from_data(core.Data(policy)).to_object()
        expiration = json_policy.get("expiration")
        if expiration is None:
            return False
        expiration = int(
            time.mktime(time.strptime(expiration, "%Y-%m-%dT%H:%M:%S.%fZ"))
        )
        if expiration < time.time():
            return False
        return True

    def remove_stored_save_key_data(self):
        self.save_file.remove_dict(ServerHandler.get_save_key_key())

    def save_auth_token(self, auth_token: str):
        self.save_file.store_string(ServerHandler.get_auth_token_key(), auth_token)

    def get_stored_auth_token(self) -> str | None:
        token = self.save_file.get_string(ServerHandler.get_auth_token_key())
        return token

    def remove_stored_auth_token(self):
        self.save_file.remove_string(ServerHandler.get_auth_token_key())

    def get_password_new(self) -> str | None:
        self.print_key("getting_password")

        url = f"{self.auth_url}/v1/users"
        data = {
            "accountCode": self.save_file.inquiry_code,
            "accountCreatedAt": int(self.save_file.energy_penalty_timestamp),
            "nonce": core.Random.get_hex_string(32),
        }
        password = self.do_password_request(url, data)
        return password

    @staticmethod
    def log_error(key: str, result: RequestResult):
        if "EXPECT_THIS_TO_FAIL" in result.data:
            return
        if result.response is None:
            log_text = "Failed to make request. Check your internet connection."
            core.core_data.logger.log_error(log_text)
            return
        log_text = (
            f"Error: {key}\n"
            f"URL: {result.url}\n"
            f"Response Headers: {result.response.headers}\n"
            f"Response Body: {result.response.content.decode('utf-8')}\n"
            f"Status Code: {result.response.status_code}\n"
            f"Reason: {result.response.reason}\n"
            f"Request Headers: {result.headers}\n"
            f"Request Body: {result.data}\n"
        )
        core.core_data.logger.log_error(log_text)

    def do_password_request(self, url: str, dict_data: dict[str, Any]) -> str | None:
        result = self.do_request(url, dict_data)
        if result.payload is None:
            ServerHandler.log_error("password_fail", result)
            return None
        payload = result.payload
        password = payload.get("password", None)
        if password is None:
            ServerHandler.log_error("password_fail", result)
            self.remove_stored_password()
            return None
        password_refresh_token = payload.get("passwordRefreshToken", None)
        if password_refresh_token is None:
            ServerHandler.log_error("password_fail", result)
            self.remove_stored_password()
            return None
        account_code = payload.get("accountCode", None)
        timestamp = result.timestamp

        self.save_file.password_refresh_token = password_refresh_token
        self.save_password(password)
        if account_code:
            self.save_file.inquiry_code = account_code
            self.remove_stored_auth_token()
            self.remove_stored_save_key_data()

            if timestamp is not None:
                self.save_file.energy_penalty_timestamp = int(timestamp)
            if not self.update_managed_items():
                return None

        return password

    def do_request(self, url: str, dict_data: dict[str, Any]) -> RequestResult:
        data = (
            core.JsonFile.from_object(dict_data)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
        headers = core.AccountHeaders(self.save_file, data).get_headers()
        response = core.RequestHandler(url, headers, core.Data(data)).post()
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, data))
            return RequestResult(url, response, headers, data)
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            return RequestResult(url, response, headers, data)

        timestamp = json.get("timestamp", None)

        payload = json.get("payload", {})
        return RequestResult(url, response, headers, data, payload, timestamp)

    def refresh_password(self) -> str | None:
        self.print_key("refreshing_password")

        url = f"{self.auth_url}/v1/user/password"
        data = {
            "accountCode": self.save_file.inquiry_code,
            "passwordRefreshToken": self.save_file.password_refresh_token,
            "nonce": core.Random.get_hex_string(32),
        }
        return self.do_password_request(url, data)

    def get_auth_token_new(self, password: str) -> str | None:
        self.print_key("getting_auth_token")

        url = f"{self.auth_url}/v1/tokens"
        data = core.ClientInfo.from_save_file(self.save_file).get_client_info()
        data["password"] = password
        data["accountCode"] = self.save_file.inquiry_code

        result = self.do_request(url, data)
        if result.payload is None:
            ServerHandler.log_error("auth_token_fail", result)
            self.remove_stored_auth_token()
            self.remove_stored_password()
            return None
        payload = result.payload
        auth_token = payload.get("token", None)
        if auth_token is None:
            ServerHandler.log_error("auth_token_fail", result)
            self.remove_stored_auth_token()
            self.remove_stored_password()
            return None
        self.save_auth_token(auth_token)
        return auth_token

    def get_password(self, tries: int = 0) -> str | None:
        password = self.get_stored_password()
        if password is not None:
            return password
        password = self.refresh_password()
        if password is not None:
            return password
        password = self.get_password_new()
        if password is not None:
            return password
        self.create_new_account()
        if tries >= 1:
            return None
        return self.get_password(tries + 1)

    def validate_auth_token(self, auth_token: str) -> bool:
        token = jwt.decode(  # type: ignore
            auth_token,
            algorithms=["HS256"],
            options={"verify_signature": False},
        )
        if not token:
            return False
        if token.get("exp", 0) < time.time():
            return False
        if token.get("accountCode", None) != self.save_file.inquiry_code:
            return False

        return True

    def get_auth_token(self, tries: int = 1) -> str | None:
        auth_token = self.get_stored_auth_token()
        if auth_token is not None:
            if self.validate_auth_token(auth_token):
                return auth_token
            self.remove_stored_auth_token()
        password = self.get_password()
        if password is None:
            return None
        auth_token = self.get_stored_auth_token()
        if auth_token is not None:
            return auth_token
        auth_token = self.get_auth_token_new(password)
        if auth_token is not None:
            return auth_token

        if tries > 0:
            self.print_key("retry_auth_token")
            return self.get_auth_token(tries - 1)

        return None

    def log_no_internet(self, result: RequestResult):
        ServerHandler.log_error("no_internet", result)
        if self.print:
            core.print_no_internet()

    def get_save_key_new(self, auth_token: str) -> dict[str, Any] | None:
        self.print_key("getting_save_key")

        nonce = core.Random.get_hex_string(32)
        url = f"{self.save_url}/v2/save/key?nonce={nonce}"
        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "authorization": "Bearer " + auth_token,
            "nyanko-timestamp": str(int(time.time())),
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
        response = core.RequestHandler(url, headers).get()
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, ""))
            return None
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            ServerHandler.log_error(
                "save_key_fail", RequestResult(url, response, headers, "")
            )
            self.remove_stored_auth_token()
            return None
        payload = json.get("payload", {})
        self.save_save_key_data(payload)
        return payload

    def get_save_key(self) -> dict[str, Any] | None:
        # save_key = self.get_stored_save_key_data()
        # if save_key and save_key.get("key", None):
        #    return save_key
        auth_token = self.get_auth_token()
        if auth_token is None:
            return None
        # save_key = self.get_stored_save_key_data()
        # if save_key:
        #    return save_key
        save_key = self.get_save_key_new(auth_token)
        if save_key is not None:
            return save_key

        return None

    def get_upload_request_form(
        self,
        save_key: dict[str, str],
    ) -> core.MultipartForm:
        save_data = self.save_file.to_data()
        form_data = core.MultipartForm()
        for key, value in save_key.items():
            if key == "url":
                continue
            form_data.add_key(key, value.encode(), "text/plain")

        form_data.add_key(
            "file", save_data.to_bytes(), "application/octet-stream", "file.sav"
        )
        return form_data

    def upload_save_data(self, save_key: dict[str, Any]) -> bool:
        self.print_key("uploading_save_file")

        form = self.get_upload_request_form(save_key)
        if form is None:
            self.remove_stored_save_key_data()
            return False
        url = save_key.get("url")
        if url is None:
            url = f"{self.aws_url}/"
        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
        response = core.RequestHandler(url, headers, form=form).post(no_timeout=True)
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, ""))
            return False
        if response.status_code != 204:
            ServerHandler.log_error(
                "upload_fail_aws",
                RequestResult(
                    url,
                    response,
                    headers,
                    form.get_all_type("text-plain"),
                ),
            )

            self.remove_stored_save_key_data()
            return False
        return True

    def print_key(self, key: str, **kwargs: Any):
        if self.print:
            color.ColoredText.localize(key, **kwargs)

    def get_codes(self, upload_managed_items: bool = True) -> tuple[str, str] | None:
        self.save_file.show_ban_message = False

        auth_token = self.get_auth_token()
        if auth_token is None:
            return None

        save_key = self.get_save_key()

        if save_key is None:
            self.remove_stored_save_key_data()
            return None

        if not self.upload_save_data(save_key):
            return None

        self.print_key("getting_codes")

        bmd = core.BackupMetaData(self.save_file)
        meta_data = bmd.create(save_key["key"], upload_managed_items)

        url = f"{self.save_url}/v2/transfers"
        headers = core.AccountHeaders(self.save_file, meta_data).get_headers()
        headers["authorization"] = "Bearer " + auth_token

        response = core.RequestHandler(url, headers, core.Data(meta_data)).post()
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, meta_data))
            return None
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            ServerHandler.log_error(
                "upload_fail_transfers",
                RequestResult(url, response, headers, meta_data),
            )
            self.remove_stored_auth_token()
            return None
        payload = json.get("payload", {})
        transfer_code = payload.get("transferCode", None)
        confirmation_code = payload.get("pin", None)
        if transfer_code is None or confirmation_code is None:
            ServerHandler.log_error(
                "upload_fail_transfers",
                RequestResult(url, response, headers, ""),
            )
            self.remove_stored_auth_token()
            return None
        bmd.remove_managed_items()
        if self.print:
            print()
        return (transfer_code, confirmation_code)

    def has_managed_items(self) -> bool:
        bmd = core.BackupMetaData(self.save_file)
        managed_items = bmd.get_managed_items()
        if len(managed_items) == 0:
            return False
        return True

    def upload_meta_data(self) -> bool:
        auth_token = self.get_auth_token()
        if auth_token is None:
            return False

        save_key = self.get_save_key()
        if save_key is None:
            self.remove_stored_save_key_data()
            return False

        if not self.upload_save_data(save_key):
            return False

        bmd = core.BackupMetaData(self.save_file)
        meta_data = bmd.create(save_key["key"])

        url = f"{self.save_url}/v2/backups"
        headers = core.AccountHeaders(self.save_file, meta_data).get_headers()
        headers["authorization"] = "Bearer " + auth_token

        response = core.RequestHandler(url, headers, core.Data(meta_data)).post()
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, meta_data))
            return False
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return False
        bmd.remove_managed_items()
        return True

    def get_new_inquiry_code(self) -> str | None:
        url = f"{self.backups_url}/?action=createAccount&referenceId="

        response = core.RequestHandler(url).get()
        if response is None:
            self.log_no_internet(RequestResult(url, None, {}, ""))
            return None
        data = response.json()
        iq = data["accountId"]
        return iq

    def create_new_account(self) -> bool:
        new_iq = self.get_new_inquiry_code()
        if new_iq is None:
            return False
        self.save_file.inquiry_code = new_iq
        self.remove_stored_auth_token()
        self.remove_stored_save_key_data()
        self.remove_stored_password()
        fail_text = "EXPECT_THIS_TO_FAIL"
        start_count = (40 - len(fail_text)) // 2
        end_count = 40 - len(fail_text) - start_count
        self.save_file.password_refresh_token = (
            "_" * start_count + fail_text + "_" * end_count
        )
        password = self.get_password()
        auth_token = self.get_auth_token()
        save_key_data = self.get_save_key()
        self.update_managed_items()
        self.save_file.show_ban_message = False
        if password is None or auth_token is None or save_key_data is None:
            return False
        return True

    @staticmethod
    def from_codes(
        transfer_code: str,
        confirmation_code: str,
        cc: core.CountryCode,
        gv: core.GameVersion,
        print: bool = True,
        save_backup: bool = True,
    ) -> tuple[ServerHandler | None, RequestResult | None]:
        url = f"{ServerHandler.save_url}/v2/transfers/{transfer_code}/reception"
        data = core.ClientInfo(cc, gv).get_client_info()
        data["pin"] = confirmation_code
        data_str = (
            core.JsonFile.from_object(data)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )

        headers = {
            "content-type": "application/json",
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
        response = core.RequestHandler(url, headers, core.Data(data_str)).post()
        if response is None:
            if print:
                core.print_no_internet()
            return None, None
        resp_headers = response.headers
        content_type = resp_headers.get("content-type", "")
        if content_type != "application/octet-stream":
            return None, RequestResult(url, response, headers, data_str)

        save_data = response.content

        if save_backup:
            temp_path = (
                core.Path.get_documents_folder()
                .add("saves")
                .generate_dirs()
                .add("transfer_backup")
            )
            try:
                temp_path.write(core.Data(save_data))
            except Exception as e:
                color.ColoredText.localize(
                    "transfer_backup_fail", path=str(temp_path), error=e
                )
            else:
                if print:
                    color.ColoredText.localize("transfer_backup", path=str(temp_path))

        save_file = core.SaveFile(core.Data(save_data), cc=cc)

        password_refresh_token = resp_headers.get("Nyanko-Password-Refresh-Token")
        if password_refresh_token is not None:
            save_file.password_refresh_token = password_refresh_token

        server_handler = ServerHandler(save_file)
        password = resp_headers.get("Nyanko-Password")
        if password is not None:
            server_handler.save_password(password)

        return server_handler, RequestResult(url, response, headers, data_str)

    def update_managed_items(self) -> bool:
        auth_token = self.get_auth_token()
        if auth_token is None:
            return False
        data = {
            "catfoodAmount": self.save_file.catfood,
            "isPaid": True,
            "legendTicketAmount": self.save_file.legend_tickets,
            "nonce": core.Random.get_hex_string(32),
            "platinumTicketAmount": self.save_file.platinum_tickets,
            "rareTicketAmount": self.save_file.rare_tickets,
        }
        data_str = (
            core.JsonFile.from_object(data)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
        url = f"{self.managed_item_url}/v1/managed-items"
        headers = core.AccountHeaders(self.save_file, data_str).get_headers()
        headers["authorization"] = "Bearer " + auth_token
        response = core.RequestHandler(url, headers, core.Data(data_str)).post()
        if response is None:
            self.log_no_internet(RequestResult(url, None, headers, data_str))
            return False
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return False

        core.BackupMetaData(self.save_file).remove_managed_items()
        return True

    def download_event_data(self, filename: str) -> core.Data | None:
        url = (
            self.events_url
            + f"/battlecats{self.save_file.cc.get_patching_code()}_production/{filename}"
        )

        auth_token = self.get_auth_token()

        if auth_token is None:
            return None

        url += f"?jwt={auth_token}"

        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; Pixel 2 Build/PQ3A.190801.002)",
        }

        resp = core.RequestHandler(url, headers).get()

        if resp is None:
            return None

        return core.Data(resp.content)

    def download_gatya_data(self) -> core.Data | None:
        return self.download_event_data("gatya.tsv")

    def download_item_data(self) -> core.Data | None:
        return self.download_event_data("item.tsv")

    def download_sale_data(self) -> core.Data | None:
        return self.download_event_data("sale.tsv")
