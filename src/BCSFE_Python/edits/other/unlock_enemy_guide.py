import helper

def enemy_guide(save_stats):
    enemy_guide = save_stats["enemy_guide"]
    total = len(enemy_guide)

    ids = helper.get_range_input(helper.coloured_text("Enter enemy ids (Look up enemy release order battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), total)
    
    for i in range(len(ids)):
        enemy_guide[ids[i]] = 1
    save_stats["enemy_guide"] = enemy_guide
    print("Successfully unlocked enemy guide")
    return save_stats