"""Update, edit and parse item tracker"""

import json
from typing import Any

from . import config_manager, helper, managed_item


class TrackerItem:
    """Tracker item"""

    def __init__(
        self, value: int, managed_item_type: managed_item.ManagedItemType
    ) -> None:
        """Initialize the tracker item"""

        self.value = value
        self.managed_item_type = managed_item_type


class TrackerItems:
    """Tracker items"""

    def __init__(self, tracker_data: dict[str, int]) -> None:
        self.catfood = TrackerItem(
            tracker_data["catfood"], managed_item.ManagedItemType.CATFOOD
        )
        self.rare_ticket = TrackerItem(
            tracker_data["rareTicket"], managed_item.ManagedItemType.RARE_TICKET
        )
        self.platinum_ticket = TrackerItem(
            tracker_data["platinumTicket"], managed_item.ManagedItemType.PLATINUM_TICKET
        )
        self.legend_ticket = TrackerItem(
            tracker_data["legendTicket"], managed_item.ManagedItemType.LEGEND_TICKET
        )

    def to_dict(self):
        """Convert to dict"""

        return {
            "catfood": self.catfood.value,
            "rareTicket": self.rare_ticket.value,
            "platinumTicket": self.platinum_ticket.value,
            "legendTicket": self.legend_ticket.value,
        }


class Tracker:
    """ItemTracker"""

    def __init__(self):
        self.items = TrackerItems(self.read_tracker())

    def read_tracker(self) -> dict[str, int]:
        """Read the item tracker"""

        data = helper.read_file_string(helper.get_file("item_tracker.json"))
        return json.loads(data)

    def write_tracker(self):
        """Write the item tracker"""

        data = json.dumps(self.items.to_dict())
        helper.write_file_string(helper.get_file("item_tracker.json"), data)

    def update_tracker(self, amount: int, item_type: managed_item.ManagedItemType):
        """Update the item tracker"""

        self.items.__dict__[item_type.value].value += amount

        self.write_tracker()

    def set_tracker_current(self, save_stats: dict[str, Any]):
        """Set the current item tracker"""

        data = {
            "catfood": save_stats["cat_food"]["Value"],
            "rareTicket": save_stats["rare_tickets"]["Value"],
            "platinumTicket": save_stats["platinum_tickets"]["Value"],
            "legendTicket": save_stats["legend_tickets"]["Value"],
        }

        self.items = TrackerItems(data)
        self.write_tracker()

    def reset_tracker(self):
        """Reset the item tracker"""
        data = {
            "catfood": 0,
            "rareTicket": 0,
            "platinumTicket": 0,
            "legendTicket": 0,
        }

        self.items = TrackerItems(data)
        self.write_tracker()

    def has_data(self) -> bool:
        """Check if any of the items in the tracker are greater than 0"""

        if not config_manager.get_config_value_category("SERVER", "UPLOAD_METADATA"):
            return False

        for item in self.items.__dict__.values():
            if item.value > 0:
                return True
        return False

    def parse_tracker_managed(self) -> list[managed_item.ManagedItem]:
        """Parse the item tracker as managed items"""
        data = self.items.to_dict()
        items: list[managed_item.ManagedItem] = []
        for key, value in data.items():
            if value > 0:
                detail_type = managed_item.DetailType.GET
            elif value < 0:
                detail_type = managed_item.DetailType.USE
                value = abs(value)
            else:
                continue
            items.append(managed_item.ManagedItem(value, detail_type, managed_item.ManagedItemType(key)))
        return items
