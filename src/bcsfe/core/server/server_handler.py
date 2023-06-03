import time
from typing import Any, Optional
from bcsfe.core import io, crypto, server, request, country_code, game_version
import jwt


class ServerHandler:
    auth_url = "https://nyanko-auth.ponosgames.com"
    save_url = "https://nyanko-save.ponosgames.com"
    backups_url = "https://nyanko-backups.ponosgames.com"
    aws_url = "https://nyanko-service-data-prd.s3.amazonaws.com"
    managed_item_url = "https://nyanko-managed-item.ponosgames.com"

    def __init__(self, save_file: io.save.SaveFile):
        self.save_file = save_file
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

    def get_stored_password(self) -> Optional[str]:
        return self.save_file.get_string(ServerHandler.get_password_key())

    def remove_stored_password(self):
        self.save_file.remove_string(ServerHandler.get_password_key())

    def save_save_key_data(self, save_key: dict[str, Any]):
        self.save_file.store_dict(ServerHandler.get_save_key_key(), save_key)

    def get_stored_save_key_data(self) -> Optional[dict[str, Any]]:
        return self.save_file.get_dict(ServerHandler.get_save_key_key())

    def remove_stored_save_key_data(self):
        self.save_file.remove_dict(ServerHandler.get_save_key_key())

    def save_auth_token(self, auth_token: str):
        self.save_file.store_string(ServerHandler.get_auth_token_key(), auth_token)

    def get_stored_auth_token(self) -> Optional[str]:
        token = self.save_file.get_string(ServerHandler.get_auth_token_key())
        return token

    def remove_stored_auth_token(self):
        self.save_file.remove_string(ServerHandler.get_auth_token_key())

    def get_password_new(self) -> Optional[str]:
        url = f"{self.auth_url}/v1/users"
        data = {
            "accountCode": self.save_file.inquiry_code,
            "accountCreatedAt": int(self.save_file.account_created_timestamp),
            "nonce": crypto.Random.get_hex_string(32),
        }
        password = self.do_password_request(url, data)
        return password

    def do_password_request(self, url: str, dict_data: dict[str, Any]) -> Optional[str]:
        response = self.do_request(url, dict_data)
        if response is None:
            return None
        payload, timestamp = response
        password = payload.get("password", None)
        if password is None:
            self.remove_stored_password()
            return None
        password_refresh_token = payload.get("passwordRefreshToken", None)
        if password_refresh_token is None:
            self.remove_stored_password()
            return None
        account_code = payload.get("accountCode", None)

        self.save_file.password_refresh_token = password_refresh_token
        self.save_password(password)
        if account_code:
            self.save_file.inquiry_code = account_code
            if timestamp:
                self.save_file.account_created_timestamp = timestamp
            if not self.update_managed_items():
                return None

        return password

    def do_request(
        self, url: str, dict_data: dict[str, Any]
    ) -> Optional[tuple[dict[str, Any], Optional[int]]]:
        data = (
            io.json_file.JsonFile.from_object(dict_data)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
        headers = server.headers.AccountHeaders(self.save_file, data).get_headers()
        response = request.RequestHandler(url, headers, io.data.Data(data)).post()
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            return None

        timestamp = json.get("timestamp", None)

        payload = json.get("payload", {})
        return payload, timestamp

    def refresh_password(self) -> Optional[str]:
        url = f"{self.auth_url}/v1/user/password"
        data = {
            "accountCode": self.save_file.inquiry_code,
            "passwordRefreshToken": self.save_file.password_refresh_token,
            "nonce": crypto.Random.get_hex_string(32),
        }
        return self.do_password_request(url, data)

    def get_auth_token_new(self, password: str) -> Optional[str]:
        url = f"{self.auth_url}/v1/tokens"
        data = server.client_info.ClientInfo.from_save_file(
            self.save_file
        ).get_client_info()
        data["password"] = password
        data["accountCode"] = self.save_file.inquiry_code

        response = self.do_request(url, data)
        if response is None:
            return None
        payload, _ = response
        auth_token = payload.get("token", None)
        if auth_token is None:
            self.remove_stored_auth_token()
            return None
        self.save_auth_token(auth_token)
        return auth_token

    def get_password(self) -> Optional[str]:
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
        return self.get_password()

    def validate_auth_token(self, auth_token: str) -> bool:
        token = jwt.decode(
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

    def get_auth_token(self) -> Optional[str]:
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
        return None

    def get_save_key_new(self, auth_token: str) -> Optional[dict[str, Any]]:
        nonce = crypto.Random.get_hex_string(32)
        url = f"{self.save_url}/v2/save/key?nonce={nonce}"
        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "authorization": "Bearer " + auth_token,
            "nyanko-timestamp": str(int(time.time())),
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
        response = request.RequestHandler(url, headers).get()
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return None
        payload = json.get("payload", {})
        self.save_save_key_data(payload)
        return payload

    def get_save_key(self) -> Optional[dict[str, Any]]:
        save_key = self.get_stored_save_key_data()
        if save_key:
            return save_key
        auth_token = self.get_auth_token()
        if auth_token is None:
            return None
        save_key = self.get_stored_save_key_data()
        if save_key:
            return save_key
        save_key = self.get_save_key_new(auth_token)
        if save_key is not None:
            return save_key
        return None

    def get_upload_request_body(self, boundary: str) -> Optional[io.data.Data]:
        save_key = self.get_save_key()
        if save_key is None:
            return None
        save_data = self.save_file.to_data()
        body = io.data.Data()
        keys = [
            "key",
            "policy",
            "x-amz-signature",
            "x-amz-credential",
            "x-amz-algorithm",
            "x-amz-date",
            "x-amz-security-token",
        ]
        for key in keys:
            body.add_line(f"--{boundary}")
            body.add_line(f'Content-Disposition: form-data; name="{key}"')
            body.add_line("Content-Type: text/plain")
            body.add_line()
            body.add_line(save_key[key])

        body.add_line(f"--{boundary}")
        body.add_line(
            'Content-Disposition: form-data; name="file"; filename="file.sav"'
        )
        body.add_line("Content-Type: application/octet-stream")
        body.add_line()
        body.add_line(save_data)
        body.add_line(f"--{boundary}--")
        return body

    def upload_save_data(self) -> bool:
        boundary = (
            f"__-----------------------{crypto.Random.get_digits_string(9)}-2147483648"
        )

        body = self.get_upload_request_body(boundary)
        if body is None:
            return False
        url = f"{self.aws_url}/"
        headers = {
            "accept-encoding": "gzip",
            "connection": "keep-alive",
            "content-type": f"multipart/form-data; boundary={boundary}",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
        response = request.RequestHandler(url, headers, body).post()
        if response.status_code != 204:
            self.remove_stored_save_key_data()
            return False
        return True

    def get_codes(self) -> Optional[tuple[str, str]]:
        if not self.upload_save_data():
            return None
        auth_token = self.get_auth_token()
        if auth_token is None:
            return None
        meta_data = server.managed_item.BackupMetaData(self.save_file).create()

        url = f"{self.save_url}/v2/transfers"
        headers = server.headers.AccountHeaders(self.save_file, meta_data).get_headers()
        headers["authorization"] = "Bearer " + auth_token

        response = request.RequestHandler(url, headers, io.data.Data(meta_data)).post()
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return None
        payload = json.get("payload", {})
        transfer_code = payload.get("transferCode", None)
        confirmation_code = payload.get("pin", None)
        if transfer_code is None or confirmation_code is None:
            self.remove_stored_auth_token()
            return None

        return (transfer_code, confirmation_code)

    def upload_meta_data(self) -> bool:
        if not self.upload_save_data():
            return False
        auth_token = self.get_auth_token()
        if auth_token is None:
            return False
        meta_data = server.managed_item.BackupMetaData(self.save_file).create()

        url = f"{self.save_url}/v2/backups"
        headers = server.headers.AccountHeaders(self.save_file, meta_data).get_headers()
        headers["authorization"] = "Bearer " + auth_token

        response = request.RequestHandler(url, headers).post()
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return False
        return True

    def get_new_inquiry_code(self) -> str:
        url = f"{self.backups_url}/?action=createAccount&referenceId="

        response = request.RequestHandler(url).get()
        data = response.json()
        iq = data["accountId"]
        return iq

    def create_new_account(self) -> bool:
        self.save_file.inquiry_code = self.get_new_inquiry_code()
        self.remove_stored_auth_token()
        self.remove_stored_save_key_data()
        self.remove_stored_password()
        self.save_file.password_refresh_token = ""
        password = self.get_password()
        auth_token = self.get_auth_token()
        save_key_data = self.get_save_key()
        if password is None or auth_token is None or save_key_data is None:
            return False
        return True

    @staticmethod
    def from_codes(
        transfer_code: str,
        confirmation_code: str,
        cc: country_code.CountryCode,
        gv: game_version.GameVersion,
    ) -> Optional["ServerHandler"]:
        url = f"{ServerHandler.save_url}/v2/transfers/{transfer_code}/reception"
        data = server.client_info.ClientInfo(cc, gv).get_client_info()
        data["pin"] = confirmation_code
        data_str = (
            io.json_file.JsonFile.from_object(data)
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
        response = request.RequestHandler(url, headers, io.data.Data(data_str)).post()
        headers = response.headers
        content_type = headers.get("content-type", "")
        if content_type != "application/octet-stream":
            return None

        save_data = response.content
        save_file = io.save.SaveFile(io.data.Data(save_data))

        password_refresh_token = headers.get("Nyanko-Password-Refresh-Token")
        if password_refresh_token is None:
            return None
        save_file.password_refresh_token = password_refresh_token

        server_handler = ServerHandler(save_file)
        password = headers.get("Nyanko-Password")
        if password is None:
            return None
        server_handler.save_password(password)

        return server_handler

    def update_managed_items(self) -> bool:
        auth_token = self.get_auth_token()
        if auth_token is None:
            return False
        data = {
            "catfoodAmount": self.save_file.catfood,
            "isPaid": False,
            "legendTicketAmount": self.save_file.legend_tickets,
            "nonce": crypto.Random.get_hex_string(32),
            "platinumTicketAmount": self.save_file.platinum_tickets,
            "rareTicketAmount": self.save_file.rare_tickets,
        }
        data_str = (
            io.json_file.JsonFile.from_object(data)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
        url = f"{self.managed_item_url}/v1/managed-items"
        headers = server.headers.AccountHeaders(self.save_file, data_str).get_headers()
        headers["authorization"] = "Bearer " + auth_token
        response = request.RequestHandler(url, headers, io.data.Data(data_str)).post()
        json: dict[str, Any] = response.json()
        status_code = json.get("statusCode", 0)
        if status_code != 1:
            self.remove_stored_auth_token()
            return False
        return True
