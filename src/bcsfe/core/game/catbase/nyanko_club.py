from __future__ import annotations
import datetime
import random
import time
from typing import Any

from bcsfe import core
from bcsfe.cli import dialog_creator, color


class NyankoClub:
    def __init__(
        self,
        officer_id: int,
        total_renewal_times: int,
        start_date_now: float,
        end_date_now: float,
        start_date_next: float,
        end_date_next: float,
        start_date_total: float,
        end_date_total: float,
        time_error_end: float,
        total_state_updates: int,
        login_bonus_date: float,
        claimed_rewards: dict[int, int],
        remaing_days_popup: float,
        first_popup_flag: bool,
        badge_flag: bool | None = None,
    ):
        self.officer_id = officer_id
        self.total_renewal_times = total_renewal_times
        self.start_date_now = start_date_now
        self.end_date_now = end_date_now
        self.start_date_next = start_date_next
        self.end_date_next = end_date_next
        self.start_date_total = start_date_total
        self.end_date_total = end_date_total
        self.time_error_end = time_error_end
        self.total_state_updates = total_state_updates
        self.login_bonus_date = login_bonus_date
        self.claimed_rewards = claimed_rewards
        self.remaing_days_popup = remaing_days_popup
        self.first_popup_flag = first_popup_flag
        self.badge_flag = badge_flag

    @staticmethod
    def init() -> NyankoClub:
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
    def read(data: core.Data, gv: core.GameVersion) -> NyankoClub:
        officer_id = data.read_int()
        total_renewal_times = data.read_int()
        start_date_now = data.read_double()
        end_date_now = data.read_double()
        start_date_next = data.read_double()
        end_date_next = data.read_double()
        start_date_total = data.read_double()
        end_date_total = data.read_double()
        time_error_end = data.read_double()
        total_state_updates = data.read_int()
        login_bonus_date = data.read_double()
        claimed_rewards = data.read_int_int_dict()
        remaing_days_popup = data.read_double()
        first_popup_flag = data.read_bool()
        if gv >= 80100:
            badge_flag = data.read_bool()
        else:
            badge_flag = None
        return NyankoClub(
            officer_id,
            total_renewal_times,
            start_date_now,
            end_date_now,
            start_date_next,
            end_date_next,
            start_date_total,
            end_date_total,
            time_error_end,
            total_state_updates,
            login_bonus_date,
            claimed_rewards,
            remaing_days_popup,
            first_popup_flag,
            badge_flag,
        )

    def write(self, data: core.Data, gv: core.GameVersion):
        data.write_int(self.officer_id)
        data.write_int(self.total_renewal_times)
        data.write_double(self.start_date_now)
        data.write_double(self.end_date_now)
        data.write_double(self.start_date_next)
        data.write_double(self.end_date_next)
        data.write_double(self.start_date_total)
        data.write_double(self.end_date_total)
        data.write_double(self.time_error_end)
        data.write_int(self.total_state_updates)
        data.write_double(self.login_bonus_date)
        data.write_int_int_dict(self.claimed_rewards)
        data.write_double(self.remaing_days_popup)
        data.write_bool(self.first_popup_flag)
        if gv >= 80100:
            data.write_bool(self.badge_flag or False)

    def serialize(self) -> dict[str, Any]:
        return {
            "officer_id": self.officer_id,
            "total_renewal_times": self.total_renewal_times,
            "start_date_now": self.start_date_now,
            "end_date_now": self.end_date_now,
            "start_date_next": self.start_date_next,
            "end_date_next": self.end_date_next,
            "start_date_total": self.start_date_total,
            "end_date_total": self.end_date_total,
            "time_error_end": self.time_error_end,
            "total_state_updates": self.total_state_updates,
            "login_bonus_date": self.login_bonus_date,
            "claimed_rewards": self.claimed_rewards,
            "remaing_days_popup": self.remaing_days_popup,
            "first_popup_flag": self.first_popup_flag,
            "badge_flag": self.badge_flag,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> NyankoClub:
        return NyankoClub(
            data.get("officer_id", 0),
            data.get("total_renewal_times", 0),
            data.get("start_date_now", 0.0),
            data.get("end_date_now", 0.0),
            data.get("start_date_next", 0.0),
            data.get("end_date_next", 0.0),
            data.get("start_date_total", 0.0),
            data.get("end_date_total", 0.0),
            data.get("time_error_end", 0.0),
            data.get("total_state_updates", 0),
            data.get("login_bonus_date", 0.0),
            data.get("claimed_rewards", {}),
            data.get("remaing_days_popup", 0.0),
            data.get("first_popup_flag", False),
            data.get("badge_flag", False),
        )

    def __repr__(self):
        return f"<NyankoClub {self.officer_id}>"

    def __str__(self):
        return f"NyankoClub {self.officer_id}"

    def get_gold_pass(
        self, officer_id: int, total_days: int, save_file: core.SaveFile
    ):
        self.officer_id = officer_id
        start_date_now = int(time.time())
        end_date_now = (
            start_date_now + datetime.timedelta(days=total_days).total_seconds()
        )
        end_date_total = (
            start_date_now
            + datetime.timedelta(days=total_days * 2).total_seconds()
        )

        self.total_renewal_times = 2
        self.start_date_now = start_date_now
        self.end_date_now = end_date_now

        self.start_date_next = end_date_now
        self.end_date_next = end_date_total

        self.start_date_total = start_date_now
        self.end_date_total = end_date_total

        self.time_error_end = start_date_now

        self.total_state_updates = 2

        self.login_bonus_date = end_date_now

        self.remaing_days_popup = 0.0
        self.first_popup_flag = True
        self.badge_flag = False

        login = save_file.logins.get_login(5100)
        if login is not None:
            login.count = 0

        self.claimed_rewards = {}

    def remove_gold_pass(self, save_file: core.SaveFile):
        self.officer_id = -1
        self.total_renewal_times = 0
        self.start_date_now = 0.0
        self.end_date_now = 0.0
        self.start_date_next = 0.0
        self.end_date_next = 0.0
        self.start_date_total = 0.0
        self.end_date_total = 0.0
        self.time_error_end = 0.0
        self.total_state_updates = 0
        self.login_bonus_date = 0.0
        self.remaing_days_popup = 0.0
        self.first_popup_flag = False
        self.badge_flag = False

        login = save_file.logins.get_login(5100)
        if login is not None:
            login.count = 0

        self.claimed_rewards = {}

    @staticmethod
    def get_random_officer_id() -> int:
        return random.randint(1, 2**16 - 1)

    @staticmethod
    def edit_gold_pass(save_file: core.SaveFile):
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
