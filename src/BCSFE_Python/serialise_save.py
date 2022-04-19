import datetime
import json
import os
import traceback
from . import helper
import dateutil.parser
from . import parse_save


def write(save_data, number, bytes=None):
    if bytes == None:
        bytes = number["Length"]
    if type(number) == dict:
        number = number["Value"]
    number = int(number)
    data = list(helper.to_little(number, bytes))

    save_data += data

    return save_data


def create_list_separated(data, bytes):
    ls = []
    for i in range(len(data)):
        byte_data = list(helper.to_little(data[i], bytes))
        ls += byte_data
    return ls


def write_length_data(save_data, data, length_bytes=4, bytes=4, write_length=True, length=None):
    if write_length == False and length == None:
        length = len(data)
    if type(data) == dict:
        data = data["Value"]

    if write_length:
        if length == None:
            length = len(data)
        length_data = list(helper.to_little(length, length_bytes))
        save_data += length_data

    save_data += create_list_separated(data, bytes)

    return save_data


def serialise_time_data_skip(save_data, time, float_val, dst_flag, dst=0):
    time = dateutil.parser.parse(time)
    save_data = write(save_data, time.year, 4)
    save_data = write(save_data, time.year, 4)

    save_data = write(save_data, time.month, 4)
    save_data = write(save_data, time.month, 4)

    save_data = write(save_data, time.day, 4)
    save_data = write(save_data, time.day, 4)

    save_data = write(save_data, float_val, 8)

    save_data = write(save_data, time.hour, 4)
    save_data = write(save_data, time.minute, 4)
    save_data = write(save_data, time.second, 4)

    if dst_flag:
        save_data = write(save_data, dst, 1)

    return save_data


def serialise_time_data(save_data, time, dst_flag, dst=0):
    time = dateutil.parser.parse(time)
    if dst_flag:
        save_data = write(save_data, dst, 1)

    save_data = write(save_data, time.year, 4)
    save_data = write(save_data, time.month, 4)
    save_data = write(save_data, time.day, 4)
    save_data = write(save_data, time.hour, 4)
    save_data = write(save_data, time.minute, 4)
    save_data = write(save_data, time.second, 4)

    return save_data


def serialise_equip_slots(save_data, equip_slots):
    save_data = write(save_data, len(equip_slots), 1)
    for slot in equip_slots:
        save_data = write_length_data(save_data, slot, 0, 4, False)
    return save_data


def serialise_main_story(save_data, story_chapters):
    save_data = write_length_data(
        save_data, story_chapters["Chapter Progress"], write_length=False)
    for chapter in story_chapters["Times Cleared"]:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_treasures(save_data, treasures):
    for chapter in treasures:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_cat_upgrades(save_data, cat_upgrades):
    data = []
    length = len(cat_upgrades["Base"])
    for id in range(length):
        data.append(cat_upgrades["Plus"][id])
        data.append(cat_upgrades["Base"][id])
    write_length_data(save_data, data, 4, 2, True, length)
    return save_data


def serialise_blue_upgrades(save_data, blue_upgrades):
    data = []
    length = len(blue_upgrades["Base"])
    for id in range(length):
        data.append(blue_upgrades["Plus"][id])
        data.append(blue_upgrades["Base"][id])
    write_length_data(save_data, data, 4, 2, False)
    return save_data


def serialise_utf8_string(save_data, string, length_bytes=4, write_length=True, length=None):
    if type(string) == dict:
        string = string
    data = string.encode("utf-8")

    save_data = write_length_data(save_data, data, 4, 1, write_length, length)
    return save_data


def serialise_event_stages_current(save_data, event_current):
    unknown_val = event_current["unknown"]
    total_sub_chapters = event_current["total"] // unknown_val
    stars_per_sub_chapter = event_current["stars"]
    stages_per_sub_chapter = event_current["stages"]

    save_data = write(save_data, unknown_val, 1)
    save_data = write(save_data, total_sub_chapters, 2)
    save_data = write(save_data, stars_per_sub_chapter, 1)
    save_data = write(save_data, stages_per_sub_chapter, 1)

    for i in range(len(event_current["Clear"])):
        save_data = write_length_data(
            save_data, event_current["Clear"][i], 1, 1, False)

    return save_data


def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def serialise_event_stages(save_data, event_stages):
    lengths = event_stages["Lengths"]
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    for chapter in event_stages["Value"]["clear_progress"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)

    clear_amount = [0] * total * stars * stages
    clear_amount_data = event_stages["Value"]["clear_amount"]
    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                clear_amount[i*stages*stars + j*stars +
                             k] = clear_amount_data[i][k][j]

    save_data = write_length_data(save_data, clear_amount, 4, 2, False)

    for chapter in event_stages["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)
    return save_data


def serialise_wierd_plat_ticket_data(save_data, data):
    save_data = write(save_data, data["total"])
    for dict in data["Value"]:
        save_data = write(save_data, dict["unknown_48"])
        save_data = serialise_utf8_string(save_data, dict["string"])
        save_data = write(save_data, dict["unknown_49"])
    return save_data


def serialise_dumped_data(save_data, data):
    for item in data:
        save_data = write(save_data, item)
    return save_data


def serialise_outbreaks(save_data, outbreaks):
    data = outbreaks["data"]
    outbreak_data = outbreaks["outbreaks"]
    save_data = serialise_dumped_data(save_data, data)

    save_data = write(save_data, len(outbreak_data), 4)
    for chapter_id in outbreak_data:
        save_data = write(save_data, int(chapter_id), 4)
        save_data = write(save_data, outbreaks["stages_counts"][chapter_id], 4)
        for level_id in outbreak_data[chapter_id]:
            save_data = write(save_data, level_id, 4)
            save_data = write(
                save_data, outbreak_data[chapter_id][level_id], 1)

    return save_data


def serialise_ototo_cat_cannon(save_data, ototo_cannon):
    save_data = write(save_data, len(ototo_cannon), 4)
    for cannon_id in ototo_cannon:
        cannon = ototo_cannon[cannon_id]

        save_data = write(save_data, int(cannon_id), 4)
        save_data = write(save_data, cannon["len_val"], 4)
        save_data = write(save_data, cannon["unlock_flag"], 4)
        save_data = write(save_data, cannon["level"], 4)
    return save_data


def serialise_uncanny_current(save_data, uncanny_current):
    total_sub_chapters = uncanny_current["total"]
    stars_per_sub_chapter = uncanny_current["stars"]
    stages_per_sub_chapter = uncanny_current["stages"]

    save_data = write(save_data, total_sub_chapters, 4)
    save_data = write(save_data, stages_per_sub_chapter, 4)
    save_data = write(save_data, stars_per_sub_chapter, 4)

    for i in range(len(uncanny_current["Clear"])):
        save_data = write_length_data(
            save_data, uncanny_current["Clear"][i], 4, 4, False)

    return save_data


def serialise_uncanny_progress(save_data, uncanny):
    lengths = uncanny["Lengths"]
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    for chapter in uncanny["Value"]["clear_progress"]:
        save_data = write_length_data(save_data, chapter, 4, 4, False)

    clear_amount = [0] * total * stars * stages
    clear_amount_data = uncanny["Value"]["clear_amount"]
    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                clear_amount[i*stages*stars + j*stars +
                             k] = clear_amount_data[i][k][j]

    save_data = write_length_data(save_data, clear_amount, 4, 4, False)

    for chapter in uncanny["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 4, 4, False)
    return save_data


def serialise_talent_data(save_data, talents):
    save_data = write(save_data, len(talents), 4)
    for cat_id in talents:
        cat_talent_data = talents[cat_id]
        save_data = write(save_data, int(cat_id), 4)
        save_data = write(save_data, len(cat_talent_data), 4)
        for talent in cat_talent_data:
            save_data = write(save_data, talent["id"], 4)
            save_data = write(save_data, talent["level"], 4)
    return save_data


def serialise_gauntlet_current(save_data, gauntlet_current):
    save_data = write(save_data, gauntlet_current["total"], 2)
    save_data = write(save_data, gauntlet_current["stages"], 1)
    save_data = write(save_data, gauntlet_current["stars"], 1)

    for i in range(len(gauntlet_current["Clear"])):
        save_data = write_length_data(
            save_data, gauntlet_current["Clear"][i], 1, 1, False)

    return save_data


def serialise_gauntlet_progress(save_data, gauntlets):
    lengths = gauntlets["Lengths"]
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    for chapter in gauntlets["Value"]["clear_progress"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)

    clear_amount = [0] * total * stars * stages
    clear_amount_data = gauntlets["Value"]["clear_amount"]
    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                clear_amount[i*stages*stars + j*stars +
                             k] = clear_amount_data[i][k][j]

    save_data = write_length_data(save_data, clear_amount, 4, 2, False)

    for chapter in gauntlets["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)
    return save_data


def serialise_talent_orbs(save_data, talent_orbs, game_verison):
    save_data = write(save_data, len(talent_orbs), 2)
    for orb_id in talent_orbs:
        save_data = write(save_data, int(orb_id), 2)
        if game_verison["Value"] < 110400:
            save_data = write(save_data, talent_orbs[orb_id], 1)
        else:
            save_data = write(save_data, talent_orbs[orb_id], 2)
    return save_data


def serialise_aku(save_data, aku):
    lengths = aku["Lengths"]
    save_data = write(save_data, lengths["total"], 2)
    save_data = write(save_data, lengths["stages"], 1)
    save_data = write(save_data, lengths["stars"], 1)
    save_data = serialise_gauntlet_progress(save_data, aku)
    return save_data


def serialise_tower(save_data, tower):
    save_data = write(save_data, tower["current"]["total"], 4)
    save_data = write(save_data, tower["current"]["stars"], 4)

    for i in range(len(tower["current"]["selected"])):
        save_data = write_length_data(
            save_data, tower["current"]["selected"][i], 4, 4, False)

    save_data = write(save_data, tower["progress"]["total"], 4)
    save_data = write(save_data, tower["progress"]["stars"], 4)

    for i in range(len(tower["progress"]["clear_progress"])):
        save_data = write_length_data(
            save_data, tower["progress"]["clear_progress"][i], 4, 4, False)

    total = tower["progress"]["total"]
    stages = tower["progress"]["stages"]
    stars = tower["progress"]["stars"]
    save_data = write(save_data, total, 4)
    save_data = write(save_data, stages, 4)
    save_data = write(save_data, stars, 4)

    clear_amount = [0] * total * stars * stages
    clear_amount_data = tower["progress"]["clear_amount"]

    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                clear_amount[i*stages*stars + j*stars +
                             k] = clear_amount_data[i][k][j]

    save_data = write_length_data(save_data, clear_amount, 4, 4, False)

    save_data = serialise_dumped_data(save_data, tower["data"])

    return save_data

def export_json(save_stats, path):
    ordered_data = parse_save.re_order(save_stats)
    if os.path.isdir(path):
        path = os.path.join(path, "save_data.json")
    f = open(path, "w")
    f.write(json.dumps(ordered_data, indent=4))
    helper.coloured_text(f"Successfully wrote json to &{os.path.abspath(path)}&")

def exit_serialiser(save_data, save_stats):
    ordered_data = parse_save.re_order(save_stats)

    f = open("save_data.json", "w")
    f.write(json.dumps(ordered_data, indent=4))
    return serialise_utf8_string(save_data, save_stats["hash"], write_length=False)


def check_gv(save_data, save_stats, game_version):
    if save_stats["game_version"]["Value"] < game_version:
        save_data = exit_serialiser(save_data, save_stats)
        return {"save_data": save_data, "exit": True}
    else:
        return {"save_data": save_data, "exit": False}


def serialise_medals(save_data, medals):
    save_data = write_length_data(save_data, medals["medal_data_1"], 2, 2)
    medal_data_2 = medals["medal_data_2"]
    save_data = write(save_data, len(medal_data_2), 2)
    for medal_id in medal_data_2:
        save_data = write(save_data, medal_data_2[medal_id], 1)
        save_data = write(save_data, medal_id, 2)
    return save_data


def serialise_play_time(save_data, play_time):
    time_data = play_time.split(":")
    hours = int(time_data[0])
    minutes = int(time_data[1])
    seconds = int(time_data[2])
    delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    value = delta.total_seconds() * 30
    save_data = write(save_data, value, 4)
    return save_data


def start_serialize(save_stats):
    try:
        save_data = serialize_save(save_stats)
    except Exception:
        helper.coloured_text(
            "\nError: An error has occurred while writing your save stats:", base=helper.red)
        traceback.print_exc()
        helper.coloured_text(
            "\nPlease report this to &#bug-reports&, and/or &dm me your save& on discord.\nPress enter to exit:", is_input=True)
        exit()
    return save_data


def serialize_save(save_stats):
    save_data = []

    save_data = write(save_data, save_stats["game_version"])

    save_data = write(save_data, save_stats["unknown_1"])

    save_data = write(save_data, save_stats["cat_food"])
    save_data = write(save_data, save_stats["current_energy"])

    save_data = serialise_time_data_skip(
        save_data, save_stats["time"], save_stats["float_val_1"], save_stats["dst"], save_stats["dst_val"])

    save_data = write_length_data(
        save_data, save_stats["unknown_flags_1"], write_length=False)

    save_data = write(save_data, save_stats["xp"])

    save_data = write(save_data, save_stats["tutorial_cleared"])

    save_data = write_length_data(
        save_data, save_stats["unknown_flags_2"], write_length=False)
    save_data = write(save_data, save_stats["unknown_flag_1"])

    save_data = serialise_equip_slots(save_data, save_stats["slots"])
    save_data = write(save_data, save_stats["cat_stamp_current"])

    save_data = write_length_data(
        save_data, save_stats["cat_stamp_collected"], write_length=False)
    save_data = write_length_data(
        save_data, save_stats["unknown_2"], write_length=False)

    save_data = serialise_main_story(save_data, save_stats["story_chapters"])
    save_data = serialise_treasures(save_data, save_stats["treasures"])

    save_data = write_length_data(save_data, save_stats["enemy_guide"])

    save_data = write_length_data(save_data, save_stats["cats"])
    save_data = serialise_cat_upgrades(save_data, save_stats["cat_upgrades"])
    save_data = write_length_data(save_data, save_stats["current_forms"])

    save_data = serialise_blue_upgrades(save_data, save_stats["blue_upgrades"])

    save_data = write_length_data(save_data, save_stats["menu_unlocks"])
    save_data = write_length_data(save_data, save_stats["unknown_5"])

    save_data = write_length_data(
        save_data, save_stats["battle_items"], 4, 4, False, 6)
    save_data = write_length_data(save_data, save_stats["new_dialogs"])

    save_data = write_length_data(save_data, save_stats["unknown_6"])
    save_data = write_length_data(
        save_data, save_stats["unknown_7"], write_length=False)

    save_data = write(save_data, save_stats["lock_item"])
    save_data = write_length_data(
        save_data, save_stats["locked_items"], 1, 1, False, 6)

    save_data = serialise_time_data(
        save_data, save_stats["second_time"], save_stats["dst"], save_stats["dst_val"])

    save_data = write_length_data(
        save_data, save_stats["unknown_8"], write_length=False)

    save_data = serialise_time_data(
        save_data, save_stats["second_time"], save_stats["dst"], save_stats["dst_val"])

    save_data = write(save_data, save_stats["unknown_9"])

    save_data = serialise_utf8_string(save_data, save_stats["thirty2_code"])

    save_data = write(
        save_data, save_stats["unknown_10"], save_stats["unknown_10"]["Length"])
    save_data = write_length_data(
        save_data, save_stats["unknown_11"], write_length=False)

    save_data = write(save_data, save_stats["normal_tickets"])
    save_data = write(save_data, save_stats["rare_tickets"])

    save_data = write_length_data(save_data, save_stats["other_cat_data"])

    save_data = write_length_data(
        save_data, save_stats["unknown_12"], write_length=False)

    save_data = write_length_data(
        save_data, save_stats["cat_storage_id"], 2, 4)
    save_data = write_length_data(
        save_data, save_stats["cat_storage_type"], 2, 4, False)

    save_data = serialise_event_stages_current(
        save_data, save_stats["event_current"])
    save_data = serialise_event_stages(save_data, save_stats["event_stages"])

    save_data = write_length_data(
        save_data, save_stats["unknown_15"], write_length=False)
    save_data = write_length_data(save_data, save_stats["unknown_16"])

    save_data = write(save_data, save_stats["rare_gacha_seed"])

    save_data = write(save_data, save_stats["unknown_17"])
    save_data = write(save_data, save_stats["unknown_18"])

    save_data = serialise_time_data(
        save_data, save_stats["second_time"], save_stats["dst"], save_stats["dst_val"])

    save_data = write(
        save_data, save_stats["unknown_19"], save_stats["unknown_19"]["Length"])

    save_data = write(save_data, save_stats["unlocked_slots"])

    save_data = write(save_data, save_stats["unknown_20"]["Length_1"], 4)
    save_data = write(save_data, save_stats["unknown_20"]["Length_2"], 4)
    save_data = write_length_data(
        save_data, save_stats["unknown_20"], write_length=False)
    save_data = write_length_data(
        save_data, save_stats["unknown_21"], write_length=False)

    save_data = write_length_data(
        save_data, save_stats["catseye_related_data"])

    save_data = write_length_data(
        save_data, save_stats["unknown_22"], write_length=False)

    save_data = write_length_data(
        save_data, save_stats["user_rank_rewards"], 4, 1)

    save_data = write(save_data, save_stats["unknown_23"])

    save_data = write_length_data(save_data, save_stats["unlocked_forms"])

    save_data = serialise_utf8_string(save_data, save_stats["transfer_code"])
    save_data = serialise_utf8_string(
        save_data, save_stats["confirmation_code"])
    save_data = write(save_data, save_stats["transfer_flag"])

    lengths = save_stats["stage_data_related_1"]["Lengths"]
    length = lengths[0] * lengths[1] * lengths[2]
    save_data = write_length_data(save_data, lengths, write_length=False)
    save_data = write_length_data(
        save_data, save_stats["stage_data_related_1"], 4, 1, False, length)

    lengths = save_stats["stage_data_related_2"]["Lengths"]
    length = lengths[0] * lengths[1] * lengths[2]
    save_data = write_length_data(save_data, lengths, write_length=False)
    save_data = write_length_data(
        save_data, save_stats["stage_data_related_2"], 4, 4, False, length)

    save_data = serialise_utf8_string(save_data, save_stats["inquiry_code"])
    save_data = serialise_play_time(save_data, save_stats["play_time"])
    save_data = write(save_data, save_stats["unknown_25"])
    save_data = write_length_data(save_data, flatten_list(
        save_stats["itf_timed_scores"]), 4, 4, write_length=False)
    save_data = write(save_data, save_stats["unknown_27"])

    save_data = write_length_data(save_data, save_stats["cat_related_data_1"])

    save_data = write(save_data, save_stats["unknown_28"])
    save_data = write(save_data, save_stats["gv_45"])
    save_data = write(save_data, save_stats["gv_46"])
    save_data = write(save_data, save_stats["unknown_29"])
    save_data = write(save_data, save_stats["unknown_30"])
    save_data = write_length_data(
        save_data, save_stats["lucky_tickets_1"], write_length=False)
    save_data = write_length_data(
        save_data, save_stats["unknown_32"], write_length=False)
    save_data = write(save_data, save_stats["gv_47"])
    save_data = write(save_data, save_stats["gv_48"])
    save_data = write(save_data, save_stats["unknown_34"])
    save_data = write_length_data(save_data, save_stats["unknown_35"])
    save_data = write(save_data, save_stats["unknown_36"])

    save_data = write(save_data, save_stats["user_rank_popups"])

    save_data = write(save_data, save_stats["unknown_37"])
    save_data = write(save_data, save_stats["gv_49"])
    save_data = write(save_data, save_stats["gv_50"])
    save_data = write(save_data, save_stats["gv_51"])

    save_data = write_length_data(
        save_data, save_stats["cat_guide_collected"], bytes=1)
    save_data = write(save_data, save_stats["gv_52"])

    save_data = write_length_data(
        save_data, save_stats["unknown_40"], write_length=False, bytes=8)

    save_data = write_length_data(save_data, save_stats["cat_fruit"])

    save_data = write_length_data(save_data, save_stats["cat_related_data_3"])
    save_data = write_length_data(save_data, save_stats["catseye_cat_data"])
    save_data = write_length_data(save_data, save_stats["catseyes"])
    save_data = write_length_data(save_data, save_stats["catamins"])

    save_data = write(save_data, save_stats["unknown_42"])
    save_data = write(save_data, save_stats["gamatoto_xp"])

    save_data = write_length_data(
        save_data, save_stats["unknown_43"], write_length=False)
    save_data = write_length_data(save_data, save_stats["unknown_44"], bytes=1)
    save_data = write_length_data(
        save_data, save_stats["unknown_45"], bytes=12*4)

    save_data = write(save_data, save_stats["gv_53"])

    save_data = write_length_data(save_data, save_stats["helpers"])

    save_data = write(save_data, save_stats["unknown_47"])

    save_data = write(save_data, save_stats["gv_54"])
    save_data = serialise_wierd_plat_ticket_data(
        save_data, save_stats["wierd_plat_ticket_data"])
    save_data = write(save_data, save_stats["gv_54"])
    save_data = write(save_data, save_stats["gamatoto_skin"])
    save_data = write(save_data, save_stats["platinum_tickets"])

    save_data = write_length_data(save_data, save_stats["unknown_48"], bytes=8)
    save_data = write(save_data, save_stats["unknown_49"])
    save_data = write_length_data(
        save_data, save_stats["unknown_50"], write_length=False)

    save_data = write(save_data, save_stats["gv_55"])

    save_data = write(save_data, save_stats["unknown_51"])

    save_data = serialise_outbreaks(save_data, save_stats["outbreaks"])

    save_data = write(save_data, save_stats["unknown_52"])
    save_data = write_length_data(save_data, save_stats["unknown_53"])
    save_data = write_length_data(save_data, save_stats["unknown_54"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_55"])

    save_data = write_length_data(save_data, save_stats["base_materials"])

    save_data = write(save_data, save_stats["unknown_56"])
    save_data = write(save_data, save_stats["unknown_57"])
    save_data = write(save_data, save_stats["unknown_58"])

    save_data = write(save_data, save_stats["engineers"])
    save_data = serialise_ototo_cat_cannon(
        save_data, save_stats["ototo_cannon"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_59"])
    save_data = serialise_tower(save_data, save_stats["tower"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_60"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_61"])
    save_data = write(save_data, save_stats["challenge"]["Score"])
    save_data = write(save_data, save_stats["challenge"]["Cleared"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_102"])

    save_data = serialise_uncanny_current(
        save_data, save_stats["uncanny_current"])
    save_data = serialise_uncanny_progress(save_data, save_stats["uncanny"])

    save_data = write(save_data, save_stats["unknown_62"])
    save_data = write_length_data(
        save_data, save_stats["unknown_63"], write_length=False)

    save_data = serialise_uncanny_current(
        save_data, save_stats["unknown_64"]["current"])
    save_data = serialise_uncanny_progress(
        save_data, save_stats["unknown_64"]["progress"])

    save_data = write(save_data, save_stats["unknown_65"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_66"])

    save_data = write_length_data(
        save_data, save_stats["lucky_tickets_2"], write_length=False)

    save_data = write_length_data(
        save_data, save_stats["unknown_67"], write_length=False)

    save_data = write(save_data, save_stats["unknown_68"])

    save_data = write(save_data, save_stats["gv_77"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_69"])

    save_data = serialise_talent_data(save_data, save_stats["talents"])
    save_data = write(save_data, save_stats["np"])

    save_data = write(save_data, save_stats["unknown_70"])

    save_data = write(save_data, save_stats["gv_80000"])

    save_data = write(save_data, save_stats["unknown_71"])

    save_data = write(save_data, save_stats["leadership"])

    save_data = write(save_data, save_stats["unknown_72"])

    save_data = write(save_data, save_stats["gv_80200"])

    save_data = write(save_data, save_stats["unknown_73"])

    save_data = write(save_data, save_stats["gv_80300"])

    save_data = write_length_data(save_data, save_stats["unknown_74"])

    save_data = write(save_data, save_stats["gv_80500"])

    save_data = write_length_data(save_data, save_stats["unknown_75"], 2)
    save_data = serialise_dumped_data(save_data, save_stats["unknown_76"])

    save_data = write(save_data, save_stats["gv_80700"])

    save_data = write(save_data, save_stats["unknown_104"])

    save_data = write(save_data, save_stats["restart_pack"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_101"])
    save_data = serialise_medals(save_data, save_stats["medals"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_103"])

    save_data = serialise_gauntlet_current(
        save_data, save_stats["gauntlet_current"])
    save_data = serialise_gauntlet_progress(save_data, save_stats["gauntlets"])

    save_data = write_length_data(
        save_data, save_stats["unknown_77"], bytes=1, write_length=False)

    save_data = write(save_data, save_stats["gv_90300"])

    save_data = serialise_gauntlet_current(save_data, save_stats["unknown_78"])
    save_data = serialise_gauntlet_progress(
        save_data, save_stats["unknown_79"])
    save_data = write_length_data(
        save_data, save_stats["unknown_80"], bytes=1, write_length=False)
    save_data = serialise_dumped_data(save_data, save_stats["unknown_81"])
    save_data = serialise_gauntlet_current(save_data, save_stats["unknown_82"])
    save_data = serialise_gauntlet_progress(
        save_data, save_stats["unknown_83"])
    save_data = write_length_data(
        save_data, save_stats["unknown_84"], bytes=1, write_length=False)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_85"])

    save_data = serialise_talent_orbs(
        save_data, save_stats["talent_orbs"], save_stats["game_version"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_86"])

    save_data = write(save_data, save_stats["legend_tickets"])

    save_data = write_length_data(
        save_data, save_stats["unknown_87"], bytes=5, length_bytes=1)
    save_data = write(save_data, save_stats["unknown_88"])

    save_data = serialise_utf8_string(save_data, save_stats["token"])
    save_data = write(save_data, save_stats["unknown_89"])
    save_data = write(save_data, save_stats["unknown_90"])
    save_data = write(save_data, save_stats["unknown_91"])

    data = check_gv(save_data, save_stats, 100000)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100000"])

    save_data = write(save_data, save_stats["unknown_92"])

    data = check_gv(save_data, save_stats, 100100)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100100"])

    save_data = write_length_data(
        save_data, save_stats["unknown_93"], bytes=19, write_length=False)

    data = check_gv(save_data, save_stats, 100300)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100300"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_94"])
    save_data = write(save_data, save_stats["platinum_shards"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_100"])

    data = check_gv(save_data, save_stats, 100700)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100700"])

    save_data = serialise_aku(save_data, save_stats["aku"])

    save_data = write(save_data, save_stats["unknown_95"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_96"])

    data = check_gv(save_data, save_stats, 100900)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100900"])

    save_data = write(save_data, save_stats["unknown_97"])

    data = check_gv(save_data, save_stats, 101000)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_101000"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_98"])

    data = check_gv(save_data, save_stats, 110000)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_110000"])

    save_data = write(save_data, save_stats["extra_data"])

    save_data = exit_serialiser(save_data, save_stats)

    return bytes(save_data)
