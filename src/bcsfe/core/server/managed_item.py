from __future__ import annotations

"""ManagedItem class for bcsfe."""

from enum import Enum
from typing import Any
import uuid
import time
from bcsfe import core


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
        self,
        amount: int,
        detail_type: DetailType,
        managed_item_type: ManagedItemType,
        detail_code: str = "",
        detail_created_at: int = 0,
    ):
        self.amount = amount
        self.detail_type = detail_type
        self.managed_item_type = managed_item_type
        if not detail_code:
            detail_code = str(uuid.uuid4())
        self.detail_code = detail_code
        if not detail_created_at:
            detail_created_at = int(time.time())
        self.detail_created_at = detail_created_at

    @staticmethod
    def from_change(
        change: int, managed_item_type: ManagedItemType
    ) -> ManagedItem:
        """Create a managed item from a change."""
        if change > 0:
            detail_type = DetailType.GET
        else:
            detail_type = DetailType.USE
        managed_item = ManagedItem(abs(change), detail_type, managed_item_type)
        return managed_item

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

        return f"{self.amount}_{self.detail_created_at}_{self.managed_item_type.value}_{self.detail_type.value}"

    @staticmethod
    def from_short_form(short_form: str) -> ManagedItem:
        values = short_form.split("_")
        try:
            amount = int(values[0])
        except (IndexError, ValueError):
            amount = 0

        try:
            detail_created_at = int(values[1])
        except (IndexError, ValueError):
            detail_created_at = 0

        try:
            managed_item_type = values[2]
        except IndexError:
            managed_item_type = ManagedItemType.CATFOOD.value

        try:
            detail_type = values[3]
        except IndexError:
            detail_type = DetailType.GET.value

        return ManagedItem(
            amount,
            DetailType(detail_type),
            ManagedItemType(managed_item_type),
            detail_created_at=detail_created_at,
        )

    def __str__(self) -> str:
        return f"{self.amount} {self.managed_item_type.value} ({self.detail_type.value})"

    def __repr__(self) -> str:
        return f"{self.amount} {self.managed_item_type.value} ({self.detail_type.value})"


class BackupMetaData:
    def __init__(
        self,
        save_file: core.SaveFile,
    ):
        self.save_file = save_file
        self.identifier = "managed_items"

    def set_managed_items(self, managed_items: list[ManagedItem]):
        self.save_file.remove_strings(self.identifier)
        for managed_item in managed_items:
            string = managed_item.to_short_form()
            self.save_file.store_string(
                self.identifier, string, overwrite=False
            )

    def get_managed_items(self) -> list[ManagedItem]:
        managed_items: list[ManagedItem] = []
        managed_items_str = self.save_file.get_strings(self.identifier)
        for managed_item_str in managed_items_str:
            managed_item = ManagedItem.from_short_form(managed_item_str)
            if managed_item.amount == 0:
                continue
            managed_items.append(managed_item)
        return managed_items

    def add_managed_item(self, managed_item: ManagedItem):
        if managed_item.amount == 0:
            return
        managed_items = self.get_managed_items()
        managed_items.append(managed_item)
        self.set_managed_items(managed_items)

    def remove_managed_items(self) -> None:
        self.save_file.remove_strings(self.identifier)

    def create(
        self, save_key: str | None = None, add_managed_items: bool = True
    ) -> str:
        """Create the backup metadata."""

        return BackupMetaData.create_static(
            self.save_file.inquiry_code,
            self.save_file.officer_pass.play_time,
            self.save_file.calculate_user_rank(),
            self.get_managed_items(),
            save_key,
            add_managed_items,
        )

    @staticmethod
    def create_static(
        iq: str,
        playtime: int,
        userrank: int,
        items: list[ManagedItem],
        save_key: str | None = None,
        add_managed_items: bool = True,
    ):
        managed_items: list[dict[str, Any]] = []
        if add_managed_items:
            for managed_item in items:
                if managed_item.amount == 0:
                    continue
                managed_items.append(managed_item.to_dict())

        managed_items_json = core.JsonFile.from_object(managed_items)
        managed_items_str = (
            managed_items_json.to_data(indent=None).to_str().replace(" ", "")
        )

        backup_metadata: dict[str, Any] = {
            "managedItemDetails": managed_items,
            "nonce": core.Random.get_hex_string(32),
            "playTime": playtime,
            "rank": userrank,
            "receiptLogIds": [],
            "signature_v1": core.NyankoSignature(
                iq, managed_items_str
            ).generate_signature_v1(),
        }
        if save_key is not None:
            backup_metadata["saveKey"] = save_key
        return (
            core.JsonFile.from_object(backup_metadata)
            .to_data(indent=None)
            .to_str()
            .replace(" ", "")
        )
