import helper

def upgrade_cats(save_stats):
    cats = save_stats["cat_upgrades"]
    base = cats["Base"]
    ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), len(base))
    return upgrade_cats_ids(save_stats, ids)

def upgrade_current_cats(save_stats):
    cats = save_stats["cats"]
    cat_ids = []
    for i in range(len(cats)):
        if cats[i] == 1: cat_ids.append(i)
    save_stats = upgrade_cats_ids(save_stats, cat_ids)

    return save_stats

def get_rarities():
    path = helper.get_files_path("game_data/rarity/unitbuy.csv")
    data = helper.open_file_s(path).splitlines()

    rarity_ids = []
    for cat in data:
        line = cat.split(",")
        if len(line) < 3: continue
        rarity = line[13]
        rarity_ids.append(rarity)
    return rarity_ids

def get_rarity(ids):
    rarities = get_rarities()
    cat_ids = []
    for id in ids:
        id = helper.validate_int(id)
        if id == None:
            print("Please input a valid number")
            continue
        id -= 1
        for i in range(len(rarities)):
            if int(rarities[i]) == id:
                cat_ids.append(i)
    return cat_ids

types = ["Normal", "Special", "Rare", "Super Rare", "Uber Super Rare", "Legend Rare"]
def upgrade_cat_rarity(save_stats):
    ids = helper.selection_list(types, "upgrade", True)
    
    cat_ids = get_rarity(ids)

    save_stats = upgrade_cats_ids(save_stats, cat_ids)
    
    return save_stats

def upgrade_handler(data, ids, item_name):
    base = data["Base"]
    plus = data["Plus"]
    individual = "1"
    if len(ids) > 1:
        individual = helper.coloured_text(f"Do you want to upgrade each {item_name} individually(&1&), or all at once(&2&):", is_input=True)
    first = True
    base_lvl = None
    plus_lvl = None
    for id in ids:
        if individual == "2" and first:
            levels = get_plus_base(helper.coloured_text(f"Enter the base level followed by a \"&+&\" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n", is_input=True))
            base_lvl = levels[0]
            plus_lvl = levels[1]
            first = False
        elif individual == "1":
            levels = get_plus_base(helper.coloured_text(f"Enter the base level for {item_name}: &{id}& followed by a \"&+&\" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n", is_input=True))
            base_lvl = levels[0]
            plus_lvl = levels[1]
        if base_lvl != None:
            base[id] = base_lvl-1
        if plus_lvl != None:
            plus[id] = plus_lvl
    
    data["Base"] = base
    data["Plus"] = plus

    return data

def set_user_popups(save_stats):
    save_stats["user_rank_popups"]["Value"] = 0xffffff
    return save_stats

def upgrade_cats_ids(save_stats, ids):
    save_stats["cat_upgrades"] = upgrade_handler(save_stats["cat_upgrades"], ids, "cat")
    save_stats = set_user_popups(save_stats)
    print("Successfully set cat levels")
    return save_stats
    
        

def get_plus_base(input):
    split = input.split("+")
    base = None
    plus = None
    if split[0]:
        base = helper.validate_int(split[0])
    if split[1]:
        plus = helper.validate_int(split[1])
    return [base, plus]