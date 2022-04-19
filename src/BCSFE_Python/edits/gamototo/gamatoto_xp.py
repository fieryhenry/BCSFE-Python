from BCSFE_Python import helper

def get_boundaries():
    boundaries = open(helper.get_files_path("game_data/gamatoto/GamatotoExpedition.csv"), "r").readlines()
    previous = 0
    xp_requirements = []
    previous = 0
    for line in boundaries:
        requirement = int(line.split(",")[0])
        if previous >= requirement:
            break
        xp_requirements.append(requirement)
        previous = requirement
    return xp_requirements

def get_level_from_xp(xp):
    xp_requirements = get_boundaries()
    level = 1
    for i in range(len(xp_requirements)):
        requirement = xp_requirements[i]
        if xp >= requirement:
            level += 1
    return {"level": level, "max_level" : len(xp_requirements), "max_xp" : xp_requirements[-2]}

def get_xp_from_level(level):
    xp_requirements = get_boundaries()
    if level <= 1: xp = 0
    else: xp = xp_requirements[level-2]
    return xp

def edit_gamatoto_xp(save_stats):
    xp = save_stats["gamatoto_xp"]

    data = get_level_from_xp(xp["Value"])
    level = data["level"]

    helper.coloured_text(f"Gamatoto xp: &{xp['Value']}&\nLevel: &{level}&")
    raw = helper.coloured_text("Do you want to edit raw xp(&1&) or the level(&2&)?:", is_input=True)

    if raw == "1":
        xp = helper.edit_item(xp, None, "Gamatoto XP")
    elif raw == "2":
        level = helper.edit_item(level, data["max_level"], "Gamatoto Level", add_plural=True)
        xp["Value"] = get_xp_from_level(level)

    save_stats["gamatoto_xp"] = xp
    return save_stats
