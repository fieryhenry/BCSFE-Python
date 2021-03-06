"""Handler for serialising save data from dict"""

import json
import os
import struct
import sys
import traceback
from typing import Union

import dateutil.parser

from . import helper, parse_save, updater, user_input_handler


def write(save_data: bytes, number: int, length: int = None) -> bytes:
    """Writes a little endian number to the save data"""
    if length is None:
        length = number["Length"]
    if isinstance(number, dict):
        number = number["Value"]
    number = int(number)
    data = list(helper.num_to_bytes(number, length))

    save_data += data

    return save_data


def create_list_separated(data: list, length: int) -> list:
    """Creates a list of bytes from a list of numbers"""

    lst = []
    for item in data:
        byte_data = list(helper.num_to_bytes(item, length))
        lst += byte_data
    return lst


def create_list_double(data: list) -> list:
    """Creates a list of bytes from a list of doubles"""

    lst = []
    for item in data:
        byte_data = list(struct.pack("d", item))
        lst += byte_data
    return lst


def write_length_data(
    save_data: bytes,
    data: Union[list, dict],
    length_bytes: int = 4,
    bytes_per_val: int = 4,
    write_length: bool = True,
    length: int = None,
) -> bytes:
    """Writes a list of ints to the save data"""

    if write_length is False and length is None:
        length = len(data)
    if isinstance(data, dict):
        data = data["Value"]

    if write_length:
        if length is None:
            length = len(data)
        length_data = list(helper.num_to_bytes(length, length_bytes))
        save_data += length_data

    save_data += create_list_separated(data, bytes_per_val)

    return save_data


def write_length_doubles(
    save_data: bytes,
    data: Union[list, dict],
    length_bytes: int = 4,
    write_length: bool = True,
    length: int = None,
) -> bytes:
    """Writes a list of doubles to the save data"""

    if write_length is False and length is None:
        length = len(data)
    if isinstance(data, dict):
        data = data["Value"]

    if write_length:
        if length is None:
            length = len(data)
        length_data = list(helper.num_to_bytes(length, length_bytes))
        save_data += length_data

    save_data += create_list_double(data)

    return save_data


def serialise_time_data_skip(
    save_data: bytes,
    time_data: str,
    time_stamp: float,
    dst_flag: bool,
    duplicate: dict,
    dst: int = 0,
) -> bytes:
    time = dateutil.parser.parse(time_data)
    save_data = write(save_data, time.year, 4)
    save_data = write(save_data, duplicate["yy"], 4)

    save_data = write(save_data, time.month, 4)
    save_data = write(save_data, duplicate["mm"], 4)

    save_data = write(save_data, time.day, 4)
    save_data = write(save_data, duplicate["dd"], 4)

    save_data = write_double(save_data, time_stamp)

    save_data = write(save_data, time.hour, 4)
    save_data = write(save_data, time.minute, 4)
    save_data = write(save_data, time.second, 4)

    if dst_flag:
        save_data = write(save_data, dst, 1)

    return save_data


def serialise_time_data(
    save_data: bytes, time: str, dst_flag: bool, dst: int = 0
) -> bytes:
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


def serialise_equip_slots(save_data: bytes, equip_slots: list) -> bytes:
    save_data = write(save_data, len(equip_slots), 1)
    for slot in equip_slots:
        save_data = write_length_data(save_data, slot, 0, 4, False)
    return save_data


def serialise_main_story(save_data: bytes, story_chapters: dict) -> bytes:
    save_data = write_length_data(
        save_data, story_chapters["Chapter Progress"], write_length=False
    )
    for chapter in story_chapters["Times Cleared"]:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_treasures(save_data: bytes, treasures: list) -> bytes:
    for chapter in treasures:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_cat_upgrades(save_data: bytes, cat_upgrades: dict) -> bytes:
    data = []
    length = len(cat_upgrades["Base"])
    for cat_id in range(length):
        data.append(cat_upgrades["Plus"][cat_id])
        data.append(cat_upgrades["Base"][cat_id])
    write_length_data(save_data, data, 4, 2, True, length)
    return save_data


def serialise_blue_upgrades(save_data: bytes, blue_upgrades: dict) -> bytes:
    data = []
    length = len(blue_upgrades["Base"])
    for blue_id in range(length):
        data.append(blue_upgrades["Plus"][blue_id])
        data.append(blue_upgrades["Base"][blue_id])
    write_length_data(save_data, data, 4, 2, False)
    return save_data


def serialise_utf8_string(
    save_data: bytes,
    string: Union[dict, str],
    length_bytes: int = 4,
    write_length: bool = True,
    length: int = None,
) -> bytes:
    """Writes a string to the save data"""

    if isinstance(string, dict):
        string = string["Value"]
    data = string.encode("utf-8")

    save_data = write_length_data(
        save_data, data, length_bytes, 1, write_length, length
    )
    return save_data


def serialise_event_stages_current(save_data: bytes, event_current: dict) -> bytes:
    unknown_val = event_current["unknown"]
    total_sub_chapters = event_current["total"] // unknown_val
    stars_per_sub_chapter = event_current["stars"]
    stages_per_sub_chapter = event_current["stages"]

    save_data = write(save_data, unknown_val, 1)
    save_data = write(save_data, total_sub_chapters, 2)
    save_data = write(save_data, stars_per_sub_chapter, 1)
    save_data = write(save_data, stages_per_sub_chapter, 1)

    for i in range(len(event_current["Clear"])):
        save_data = write_length_data(save_data, event_current["Clear"][i], 1, 1, False)

    return save_data


def flatten_list(_2d_list) -> list:
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if isinstance(element, list):
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def serialise_event_stages(save_data: bytes, event_stages: dict) -> bytes:
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
                clear_amount[i * stages * stars + j * stars + k] = clear_amount_data[i][
                    k
                ][j]

    save_data = write_length_data(save_data, clear_amount, 4, 2, False)

    for chapter in event_stages["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)
    return save_data


def serialse_purchase_receipts(save_data: bytes, data: dict) -> bytes:
    save_data = write(save_data, len(data), 4)
    for item in data:
        save_data = write(save_data, item["unknown_4"], 4)
        save_data = write(save_data, len(item["item_packs"]), 4)
        for string_dict in item["item_packs"]:
            save_data = serialise_utf8_string(save_data, string_dict["Value"])
            save_data = write(save_data, string_dict["unknown_1"], 1)
    return save_data


def serialise_dumped_data(save_data: bytes, data: list) -> bytes:
    for item in data:
        save_data = write(save_data, item)
    return save_data


def serialise_outbreaks(save_data: bytes, outbreaks: dict) -> bytes:
    outbreak_data = outbreaks["outbreaks"]

    save_data = write(save_data, len(outbreak_data), 4)
    for chapter_id in outbreak_data:
        save_data = write(save_data, int(chapter_id), 4)
        save_data = write(save_data, outbreaks["stages_counts"][chapter_id], 4)
        for level_id in outbreak_data[chapter_id]:
            save_data = write(save_data, level_id, 4)
            save_data = write(save_data, outbreak_data[chapter_id][level_id], 1)

    return save_data


def serialise_ototo_cat_cannon(save_data: bytes, ototo_cannon: dict) -> bytes:
    save_data = write(save_data, len(ototo_cannon), 4)
    for cannon_id in ototo_cannon:
        cannon = ototo_cannon[cannon_id]

        save_data = write(save_data, int(cannon_id), 4)
        save_data = write(save_data, cannon["len_val"], 4)
        save_data = write(save_data, cannon["unlock_flag"], 4)
        save_data = write(save_data, cannon["level"], 4)
    return save_data


def serialise_uncanny_current(save_data: bytes, uncanny_current: dict) -> bytes:
    total_sub_chapters = uncanny_current["total"]
    stars_per_sub_chapter = uncanny_current["stars"]
    stages_per_sub_chapter = uncanny_current["stages"]

    save_data = write(save_data, total_sub_chapters, 4)
    save_data = write(save_data, stages_per_sub_chapter, 4)
    save_data = write(save_data, stars_per_sub_chapter, 4)

    for i in range(len(uncanny_current["Clear"])):
        save_data = write_length_data(
            save_data, uncanny_current["Clear"][i], 4, 4, False
        )

    return save_data


def serialise_uncanny_progress(save_data: bytes, uncanny: dict) -> bytes:
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
                clear_amount[i * stages * stars + j * stars + k] = clear_amount_data[i][
                    k
                ][j]

    save_data = write_length_data(save_data, clear_amount, 4, 4, False)

    for chapter in uncanny["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 4, 4, False)
    return save_data


def serialise_talent_data(save_data: bytes, talents: dict) -> bytes:
    save_data = write(save_data, len(talents), 4)
    for cat_id in talents:
        cat_talent_data = talents[cat_id]
        save_data = write(save_data, int(cat_id), 4)
        save_data = write(save_data, len(cat_talent_data), 4)
        for talent in cat_talent_data:
            save_data = write(save_data, talent["id"], 4)
            save_data = write(save_data, talent["level"], 4)
    return save_data


def serialise_gauntlet_current(save_data: bytes, gauntlet_current: dict) -> bytes:
    save_data = write(save_data, gauntlet_current["total"], 2)
    save_data = write(save_data, gauntlet_current["stages"], 1)
    save_data = write(save_data, gauntlet_current["stars"], 1)

    for i in range(len(gauntlet_current["Clear"])):
        save_data = write_length_data(
            save_data, gauntlet_current["Clear"][i], 1, 1, False
        )

    return save_data


def serialise_gauntlet_progress(save_data: bytes, gauntlets: dict) -> bytes:
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
                clear_amount[i * stages * stars + j * stars + k] = clear_amount_data[i][
                    k
                ][j]

    save_data = write_length_data(save_data, clear_amount, 4, 2, False)

    for chapter in gauntlets["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)
    return save_data


def serialise_talent_orbs(
    save_data: bytes, talent_orbs: dict, game_verison: dict
) -> bytes:
    save_data = write(save_data, len(talent_orbs), 2)
    for orb_id in talent_orbs:
        save_data = write(save_data, int(orb_id), 2)
        if game_verison["Value"] < 110400:
            save_data = write(save_data, talent_orbs[orb_id], 1)
        else:
            save_data = write(save_data, talent_orbs[orb_id], 2)
    return save_data


def serialise_aku(save_data: bytes, aku: dict) -> bytes:
    lengths = aku["Lengths"]
    save_data = write(save_data, lengths["total"], 2)
    save_data = write(save_data, lengths["stages"], 1)
    save_data = write(save_data, lengths["stars"], 1)
    save_data = serialise_gauntlet_progress(save_data, aku)
    return save_data


def serialise_tower(save_data: bytes, tower: dict) -> bytes:
    save_data = write(save_data, tower["current"]["total"], 4)
    save_data = write(save_data, tower["current"]["stars"], 4)

    for i in range(len(tower["current"]["selected"])):
        save_data = write_length_data(
            save_data, tower["current"]["selected"][i], 4, 4, False
        )

    save_data = write(save_data, tower["progress"]["total"], 4)
    save_data = write(save_data, tower["progress"]["stars"], 4)

    for i in range(len(tower["progress"]["clear_progress"])):
        save_data = write_length_data(
            save_data, tower["progress"]["clear_progress"][i], 4, 4, False
        )

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
                clear_amount[i * stages * stars + j * stars + k] = clear_amount_data[i][
                    k
                ][j]

    save_data = write_length_data(save_data, clear_amount, 4, 4, False)

    save_data = serialise_dumped_data(save_data, tower["data"])

    return save_data


def export_json(save_stats: dict, path: str):
    ordered_data = parse_save.re_order(save_stats)
    if os.path.isdir(path):
        path = os.path.join(path, "save_data.json")
    helper.write_file_string(path, json.dumps(ordered_data, indent=4))
    helper.colored_text(f"Successfully wrote json to &{os.path.abspath(path)}&")


def exit_serialiser(save_data: bytes, save_stats) -> bytes:
    return serialise_utf8_string(save_data, save_stats["hash"], write_length=False)


def check_gv(save_data: bytes, save_stats: dict, game_version: int) -> dict:
    if save_stats["game_version"]["Value"] < game_version:
        save_data = exit_serialiser(save_data, save_stats)
        return {"save_data": save_data, "exit": True}
    else:
        return {"save_data": save_data, "exit": False}


def serialise_medals(save_data: bytes, medals: dict) -> bytes:
    save_data = write_length_data(save_data, medals["medal_data_1"], 2, 2)
    medal_data_2 = medals["medal_data_2"]
    save_data = write(save_data, len(medal_data_2), 2)
    for medal_id in medal_data_2:
        save_data = write(save_data, medal_id, 2)
        save_data = write(save_data, medal_data_2[medal_id], 1)
    return save_data


def serialise_play_time(save_data: bytes, play_time: dict) -> bytes:
    frames = helper.time_to_frames(play_time)
    save_data = write(save_data, frames, 4)
    return save_data


def serialise_mission_segment(save_data: bytes, data: dict) -> bytes:
    save_data = write(save_data, len(data), 4)
    for mission in data:
        save_data = write(save_data, mission, 4)
        save_data = write(save_data, data[mission], 4)
    return save_data


def serialise_missions(save_data: bytes, missions: dict) -> bytes:
    save_data = serialise_mission_segment(save_data, missions["flags"])
    save_data = serialise_mission_segment(save_data, missions["values"])
    return save_data


def serialise_dojo(save_data: bytes, dojo_data: dict) -> bytes:
    save_data = write(save_data, len(dojo_data), 4)
    for subchapter_id in dojo_data:
        subchapter_data = dojo_data[subchapter_id]

        save_data = write(save_data, subchapter_id, 4)
        save_data = write(save_data, len(subchapter_data), 4)

        for stage_id in subchapter_data:
            score = subchapter_data[stage_id]

            save_data = write(save_data, stage_id, 4)
            save_data = write(save_data, score, 4)
    return save_data


def write_double(save_data: bytes, number: float) -> bytes:
    """Writes a double to the save data"""

    if isinstance(number, dict):
        number = number["Value"]
    number = float(number)
    data = struct.pack("d", number)

    save_data += data

    return save_data


def start_serialize(save_stats: dict) -> dict:
    """Starts the serialisation process"""
    if "editor_version" not in save_stats:
        helper.colored_text("An invalid save file / json file has been provided")
        sys.exit(1)
    try:
        if save_stats["editor_version"] != updater.get_local_version():
            print(
                "WARNING: this json data was created in an older editor version and may not work"
            )
        save_data = serialize_save(save_stats)
    except Exception:
        helper.colored_text(
            "\nError: An error has occurred while writing your save stats:",
            base=helper.RED,
        )
        traceback.print_exc()
        user_input_handler.colored_input(
            "\nPlease report this to &#bug-reports&, and/or &dm me your save& on discord.\nPress enter to exit:"
        )
        sys.exit(1)
    return save_data


def serialize_save(save_stats: dict) -> dict:
    """Serialises the save stats"""

    save_data = []

    save_data = write(save_data, save_stats["game_version"])

    save_data = write(save_data, save_stats["unknown_1"])

    save_data = write(save_data, save_stats["sound_effects"])
    save_data = write(save_data, save_stats["music"])

    save_data = write(save_data, save_stats["cat_food"])
    save_data = write(save_data, save_stats["current_energy"])
    if save_stats["extra_time_data"]:
        save_data = write(save_data, save_stats["extra_time_data"])
    save_data = serialise_time_data_skip(
        save_data,
        save_stats["time"],
        save_stats["time_stamp"],
        save_stats["dst"],
        save_stats["duplicate_time"],
        save_stats["dst_val"],
    )

    save_data = write_length_data(
        save_data, save_stats["unknown_flags_1"], write_length=False
    )

    save_data = write(save_data, save_stats["xp"])

    save_data = write(save_data, save_stats["tutorial_cleared"])

    save_data = write_length_data(
        save_data, save_stats["unknown_flags_2"], write_length=False
    )
    save_data = write(save_data, save_stats["unknown_flag_1"])

    save_data = serialise_equip_slots(save_data, save_stats["slots"])
    save_data = write(save_data, save_stats["cat_stamp_current"])

    save_data = write_length_data(
        save_data, save_stats["cat_stamp_collected"], write_length=False
    )
    save_data = write_length_data(
        save_data, save_stats["unknown_2"], write_length=False
    )

    save_data = serialise_main_story(save_data, save_stats["story_chapters"])
    save_data = serialise_treasures(save_data, save_stats["treasures"])

    save_data = write_length_data(save_data, save_stats["enemy_guide"])

    save_data = write_length_data(save_data, save_stats["cats"])
    save_data = serialise_cat_upgrades(save_data, save_stats["cat_upgrades"])
    save_data = write_length_data(save_data, save_stats["current_forms"])

    save_data = serialise_blue_upgrades(save_data, save_stats["blue_upgrades"])

    save_data = write_length_data(save_data, save_stats["menu_unlocks"])
    save_data = write_length_data(save_data, save_stats["unknown_5"])

    save_data = write_length_data(save_data, save_stats["battle_items"], 4, 4, False, 6)
    save_data = write_length_data(save_data, save_stats["new_dialogs"])

    save_data = write(save_data, save_stats["unknown_6"])
    save_data = write_length_data(
        save_data, save_stats["unknown_7"], write_length=False
    )

    save_data = write(save_data, save_stats["lock_item"])
    save_data = write_length_data(save_data, save_stats["locked_items"], 1, 1, False, 6)

    save_data = serialise_time_data(
        save_data, save_stats["second_time"], save_stats["dst"], save_stats["dst_val"]
    )

    save_data = write_length_data(
        save_data, save_stats["unknown_8"], write_length=False
    )

    save_data = serialise_time_data(
        save_data, save_stats["third_time"], save_stats["dst"], save_stats["dst_val"]
    )

    save_data = write(save_data, save_stats["unknown_9"])

    save_data = serialise_utf8_string(save_data, save_stats["thirty2_code"])

    save_data = write(
        save_data, save_stats["unknown_10"], save_stats["unknown_10"]["Length"]
    )
    save_data = write_length_data(
        save_data, save_stats["unknown_11"], write_length=False
    )

    save_data = write(save_data, save_stats["normal_tickets"])
    save_data = write(save_data, save_stats["rare_tickets"])

    save_data = write_length_data(save_data, save_stats["other_cat_data"])

    save_data = write_length_data(
        save_data, save_stats["unknown_12"], write_length=False
    )

    if save_stats["cat_storage"]["len"]:
        save_data = write(save_data, len(save_stats["cat_storage"]["ids"]), 2)
    save_data = write_length_data(
        save_data, save_stats["cat_storage"]["ids"], 2, 4, False
    )
    save_data = write_length_data(
        save_data, save_stats["cat_storage"]["types"], 2, 4, False
    )

    save_data = serialise_event_stages_current(save_data, save_stats["event_current"])
    save_data = serialise_event_stages(save_data, save_stats["event_stages"])

    save_data = write_length_data(
        save_data, save_stats["unknown_15"], write_length=False
    )

    save_data = write_length_data(save_data, save_stats["unit_drops"])
    save_data = write(save_data, save_stats["rare_gacha_seed"])

    save_data = write(save_data, save_stats["unknown_17"])
    save_data = write(save_data, save_stats["unknown_18"])

    save_data = serialise_time_data(
        save_data, save_stats["fourth_time"], save_stats["dst"], save_stats["dst_val"]
    )

    save_data = write_length_data(save_data, save_stats["unknown_105"], 4, 4, False)

    save_data = write(save_data, save_stats["unknown_107"])
    if save_stats["dst"]:
        save_data = serialise_utf8_string(save_data, save_stats["unknown_110"])
    save_data = write(save_data, len(save_stats["unknown_108"]), 4)
    for i in range(len(save_stats["unknown_108"])):
        save_data = serialise_utf8_string(save_data, save_stats["unknown_108"][i])

    if save_stats["dst"]:
        save_data = write_length_doubles(
            save_data, save_stats["time_stamps"], write_length=False
        )

        save_data = write(save_data, len(save_stats["unknown_112"]), 4)
        for string in save_stats["unknown_112"]:
            save_data = serialise_utf8_string(save_data, string)
        save_data = write(save_data, save_stats["energy_notice"])
        save_data = write(save_data, save_stats["game_version_2"])

    save_data = write(save_data, save_stats["unknown_111"])
    save_data = write(save_data, save_stats["unlocked_slots"])

    save_data = write(save_data, save_stats["unknown_20"]["Length_1"], 4)
    save_data = write(save_data, save_stats["unknown_20"]["Length_2"], 4)
    save_data = write_length_data(
        save_data, save_stats["unknown_20"], write_length=False
    )

    save_data = write_length_doubles(
        save_data, save_stats["time_stamps_2"][:-1], write_length=False
    )

    save_data = write(save_data, save_stats["trade_progress"])

    if save_stats["dst"]:
        save_data = write_double(save_data, save_stats["time_stamps_2"][-1])
    else:
        save_data = write(save_data, save_stats["unknown_24"])

    save_data = write_length_data(save_data, save_stats["catseye_related_data"])

    save_data = write_length_data(
        save_data, save_stats["unknown_22"], write_length=False
    )

    save_data = write_length_data(save_data, save_stats["user_rank_rewards"], 4, 1)

    if not save_stats["dst"]:
        save_data = write_double(save_data, save_stats["time_stamps_2"][-1])

    save_data = write_length_data(save_data, save_stats["unlocked_forms"])

    save_data = serialise_utf8_string(save_data, save_stats["transfer_code"])
    save_data = serialise_utf8_string(save_data, save_stats["confirmation_code"])
    save_data = write(save_data, save_stats["transfer_flag"])

    lengths = save_stats["stage_data_related_1"]["Lengths"]
    length = lengths[0] * lengths[1] * lengths[2]
    save_data = write_length_data(save_data, lengths, write_length=False)
    save_data = write_length_data(
        save_data, save_stats["stage_data_related_1"], 4, 1, False, length
    )

    lengths = save_stats["event_timed_scores"]["Lengths"]
    length = lengths[0] * lengths[1] * lengths[2]
    save_data = write_length_data(save_data, lengths, write_length=False)
    save_data = write_length_data(
        save_data, save_stats["event_timed_scores"], 4, 4, False, length
    )

    save_data = serialise_utf8_string(save_data, save_stats["inquiry_code"])
    save_data = serialise_play_time(save_data, save_stats["play_time"])
    save_data = write(save_data, save_stats["unknown_25"])
    save_data = write_length_data(
        save_data,
        flatten_list(save_stats["itf_timed_scores"]),
        4,
        4,
        write_length=False,
    )
    save_data = write(save_data, save_stats["unknown_27"])

    save_data = write_length_data(save_data, save_stats["cat_related_data_1"])

    save_data = write(save_data, save_stats["unknown_28"])
    save_data = write(save_data, save_stats["gv_45"])
    save_data = write(save_data, save_stats["gv_46"])
    save_data = write(save_data, save_stats["unknown_29"])
    save_data = write_length_data(save_data, save_stats["lucky_tickets_1"])
    save_data = write_length_data(save_data, save_stats["unknown_32"])

    save_data = write(save_data, save_stats["gv_47"])
    save_data = write(save_data, save_stats["gv_48"])

    if not save_stats["dst"]:
        save_data = write(save_data, save_stats["energy_notice"])

    save_data = write_double(save_data, save_stats["account_created_time_stamp"])
    save_data = write_length_data(save_data, save_stats["unknown_35"])
    save_data = write(save_data, save_stats["unknown_36"])

    save_data = write(save_data, save_stats["user_rank_popups"])

    save_data = write(save_data, save_stats["unknown_37"])
    save_data = write(save_data, save_stats["gv_49"])
    save_data = write(save_data, save_stats["gv_50"])
    save_data = write(save_data, save_stats["gv_51"])

    save_data = write_length_data(
        save_data, save_stats["cat_guide_collected"], bytes_per_val=1
    )
    save_data = write(save_data, save_stats["gv_52"])

    save_data = write_length_doubles(
        save_data, save_stats["time_stamps_3"], write_length=False
    )

    save_data = write_length_data(save_data, save_stats["cat_fruit"])

    save_data = write_length_data(save_data, save_stats["cat_related_data_3"])
    save_data = write_length_data(save_data, save_stats["catseye_cat_data"])
    save_data = write_length_data(save_data, save_stats["catseyes"])
    save_data = write_length_data(save_data, save_stats["catamins"])

    seconds = helper.time_to_seconds(save_stats["gamatoto_time_left"])
    save_data = write_double(save_data, float(seconds))
    save_data = write(save_data, save_stats["gamatoto_exclamation"])
    save_data = write(save_data, save_stats["gamatoto_xp"])
    save_data = write(save_data, save_stats["gamamtoto_destination"])
    save_data = write(save_data, save_stats["gamatoto_recon_length"])

    save_data = write(save_data, save_stats["unknown_43"])

    save_data = write(save_data, save_stats["gamatoto_complete_notification"])

    save_data = write_length_data(save_data, save_stats["unknown_44"], bytes_per_val=1)
    save_data = write_length_data(
        save_data, save_stats["unknown_45"], bytes_per_val=12 * 4
    )

    save_data = write(save_data, save_stats["gv_53"])

    save_data = write_length_data(save_data, save_stats["helpers"])

    save_data = write(save_data, save_stats["unknown_47"])

    save_data = write(save_data, save_stats["gv_54"])
    save_data = serialse_purchase_receipts(save_data, save_stats["purchases"])
    save_data = write(save_data, save_stats["gv_54"])
    save_data = write(save_data, save_stats["gamatoto_skin"])
    save_data = write(save_data, save_stats["platinum_tickets"])

    save_data = write_length_data(save_data, save_stats["unknown_48"], bytes_per_val=8)
    save_data = write(save_data, save_stats["unknown_49"])
    save_data = write_length_data(
        save_data, save_stats["unknown_50"], write_length=False
    )

    save_data = write(save_data, save_stats["gv_55"])

    save_data = write(save_data, save_stats["unknown_51"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_113"])

    save_data = serialise_dojo(save_data, save_stats["dojo_data"])

    save_data = write(save_data, save_stats["unknown_114"])

    save_data = write(save_data, save_stats["gv_58"])

    save_data = write(save_data, save_stats["unknown_115"])

    save_data = serialise_outbreaks(save_data, save_stats["outbreaks"])

    save_data = write_double(save_data, save_stats["unknown_52"])
    save_data = write_length_data(save_data, save_stats["unknown_53"])
    save_data = write_length_data(save_data, save_stats["unknown_54"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_55"])

    save_data = write_length_data(save_data, save_stats["base_materials"])

    save_data = write(save_data, save_stats["unknown_56"])
    save_data = write(save_data, save_stats["unknown_57"])
    save_data = write(save_data, save_stats["unknown_58"])

    save_data = write(save_data, save_stats["engineers"])
    save_data = serialise_ototo_cat_cannon(save_data, save_stats["ototo_cannon"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_59"])
    save_data = serialise_tower(save_data, save_stats["tower"])
    save_data = serialise_missions(save_data, save_stats["missions"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_60"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_61"])
    save_data = write(save_data, save_stats["challenge"]["Score"])
    save_data = write(save_data, save_stats["challenge"]["Cleared"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_102"])

    save_data = serialise_uncanny_current(save_data, save_stats["uncanny_current"])
    save_data = serialise_uncanny_progress(save_data, save_stats["uncanny"])

    save_data = write(save_data, save_stats["unknown_62"])
    save_data = write_length_data(
        save_data, save_stats["unknown_63"], write_length=False
    )

    save_data = serialise_uncanny_current(
        save_data, save_stats["unknown_64"]["current"]
    )
    save_data = serialise_uncanny_progress(
        save_data, save_stats["unknown_64"]["progress"]
    )

    save_data = write(save_data, save_stats["unknown_65"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_66"])

    save_data = write_length_data(
        save_data, save_stats["lucky_tickets_2"], write_length=False
    )

    save_data = write_length_data(
        save_data, save_stats["unknown_67"], write_length=False
    )

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
    if save_stats["dst"]:
        if save_stats["gv_100600"]["Value"] == 100600:
            save_data = write(save_data, save_stats["unknown_104"])
            save_data = write(save_data, save_stats["gv_100600"])

    save_data = write(save_data, save_stats["restart_pack"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_101"])
    save_data = serialise_medals(save_data, save_stats["medals"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_103"])

    save_data = serialise_gauntlet_current(save_data, save_stats["gauntlet_current"])
    save_data = serialise_gauntlet_progress(save_data, save_stats["gauntlets"])

    save_data = write_length_data(
        save_data, save_stats["unknown_77"], bytes_per_val=1, write_length=False
    )

    save_data = write(save_data, save_stats["gv_90300"])

    save_data = serialise_gauntlet_current(save_data, save_stats["unknown_78"])
    save_data = serialise_gauntlet_progress(save_data, save_stats["unknown_79"])
    save_data = write_length_data(
        save_data, save_stats["unknown_80"], bytes_per_val=1, write_length=False
    )
    save_data = serialise_dumped_data(save_data, save_stats["unknown_81"])
    save_data = serialise_gauntlet_current(save_data, save_stats["unknown_82"])
    save_data = serialise_gauntlet_progress(save_data, save_stats["unknown_83"])
    save_data = write_length_data(
        save_data, save_stats["unknown_84"], bytes_per_val=1, write_length=False
    )

    save_data = serialise_dumped_data(save_data, save_stats["unknown_85"])

    save_data = serialise_talent_orbs(
        save_data, save_stats["talent_orbs"], save_stats["game_version"]
    )

    save_data = serialise_dumped_data(save_data, save_stats["unknown_86"])
    if save_stats["game_version"]["Value"] >= 110600:
        save_data = write(save_data, len(save_stats["slot_names"]), 1)
    for slot_name in save_stats["slot_names"]:
        save_data = serialise_utf8_string(save_data, slot_name)

    save_data = write(save_data, save_stats["gv_91000"])

    save_data = write(save_data, save_stats["legend_tickets"])

    save_data = write_length_data(
        save_data, save_stats["unknown_87"], bytes_per_val=5, length_bytes=1
    )
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

    save_data = write(save_data, save_stats["date_int"])

    data = check_gv(save_data, save_stats, 100100)
    save_data = data["save_data"]
    if data["exit"]:
        return save_data
    save_data = write(save_data, save_stats["gv_100100"])

    save_data = write_length_data(
        save_data, save_stats["unknown_93"], bytes_per_val=19, write_length=False
    )

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
