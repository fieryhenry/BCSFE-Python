"""Handler for getting the gold pass"""

import datetime
import time
from typing import Any
from ... import helper


def get_gold_pass_val(save_stats: dict[str, Any], total_days: int) -> dict[str, Any]:
    """Give the gold pass"""

    gold_pass = save_stats["gold_pass"]

    start_date = int(time.time())
    expiry_date = start_date + datetime.timedelta(days=total_days).total_seconds()
    expiry_date_2 = start_date + datetime.timedelta(days=total_days * 2).total_seconds()

    gold_pass["officer_id"]["Value"] = 1
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

def get_gold_pass(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Give the gold pass"""

    save_stats = get_gold_pass_val(save_stats, 30)

    helper.colored_text("Successfully gave the gold pass", helper.GREEN)

    return save_stats
