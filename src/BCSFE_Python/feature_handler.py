"""Handler for selecting and running editor features"""

from typing import Any, Union

from . import (
    adb_handler,
    helper,
    server_handler,
    user_input_handler,
    serialise_save,
    patcher,
    config_manager,
)
from .edits import basic, cats, gamototo, levels, other

path = ""


def save_and_exit(save_stats: dict[str, Any]) -> None:
    """Serialise the save data and exit"""

    save_data = serialise_save.start_serialize(save_stats)
    helper.write_save_data(save_data, save_stats["version"], path, True)
    helper.check_tracker(save_stats, path)
    helper.exit_editor()


def save_and_upload(save_stats: dict[str, Any]) -> None:
    """Serialise the save data, and upload it to the game server"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = helper.write_save_data(save_data, save_stats["version"], path, False)
    upload_data = server_handler.upload_handler(save_stats, path)
    if upload_data is None:
        helper.exit_editor()
    if not upload_data["transferCode"]:
        helper.colored_text(
            "Error uploading save data\nPlease report this in #bug-reports"
        )
    else:
        helper.colored_text(f"Transfer code : &{upload_data['transferCode']}&")
        helper.colored_text(f"Confirmation Code : &{upload_data['pin']}&")
    helper.exit_editor()


def fix_elsewhere_old(save_stats: dict[str, Any]) -> dict[str, Any]:
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


def save_and_push(save_stats: dict[str, Any]) -> None:
    """Serialise the save data and and push it to the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(path, save_data)
    helper.check_tracker(save_stats, path)
    adb_handler.adb_push_save_data(save_stats["version"], path)
    helper.exit_editor()


def save_and_push_rerun(save_stats: dict[str, Any]) -> None:
    """Serialise the save data and push it to the game and restart the game"""

    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    helper.write_file_bytes(path, save_data)
    helper.check_tracker(save_stats, path)
    adb_handler.adb_push_save_data(save_stats["version"], path)
    adb_handler.rerun_game(save_stats["version"])
    helper.exit_editor()


def export(save_stats: dict[str, Any]) -> None:
    """Export the save stats to a json file"""

    helper.export_json(save_stats, path + ".json")
    helper.exit_editor()


def clear_data(save_stats: dict[str, Any]) -> None:
    """Clear data wrapper for the clear_data function"""

    confirm = input("Do want to clear your data (y/n)?:").lower()
    if confirm == "y":
        adb_handler.adb_clear_save_data(save_stats["version"])
        print("Data cleared")
    helper.exit_editor()


def upload_metadata(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Upload the metadata to the game server"""

    _, save_stats = server_handler.meta_data_upload_handler(save_stats, path)
    return save_stats


def set_managed_items(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Set the managed items for the save stats"""

    data = server_handler.check_gen_token(save_stats)
    token = data["token"]
    save_stats = data["save_stats"]
    if token is None:
        helper.colored_text("Error generating token")
        return save_stats
    server_handler.update_managed_items(save_stats["inquiry_code"], token, save_stats)
    return save_stats


features: dict[str, Any] = {
    "Save Management": {
        "Save changes and upload to game servers (get transfer and confirmation codes)": save_and_upload,
        "Save changes and exit": save_and_exit,
        "Save changes and push save data to the game (don't re-open game)": save_and_push,
        "Save changes and push save data to the game (re-open game)": save_and_push_rerun,
        "Export save data as json (not desinged to be that readable)": export,
        "Clear save data (used to generate a new account without re-installing the game)": clear_data,
        "Upload tracked bannable items (This is done automatically when saving and exiting)": upload_metadata,
        # "Set managed items (This is done automatically when saving and exiting)": set_managed_items,
    },
    "Items": {
        "Cat Food": basic.basic_items.edit_cat_food,
        "XP": basic.basic_items.edit_xp,
        "Normal Tickets": basic.basic_items.edit_normal_tickets,
        "Rare Tickets": basic.basic_items.edit_rare_tickets,
        "Platinum Tickets": basic.basic_items.edit_platinum_tickets,
        "Platinum Shards": basic.basic_items.edit_platinum_shards,
        "Legend Tickets": basic.basic_items.edit_legend_tickets,
        "NP": basic.basic_items.edit_np,
        "Leadership": basic.basic_items.edit_leadership,
        "Battle Items": basic.basic_items.edit_battle_items,
        "Catseyes": basic.basic_items.edit_catseyes,
        "Cat Fruit / Behemoth Stones": basic.basic_items.edit_catfruit,
        "Talent Orbs": basic.talent_orbs.edit_talent_orbs,
        "Catamins": basic.basic_items.edit_catamins,
    },
    "Gamatoto / Ototo": {
        "Ototo Engineers": basic.basic_items.edit_engineers,
        "Base materials": basic.basic_items.edit_base_materials,
        "Catamins": basic.basic_items.edit_catamins,
        "Gamatoto XP / Level": gamototo.gamatoto_xp.edit_gamatoto_xp,
        "Ototo Cat Cannon": gamototo.ototo_cat_cannon.edit_cat_cannon,
        "Gamatoto Helpers": gamototo.helpers.edit_helpers,
        "Fix gamatoto from crashing the game": gamototo.fix_gamatoto.fix_gamatoto,
    },
    "Cats / Special Skills": {
        "Get Cats": cats.get_remove_cats.get_cat,
        "Remove Cats": cats.get_remove_cats.remove_cats,
        "Upgrade Cats": cats.upgrade_cats.upgrade_cats,
        "True Form Cats": cats.evolve_cats.get_evolve,
        "Force True Form Cats (will lead to blank cats for cats without a true form)": cats.evolve_cats.get_evolve_forced,
        "Remove True Forms": cats.evolve_cats.remove_evolve,
        "Talents": cats.talents.edit_talents,
        "Collect Cat Guide": cats.clear_cat_guide.clear_cat_guide,
        "Remove Cat Guide": cats.clear_cat_guide.remove_cat_guide,
        'Get stage unit drops - removes the "Clear this stage to get special cat" dialog': cats.chara_drop.get_character_drops,
        "Upgrade special skills / abilities": cats.upgrade_blue.upgrade_blue,
    },
    "Levels / Treasures": {
        "Main Story Chapters Clear / Unclear": levels.main_story.edit_main_story,
        "Main Story Treasures": levels.treasures.specific_treasures,
        "Zombie Stages / Outbreaks": levels.outbreaks.edit_outbreaks,
        "Event Stages": levels.event_stages.event_stages,
        "Stories of Legend": levels.event_stages.stories_of_legend,
        "Uncanny Legends": levels.uncanny.edit_uncanny,
        "Aku Realm/Gates": levels.aku.edit_aku,
        "Gauntlets": levels.gauntlet.edit_gauntlet,
        "Into the Future Timed Scores": levels.itf_timed_scores.timed_scores,
        "Challenge Battle Score": basic.basic_items.edit_challenge_battle,
        "Towers": levels.towers.edit_tower,
        "Clear Tutorial": levels.clear_tutorial.clear_tutorial,
        "Catclaw Dojo Score (Hall of Initiates)": basic.basic_items.edit_dojo_score,
    },
    "Inquiry Code / Token / Account": {
        "Inquiry Code": basic.basic_items.edit_inquiry_code,
        "Token": basic.basic_items.edit_token,
        "Fix elsewhere error / Unban account": other.fix_elsewhere.fix_elsewhere,
        "Old Fix elsewhere error / Unban account (needs 2 save files)": fix_elsewhere_old,
        "Create a new account / Duplicate account": other.create_new_account.create_new_account,
    },
    "Other": {
        "Rare Gacha Seed": basic.basic_items.edit_rare_gacha_seed,
        "Unlocked Equip Slots": basic.basic_items.edit_unlocked_slots,
        "Get Restart Pack / Returner Mode": basic.basic_items.edit_restart_pack,
        "Meow Medals": other.meow_medals.medals,
        "Play Time": other.play_time.edit_play_time,
        "Unlock / Remove Enemy Guide Entries": other.unlock_enemy_guide.enemy_guide,
        "Catnip Challenges / Missions": other.missions.edit_missions,
        "Normal Ticket Max Trade Progress (allows for unbannable rare tickets)": other.trade_progress.set_trade_progress,
        "Unlock the Equip Menu": other.unlock_equip_menu.unlock_equip,
        "Get Gold Pass": other.get_gold_pass.get_gold_pass,
        "Claim all user rank rewards (does not give any items)": other.claim_user_rank_rewards.claim,
    },
}


def get_feature(
    selected_features: Any, search_string: str, results: dict[str, Any]
) -> dict[str, Any]:
    """Search for a feature if the feature name contains the search string"""

    for feature in selected_features:
        feature_data = selected_features[feature]
        if isinstance(feature_data, dict):
            feature_data = get_feature(feature_data, search_string, results)
        if search_string.lower().replace(" ", "") in feature.lower().replace(" ", ""):
            results[feature] = selected_features[feature]
    return results


def show_options(
    save_stats: dict[str, Any], features_to_use: dict[str, Any]
) -> dict[str, Any]:
    """Allow the user to either enter a feature number or a feature name, and get the features that match"""

    if (
        not config_manager.get_config_value_category("EDITOR", "SHOW_CATEGORIES")
        and features == features_to_use
    ):
        user_input = ""
    else:
        prompt = (
            "What do you want to edit (some options contain other features within them)"
        )
        if config_manager.get_config_value_category(
            "EDITOR", "SHOW_FEATURE_SELECT_EXPLAINATION"
        ):
            prompt += "\nYou can enter a number to run a feature or a word to search for that feature (e.g entering catfood will run the Cat Food feature, and entering tickets will show you all the features that edit tickets)\nYou can press enter to see a list of all of the features"
        user_input = user_input_handler.colored_input(f"{prompt}:\n")
    user_int = helper.check_int(user_input)
    results = []
    if user_int is None:
        results = get_feature(features_to_use, user_input, {})
    else:
        if user_int < 1 or user_int > len(features_to_use) + 1:
            helper.colored_text("Value out of range", helper.RED)
            return show_options(save_stats, features_to_use)
        if features != features_to_use:
            if user_int - 2 < 0:
                return menu(save_stats)
            results = features_to_use[list(features_to_use)[user_int - 2]]
        else:
            results = features_to_use[list(features_to_use)[user_int - 1]]
    if not isinstance(results, dict):
        return results(save_stats)
    if len(results) == 0:
        helper.colored_text("No feature found with that name.", helper.RED)
        return menu(save_stats)
    if len(results) == 1:
        return results[list(results)[0]](save_stats)

    helper.colored_list(["Go Back"] + list(results))
    return show_options(save_stats, results)


def menu(
    save_stats: dict[str, Any], path_save: Union[str, None] = None
) -> dict[str, Any]:
    """Show the menu and allow the user to select a feature to edit"""
    global features

    actual_features = features

    if config_manager.get_config_value_category("EDITOR", "HIDE_BANNABLE_ITEMS"):
        bannables = ["Cat Food", "Rare Tickets", "Platinum Tickets", "Legend Tickets"]
        for bannable in bannables:
            if bannable in actual_features["Items"]:
                del features["Items"][bannable]
        helper.colored_text("&Banned items are now hidden")

    if path_save:
        global path
        path = path_save
    if config_manager.get_config_value_category("EDITOR", "SHOW_CATEGORIES"):
        helper.colored_list(list(features))
    save_stats = show_options(save_stats, features)
    features = actual_features

    return save_stats
