"""ManagedItem class for the BCSFE editor."""

from enum import Enum
from typing import Any
import uuid
from . import server_handler


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
        self.detail_created_at = server_handler.get_current_time() - 109600

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

