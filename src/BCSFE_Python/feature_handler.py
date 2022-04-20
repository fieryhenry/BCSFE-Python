from BCSFE_Python import helper
from BCSFE_Python import patcher
from BCSFE_Python import serialise_save
from BCSFE_Python.edits.basic_items import basic, talent_orbs, meow_medals, play_time
from BCSFE_Python.edits.gamototo import gamatoto_xp, ototo_cat_cannon, helpers
from BCSFE_Python.edits.cats import evolve_cats, get_remove_cats, upgrade_blue, upgrade_cats, talents
from BCSFE_Python.edits.levels import aku, event_stages, gauntlet, itf_timed_scores, main_story, outbreaks, towers, treasures, uncanny

path = ""

def save_and_exit(save_stats):
    save_data = serialise_save.start_serialize(save_stats)
    helper.write_save_data(save_data, save_stats["version"], path)

def fix_elsewhere(save_stats):
    main_token = save_stats["token"]
    main_iq = save_stats["inquiry_code"]
    print("Select a save file that is currently loaded in-game that doesn't have the elsehere error and is not banned\nPress enter to continue")
    new_path = helper.sel_save()
    if not new_path:
        print("Please select a save file")
        return
    
    data = helper.load_save_file(new_path)
    new_stats = data["save_stats"]
    new_token = new_stats["token"]
    new_iq = new_stats["inquiry_code"]
    save_stats["token"] = new_token
    save_stats["inquiry_code"] = new_iq
    
    helper.coloured_text(f"Replaced inquiry code: &{main_iq}& with &{new_iq}&")
    helper.coloured_text(f"Replaced token: &{main_token}& with &{new_token}&")
    return save_stats

def save_and_push(save_stats):
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file(save_data, path, False)
    helper.adb_push(save_stats["version"], path, False)
    exit()

def save_and_push_rerun(save_stats):
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file(save_data, path, False)
    helper.adb_push(save_stats["version"], path, True)
    exit()


def export(save_stats):
    serialise_save.export_json(save_stats, path + ".json")
    exit()

def clear_data(save_stats):
    confirm = input("Do want to clear your data (y/n)?:").lower()
    if confirm == "y":
        helper.adb_clear(save_stats["version"])
        print("Data cleared")
    exit()
features = {
    "Save Management":
    {
        "Save changes and exit": save_and_exit,
        "Save changes and push save data to the game (don't re-open game)": save_and_push,
        "Save changes and push save data to the game (re-open game)": save_and_push_rerun,
        "Export save data as json (not desinged to be that readable)": export,
        "Clear save data (used to generate a new account without re-installing the game)" : clear_data,
    },
    "Items":
        {
            "Cat Food": basic.edit_cat_food,
            "XP": basic.edit_xp,
            "Normal Tickets": basic.edit_normal_tickets,
            "Rare Tickets": basic.edit_rare_tickets,
            "Platinum Tickets": basic.edit_platinum_tickets,
            "Platinum Shards": basic.edit_platinum_shards,
            "Legend Tickets" : basic.edit_legend_tickets,
            "NP": basic.edit_np,
            "Leadership": basic.edit_leadership,
            "Battle Items": basic.edit_battle_items,
            "Catseyes": basic.edit_catseyes,
            "Cat Fruit": basic.edit_catfruit,
            "Talent Orbs": talent_orbs.edit_talent_orbs,
    },
    "Gamatoto / Ototo":
        {
            "Ototo Engineers": basic.edit_engineers,
            "Base materials": basic.edit_base_materials,
            "Catamins": basic.edit_catamins,
            "Gamatoto XP / Level": gamatoto_xp.edit_gamatoto_xp,
            "Ototo Cat Cannon": ototo_cat_cannon.edit_cat_cannon,
            "Gamatoto Helpers": helpers.edit_helpers,
    },
    "Cats / Special Skills":
        {
            "Get Cats": get_remove_cats.get_cat,
            "Remove Cats": get_remove_cats.remove_cats,
            "Upgrade Cats": upgrade_cats.upgrade_cats,
            "Upgrade Current Cats": upgrade_cats.upgrade_current_cats,
            "Upgrade Special Skills / Base upgrades (The ones that are blue)": upgrade_blue.upgrade_blue,
            "True Form Current Cats": evolve_cats.get_evolve_current,
            "True Form Cats": evolve_cats.get_evolve,
            "Force True Form Cats": evolve_cats.get_evolve_forced,
            "Remove True Forms": evolve_cats.remove_evolve,
            "Talents" : talents.edit_talents,
        },
    "Levels / Treasures" :
        {
            "Main Story Chapters Clear" : main_story.main_story,
            "Main Story Chapters Treasures" : treasures.treasures,
            "Zombie Stages / Outbreaks" : outbreaks.edit_outbreaks,
            "Event Stages" : event_stages.event_stages,
            "Stories of Legend" : event_stages.stories_of_legend,
            "Uncanny Legends" : uncanny.edit_uncanny,
            "Aku Realm/Gates" : aku.edit_aku,
            "Gauntlets" : gauntlet.edit_gauntlet,
            "Into the Future Timed Scores" : itf_timed_scores.timed_scores,
            "Challenge Battle" : basic.edit_challenge_battle,
            "Towers" : towers.edit_tower,
        },
    "Inquiry Code / Token":
        {
            "Inquiry Code": basic.edit_inquiry_code,
            "Token": basic.edit_token,
            "Fix elsewhere error / Unban account" : fix_elsewhere,
        },
    "Other":
        {
            "Rare Gacha Seed" : basic.edit_rare_gacha_seed,
            "Unlocked Equip Slots" : basic.edit_unlocked_slots,
            "Restart Pack" : basic.edit_restart_pack,
            "Meow Medals" : meow_medals.medals,
            "Play Time" : play_time.edit_play_time,
        }
}
def search_dict(dictionary, item, results=[]):
    for k, v in dictionary.items():
        if type(v) == dict:
            search_dict(v, item, results)
        else:
            if item.lower() in k.lower().replace(" ", ""):
                results.append({"Name": k, "Function": v})
    return results
def show_options(user_input, save_stats, feature_dict):
    result_input = helper.validate_int(user_input)
    to_search = user_input

    if result_input != None:
        name = list(feature_dict)[result_input-1]
        result_data = feature_dict[name]
        results = []
        for result in result_data:
            results.append(
                {"Name": result, "Function": feature_dict[name][result]})
    else:
        to_search = to_search.replace(" ", "")
        results = search_dict(feature_dict, to_search, [])
    if len(results) == 1:
        save_stats = results[0]["Function"](save_stats)
    else:
        options = []
        for i in range(len(results)):
            options.append(results[i]["Name"])
        if not options:
            print(f"Error a feature with name: {user_input} doesn't exist")
            return save_stats
        helper.create_list(options)
        user_input = input("Enter an option:\n")
        index = helper.validate_int(user_input)
        if index != None:
            if type(results[index-1]["Function"]) == dict:
                return show_options(user_input, save_stats, feature_dict[name])
            save_stats = results[index-1]["Function"](save_stats)
    return save_stats

def display_features():
    helper.create_list(list(features))
def menu(save_stats, path_save):
    global path
    path = path_save
    display_features()
    user_input = input(
        "What do you want to edit (some options contain other features within them)\nYou can enter a number to run a feature or a word to search for that feature (e.g entering catfood will run the Cat Food feature, and entering tickets will show you all the features that edit tickets)\nYou can press enter to see all of the features:\n")
    save_stats = show_options(user_input, save_stats, features)

    return save_stats