import helper

def enemy_guide(save_stats):
    enemy_guide = save_stats["enemy_guide"]
    total = len(enemy_guide)
    unlock = helper.coloured_text("Do you want to remove enemy guide entries &(1)& or unlock them &(2)&:", is_input=True)
    set_val = 1
    if unlock == "1": set_val = 0
    ids = helper.get_range_input(helper.coloured_text("Enter enemy ids (Look up enemy release order battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), total)
    
    for i in range(len(ids)):
        id = ids[i]
        if id >= 2:
            id -= 2
        enemy_guide[id] = set_val
    save_stats["enemy_guide"] = enemy_guide
    if unlock == "1":
        print("Successfully removed enemy guide entries")
    else:
        print("Successfully unlocked enemy guide entries")
    return save_stats