from __future__ import annotations

import requests

from bcsfe import core


class MultiPartFile:
    def __init__(self, content: bytes, content_type: str, filename: str | None = None):
        self.content = content
        self.content_type = content_type
        self.filename = filename


class MultipartForm:
    def __init__(self):
        self.data: dict[str, MultiPartFile] = {}

    def into_files(
        self,
    ) -> dict[str, tuple[str | None, bytes, str]]:
        out = {}
        for name, data in self.data.items():
            out[name] = (data.filename, data.content, data.content_type)

        return out

    def add_key(
        self, key: str, content: bytes, content_type: str, filename: str | None = None
    ):
        self.data[key] = MultiPartFile(content, content_type, filename)

    def get_all_type(self, content_type: str) -> str:
        data = ""
        for key, file in self.data.items():
            if file.content_type == content_type:
                content = file.content.decode("utf-8", errors="ignore")
                data += f"key: {key}, data: {content}\n"

        return data


class RequestHandler:
    """Handles HTTP requests."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: core.Data | None = None,
        form: MultipartForm | None = None,
    ):
        """Initializes a new instance of the RequestHandler class.

        Args:
            url (str): URL to request.
            headers (dict[str, str] | None, optional): Headers to send with the request. Defaults to None.
            data (core.Data | None, optional): Data to send with the request. Defaults to None.
        """
        if data is None:
            data = core.Data()
        self.url = url
        self.headers = headers
        self.data = data
        self.form = form

    def get(
        self,
        stream: bool = False,
        no_timeout: bool = False,
    ) -> requests.Response | None:
        """Sends a GET request.

        Returns:
            requests.Response: Response from the server.
        """
        try:
            return requests.get(
                self.url,
                headers=self.headers,
                timeout=(
                    None
                    if no_timeout
                    else core.core_data.config.get_int(
                        core.ConfigKey.MAX_REQUEST_TIMEOUT
                    )
                ),
                stream=stream,
                files=None if self.form is None else self.form.into_files(),
            )
        except requests.exceptions.ConnectionError:
            return None

    def post(self, no_timeout: bool = False) -> requests.Response | None:
        """Sends a POST request.

        Returns:
            requests.Response: Response from the server.
        """
        try:
            return requests.post(
                self.url,
                headers=self.headers,
                data=self.data.data,
                timeout=(
                    None
                    if no_timeout
                    else core.core_data.config.get_int(
                        core.ConfigKey.MAX_REQUEST_TIMEOUT
                    )
                ),
                files=None if self.form is None else self.form.into_files(),
            )
        except requests.exceptions.ConnectionError:
            return None
