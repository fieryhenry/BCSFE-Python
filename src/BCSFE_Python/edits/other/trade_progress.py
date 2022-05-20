import helper

def set_trade_progress(save_stats):
    trade_progress = save_stats["trade_progress"]
    storage = save_stats["cat_storage"]
    tickets = helper.edit_item(save_stats["rare_tickets"], 299, "Rare Tickets", custom_text=["You currently have a rare ticket amount of: ", "Enter the amount of tickets you want to &gain& "])
    trade_progress["Value"] = tickets["Value"] * 5

    space = False

    for i in range(len(storage["types"])):
        item = storage["types"][i]
        if item == 0:
            storage["ids"][i] = 1
            storage["types"][i] = 2
            space = True
            break
    if not space:
        helper.coloured_text("Your cat storage is full, please free 1 space!")
        return save_stats

    save_stats["cat_storage"] = storage
    save_stats["trade_progress"] = trade_progress
    helper.coloured_text("You now need to go into your storage and press &\"Use all\"& and then press &\"Trade for Ticket\"&")

    return save_stats