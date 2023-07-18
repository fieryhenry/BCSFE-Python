from typing import Any, Callable, Optional

import requests

from bcsfe import core


class RequestHandler:
    """Handles HTTP requests."""

    def __init__(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        data: Optional["core.Data"] = None,
    ):
        """Initializes a new instance of the RequestHandler class.

        Args:
            url (str): URL to request.
            headers (Optional[dict[str, str]], optional): Headers to send with the request. Defaults to None.
            data (Optional[core.Data], optional): Data to send with the request. Defaults to None.
        """
        if data is None:
            data = core.Data()
        self.url = url
        self.headers = headers
        self.data = data
        self.config = core.Config()

    def get(self) -> requests.Response:
        """Sends a GET request.

        Returns:
            requests.Response: Response from the server.
        """
        return requests.get(
            self.url,
            headers=self.headers,
            timeout=self.config.get(core.ConfigKey.MAX_REQUEST_TIMEOUT),
        )

    def post(self) -> requests.Response:
        """Sends a POST request.

        Returns:
            requests.Response: Response from the server.
        """
        return requests.post(
            self.url,
            headers=self.headers,
            data=self.data.data,
            timeout=self.config.get(core.ConfigKey.MAX_REQUEST_TIMEOUT),
        )
