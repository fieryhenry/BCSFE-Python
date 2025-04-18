from __future__ import annotations
from dataclasses import dataclass

from bcsfe import core
from bcsfe.cli import color, dialog_creator


@dataclass
class PlayTime:
    frames: int

    @staticmethod
    def get_fps() -> int:
        return 30

    @property
    def seconds(self) -> int:
        return self.frames // self.get_fps()

    @property
    def minutes(self) -> int:
        return self.seconds // 60

    @property
    def hours(self) -> int:
        return self.minutes // 60

    @property
    def just_seconds(self) -> int:
        return self.seconds % 60

    @property
    def just_minutes(self) -> int:
        return self.minutes % 60

    @property
    def just_hours(self) -> int:
        return self.hours % 60

    @staticmethod
    def from_hours(hours: int) -> PlayTime:
        return PlayTime(hours * 60 * 60 * PlayTime.get_fps())

    @staticmethod
    def from_minutes(minutes: int) -> PlayTime:
        return PlayTime(minutes * 60 * PlayTime.get_fps())

    @staticmethod
    def from_seconds(seconds: int) -> PlayTime:
        return PlayTime(seconds * PlayTime.get_fps())

    @staticmethod
    def from_hours_mins_secs(
        hours: int, minutes: int, seconds: int
    ) -> PlayTime:
        return (
            PlayTime.from_hours(hours)
            + PlayTime.from_minutes(minutes)
            + PlayTime.from_seconds(seconds)
        )

    def __add__(self, other: PlayTime) -> PlayTime:
        return PlayTime(self.frames + other.frames)


def edit(save_file: core.SaveFile):
    play_time = PlayTime(save_file.officer_pass.play_time)
    color.ColoredText.localize(
        "playtime_current",
        hours=play_time.hours,
        minutes=play_time.just_minutes,
        seconds=play_time.just_seconds,
        frames=play_time.frames,
    )
    hours, _ = dialog_creator.IntInput().get_input("playtime_hours_prompt", {})
    if hours is None:
        return
    minutes, _ = dialog_creator.IntInput().get_input(
        "playtime_minutes_prompt", {}
    )
    if minutes is None:
        return
    seconds, _ = dialog_creator.IntInput().get_input(
        "playtime_seconds_prompt", {}
    )
    if seconds is None:
        return

    play_time = PlayTime.from_hours_mins_secs(hours, minutes, seconds)
    save_file.officer_pass.play_time = play_time.frames
    color.ColoredText.localize(
        "playtime_edited",
        hours=play_time.hours,
        minutes=play_time.just_minutes,
        seconds=play_time.just_seconds,
        frames=play_time.frames,
    )
