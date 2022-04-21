import helper
def edit_cat_food(save_stats):
    save_stats["cat_food"] = helper.edit_item(save_stats["cat_food"], 45000, "Cat Food", True)
    return save_stats

def edit_xp(save_stats):
    save_stats["xp"] = helper.edit_item(save_stats["xp"], 99999999, "XP")
    return save_stats

def edit_normal_tickets(save_stats):
    save_stats["normal_tickets"] = helper.edit_item(save_stats["normal_tickets"], 2999, "Normal Tickets")
    return save_stats
def edit_rare_tickets(save_stats):
    save_stats["rare_tickets"] = helper.edit_item(save_stats["rare_tickets"], 299, "Rare Tickets", True)
    return save_stats
def edit_platinum_tickets(save_stats):
    save_stats["platinum_tickets"] = helper.edit_item(save_stats["platinum_tickets"], 9, "Platinum Tickets", True)
    return save_stats

def edit_platinum_shards(save_stats):
    save_stats["platinum_shards"] = helper.edit_item(save_stats["platinum_shards"], 999, "Platinum Shards")
    return save_stats

def edit_np(save_stats):
    save_stats["np"] = helper.edit_item(save_stats["np"], 9999, "NP")
    return save_stats
def edit_leadership(save_stats):
    save_stats["leadership"] = helper.edit_item(save_stats["leadership"], 9999, "Leadership")
    return save_stats

def edit_battle_items(save_stats):
    save_stats["battle_items"] = helper.edit_items_list(["Speed Up", "Treasure Radar", "Rich Cat", "Cat CPU", "Cat Jobs", "Sniper the Cat"], save_stats["battle_items"], "Battle Items", 9999, "amount")
    return save_stats

def edit_catseyes(save_stats):
    save_stats["catseyes"] = helper.edit_items_list(["Special", "Rare", "Super Rare", "Uber Super Rare", "Legend Rare"], save_stats["catseyes"], "Catseyes", 9999, "amount")
    return save_stats

def edit_catfruit(save_stats):
    max_cf = 128
    if save_stats["game_version"]["Value"] >= 110400:
        max_cf = None
    save_stats["cat_fruit"] = helper.edit_items_list(["Purple Seeds", "Red Seeds", "Blue Seeds", "Green Seeds", "Yellow Seeds", "Purple Fruit", "Red Fruit", "Blue Fruit", "Green Fruit", "Yellow Fruit", "Epic Fruit", "Elder Seeds", "Elder Fruit", "Epic Seeds", "Gold Fruit", "Aku Seeds", "Aku Fruit", "Gold Seeds"], save_stats["cat_fruit"], "Catfruit", max_cf, "amount")
    return save_stats

def edit_engineers(save_stats):
    save_stats["engineers"] = helper.edit_item(save_stats["engineers"], 4, "Ototo engineers")
    return save_stats

def edit_base_materials(save_stats):
    save_stats["base_materials"] = helper.edit_items_list(["Bricks", "Feathers", "Coal", "Sprockets", "Gold", "Meteorite", "Beast Bones", "Ammonite"], save_stats["base_materials"], "Ototo Base Materials", 9999, "amount")
    return save_stats

def edit_catamins(save_stats):
    save_stats["catamins"] = helper.edit_items_list(["Catamin A", "Catamin B", "Catamin C"], save_stats["catamins"], "Catamins", 9999, "amount")
    return save_stats

def edit_inquiry_code(save_stats):
    print("WARNING: Editing your inquiry code should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!")
    save_stats["inquiry_code"] = helper.edit_item_str(save_stats["inquiry_code"], "Inquiry Code")
    return save_stats

def edit_rare_gacha_seed(save_stats):
    save_stats["rare_gacha_seed"] = helper.edit_item(save_stats["rare_gacha_seed"], None, "Rare Gacha Seed", custom_text=["Your rare gacha seed is currently:", "Enter a new rare gacha seed:"])
    return save_stats

def edit_unlocked_slots(save_stats):
    save_stats["unlocked_slots"] = helper.edit_item(save_stats["unlocked_slots"], 15, "Equip Slots")
    return save_stats

def edit_token(save_stats):
    print("WARNING: Editing your token should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!")
    save_stats["token"] = helper.edit_item_str(save_stats["token"], "Token")
    return save_stats

def edit_restart_pack(save_stats):
    save_stats["restart_pack"]["Value"] = 1
    print("Successfully gave the restart pack")
    return save_stats

def edit_challenge_battle(save_stats):
    save_stats["challenge"]["Score"] = helper.edit_item(save_stats["challenge"]["Score"], None, "Challenge Battle Score", custom_text=["Your current score is:", "Enter a new score:"])
    save_stats["challenge"]["Cleared"]["Value"] = 1
    return save_stats

def edit_legend_tickets(save_stats):
    save_stats["legend_tickets"] = helper.edit_item(save_stats["legend_tickets"], 4, "Legend Tickets")
    return save_stats