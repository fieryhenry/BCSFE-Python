from __future__ import annotations

import requests

from bcsfe import core


class RequestHandler:
    """Handles HTTP requests."""

    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: core.Data | None = None,
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

    def get(self, stream: bool = False) -> requests.Response | None:
        """Sends a GET request.

        Returns:
            requests.Response: Response from the server.
        """
        try:
            return requests.get(
                self.url,
                headers=self.headers,
                timeout=core.core_data.config.get_int(
                    core.ConfigKey.MAX_REQUEST_TIMEOUT
                ),
                stream=stream,
            )
        except requests.exceptions.ConnectionError:
            return None

    def post(self) -> requests.Response | None:
        """Sends a POST request.

        Returns:
            requests.Response: Response from the server.
        """
        try:
            return requests.post(
                self.url,
                headers=self.headers,
                data=self.data.data,
                timeout=core.core_data.config.get_int(
                    core.ConfigKey.MAX_REQUEST_TIMEOUT
                ),
            )
        except requests.exceptions.ConnectionError:
            return None
