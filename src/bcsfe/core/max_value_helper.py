from __future__ import annotations
from typing import Any
from bcsfe import core


class MaxValueHelper:
    def __init__(self):
        self.max_value_data = self.get_max_value_data()

    def get_max_value_data(self) -> dict[str, Any]:
        file_path = core.Path("max_values.json", True)
        if not file_path.exists():
            return {}
        try:
            return core.JsonFile.from_data(file_path.read()).to_object()
        except core.JSONDecodeError:
            return {}

    def get(self, value_code: str) -> int:
        try:
            return int(self.max_value_data.get(value_code, 0))
        except ValueError:
            return 0

    def get_property(self, value_code: str, property: str) -> int:
        try:
            return int(self.max_value_data.get(value_code, {}).get(property, 0))
        except ValueError:
            return 0

    def get_old(self, value_code: str) -> int:
        return self.get_property(value_code, "old")

    def get_new(self, value_code: str) -> int:
        return self.get_property(value_code, "new")
