import helper
from edits.cats import upgrade_cats
types = ["Power", "Range", "Charge", "Efficiency", "Wallet", "Health", "Research", "Accounting", "Study", "Energy"]


def upgrade_blue_ids(save_stats, ids):
    save_stats["blue_upgrades"] = upgrade_cats.upgrade_handler(save_stats["blue_upgrades"], ids, "upgrade")
    save_stats = upgrade_cats.set_user_popups(save_stats)
    print("Successfully set special skills")
    return save_stats

def upgrade_blue(save_stats):
    levels = save_stats["blue_upgrades"]
    levels_removed = {"Base" : [levels["Base"][0]] + levels["Base"][2:], "Plus" : [levels["Plus"][0]] + levels["Plus"][2:]}

    levels_removed_formated = []
    for i in range(len(levels_removed["Base"])):
        levels_removed_formated.append(f"{levels_removed['Base'][i] +1}+{levels_removed['Plus'][i]}")

    print("What do you want to upgrade:")
    helper.create_list(types, extra_values=levels_removed_formated)

    total = len(types)+1
    ids = helper.coloured_text(f"{total}. &All at once&\nEnter a number from 1 to {total} (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    ids = helper.ls_int(ids, -1)
    new_ids = []
    for id in ids:
        if id > 0:
            id+=1
        new_ids.append(id)
    ids = new_ids
    save_stats = upgrade_blue_ids(save_stats, ids)    
    return save_stats