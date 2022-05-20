import helper

types = ["Base", "Slow Beam", "Iron Wall", "Thunderbolt", "Waterblast", "Holy Blast", "Breakerblast", "Curseblast"]

def set_level(save_stats, levels):
    cannons = save_stats["ototo_cannon"]

    levels = helper.edit_items_list(types, levels, "Ototo Cat Cannons", [19, 29, 29, 29, 29, 29, 29, 29], offset=1)
    for i in range(len(cannons)):
        cannons[i]["unlock_flag"] = 3
        if levels[i] < 0: cannons[i]["unlock_flag"] = 0

        if levels[i] < 0: levels[i] = 0
        cannons[i]["level"] = levels[i]
    save_stats["ototo_cannon"] = cannons
    return save_stats

def set_stage(save_stats, stages):
    cannons = save_stats["ototo_cannon"]

    stages = helper.edit_items_list(types[1:], stages[1:], "Ototo Cat Cannons", 3, type_name="stage")
    for i in range(len(cannons)-1):
        cannons[i+1]["unlock_flag"] = stages[i]

    save_stats["ototo_cannon"] = cannons
    return save_stats
def edit_cat_cannon(save_stats):
    cannons = save_stats["ototo_cannon"]
    levels = []
    stages = []
    for cannon in cannons:
        level = cannons[cannon]["level"]
        stage = cannons[cannon]["unlock_flag"]
        if cannons[cannon]["unlock_flag"] == 0:
            level -= 1
        levels.append(level)
        stages.append(stage)
    stage = helper.valdiate_bool(helper.coloured_text("Do you want to set the level of the cannon &(1)& or the level of construction &(2)& (e.g foundation, style, cannon):", is_input=True), "2")
    if stage:
        save_stats = set_stage(save_stats, stages)
    else:
        save_stats = set_level(save_stats, levels)
    return save_stats