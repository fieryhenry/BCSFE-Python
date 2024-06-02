from __future__ import annotations
from typing import Any
from bcsfe import core


class StampData:
    def __init__(
        self,
        current_stamp: int,
        collected_stamp: list[int],
        unknown: int,
        daily_reward: int,
    ):
        self.current_stamp = current_stamp
        self.collected_stamp = collected_stamp
        self.unknown = unknown
        self.daily_reward = daily_reward

    @staticmethod
    def init() -> StampData:
        return StampData(0, [0] * 30, 0, 0)

    @staticmethod
    def read(stream: core.Data) -> StampData:
        current_stamp = stream.read_int()
        collected_stamp = stream.read_int_list(30)
        unknown = stream.read_int()
        daily_reward = stream.read_int()
        return StampData(current_stamp, collected_stamp, unknown, daily_reward)

    def write(self, stream: core.Data):
        stream.write_int(self.current_stamp)
        stream.write_int_list(self.collected_stamp, write_length=False)
        stream.write_int(self.unknown)
        stream.write_int(self.daily_reward)

    def serialize(self) -> dict[str, Any]:
        return {
            "current_stamp": self.current_stamp,
            "collected_stamp": self.collected_stamp,
            "unknown": self.unknown,
            "daily_reward": self.daily_reward,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> StampData:
        return StampData(
            data.get("current_stamp", 0),
            data.get("collected_stamp", []),
            data.get("unknown", 0),
            data.get("daily_reward", 0),
        )

    def __repr__(self):
        return f"StampData({self.current_stamp}, {self.collected_stamp}, {self.unknown}, {self.daily_reward})"

    def __str__(self):
        return f"StampData({self.current_stamp}, {self.collected_stamp}, {self.unknown}, {self.daily_reward})"
