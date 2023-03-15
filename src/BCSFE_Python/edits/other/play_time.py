"""Handler for editting play time"""
from typing import Any

from ... import helper, user_input_handler


def edit_play_time(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting play time"""
    play_time = save_stats["play_time"]

    hours = play_time["hh"]
    minutes = play_time["mm"]

    helper.colored_text(
        f"You currently have a play time of: &{hours}& hours and &{minutes}& minutes"
    )
    hours = helper.check_int_max(
        user_input_handler.colored_input("How many hours do you want to set?:")
    )
    minutes = helper.check_int_max(
        user_input_handler.colored_input("How many minutes do you want to set?:")
    )
    if hours is None or minutes is None or hours < 0 or minutes < 0:
        print("Please enter valid numbers")
        return save_stats
    play_time["hh"] = hours
    play_time["mm"] = minutes

    save_stats["play_time"] = play_time

    print("Successfully set play time")
    return save_stats
