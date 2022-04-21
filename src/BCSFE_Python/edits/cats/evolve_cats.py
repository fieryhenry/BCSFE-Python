import helper

def get_evolve(save_stats):
    return evolve_handler(save_stats, 2, "set", False)

def get_evolve_forced(save_stats):
    return evolve_handler(save_stats, 2, "set", True)

def remove_evolve(save_stats):
    return evolve_handler(save_stats, 0, "removed", True)

def get_evolve_current(save_stats):
    cats = save_stats["cats"]
    current_cats = []
    for id in range(len(cats)):
        if cats[id] == 1:
            current_cats.append(id)
    return evolve_handler_ids(save_stats, 2, "set", current_cats, False)


def get_evolve_data():
    f = open(helper.get_files_path("game_data/true_forms/nyankoPictureBookData.csv"), "r").readlines()
    forms = []
    for line in f:
        if len(line.split(',')) < 3: break
        flag = int(line.split(",")[2])
        forms.append(flag - 1)
    return forms

def evolve_handler(save_stats, val, str, forced):
    evolves = save_stats["unlocked_forms"]
    flags = evolves
    ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), len(flags))
    return evolve_handler_ids(save_stats, val, str, ids, forced)

def evolve_handler_ids(save_stats, val, str, ids, forced):
    evolves = save_stats["unlocked_forms"]
    if not forced:
        form_data = get_evolve_data()
        length = min([len(ids), len(form_data)])
        for i in range(length):
            evolves[ids[i]] = form_data[i]
    else:
        for i in range(len(ids)):
            evolves[ids[i]] = val
    save_stats["current_forms"] = evolves

    flags_evolved = [0 if form==1 else form for form in evolves]
    save_stats["unlocked_forms"] = flags_evolved

    print(f"Successfully {str} true forms of cats")
    return save_stats