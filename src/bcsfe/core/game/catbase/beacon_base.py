from __future__ import annotations
from typing import Any
from bcsfe import core


class BeaconEventListScene:
    def __init__(
        self,
        int_dict: dict[int, int],
        str_dict: dict[int, list[str]],
        bool_dict: dict[int, bool],
    ):
        self.int_array = int_dict
        self.str_array = str_dict
        self.bool_array = bool_dict

    @staticmethod
    def init() -> BeaconEventListScene:
        return BeaconEventListScene({}, {}, {})

    @staticmethod
    def read(stream: core.Data) -> BeaconEventListScene:
        int_dict = {}
        str_dict = {}
        bool_dict = {}
        for _ in range(stream.read_int()):
            int_dict[stream.read_int()] = stream.read_int()
        for _ in range(stream.read_int()):
            str_dict[stream.read_int()] = stream.read_string_list()
        for _ in range(stream.read_int()):
            bool_dict[stream.read_int()] = stream.read_bool()
        return BeaconEventListScene(int_dict, str_dict, bool_dict)

    def write(self, stream: core.Data):
        stream.write_int(len(self.int_array))
        for key, value in self.int_array.items():
            stream.write_int(key)
            stream.write_int(value)
        stream.write_int(len(self.str_array))
        for key, value in self.str_array.items():
            stream.write_int(key)
            stream.write_string_list(value)
        stream.write_int(len(self.bool_array))
        for key, value in self.bool_array.items():
            stream.write_int(key)
            stream.write_bool(value)

    def serialize(self) -> dict[str, Any]:
        return {
            "int_array": self.int_array,
            "str_array": self.str_array,
            "bool_array": self.bool_array,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> BeaconEventListScene:
        return BeaconEventListScene(
            data.get("int_array", []),
            data.get("str_array", []),
            data.get("bool_array", []),
        )

    def __repr__(self):
        return f"BeaconEventListScene({self.int_array}, {self.str_array}, {self.bool_array})"

    def __str__(self):
        return f"BeaconEventListScene({self.int_array}, {self.str_array}, {self.bool_array})"
