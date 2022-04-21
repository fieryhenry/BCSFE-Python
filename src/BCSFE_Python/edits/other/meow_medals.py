import helper

def get_medal_names():
    medal_names = open(helper.get_files_path("game_data/medals/medalname.tsv"), "r").readlines()
    names = []
    for line in medal_names:
        line_split = line.split("\t")
        name = line_split[0].removesuffix("\n").replace("&", "and").replace("â˜…", "").removeprefix(" ")
        names.append(name)
    return names

def medals(save_stats):
    medals = save_stats["medals"]

    names = get_medal_names()
    helper.create_list(names)

    ids = helper.get_range_input(helper.coloured_text("Enter medal ids (You can enter all to get &all&, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), len(names))
    for id in ids:
        if id == 0: continue
        id -= 1
        if id not in medals["medal_data_1"]:
            medals["medal_data_1"].append(id)
            medals["medal_data_2"][id] = 1
    save_stats["medals"] = medals
    print("Successfully gave medals")
    return save_stats