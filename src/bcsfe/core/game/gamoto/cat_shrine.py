from typing import Any
from bcsfe.core import io


class CatShrine:
    def __init__(
        self,
        unknown: bool,
        stamp_1: float,
        stamp_2: float,
        shrine_gone: bool,
        flags: list[int],
        xp_offering: int,
    ):
        self.unknown = unknown
        self.stamp_1 = stamp_1
        self.stamp_2 = stamp_2
        self.shrine_gone = shrine_gone
        self.flags = flags
        self.xp_offering = xp_offering
        self.dialogs = 0

    @staticmethod
    def read(stream: io.data.Data) -> "CatShrine":
        unknown = stream.read_bool()
        stamp_1 = stream.read_double()
        stamp_2 = stream.read_double()
        shrine_gone = stream.read_bool()
        flags = stream.read_byte_list(length=stream.read_byte())
        xp_offering = stream.read_long()
        return CatShrine(unknown, stamp_1, stamp_2, shrine_gone, flags, xp_offering)

    def write(self, stream: io.data.Data):
        stream.write_bool(self.unknown)
        stream.write_double(self.stamp_1)
        stream.write_double(self.stamp_2)
        stream.write_bool(self.shrine_gone)
        stream.write_byte(len(self.flags))
        stream.write_byte_list(self.flags, write_length=False)
        stream.write_long(self.xp_offering)

    def read_dialogs(self, stream: io.data.Data):
        self.dialogs = stream.read_int()

    def write_dialogs(self, stream: io.data.Data):
        stream.write_int(self.dialogs)

    def serialize(self) -> dict[str, Any]:
        return {
            "unknown": self.unknown,
            "stamp_1": self.stamp_1,
            "stamp_2": self.stamp_2,
            "shrine_gone": self.shrine_gone,
            "flags": self.flags,
            "xp_offering": self.xp_offering,
            "dialogs": self.dialogs,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "CatShrine":
        shrine = CatShrine(
            data.get("unknown", False),
            data.get("stamp_1", 0.0),
            data.get("stamp_2", 0.0),
            data.get("shrine_gone", False),
            data.get("flags", []),
            data.get("xp_offering", 0),
        )
        shrine.dialogs = data.get("dialogs", 0)
        return shrine

    def __repr__(self):
        return (
            f"CatShrine("
            f"unknown={self.unknown}, "
            f"stamp_1={self.stamp_1}, "
            f"stamp_2={self.stamp_2}, "
            f"shrine_gone={self.shrine_gone}, "
            f"flags={self.flags}, "
            f"xp_offering={self.xp_offering}, "
            f"dialogs={self.dialogs}"
            f")"
        )

    def __str__(self):
        return self.__repr__()
