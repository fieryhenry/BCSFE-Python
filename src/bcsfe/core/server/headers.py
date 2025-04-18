from __future__ import annotations
import time
from bcsfe import core


class AccountHeaders:
    def __init__(self, save_file: core.SaveFile, data: str):
        self.save_file = save_file
        self.data = data

    def get_headers(self) -> dict[str, str]:
        return AccountHeaders.get_headers_static(
            self.save_file.inquiry_code, self.data
        )

    @staticmethod
    def get_headers_static(iq: str, data: str):
        return {
            "accept-enconding": "gzip",
            "connection": "keep-alive",
            "content-type": "application/json",
            "nyanko-signature": core.NyankoSignature(
                iq, data
            ).generate_signature(),
            "nyanko-timestamp": str(int(time.time())),
            "nyanko-signature-version": "1",
            "nyanko-signature-algorithm": "HMACSHA256",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; SM-G955F Build/N2G48B)",
        }
