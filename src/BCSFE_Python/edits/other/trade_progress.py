"""Handler for editting trade progress to allow for unbannable rare tickets"""

from ... import helper, item


def set_trade_progress(save_stats: dict) -> dict:
    """Handler for editting trade progress to allow for unbannable rare tickets"""

    trade_progress = save_stats["trade_progress"]
    storage = save_stats["cat_storage"]
    tickets = item.Item(
        name="Rare Tickets",
        max_value=299,
        value=save_stats["rare_tickets"]["Value"],
        edit_name="amount",
        set_name="gain",
    )
    tickets.edit()
    trade_progress["Value"] = tickets.value * 5

    space = False

    for i in range(len(storage["types"])):
        storage_item = storage["types"][i]
        if storage_item == 0:
            storage["ids"][i] = 1
            storage["types"][i] = 2
            space = True
            break
    if not space:
        helper.colored_text("Your cat storage is full, please free 1 space!")
        return save_stats

    save_stats["cat_storage"] = storage
    save_stats["trade_progress"] = trade_progress
    helper.colored_text(
        'You now need to go into your storage and press &"Use all"& and then press &"Trade for Ticket"&'
    )

    return save_stats
