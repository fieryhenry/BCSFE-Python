from __future__ import annotations
from typing import Any

from bcsfe import core
from bcsfe.cli import color, dialog_creator


class Mission:
    def __init__(
        self,
        clear_state: int | None = None,
        requirement: int | None = None,
        progress_type: int | None = None,
        gamatoto_value: int | None = None,
        nyancombo_value: int | None = None,
        user_rank_value: int | None = None,
        expiry_value: int | None = None,
        preparing_value: int | bool | None = None,
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
    def init() -> Mission:
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
    def deserialize(data: dict[str, Any]) -> Mission:
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
        preparing_values: dict[int, int | bool],
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
    def init() -> Missions:
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
    def read(stream: core.Data, gv: core.GameVersion) -> Missions:
        clear_states: dict[int, int] = stream.read_int_int_dict()
        requirements: dict[int, int] = stream.read_int_int_dict()
        progress_types: dict[int, int] = stream.read_int_int_dict()
        gamatoto_values: dict[int, int] = stream.read_int_int_dict()
        nyancombo_values: dict[int, int] = stream.read_int_int_dict()
        user_rank_values: dict[int, int] = stream.read_int_int_dict()
        expiry_values: dict[int, int] = stream.read_int_int_dict()
        preparing_values: dict[int, int | bool] = {}

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

    def write(self, stream: core.Data, gv: core.GameVersion):
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

    def read_weekly_missions(self, stream: core.Data):
        self.weekly_missions: dict[int, bool] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            self.weekly_missions[key] = stream.read_bool()

    def write_weekly_missions(self, stream: core.Data):
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

    @staticmethod
    def edit_missions(save_file: core.SaveFile):
        missions = save_file.missions

        names = core.core_data.get_mission_names(save_file)
        conditions = core.core_data.get_mission_conditions(save_file)
        if names.names is None or conditions.conditions is None:
            return
        options: list[str] = []
        mssion_ids: list[int] = []
        for mission_id, name in names.names.items():
            if mission_id in missions.clear_states:
                name = name.split("<br>")[0]
                condition = conditions.conditions.get(mission_id)
                if not condition:
                    continue
                name = name.replace("%d", str(condition.progress_count))
                if "%@" in name and len(condition.conditions_value) > 2:
                    name = name.replace(
                        "%@", str(condition.conditions_value[2])
                    )
                options.append(name)
                mssion_ids.append(mission_id)

        re_claim = dialog_creator.ChoiceInput.from_reduced(
            ["complete_reward", "complete_claim", "uncomplete"],
            dialog="select_mission_claim",
            single_choice=True,
        ).single_choice()
        if re_claim is None:
            return
        re_claim -= 1

        choices, _ = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="select_missions"
        ).multiple_choice(localized_options=False)
        if choices is None:
            return
        for choice in choices:
            mission_id = mssion_ids[choice]
            if re_claim == 0:
                missions.clear_states[mission_id] = 2
                condition = conditions.get_condition(mission_id)
                if condition is not None:
                    missions.requirements[mission_id] = condition.progress_count
            elif re_claim == 1:
                missions.clear_states[mission_id] = 4
                condition = conditions.get_condition(mission_id)
                if condition is not None:
                    missions.requirements[mission_id] = condition.progress_count
            elif re_claim == 2:
                missions.clear_states[mission_id] = 0
                if mission_id in missions.requirements:
                    missions.requirements[mission_id] = 0

        color.ColoredText.localize("missions_edited")


class MissionCondition:
    def __init__(
        self,
        mission_id: int,
        mission_type: int,
        conditions_type: int,
        progress_count: int,
        conditions_value: list[int],
    ):
        self.mission_id = mission_id
        self.mission_type = mission_type
        self.conditions_type = conditions_type
        self.progress_count = progress_count
        self.conditions_value = conditions_value


class MissionConditions:
    def __init__(self, save: core.SaveFile):
        self.save = save
        self.conditions = self.get_conditions()

    def get_conditions(self) -> dict[int, MissionCondition] | None:
        file_name = "Mission_Condition.csv"
        gdg = core.core_data.get_game_data_getter(self.save)
        file = gdg.download("DataLocal", file_name)
        if file is None:
            return None
        csv = core.CSV(file)
        conditions: dict[int, MissionCondition] = {}
        for row in csv:
            conditions[row[0].to_int()] = MissionCondition(
                row[0].to_int(),
                row[1].to_int(),
                row[2].to_int(),
                row[3].to_int(),
                row[4:].to_int_list(),
            )
        return conditions

    def get_condition(self, mission_id: int) -> MissionCondition | None:
        if self.conditions is None:
            return None
        return self.conditions.get(mission_id)


class MissionNames:
    def __init__(self, save: core.SaveFile):
        self.save = save
        self.names = self.get_names()

    def get_names(self) -> dict[int, str] | None:
        file_name = "Mission_Name.csv"
        gdg = core.core_data.get_game_data_getter(self.save)
        file = gdg.download("resLocal", file_name)
        if file is None:
            return None
        csv = core.CSV(
            file, delimiter=core.Delimeter.from_country_code_res(self.save.cc)
        )
        names: dict[int, str] = {}
        for row in csv:
            names[row[0].to_int()] = row[1].to_str()
        return names
