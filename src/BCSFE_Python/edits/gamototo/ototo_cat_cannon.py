from BCSFE_Python import helper

def edit_cat_cannon(save_stats):
    types = ["Base", "Slow Beam", "Iron Wall", "Thunderbolt", "Waterblast", "Holy Blast", "Breakerblast", "Curseblast"]
    cannons = save_stats["ototo_cannon"]
    levels = []
    for cannon in cannons:
        level = cannons[cannon]["level"]
        if cannons[cannon]["unlock_flag"] == 0:
            level -= 1
        levels.append(level)
    levels = helper.edit_items_list(types, levels, "Ototo Cat Cannons", [19, 29, 29, 29, 29, 29, 29, 29], offset=1)

    for i in range(len(cannons)):
        cannons[i]["unlock_flag"] = 3
        if levels[i] < 0: cannons[i]["unlock_flag"] = 0

        if levels[i] < 0: levels[i] = 0
        cannons[i]["level"] = levels[i]
    save_stats["ototo_cannon"] = cannons
    return save_stats