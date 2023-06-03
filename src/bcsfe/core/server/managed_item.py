"""ManagedItem class for bcsfe."""

from enum import Enum
from typing import Any
import uuid
import time
from bcsfe.core import io, crypto, server


class DetailType(Enum):
    """Enum for the different types of details."""

    GET = "get"
    USE = "use"


class ManagedItemType(Enum):
    """Enum for the different types of managed items."""

    CATFOOD = "catfood"
    RARE_TICKET = "rareTicket"
    PLATINUM_TICKET = "platinumTicket"
    LEGEND_TICKET = "legendTicket"


class ManagedItem:
    """Managed item for backupmetadata"""

    def __init__(
        self, amount: int, detail_type: DetailType, managed_item_type: ManagedItemType
    ):
        self.amount = amount
        self.detail_type = detail_type
        self.managed_item_type = managed_item_type
        self.detail_code = str(uuid.uuid4())
        self.detail_created_at = int(time.time())

    def to_dict(self) -> dict[str, Any]:
        """Convert the managed item to a dictionary."""

        data = {
            "amount": self.amount,
            "detailCode": self.detail_code,
            "detailCreatedAt": self.detail_created_at,
            "detailType": self.detail_type.value,
            "managedItemType": self.managed_item_type.value,
        }
        return data

    def to_short_form(self) -> str:
        """Convert the managed item to a short form."""

        return f"{self.amount}_{self.detail_type.value}_{self.managed_item_type.value}"

    @staticmethod
    def from_short_form(short_form: str) -> "ManagedItem":
        amount, detail_type, managed_item_type = short_form.split("_")
        amount = int(amount)
        detail_type = DetailType(detail_type)
        managed_item_type = ManagedItemType(managed_item_type)
        managed_item = ManagedItem(amount, detail_type, managed_item_type)
        return managed_item


class BackupMetaData:
    def __init__(
        self,
        save_file: io.save.SaveFile,
    ):
        self.save_file = save_file
        self.identifier = "managed_items"

    def set_managed_items(self, managed_items: list[ManagedItem]):
        self.save_file.remove_strings(self.identifier)
        for managed_item in managed_items:
            string = managed_item.to_short_form()
            self.save_file.store_string(self.identifier, string, overwrite=False)

    def get_managed_items(self) -> list[ManagedItem]:
        managed_items: list[ManagedItem] = []
        managed_items_str = self.save_file.get_strings(self.identifier)
        for managed_item_str in managed_items_str:
            managed_item = ManagedItem.from_short_form(managed_item_str)
            managed_items.append(managed_item)
        return managed_items

    def create(self) -> str:
        """Create the backup metadata."""

        managed_items: list[dict[str, Any]] = []
        for managed_item in self.get_managed_items():
            managed_items.append(managed_item.to_dict())

        managed_items_str = io.json_file.JsonFile.from_object(managed_items)
        managed_items_str = (
            managed_items_str.to_data(indent=None).to_str().replace(" ", "")
        )

        backup_metadata: dict[str, Any] = {
            "managedItemDetails": managed_items,
            "nonce": crypto.Random.get_hex_string(32),
            "playTime": self.save_file.officer_pass.play_time,
            "rank": self.save_file.calculate_user_rank(),
            "receiptLogIds": [],
            "signature_v1": crypto.NyankoSignature(
                self.save_file.inquiry_code, managed_items_str
            ).generate_signature_v1(),
        }
        save_key = server.server_handler.ServerHandler(self.save_file).get_save_key()
        if save_key is not None:
            backup_metadata["saveKey"] = save_key["key"]
        return (
            io.json_file.JsonFile.from_object(backup_metadata)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
