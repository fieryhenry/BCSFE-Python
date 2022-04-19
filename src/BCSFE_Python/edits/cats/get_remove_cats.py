from BCSFE_Python import helper


def get_cat(save_stats):
    return cat_handler(save_stats, 1, "gave")

def remove_cats(save_stats):
    return cat_handler(save_stats, 0, "removed")

def cat_handler(save_stats, val, str):
    cats = save_stats["cats"]
    ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), len(cats))
    for i in range(len(ids)):
        cats[ids[i]] = val
    save_stats["cats"] = cats
    print(f"Successfully {str} cats")
    return save_stats