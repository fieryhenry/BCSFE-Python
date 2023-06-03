from typing import Any
from bcsfe.core import io


class Helper:
    def __init__(self, id: int):
        self.id = id

    @staticmethod
    def read(stream: io.data.Data) -> "Helper":
        id = stream.read_int()
        return Helper(id)

    def write(self, stream: io.data.Data):
        stream.write_int(self.id)

    def serialize(self) -> dict[str, Any]:
        return {"id": self.id}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Helper":
        return Helper(data["id"])

    def __repr__(self) -> str:
        return f"Helper(id={self.id!r})"

    def __str__(self) -> str:
        return f"Helper(id={self.id!r})"

    def is_valid(self) -> bool:
        return self.id != -1


class Helpers:
    def __init__(self, helpers: list[Helper]):
        self.helpers = helpers

    @staticmethod
    def read(stream: io.data.Data) -> "Helpers":
        total = stream.read_int()
        helpers: list[Helper] = []
        for _ in range(total):
            helpers.append(Helper.read(stream))
        return Helpers(helpers)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.helpers))
        for helper in self.helpers:
            helper.write(stream)

    def serialize(self) -> dict[str, list[dict[str, Any]]]:
        return {"helpers": [helper.serialize() for helper in self.helpers]}

    @staticmethod
    def deserialize(data: dict[str, list[dict[str, Any]]]) -> "Helpers":
        return Helpers([Helper.deserialize(helper) for helper in data["helpers"]])

    def __repr__(self) -> str:
        return f"Helpers(helpers={self.helpers!r})"

    def __str__(self) -> str:
        return f"Helpers(helpers={self.helpers!r})"


class Gamatoto:
    def __init__(
        self,
        remaining_seconds: float,
        return_flag: bool,
        xp: int,
        dest_id: int,
        recon_length: int,
        unknown: int,
        notif_value: int,
    ):
        self.remaining_seconds = remaining_seconds
        self.return_flag = return_flag
        self.xp = xp
        self.dest_id = dest_id
        self.recon_length = recon_length
        self.unknown = unknown
        self.notif_value = notif_value

    @staticmethod
    def read(stream: io.data.Data) -> "Gamatoto":
        remaining_seconds = stream.read_double()
        return_flag = stream.read_bool()
        xp = stream.read_int()
        dest_id = stream.read_int()
        recon_length = stream.read_int()
        unknown = stream.read_int()
        notif_value = stream.read_int()
        return Gamatoto(
            remaining_seconds,
            return_flag,
            xp,
            dest_id,
            recon_length,
            unknown,
            notif_value,
        )

    def write(self, stream: io.data.Data):
        stream.write_double(self.remaining_seconds)
        stream.write_bool(self.return_flag)
        stream.write_int(self.xp)
        stream.write_int(self.dest_id)
        stream.write_int(self.recon_length)
        stream.write_int(self.unknown)
        stream.write_int(self.notif_value)

    def read_2(self, stream: io.data.Data):
        self.helpers = Helpers.read(stream)
        self.is_ad_present = stream.read_bool()

    def write_2(self, stream: io.data.Data):
        self.helpers.write(stream)
        stream.write_bool(self.is_ad_present)

    def read_skin(self, stream: io.data.Data):
        self.skin = stream.read_int()

    def write_skin(self, stream: io.data.Data):
        stream.write_int(self.skin)

    def read_collab_data(self, stream: io.data.Data):
        self.collab_flags: dict[int, bool] = stream.read_int_bool_dict()
        self.collab_durations: dict[int, float] = stream.read_int_double_dict()

    def write_collab_data(self, stream: io.data.Data):
        stream.write_int_bool_dict(self.collab_flags)
        stream.write_int_double_dict(self.collab_durations)

    def serialize(self) -> dict[str, Any]:
        return {
            "remaining_seconds": self.remaining_seconds,
            "return_flag": self.return_flag,
            "xp": self.xp,
            "dest_id": self.dest_id,
            "recon_length": self.recon_length,
            "unknown": self.unknown,
            "notif_value": self.notif_value,
            "helpers": self.helpers.serialize(),
            "is_ad_present": self.is_ad_present,
            "skin": self.skin,
            "collab_flags": self.collab_flags,
            "collab_durations": self.collab_durations,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Gamatoto":
        gamatoto = Gamatoto(
            data["remaining_seconds"],
            data["return_flag"],
            data["xp"],
            data["dest_id"],
            data["recon_length"],
            data["unknown"],
            data["notif_value"],
        )
        gamatoto.helpers = Helpers.deserialize(data["helpers"])
        gamatoto.is_ad_present = data["is_ad_present"]
        gamatoto.skin = data["skin"]
        gamatoto.collab_flags = data["collab_flags"]
        gamatoto.collab_durations = data["collab_durations"]
        return gamatoto

    def __repr__(self):
        return (
            f"Gamatoto(remaining_seconds={self.remaining_seconds!r}, "
            f"return_flag={self.return_flag!r}, xp={self.xp!r}, "
            f"dest_id={self.dest_id!r}, recon_length={self.recon_length!r}, "
            f"unknown={self.unknown!r}, notif_value={self.notif_value!r}, "
            f"helpers={self.helpers!r}, is_ad_present={self.is_ad_present!r}, "
            f"skin={self.skin!r}, collab_flags={self.collab_flags!r}, "
            f"collab_durations={self.collab_durations!r})"
        )

    def __str__(self):
        return self.__repr__()
