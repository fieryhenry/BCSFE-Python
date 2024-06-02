from __future__ import annotations
from typing import Any
from bcsfe import core


class MySale:
    def __init__(self, dict_1: dict[int, int], dict_2: dict[int, bool]):
        self.dict_1 = dict_1
        self.dict_2 = dict_2

    @staticmethod
    def init() -> MySale:
        return MySale({}, {})

    @staticmethod
    def read_bonus_hash(stream: core.Data):
        variable_length = stream.read_variable_length_int()
        dict_1 = {}
        for _ in range(variable_length):
            key = stream.read_variable_length_int()
            value = stream.read_variable_length_int()
            dict_1[key] = value

        variable_length = stream.read_variable_length_int()
        dict_2 = {}
        for _ in range(variable_length):
            key = stream.read_variable_length_int()
            value = stream.read_byte()
            dict_2[key] = value

        return MySale(dict_1, dict_2)

    def write_bonus_hash(self, stream: core.Data):
        stream.write_variable_length_int(len(self.dict_1))
        for key, value in self.dict_1.items():
            stream.write_variable_length_int(key)
            stream.write_variable_length_int(value)

        stream.write_variable_length_int(len(self.dict_2))
        for key, value in self.dict_2.items():
            stream.write_variable_length_int(key)
            stream.write_byte(value)

    def serialize(self) -> dict[str, Any]:
        return {
            "dict_1": self.dict_1,
            "dict_2": self.dict_2,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> MySale:
        return MySale(data.get("dict_1", {}), data.get("dict_2", {}))

    def __repr__(self) -> str:
        return f"MySale(dict_1={self.dict_1}, dict_2={self.dict_2})"

    def __str__(self) -> str:
        return f"MySale(dict_1={self.dict_1}, dict_2={self.dict_2})"
