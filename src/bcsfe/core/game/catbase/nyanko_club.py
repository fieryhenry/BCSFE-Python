import datetime
import random
import time
from typing import Any, Optional

from bcsfe import core
from bcsfe.cli import dialog_creator, color


class NyankoClub:
    def __init__(
        self,
        officer_id: int,
        total_renewal_times: int,
        start_date: float,
        end_date: float,
        unknown_ts_1: float,
        unknown_ts_2: float,
        start_date_2: float,
        end_date_2: float,
        unknown_ts_3: float,
        flag: int,
        end_date_3: float,
        claimed_rewards: dict[int, int],
        unknown_ts_4: float,
        unknown_bool_1: bool,
        unknown_bool_2: Optional[bool] = None,
    ):
        self.officer_id = officer_id
        self.total_renewal_times = total_renewal_times
        self.start_date = start_date
        self.end_date = end_date
        self.unknown_ts_1 = unknown_ts_1
        self.unknown_ts_2 = unknown_ts_2
        self.start_date_2 = start_date_2
        self.end_date_2 = end_date_2
        self.unknown_ts_3 = unknown_ts_3
        self.flag = flag
        self.end_date_3 = end_date_3
        self.claimed_rewards = claimed_rewards
        self.unknown_ts_4 = unknown_ts_4
        self.unknown_bool_1 = unknown_bool_1
        self.unknown_bool_2 = unknown_bool_2

    @staticmethod
    def init() -> "NyankoClub":
        return NyankoClub(
            0,
            0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0,
            0.0,
            {},
            0.0,
            False,
            False,
        )

    @staticmethod
    def read(data: "core.Data", gv: "core.GameVersion") -> "NyankoClub":
        officer_id = data.read_int()
        total_renewal_times = data.read_int()
        start_date = data.read_double()
        end_date = data.read_double()
        unknown_ts_1 = data.read_double()
        unknown_ts_2 = data.read_double()
        start_date_2 = data.read_double()
        end_date_2 = data.read_double()
        unknown_ts_3 = data.read_double()
        flag = data.read_int()
        end_date_3 = data.read_double()
        claimed_rewards = data.read_int_int_dict()
        unknown_ts_4 = data.read_double()
        unknown_bool_1 = data.read_bool()
        if gv >= 80100:
            unknown_bool_2 = data.read_bool()
        else:
            unknown_bool_2 = None
        return NyankoClub(
            officer_id,
            total_renewal_times,
            start_date,
            end_date,
            unknown_ts_1,
            unknown_ts_2,
            start_date_2,
            end_date_2,
            unknown_ts_3,
            flag,
            end_date_3,
            claimed_rewards,
            unknown_ts_4,
            unknown_bool_1,
            unknown_bool_2,
        )

    def write(self, data: "core.Data", gv: "core.GameVersion"):
        data.write_int(self.officer_id)
        data.write_int(self.total_renewal_times)
        data.write_double(self.start_date)
        data.write_double(self.end_date)
        data.write_double(self.unknown_ts_1)
        data.write_double(self.unknown_ts_2)
        data.write_double(self.start_date_2)
        data.write_double(self.end_date_2)
        data.write_double(self.unknown_ts_3)
        data.write_int(self.flag)
        data.write_double(self.end_date_3)
        data.write_int_int_dict(self.claimed_rewards)
        data.write_double(self.unknown_ts_4)
        data.write_bool(self.unknown_bool_1)
        if gv >= 80100:
            data.write_bool(self.unknown_bool_2 or False)

    def serialize(self) -> dict[str, Any]:
        return {
            "officer_id": self.officer_id,
            "total_renewal_times": self.total_renewal_times,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "unknown_ts_1": self.unknown_ts_1,
            "unknown_ts_2": self.unknown_ts_2,
            "start_date_2": self.start_date_2,
            "end_date_2": self.end_date_2,
            "unknown_ts_3": self.unknown_ts_3,
            "flag": self.flag,
            "end_date_3": self.end_date_3,
            "claimed_rewards": self.claimed_rewards,
            "unknown_ts_4": self.unknown_ts_4,
            "unknown_bool_1": self.unknown_bool_1,
            "unknown_bool_2": self.unknown_bool_2,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "NyankoClub":
        return NyankoClub(
            data.get("officer_id", 0),
            data.get("total_renewal_times", 0),
            data.get("start_date", 0.0),
            data.get("end_date", 0.0),
            data.get("unknown_ts_1", 0.0),
            data.get("unknown_ts_2", 0.0),
            data.get("start_date_2", 0.0),
            data.get("end_date_2", 0.0),
            data.get("unknown_ts_3", 0.0),
            data.get("flag", 0),
            data.get("end_date_3", 0.0),
            data.get("claimed_rewards", {}),
            data.get("unknown_ts_4", 0.0),
            data.get("unknown_bool_1", False),
            data.get("unknown_bool_2", False),
        )

    def __repr__(self):
        return f"<NyankoClub {self.officer_id}>"

    def __str__(self):
        return f"NyankoClub {self.officer_id}"

    def get_gold_pass(
        self, officer_id: int, total_days: int, save_file: "core.SaveFile"
    ):
        self.officer_id = officer_id
        start_date = int(time.time())
        end_date = start_date + datetime.timedelta(days=total_days).total_seconds()
        end_date_2 = (
            start_date + datetime.timedelta(days=total_days * 2).total_seconds()
        )

        self.officer_id = officer_id
        self.total_renewal_times += 1
        self.total_renewal_times = max(2, self.total_renewal_times)
        self.start_date = start_date
        self.end_date = end_date

        self.unknown_ts_1 = end_date
        self.unknown_ts_2 = end_date_2

        self.start_date_2 = start_date
        self.end_date_2 = end_date_2

        self.unknown_ts_3 = start_date

        self.flag = 2

        self.end_date_3 = end_date

        self.unknown_ts_4 = 0.0
        self.unknown_bool_1 = True
        self.unknown_bool_2 = False

        login = save_file.logins.get_login(5100)
        if login is not None:
            login.count = 0

        self.claimed_rewards = {}

    def remove_gold_pass(self, save_file: "core.SaveFile"):
        self.officer_id = -1
        self.total_renewal_times = 0
        self.start_date = 0.0
        self.end_date = 0.0
        self.unknown_ts_1 = 0.0
        self.unknown_ts_2 = 0.0
        self.start_date_2 = 0.0
        self.end_date_2 = 0.0
        self.unknown_ts_3 = 0.0
        self.flag = 0
        self.end_date_3 = 0.0
        self.unknown_ts_4 = 0.0
        self.unknown_bool_1 = False
        self.unknown_bool_2 = False

        login = save_file.logins.get_login(5100)
        if login is not None:
            login.count = 0

        self.claimed_rewards = {}

    @staticmethod
    def get_random_officer_id() -> int:
        return random.randint(1, 2**16 - 1)

    @staticmethod
    def edit_gold_pass(save_file: "core.SaveFile"):
        club = save_file.officer_pass.gold_pass

        officer_id = color.ColoredInput().localize("gold_pass_dialog").strip()
        if not officer_id:
            officer_id = NyankoClub.get_random_officer_id()

        if officer_id == "-1":
            officer_id = -1
        else:
            try:
                officer_id = int(officer_id)
            except ValueError:
                officer_id = NyankoClub.get_random_officer_id()
            officer_id = dialog_creator.IntInput().clamp_value(officer_id)

        if officer_id == -1:
            club.remove_gold_pass(save_file)
            color.ColoredText.localize("gold_pass_remove_success")
        else:
            club.get_gold_pass(officer_id, 30, save_file)
            color.ColoredText.localize("gold_pass_get_success", id=officer_id)
