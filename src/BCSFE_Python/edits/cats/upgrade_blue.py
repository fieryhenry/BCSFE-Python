import helper
from edits.cats import upgrade_cats
types = ["Power", "Range", "Charge", "Efficiency", "Wallet", "Health", "Research", "Accounting", "Study", "Energy"]


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
    individual = True
    if str(total) in ids:
        ids = range(1, total)
        ids = [format(x, '02d') for x in ids]
        individual = False
    first = True
    base_lvl = None
    plus_lvl = None
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue
        id = helper.clamp(id, 1, 10)
        id -= 1

        if not individual and first:
            vals = upgrade_cats.get_plus_base(helper.coloured_text(f"Enter the base level followed by a \"&+&\" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n", is_input=True))
            base_lvl = vals[0]
            plus_lvl = vals[1]
            first = False
        elif individual:
            vals = upgrade_cats.get_plus_base(helper.coloured_text(f"Enter the base level for &{types[id]}& followed by a \"&+&\" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n", is_input=True))
            base_lvl = vals[0]
            plus_lvl = vals[1]
        
        if id > 0: id+=1
        if base_lvl != None:
            levels["Base"][id] = base_lvl -1
        if plus_lvl != None:
            levels["Plus"][id] = plus_lvl

    save_stats["blue_upgrades"] = levels
    print("Successfully set special skills")
    
    return save_stats