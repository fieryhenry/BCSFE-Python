"""Handler for selecting and running editor features"""

import sys
from . import (
    helper,
    patcher,
    serialise_save,
    adb_handler,
    server_handler,
    user_input_handler,
)

from .edits import (
    basic_items,
    other,
    gamototo,
    cats,
    levels,
)

path = ""


def save_and_exit(save_stats: dict) -> dict:
    """Serialise the save data and exit"""

    save_data = serialise_save.start_serialize(save_stats)
    helper.write_save_data(save_data, save_stats["version"], path, True)
    sys.exit()


def save_and_upload(save_stats: dict) -> dict:
    """Serialise the save data, and upload it to the game server"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = helper.write_save_data(save_data, save_stats["version"], path, False)
    upload_data = server_handler.upload_handler(save_stats, path)
    if not upload_data:
        sys.exit()
    helper.colored_text(f"Transfer code : &{upload_data['transferCode']}&")
    helper.colored_text(f"Confirmation Code : &{upload_data['pin']}&")
    sys.exit()


def fix_elsewhere_old(save_stats: dict) -> dict:
    """Fix the elsewhere error using 2 save files"""

    main_token = save_stats["token"]
    main_iq = save_stats["inquiry_code"]
    input(
        "Select a save file that is currently loaded in-game that doesn't have the elsehere error and is not banned\nPress enter to continue:"
    )
    new_path = helper.select_file(
        "Select a clean save file", helper.get_save_file_filetype(), path
    )
    if not new_path:
        print("Please select a save file")
        return save_stats

    data = helper.load_save_file(new_path)
    new_stats = data["save_stats"]
    new_token = new_stats["token"]
    new_iq = new_stats["inquiry_code"]
    save_stats["token"] = new_token
    save_stats["inquiry_code"] = new_iq

    helper.colored_text(f"Replaced inquiry code: &{main_iq}& with &{new_iq}&")
    helper.colored_text(f"Replaced token: &{main_token}& with &{new_token}&")
    return save_stats


def save_and_push(save_stats: dict) -> dict:
    """Serialise the save data and and push it to the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(path, save_data)
    adb_handler.adb_push(save_stats["version"], path, False)
    sys.exit()


def save_and_push_rerun(save_stats: dict) -> dict:
    """Serialise the save data and push it to the game and restart the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(path, save_data)
    adb_handler.adb_push(save_stats["version"], path, True)
    sys.exit()


def export(save_stats: dict) -> dict:
    """Export the save stats to a json file"""

    serialise_save.export_json(save_stats, path + ".json")
    sys.exit()


def clear_data(save_stats: dict) -> dict:
    """Clear data wrapper for the clear_data function"""

    confirm = input("Do want to clear your data (y/n)?:").lower()
    if confirm == "y":
        adb_handler.adb_clear(save_stats["version"])
        print("Data cleared")
    sys.exit()


FEATURES = {
    "Save Management": {
        "Save changes and upload to game servers (get transfer and confirmation codes)": save_and_upload,
        "Save changes and exit": save_and_exit,
        "Save changes and push save data to the game (don't re-open game)": save_and_push,
        "Save changes and push save data to the game (re-open game)": save_and_push_rerun,
        "Export save data as json (not desinged to be that readable)": export,
        "Clear save data (used to generate a new account without re-installing the game)": clear_data,
    },
    "Items": {
        "Cat Food": basic_items.basic.edit_cat_food,
        "XP": basic_items.basic.edit_xp,
        "Normal Tickets": basic_items.basic.edit_normal_tickets,
        "Rare Tickets": basic_items.basic.edit_rare_tickets,
        "Platinum Tickets": basic_items.basic.edit_platinum_tickets,
        "Platinum Shards": basic_items.basic.edit_platinum_shards,
        "Legend Tickets": basic_items.basic.edit_legend_tickets,
        "NP": basic_items.basic.edit_np,
        "Leadership": basic_items.basic.edit_leadership,
        "Battle Items": basic_items.basic.edit_battle_items,
        "Catseyes": basic_items.basic.edit_catseyes,
        "Cat Fruit / Behemoth Stones": basic_items.basic.edit_catfruit,
        "Talent Orbs": basic_items.talent_orbs.edit_talent_orbs,
    },
    "Gamatoto / Ototo": {
        "Ototo Engineers": basic_items.basic.edit_engineers,
        "Base materials": basic_items.basic.edit_base_materials,
        "Catamins": basic_items.basic.edit_catamins,
        "Gamatoto XP / Level": gamototo.gamatoto_xp.edit_gamatoto_xp,
        "Ototo Cat Cannon": gamototo.ototo_cat_cannon.edit_cat_cannon,
        "Gamatoto Helpers": gamototo.helpers.edit_helpers,
        "Fix gamatoto from crashing the game": gamototo.fix_gamatoto.fix_gamatoto,
    },
    "Cats / Special Skills": {
        "Get Cats": cats.get_remove_cats.get_cat,
        "Get Cats Based On Rarity": cats.get_remove_cats.get_cat_rarity,
        "Remove Cats": cats.get_remove_cats.remove_cats,
        "Upgrade Cats": cats.upgrade_cats.upgrade_cats,
        "Upgrade Currently Unlocked Cats": cats.upgrade_cats.upgrade_current_cats,
        "Upgrade Cats Based On Rarity": cats.upgrade_cats.upgrade_cat_rarity,
        "Upgrade Special Skills / Base upgrades (The ones that are blue)": cats.upgrade_blue.upgrade_blue,
        "True Form Currently Unlocked Cats": cats.evolve_cats.get_evolve_current,
        "True Form Cats": cats.evolve_cats.get_evolve,
        "True Form Cats Based On Rarity": cats.evolve_cats.evolve_cat_rarity,
        "Force True Form Cats": cats.evolve_cats.get_evolve_forced,
        "Remove True Forms": cats.evolve_cats.remove_evolve,
        "Talents": cats.talents.edit_talents,
        "Collect Cat Guide": cats.clear_cat_guide.clear_cat_guide,
        "Collect Cat Guide Based On Rarity": cats.clear_cat_guide.clear_cat_guide_rarity,
        'Get stage unit drops - removes the "Clear this stage to get special cat" dialog': cats.chara_drop.get_character_drops,
    },
    "Levels / Treasures": {
        "Main Story Chapters Clear": levels.main_story.main_story,
        "Whole Chapter Main Story Treasures": levels.treasures.treasures,
        "Individual Treasures Per Stage / Treasure Groups (e.g energy drink, aqua crystal)": levels.treasures.specific_treasures,
        "Zombie Stages / Outbreaks": levels.outbreaks.edit_outbreaks,
        "Event Stages": levels.event_stages.event_stages,
        "Stories of Legend": levels.event_stages.stories_of_legend,
        "Uncanny Legends": levels.uncanny.edit_uncanny,
        "Aku Realm/Gates": levels.aku.edit_aku,
        "Gauntlets": levels.gauntlet.edit_gauntlet,
        "Into the Future Timed Scores": levels.itf_timed_scores.timed_scores,
        "Challenge Battle Score": basic_items.basic.edit_challenge_battle,
        "Towers": levels.towers.edit_tower,
        "Clear Tutorial": levels.clear_tutorial.clear_tutorial,
        "Catclaw Dojo Score (Hall of Initiates)": basic_items.basic.edit_dojo_score,
    },
    "Inquiry Code / Token": {
        "Inquiry Code": basic_items.basic.edit_inquiry_code,
        "Token": basic_items.basic.edit_token,
        "Fix elsewhere error / Unban account": other.fix_elsewhere.fix_elsewhere,
        "Old Fix elsewhere error / Unban account (needs 2 save files)": fix_elsewhere_old,
    },
    "Other": {
        "Rare Gacha Seed": basic_items.basic.edit_rare_gacha_seed,
        "Unlocked Equip Slots": basic_items.basic.edit_unlocked_slots,
        "Restart Pack": basic_items.basic.edit_restart_pack,
        "Meow Medals": other.meow_medals.medals,
        "Play Time": other.play_time.edit_play_time,
        "Unlock / Remove Enemy Guide Entries": other.unlock_enemy_guide.enemy_guide,
        "Catnip Challenges / Missions": other.missions.edit_missions,
        "Normal Ticket Max Trade Progress (allows for unbannable rare tickets)": other.trade_progress.set_trade_progress,
    },
}


def get_feature(features: dict, search_string: str, results: dict) -> dict:
    """Search for a feature if the feature name contains the search string"""

    for feature in features:
        feature_data = features[feature]
        if isinstance(feature_data, dict):
            feature_data = get_feature(feature_data, search_string, results)
        if search_string.lower().replace(" ", "") in feature.lower().replace(" ", ""):
            results[feature] = features[feature]
    return results


def show_options(save_stats: dict, features: dict) -> dict:
    """Allow the user to either enter a feature number or a feature name, and get the features that match"""

    user_input = user_input_handler.colored_input(
        "What do you want to edit (some options contain other features within them)\nYou can enter a number to run a feature or a word to search for that feature (e.g entering catfood will run the Cat Food feature, and entering tickets will show you all the features that edit tickets)\nYou can press enter to see a list of all of the features:\n"
    )
    user_int = helper.check_int(user_input)
    results = []
    if user_int is None:
        results = get_feature(features, user_input, {})
    else:
        if user_int < 1 or user_int > len(features) + 1:
            helper.colored_text("Value out of range", helper.RED)
            return show_options(save_stats, features)
        if FEATURES != features:
            if user_int - 2 < 0:
                return menu(save_stats)
            results = features[list(features)[user_int - 2]]
        else:
            results = features[list(features)[user_int - 1]]
    if not isinstance(results, dict):
        return results(save_stats)
    if len(results) == 0:
        helper.colored_text("No feature found with that name.", helper.RED)
        return menu(save_stats)
    if len(results) == 1:
        return results[list(results)[0]](save_stats)

    helper.colored_list(["Go Back"] + list(results))
    return show_options(save_stats, results)


def menu(save_stats: dict, path_save: str = None) -> dict:
    """Show the menu and allow the user to select a feature to edit"""

    if path_save:
        global path
        path = path_save
    helper.colored_list(list(FEATURES))
    save_stats = show_options(save_stats, FEATURES)

    return save_stats
