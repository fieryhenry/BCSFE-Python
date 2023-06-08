from typing import Any
from bcsfe.core import io


class Medals:
    def __init__(
        self,
        u1: int,
        u2: int,
        u3: int,
        medal_data_1: list[int],
        medal_data_2: dict[int, int],
        ub: bool,
    ):
        self.u1 = u1
        self.u2 = u2
        self.u3 = u3
        self.medal_data_1 = medal_data_1
        self.medal_data_2 = medal_data_2
        self.ub = ub

    @staticmethod
    def read(data: io.data.Data) -> "Medals":
        u1 = data.read_int()
        u2 = data.read_int()
        u3 = data.read_int()
        total_medals = data.read_short()
        medal_data_1 = data.read_short_list(total_medals)
        total_medals = data.read_short()
        medal_data_2: dict[int, int] = {}
        for _ in range(total_medals):
            key = data.read_short()
            value = data.read_byte()
            medal_data_2[key] = value
        ub = data.read_bool()
        return Medals(u1, u2, u3, medal_data_1, medal_data_2, ub)

    def write(self, data: io.data.Data) -> None:
        data.write_int(self.u1)
        data.write_int(self.u2)
        data.write_int(self.u3)
        data.write_short(len(self.medal_data_1))
        data.write_short_list(self.medal_data_1, write_length=False)
        data.write_short(len(self.medal_data_2))
        for key, value in self.medal_data_2.items():
            data.write_short(key)
            data.write_byte(value)
        data.write_bool(self.ub)

    def serialize(self) -> dict[str, Any]:
        return {
            "u1": self.u1,
            "u2": self.u2,
            "u3": self.u3,
            "medal_data_1": self.medal_data_1,
            "medal_data_2": self.medal_data_2,
            "ub": self.ub,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Medals":
        return Medals(
            data.get("u1", 0),
            data.get("u2", 0),
            data.get("u3", 0),
            data.get("medal_data_1", []),
            data.get("medal_data_2", {}),
            data.get("ub", False),
        )

    def __repr__(self) -> str:
        return (
            f"Medals(u1={self.u1}, u2={self.u2}, u3={self.u3}, "
            f"medal_data_1={self.medal_data_1}, medal_data_2={self.medal_data_2}, "
            f"ub={self.ub})"
        )

    def __str__(self) -> str:
        return self.__repr__()
