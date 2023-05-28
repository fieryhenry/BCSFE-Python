import json
from typing import Any
from . import config_manager, managed_item, helper
import os


class ManagedItems:
    def __init__(self, managed_items: dict[managed_item.ManagedItemType, int]):
        self.managed_items = managed_items

    def to_dict(self) -> dict[str, int]:
        """Convert to dict"""

        return {
            item.value: self.managed_items[item]
            for item in managed_item.ManagedItemType
        }

    @staticmethod
    def from_dict(data: dict[str, int]) -> "ManagedItems":
        """Convert from dict"""

        managed_items = {
            managed_item.ManagedItemType(item): data[item] for item in data
        }
        return ManagedItems(managed_items)


class UserInfo:
    def __init__(self, inquiry_code: str):
        self.inquiry_code = inquiry_code
        self.read_user_info()

    def get_path(self) -> str:
        """Get the path to the user info"""

        app_data_folder = config_manager.get_app_data_folder()
        path = os.path.join(app_data_folder, "user_info", self.inquiry_code + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    def create_empty_user_info(self):
        managed_items = {item: 0 for item in managed_item.ManagedItemType}
        managed_items = ManagedItems(managed_items)
        data = {
            "managedItems": managed_items.to_dict(),
            "password": "",
            "authToken": "",
        }
        self.write_user_info(data)

    def read_user_info(self):
        if not os.path.exists(self.get_path()):
            self.create_empty_user_info()
        data = helper.read_file_string(self.get_path())
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.create_empty_user_info()
            data = helper.read_file_string(self.get_path())
            data = json.loads(data)
        self.managed_items = ManagedItems.from_dict(data["managedItems"])
        self.password = data["password"]
        self.auth_token = data["authToken"]

    def write_user_info(self, data: dict[str, Any]):
        helper.write_file_string(self.get_path(), json.dumps(data, indent=4))

    def save(self):
        data = {
            "managedItems": self.managed_items.to_dict(),
            "password": self.password,
            "authToken": self.auth_token,
        }
        self.write_user_info(data)

    def get_managed_items(self) -> ManagedItems:
        return self.managed_items

    def get_password(self) -> str:
        return self.password

    def get_auth_token(self) -> str:
        return self.auth_token

    def set_managed_items(self, managed_items: ManagedItems):
        self.managed_items = managed_items
        self.save()

    def set_password(self, password: str):
        self.password = password
        self.save()

    def set_auth_token(self, auth_token: str):
        self.auth_token = auth_token
        self.save()

    def clear_managed_items(self):
        self.managed_items = ManagedItems(
            {item: 0 for item in managed_item.ManagedItemType}
        )
        self.save()

    def get_managed_items_lst(self) -> list[managed_item.ManagedItem]:
        items: list[managed_item.ManagedItem] = []
        for item in self.managed_items.managed_items:
            value = self.managed_items.managed_items[item]
            if value > 0:
                detail_type = managed_item.DetailType.GET
            elif value < 0:
                detail_type = managed_item.DetailType.USE
                value = abs(value)
            else:
                continue
            items.append(managed_item.ManagedItem(value, detail_type, item))
        return items

    def has_managed_items(self) -> bool:
        for item in self.managed_items.managed_items:
            value = self.managed_items.managed_items[item]
            if value != 0:
                return True
        return False

    def update_item(self, item_type: managed_item.ManagedItemType, amount: int):
        self.managed_items.managed_items[item_type] += amount
        self.save()

    @staticmethod
    def clear_all_items():
        app_data_folder = config_manager.get_app_data_folder()
        path = os.path.join(app_data_folder, "user_info")
        os.makedirs(path, exist_ok=True)
        files = helper.get_files_in_dir(path)
        for file in files:
            if file.endswith(".json"):
                info = UserInfo(file.replace(".json", ""))
                info.clear_managed_items()
