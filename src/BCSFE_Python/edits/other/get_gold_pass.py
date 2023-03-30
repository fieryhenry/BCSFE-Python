"""Handler for getting the gold pass"""

import datetime
import random
import time
from typing import Any
from ... import helper, user_input_handler


def remove_gold_pass_val(save_stats: dict[str, Any]) -> dict[str, Any]:
    """
    Remove the gold pass

    Args:
        save_stats (dict[str, Any]): The save stats

    Returns:
        dict[str, Any]: The save stats
    """

    gold_pass = save_stats["gold_pass"]

    gold_pass["officer_id"]["Value"] = 0xFFFFFFFF
    gold_pass["renewal_times"]["Value"] = 0
    gold_pass["start_date"] = 0
    gold_pass["expiry_date"] = 0
    gold_pass["unknown_2"][0] = 0
    gold_pass["unknown_2"][1] = 0

    gold_pass["start_date_2"] = 0
    gold_pass["expiry_date_2"] = 0
    gold_pass["unknown_3"] = 0
    gold_pass["flag_2"]["Value"] = 0
    gold_pass["expiry_date_3"] = 0

    gold_pass["unknown_4"]["Value"] = 0
    gold_pass["unknown_5"]["Value"] = 0
    gold_pass["unknown_6"]["Value"] = 0
    save_stats["gold_pass"] = gold_pass
    save_stats["login_bonuses"][5100] = 0

    return save_stats


def get_gold_pass_val(
    save_stats: dict[str, Any], total_days: int, officer_id: int
) -> dict[str, Any]:
    """
    Give the gold pass

    Args:
        save_stats (dict[str, Any]): The save stats
        total_days (int): The total days
        officer_id (int): The officer ID

    Returns:
        dict[str, Any]: The save stats
    """

    gold_pass = save_stats["gold_pass"]

    start_date = int(time.time())
    expiry_date = start_date + datetime.timedelta(days=total_days).total_seconds()
    expiry_date_2 = start_date + datetime.timedelta(days=total_days * 2).total_seconds()

    gold_pass["officer_id"]["Value"] = officer_id
    if gold_pass["renewal_times"]["Value"] == 0:
        gold_pass["renewal_times"]["Value"] = 1
    gold_pass["renewal_times"]["Value"] += 1
    gold_pass["start_date"] = start_date
    gold_pass["expiry_date"] = expiry_date
    gold_pass["unknown_2"][0] = expiry_date
    gold_pass["unknown_2"][1] = expiry_date_2

    gold_pass["start_date_2"] = start_date
    gold_pass["expiry_date_2"] = expiry_date_2
    gold_pass["unknown_3"] = start_date
    gold_pass["flag_2"]["Value"] = 2
    gold_pass["expiry_date_3"] = expiry_date

    gold_pass["unknown_4"]["Value"] = 0
    gold_pass["unknown_5"]["Value"] = 1
    gold_pass["unknown_6"]["Value"] = 0
    save_stats["gold_pass"] = gold_pass
    save_stats["login_bonuses"][5100] = 0

    return save_stats


def get_random_officer_id() -> int:
    """Get a random officer ID"""

    return random.randint(1, 2**16 - 1)


def get_gold_pass(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Give the gold pass"""

    officer_id = user_input_handler.colored_input(
        "Enter the &officer ID& you want (Press &enter& for a &random id&, and enter &-1& to &remove the gold pass&):"
    )
    if officer_id == "":
        officer_id = get_random_officer_id()
    elif officer_id == "-1":
        officer_id = -1
    else:
        officer_id = helper.check_int_max(officer_id)

    if officer_id is None:
        officer_id = 0

    if officer_id == -1:
        save_stats = remove_gold_pass_val(save_stats)
        helper.colored_text("Successfully removed the gold pass", helper.GREEN)
    else:
        helper.colored_text(f"Officer ID: &{officer_id}&", helper.GREEN, helper.WHITE)
        save_stats = get_gold_pass_val(save_stats, 30, officer_id)
        helper.colored_text("Successfully gave the gold pass", helper.GREEN)

    return save_stats
