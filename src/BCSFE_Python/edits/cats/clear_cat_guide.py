import helper
from edits.cats import upgrade_cats

def clear_cat_guide(save_stats):
    cat_guide_collected = save_stats["cat_guide_collected"]
    total = len(cat_guide_collected)
    ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), total)
    save_stats = cat_guide_ids(save_stats, ids)
    return save_stats

def clear_cat_guide_rarity(save_stats):
    ids = helper.selection_list(upgrade_cats.types, "collect", True)
    cat_ids = upgrade_cats.get_rarity(ids)
    save_stats = cat_guide_ids(save_stats, cat_ids)
    return save_stats

def cat_guide_ids(save_stats, ids):
    cat_guide_collected = save_stats["cat_guide_collected"]
    for i in range(len(ids)):
        cat_guide_collected[ids[i]] = 1
    save_stats["cat_guide_collected"] = cat_guide_collected
    print("Successfully collected gat guide")
    return save_stats