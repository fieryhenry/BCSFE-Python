from typing import Any, Optional, Union

from bcsfe import core


class Mission:
    def __init__(
        self,
        clear_state: Optional[int] = None,
        requirement: Optional[int] = None,
        progress_type: Optional[int] = None,
        gamatoto_value: Optional[int] = None,
        nyancombo_value: Optional[int] = None,
        user_rank_value: Optional[int] = None,
        expiry_value: Optional[int] = None,
        preparing_value: Optional[Union[int, bool]] = None,
    ):
        self.clear_state = clear_state
        self.requirement = requirement
        self.progress_type = progress_type
        self.gamatoto_value = gamatoto_value
        self.nyancombo_value = nyancombo_value
        self.user_rank_value = user_rank_value
        self.expiry_value = expiry_value
        self.preparing_value = preparing_value

    @staticmethod
    def init() -> "Mission":
        return Mission(
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_state": self.clear_state,
            "requirement": self.requirement,
            "progress_type": self.progress_type,
            "gamatoto_value": self.gamatoto_value,
            "nyancombo_value": self.nyancombo_value,
            "user_rank_value": self.user_rank_value,
            "expiry_value": self.expiry_value,
            "preparing_value": self.preparing_value,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Mission":
        return Mission(
            data["clear_state"],
            data["requirement"],
            data["progress_type"],
            data["gamatoto_value"],
            data["nyancombo_value"],
            data["user_rank_value"],
            data["expiry_value"],
            data["preparing_value"],
        )

    def __repr__(self):
        return f"Mission({self.clear_state}, {self.requirement}, {self.progress_type}, {self.gamatoto_value}, {self.nyancombo_value}, {self.user_rank_value}, {self.expiry_value}, {self.preparing_value})"

    def __str__(self):
        return self.__repr__()


class Missions:
    def __init__(
        self,
        clear_states: dict[int, int],
        requirements: dict[int, int],
        progress_types: dict[int, int],
        gamatoto_values: dict[int, int],
        nyancombo_values: dict[int, int],
        user_rank_values: dict[int, int],
        expiry_values: dict[int, int],
        preparing_values: dict[int, Union[int, bool]],
    ):
        self.clear_states = clear_states
        self.requirements = requirements
        self.progress_types = progress_types
        self.gamatoto_values = gamatoto_values
        self.nyancombo_values = nyancombo_values
        self.user_rank_values = user_rank_values
        self.expiry_values = expiry_values
        self.preparing_values = preparing_values
        self.weekly_missions: dict[int, bool] = {}

    @staticmethod
    def init() -> "Missions":
        return Missions(
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
        )

    @staticmethod
    def read(stream: "core.Data", gv: "core.GameVersion") -> "Missions":
        clear_states: dict[int, int] = stream.read_int_int_dict()
        requirements: dict[int, int] = stream.read_int_int_dict()
        progress_types: dict[int, int] = stream.read_int_int_dict()
        gamatoto_values: dict[int, int] = stream.read_int_int_dict()
        nyancombo_values: dict[int, int] = stream.read_int_int_dict()
        user_rank_values: dict[int, int] = stream.read_int_int_dict()
        expiry_values: dict[int, int] = stream.read_int_int_dict()
        preparing_values: dict[int, Union[int, bool]] = {}

        for _ in range(stream.read_int()):
            key = stream.read_int()
            if gv < 90300:
                preparing_values[key] = stream.read_bool()
            else:
                preparing_values[key] = stream.read_int()

        return Missions(
            clear_states,
            requirements,
            progress_types,
            gamatoto_values,
            nyancombo_values,
            user_rank_values,
            expiry_values,
            preparing_values,
        )

    def write(self, stream: "core.Data", gv: "core.GameVersion"):
        stream.write_int_int_dict(self.clear_states)
        stream.write_int_int_dict(self.requirements)
        stream.write_int_int_dict(self.progress_types)
        stream.write_int_int_dict(self.gamatoto_values)
        stream.write_int_int_dict(self.nyancombo_values)
        stream.write_int_int_dict(self.user_rank_values)
        stream.write_int_int_dict(self.expiry_values)

        stream.write_int(len(self.preparing_values))
        for key, value in self.preparing_values.items():
            stream.write_int(key)
            if gv < 90300:
                stream.write_bool(bool(value))
            else:
                stream.write_int(int(value))

    def read_weekly_missions(self, stream: "core.Data"):
        self.weekly_missions: dict[int, bool] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            self.weekly_missions[key] = stream.read_bool()

    def write_weekly_missions(self, stream: "core.Data"):
        stream.write_int(len(self.weekly_missions))
        for key, value in self.weekly_missions.items():
            stream.write_int(key)
            stream.write_bool(value)

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_states": self.clear_states,
            "requirements": self.requirements,
            "progress_types": self.progress_types,
            "gamatoto_values": self.gamatoto_values,
            "nyancombo_values": self.nyancombo_values,
            "user_rank_values": self.user_rank_values,
            "expiry_values": self.expiry_values,
            "preparing_values": self.preparing_values,
            "weekly_missions": self.weekly_missions,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]):
        missions = Missions(
            data.get("clear_states", {}),
            data.get("requirements", {}),
            data.get("progress_types", {}),
            data.get("gamatoto_values", {}),
            data.get("nyancombo_values", {}),
            data.get("user_rank_values", {}),
            data.get("expiry_values", {}),
            data.get("preparing_values", {}),
        )
        missions.weekly_missions = data.get("weekly_missions", {})
        return missions

    def __repr__(self):
        return f"<Missions {self.serialize()}>"

    def __str__(self):
        return self.__repr__()
