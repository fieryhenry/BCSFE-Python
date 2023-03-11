"""Handler for editting trade progress to allow for unbannable rare tickets"""
from typing import Any

from ... import helper, item


def set_trade_progress_val(storage: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """Handler for editting trade progress to allow for unbannable rare tickets"""

    space = False
    for i in range(len(storage["types"])):
        storage_item = storage["types"][i]
        if storage_item == 0 or (storage["ids"][i] == 1 and storage_item == 2):
            storage["ids"][i] = 1
            storage["types"][i] = 2
            space = True
            break
    return storage, space


def set_trade_progress(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting trade progress to allow for unbannable rare tickets"""

    trade_progress = save_stats["trade_progress"]
    max_value = helper.clamp(299 - save_stats["rare_tickets"]["Value"], 0, 299)
    storage = save_stats["cat_storage"]
    tickets = item.IntItem(
        name="Rare Tickets",
        max_value=max_value,
        value=item.Int(save_stats["rare_tickets"]["Value"]),
    )
    tickets.edit()
    trade_progress["Value"] = tickets.get_value() * 5

    storage, has_space = set_trade_progress_val(storage)

    if not has_space:
        helper.colored_text("Your cat storage is full, please free 1 space!")
        return save_stats

    save_stats["cat_storage"] = storage
    save_stats["trade_progress"] = trade_progress
    helper.colored_text(
        'You now need to go into your storage and press &"Use all"& and then press &"Trade for Ticket"&'
    )

    return save_stats
