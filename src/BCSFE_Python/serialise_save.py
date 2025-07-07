"""Handler for serialising save data from dict"""

import base64
import struct
from typing import Any, Union

import dateutil.parser

from . import helper, parse_save


def write(
    save_data: list[int],
    number: Union[dict[str, int], int],
    length: Union[int, None] = None,
) -> list[int]:
    """Writes a little endian number to the save data"""
    if length is None and isinstance(number, dict):
        length = number["Length"]
    if isinstance(number, dict):
        number = number["Value"]
    if length is None:
        raise ValueError("Length is None")
    number = int(number)
    data = list(helper.num_to_bytes(number, length))

    save_data += data

    return save_data


def create_list_separated(data: list[int], length: int) -> list[int]:
    """Creates a list of bytes from a list of numbers"""

    lst: list[int] = []
    for item in data:
        byte_data = list(helper.num_to_bytes(item, length))
        lst += byte_data
    return lst


def create_list_double(data: list[float]) -> list[int]:
    """Creates a list of bytes from a list of doubles"""

    lst: list[int] = []
    for item in data:
        byte_data = list(struct.pack("d", item))
        lst += byte_data
    return lst


def write_length_data(
    save_data: list[int],
    data: Union[list[int], dict[str, list[int]]],
    length_bytes: int = 4,
    bytes_per_val: int = 4,
    write_length: bool = True,
    length: Union[int, None] = None,
) -> list[int]:
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
    save_data: list[int],
    data: Union[list[float], dict[str, list[float]]],
    length_bytes: int = 4,
    write_length: bool = True,
    length: Union[None, int] = None,
) -> list[int]:
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
    save_data: list[int],
    time_data: str,
    time_stamp: float,
    dst_flag: bool,
    duplicate: dict[str, Any],
    dst: int = 0,
) -> list[int]:
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
    save_data: list[int], time: str, dst_flag: bool, dst: int = 0
) -> list[int]:
    time_d = dateutil.parser.parse(time)
    if dst_flag:
        save_data = write(save_data, dst, 1)

    save_data = write(save_data, time_d.year, 4)
    save_data = write(save_data, time_d.month, 4)
    save_data = write(save_data, time_d.day, 4)
    save_data = write(save_data, time_d.hour, 4)
    save_data = write(save_data, time_d.minute, 4)
    save_data = write(save_data, time_d.second, 4)

    return save_data


def serialise_equip_slots(
    save_data: list[int], equip_slots: list[list[int]]
) -> list[int]:
    save_data = write(save_data, len(equip_slots), 1)
    for slot in equip_slots:
        save_data = write_length_data(save_data, slot, 0, 4, False)
    return save_data


def serialise_main_story(
    save_data: list[int], story_chapters: dict[str, list[Any]]
) -> list[int]:
    save_data = write_length_data(
        save_data, story_chapters["Chapter Progress"], write_length=False
    )
    for chapter in story_chapters["Times Cleared"]:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_treasures(save_data: list[int], treasures: list[list[int]]) -> list[int]:
    for chapter in treasures:
        save_data = write_length_data(save_data, chapter, write_length=False)
    return save_data


def serialise_cat_upgrades(
    save_data: list[int], cat_upgrades: dict[str, list[int]]
) -> list[int]:
    data: list[int] = []
    length = len(cat_upgrades["Base"])
    for cat_id in range(length):
        data.append(cat_upgrades["Plus"][cat_id])
        data.append(cat_upgrades["Base"][cat_id])
    write_length_data(save_data, data, 4, 2, True, length)
    return save_data


def serialise_blue_upgrades(
    save_data: list[int], blue_upgrades: dict[str, list[int]]
) -> list[int]:
    data: list[int] = []
    length = len(blue_upgrades["Base"])
    for blue_id in range(length):
        data.append(blue_upgrades["Plus"][blue_id])
        data.append(blue_upgrades["Base"][blue_id])
    write_length_data(save_data, data, 4, 2, False)
    return save_data


def serialise_utf8_string(
    save_data: list[int],
    string: Union[dict[str, str], str],
    length_bytes: int = 4,
    write_length: bool = True,
    length: Union[int, None] = None,
) -> list[int]:
    """Writes a string to the save data"""

    if isinstance(string, dict):
        string = string["Value"]
    data = list(string.encode("utf-8"))

    save_data = write_length_data(
        save_data, data, length_bytes, 1, write_length, length
    )
    return save_data


def serialise_event_stages_current(
    save_data: list[int], event_current: dict[str, Any]
) -> list[int]:
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


def flatten_list(_2d_list: Union[list[list[Any]], list[Any]]) -> list[Any]:
    flat_list: list[Any] = []
    # Iterate through the outer list
    for element in _2d_list:
        if isinstance(element, list):
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list


def serialise_event_stages(
    save_data: list[int], event_stages: dict[str, Any]
) -> list[int]:
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


def serialse_purchase_receipts(save_data: list[int], data: dict[Any, Any]) -> list[int]:
    save_data = write(save_data, len(data), 4)
    for item in data:
        save_data = write(save_data, item["unknown_4"], 4)
        save_data = write(save_data, len(item["item_packs"]), 4)
        for string_dict in item["item_packs"]:
            save_data = serialise_utf8_string(save_data, string_dict["Value"])
            save_data = write(save_data, string_dict["unknown_1"], 1)
    return save_data


def serialise_dumped_data(
    save_data: list[int], data: list[dict[str, int]]
) -> list[int]:
    for item in data:
        save_data = write(save_data, item)
    return save_data


def serialise_outbreaks(save_data: list[int], outbreaks: dict[Any, Any]) -> list[int]:
    save_data = write(save_data, len(outbreaks), 4)
    for chapter_id in outbreaks:
        save_data = write(save_data, int(chapter_id), 4)
        save_data = write(save_data, len(outbreaks[chapter_id]), 4)
        for level_id in outbreaks[chapter_id]:
            save_data = write(save_data, level_id, 4)
            save_data = write(save_data, outbreaks[chapter_id][level_id], 1)

    return save_data


def serialise_ototo_cat_cannon(
    save_data: list[int], ototo_cannon: dict[int, Any]
) -> list[int]:
    save_data = write(save_data, len(ototo_cannon), 4)
    for cannon_id in ototo_cannon:
        cannon = ototo_cannon[cannon_id]

        save_data = write(save_data, int(cannon_id), 4)
        save_data = write(save_data, cannon["len_val"], 4)
        save_data = write(save_data, cannon["unlock_flag"], 4)
        levels = cannon["levels"]
        save_data = write(save_data, levels["effect"], 4)
        if cannon["len_val"] == 4:
            save_data = write(save_data, levels["foundation"], 4)
            save_data = write(save_data, levels["style"], 4)
    return save_data


def serialise_uncanny_current(
    save_data: list[int], uncanny_current: dict[str, Any]
) -> list[int]:
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


def serialise_event_timed_scores(
    save_data: list[int], timed_scores: dict[str, Any]
) -> list[int]:
    total_sub_chapters = timed_scores["total"]
    stars_per_sub_chapter = timed_scores["stars"]
    stages_per_sub_chapter = timed_scores["stages"]

    save_data = write(save_data, total_sub_chapters, 4)
    save_data = write(save_data, stages_per_sub_chapter, 4)
    save_data = write(save_data, stars_per_sub_chapter, 4)

    for i in range(len(timed_scores["Score"])):
        save_data = write_length_data(save_data, timed_scores["Score"][i], 4, 4, False)

    return save_data


def serialise_uncanny_progress(
    save_data: list[int], uncanny: dict[str, Any]
) -> list[int]:
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


def serialise_talent_data(save_data: list[int], talents: dict[str, Any]) -> list[int]:
    save_data = write(save_data, len(talents), 4)
    for cat_id in talents:
        cat_talent_data = talents[cat_id]
        save_data = write(save_data, int(cat_id), 4)
        save_data = write(save_data, len(cat_talent_data), 4)
        for talent in cat_talent_data:
            save_data = write(save_data, talent["id"], 4)
            save_data = write(save_data, talent["level"], 4)
    return save_data


def serialise_gauntlet_current(
    save_data: list[int], gauntlet_current: dict[str, Any]
) -> list[int]:
    save_data = write(save_data, gauntlet_current["total"], 2)
    save_data = write(save_data, gauntlet_current["stages"], 1)
    save_data = write(save_data, gauntlet_current["stars"], 1)

    for i in range(len(gauntlet_current["Clear"])):
        save_data = write_length_data(
            save_data, gauntlet_current["Clear"][i], 1, 1, False
        )

    return save_data


def serialise_gauntlet_progress(
    save_data: list[int], gauntlets: dict[str, Any]
) -> list[int]:
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


def serialise_legend_quest_current(
    save_data: list[int], legend_quest_current: dict[str, Any]
) -> list[int]:
    save_data = write(save_data, legend_quest_current["total"], 1)
    save_data = write(save_data, legend_quest_current["stages"], 1)
    save_data = write(save_data, legend_quest_current["stars"], 1)

    for i in range(len(legend_quest_current["Clear"])):
        save_data = write_length_data(
            save_data, legend_quest_current["Clear"][i], 1, 1, False
        )

    return save_data


def serialise_legend_quest_progress(
    save_data: list[int], legend_quests: dict[str, Any]
) -> list[int]:
    lengths = legend_quests["Lengths"]
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    for chapter in legend_quests["Value"]["clear_progress"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)

    clear_amount = [0] * total * stars * stages
    clear_amount_data = legend_quests["Value"]["clear_amount"]
    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                clear_amount[i * stages * stars + j * stars + k] = clear_amount_data[i][
                    k
                ][j]

    tries = [0] * total * stars * stages
    tries_data = legend_quests["Value"]["tries"]
    for i in range(total):
        for j in range(stages):
            for k in range(stars):
                tries[i * stages * stars + j * stars + k] = tries_data[i][k][j]

    save_data = write_length_data(save_data, clear_amount, 4, 2, False)
    save_data = write_length_data(save_data, tries, 4, 2, False)

    for chapter in legend_quests["Value"]["unlock_next"]:
        save_data = write_length_data(save_data, chapter, 1, 1, False)
    return save_data


def serialise_talent_orbs(
    save_data: list[int], talent_orbs: dict[str, int], game_verison: dict[str, int]
) -> list[int]:
    save_data = write(save_data, len(talent_orbs), 2)
    for orb_id in talent_orbs:
        save_data = write(save_data, int(orb_id), 2)
        if game_verison["Value"] < 110400:
            save_data = write(save_data, talent_orbs[orb_id], 1)
        else:
            save_data = write(save_data, talent_orbs[orb_id], 2)
    return save_data


def serialise_aku(save_data: list[int], aku: dict[str, Any]) -> list[int]:
    lengths = aku["Lengths"]
    save_data = write(save_data, lengths["total"], 2)
    save_data = write(save_data, lengths["stages"], 1)
    save_data = write(save_data, lengths["stars"], 1)
    save_data = serialise_gauntlet_progress(save_data, aku)
    return save_data


def serialise_tower(save_data: list[int], tower: dict[str, Any]) -> list[int]:
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


def exit_serialiser(save_data: list[int], save_stats: dict[str, Any]) -> list[int]:
    return serialise_utf8_string(save_data, save_stats["hash"], write_length=False)


def check_gv(
    save_data: list[int], save_stats: dict[str, Any], game_version: int
) -> dict[str, Any]:
    if save_stats["game_version"]["Value"] < game_version:
        save_data = exit_serialiser(save_data, save_stats)
        return {"save_data": save_data, "exit": True}
    else:
        return {"save_data": save_data, "exit": False}


def serialise_medals(save_data: list[int], medals: dict[str, Any]) -> list[int]:
    save_data = write_length_data(save_data, medals["medal_data_1"], 2, 2)
    medal_data_2 = medals["medal_data_2"]
    save_data = write(save_data, len(medal_data_2), 2)
    for medal_id in medal_data_2:
        save_data = write(save_data, medal_id, 2)
        save_data = write(save_data, medal_data_2[medal_id], 1)
    return save_data


def serialise_play_time(save_data: list[int], play_time: dict[str, Any]) -> list[int]:
    frames = helper.time_to_frames(play_time)
    save_data = write(save_data, frames, 4)
    return save_data


def serialise_mission_segment(save_data: list[int], data: dict[int, Any]) -> list[int]:
    save_data = write(save_data, len(data), 4)
    for mission in data:
        save_data = write(save_data, mission, 4)
        save_data = write(save_data, data[mission], 4)
    return save_data


def serialise_missions(
    save_data: list[int], missions_data: dict[str, Any]
) -> list[int]:
    save_data = serialise_mission_segment(save_data, missions_data["states"])
    save_data = serialise_mission_segment(save_data, missions_data["requirements"])
    save_data = serialise_mission_segment(save_data, missions_data["clear_types"])
    save_data = serialise_mission_segment(save_data, missions_data["gamatoto"])
    save_data = serialise_mission_segment(save_data, missions_data["nyancombo"])
    save_data = serialise_mission_segment(save_data, missions_data["user_rank"])
    save_data = serialise_mission_segment(save_data, missions_data["expiry"])
    save_data = serialise_mission_segment(save_data, missions_data["preparing"])

    return save_data


def serialise_dojo(save_data: list[int], dojo_data: dict[int, Any]) -> list[int]:
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


def write_double(save_data: list[int], number: float) -> list[int]:
    """Writes a double to the save data"""

    if isinstance(number, dict):
        number = number["Value"]
    number = float(number)
    data = struct.pack("d", number)

    save_data += data

    return save_data


def start_serialize(save_stats: dict[str, Any]) -> bytes:
    """Starts the serialisation process"""

    try:
        save_data = serialize_save(save_stats)
    except Exception as e:  # pylint: disable=broad-except
        helper.colored_text(
            "\nError: An error has occurred while serializing your save data:",
            base=helper.RED,
        )
        game_version = save_stats["game_version"]["Value"]
        if game_version < 110000:
            helper.colored_text(
                f"\nThis save is from before &11.0.0& (current save version is &{helper.gv_to_str(game_version)}&), so this is likely the cause for the issue. &The save editor is not designed to work with saves from before 11.0.0&"
            )
        raise e
    return save_data


def serialise_gold_pass(save_data: list[int], gold_pass: dict[str, Any]) -> list[int]:
    """Serialises the gold pass data"""

    save_data = write(save_data, gold_pass["officer_id"])
    save_data = write(save_data, gold_pass["renewal_times"])
    save_data = write_double(save_data, gold_pass["start_date"])
    save_data = write_double(save_data, gold_pass["expiry_date"])
    save_data = write_length_doubles(
        save_data, gold_pass["unknown_2"], write_length=False
    )
    save_data = write_double(save_data, gold_pass["start_date_2"])
    save_data = write_double(save_data, gold_pass["expiry_date_2"])
    save_data = write_double(save_data, gold_pass["unknown_3"])
    save_data = write(save_data, gold_pass["flag_2"])
    save_data = write_double(save_data, gold_pass["expiry_date_3"])

    save_data = write(save_data, len(gold_pass["claimed_rewards"]), 4)
    for item_id, amount in gold_pass["claimed_rewards"].items():
        save_data = write(save_data, item_id, 4)
        save_data = write(save_data, amount, 4)

    save_data = write(save_data, gold_pass["unknown_4"])
    save_data = write(save_data, gold_pass["unknown_5"])
    save_data = write(save_data, gold_pass["unknown_6"])

    return save_data


def serialise_unlock_popups(
    save_data: list[int],
    unlock_popups: list[tuple[int, int]],
    unknown_118: dict[str, int],
):
    """Serialises the unlock popups"""

    save_data = write(save_data, len(unlock_popups), 4)
    save_data = write(save_data, unknown_118)
    for popup_id in unlock_popups:
        save_data = write(save_data, popup_id[1], 1)
        save_data = write(save_data, popup_id[0], 4)
    return save_data


def serialise_cleared_slots(
    save_data: list[int], cleared_slots: dict[str, Any]
) -> list[int]:
    """
    Serialises the cleared slots

    Args:
        save_data (list[int]): The save data
        cleared_slots (dict[str, Any]): The cleared slots

    Returns:
        list[int]: The save data
    """
    cleared_slot_data = parse_save.ClearedSlots.from_dict(cleared_slots)
    save_data = write(save_data, len(cleared_slot_data.slots), 2)
    for slot in cleared_slot_data.slots:
        save_data = write(save_data, slot.slot_index, 2)
        for cat in slot.cats:
            save_data = write(save_data, cat.cat_id, 2)
            save_data = write(save_data, cat.cat_form, 1)
        save_data = write(save_data, slot.separator, 3)
    save_data = write(save_data, cleared_slot_data.end_index, 2)

    for stages_slot in cleared_slot_data.slot_stages:
        save_data = write(save_data, stages_slot.slot_index, 2)
        save_data = write(save_data, len(stages_slot.stages), 2)
        for stage in stages_slot.stages:
            save_data = write(save_data, stage.stage_id, 4)
    return save_data


def serialise_enigma_data(
    save_data: list[int], enigma_data: dict[str, Any], game_version: int
):
    """
    Serialises the enigma data

    Args:
        save_data (list[int]): The save data
        enigma_data (dict[str, Any]): The enigma data
    """
    save_data = write(save_data, enigma_data["energy_since_1"], 4)
    save_data = write(save_data, enigma_data["energy_since_2"], 4)
    save_data = write(save_data, enigma_data["enigma_level"], 1)
    save_data = write(save_data, enigma_data["unknown_2"], 1)
    save_data = write(save_data, enigma_data["unknown_3"], 1)

    save_data = write(save_data, len(enigma_data["stages"]), 1)
    for stage in enigma_data["stages"]:
        save_data = write(save_data, stage["level"], 4)
        save_data = write(save_data, stage["stage_id"], 4)
        save_data = write(save_data, stage["decoding_status"], 1)
        save_data = write_double(save_data, stage["start_time"])

    if game_version >= 140500:
        extra_data = enigma_data.get("extra_data")
        if extra_data is not None:
            save_data = write(save_data, 1, 1)

            save_data = write(save_data, extra_data[0], 4)
            save_data = write(save_data, extra_data[1], 4)
            save_data = write(save_data, extra_data[2], 1)
            save_data = write_double(save_data, extra_data[3])
        else:
            save_data = write(save_data, 0, 1)

    return save_data


def serialise_cat_shrine(
    save_data: list[int], shrine_data: dict[str, Any]
) -> list[int]:
    """
    Serialises the cat shrine data

    Args:
        save_data (list[int]): The save data
        shrine_data (dict[str, Any]): The shrine data

    Returns:
        list[int]: The save data
    """
    save_data = write_double(save_data, shrine_data["stamp_1"])
    save_data = write_double(save_data, shrine_data["stamp_2"])
    save_data = write(save_data, shrine_data["shrine_gone"], 1)
    save_data = write_length_data(save_data, shrine_data["flags"], 1, 1)
    save_data = write(save_data, shrine_data["xp_offering"], 4)
    return save_data


def write_variable_length_int(save_data: list[int], i: int) -> list[int]:
    """
    Writes a variable length integer to the save data (I have no idea how this works and what this does)

    Args:
        save_data (list[int]): The save data
        i (int): The integer to write

    Returns:
        list[int]: The save data
    """
    i_2 = 0
    i_3 = 0
    i = int(i)
    while i >= 128:
        i_2 |= ((i & 127) | 32768) << (i_3 * 8)
        i_3 += 1
        i >>= 7
    i_4 = i_2 | (i << (i_3 * 8))
    i_5 = i_3 + 1
    for i_6 in range(i_5):
        i_7 = (i_4 >> (((i_5 - i_6) - 1) * 8)) & 255
        save_data = write(save_data, i_7, 1)
    return save_data


def set_variable_data(
    save_data: list[int], data: tuple[dict[int, int], dict[int, int]]
) -> list[int]:
    """
    Sets the variable data

    Args:
        save_data (list[int]): The save data
        data (tuple[dict[int, int], dict[int, int]]): The variable data

    Returns:
        list[int]: The save data
    """
    save_data = write_variable_length_int(save_data, len(data[0]))
    for key, value in data[0].items():
        save_data = write_variable_length_int(save_data, key)
        save_data = write_variable_length_int(save_data, value)
    save_data = write_variable_length_int(save_data, len(data[1]))
    for key, value in data[1].items():
        save_data = write_variable_length_int(save_data, key)
        save_data = write(save_data, value, 1)
    return save_data


def serialise_login_bonuses(save_data: list[int], login_bonuses: dict[int, int]):
    """
    Serialises the login bonuses

    Args:
        save_data (list[int]): The save data
        login_bonuses (dict[int, int]): The login bonuses
    """
    save_data = write(save_data, len(login_bonuses), 4)
    for key, value in login_bonuses.items():
        save_data = write(save_data, key, 4)
        save_data = write(save_data, value, 4)
    return save_data


def serialise_tower_item_obtained(save_data: list[int], data: list[list[bool]]):
    """
    Serialises the tower item obtained data

    Args:
        save_data (list[int]): The save data
        data (list[list[bool]]): The tower item obtained data
    """
    save_data = write(save_data, len(data), 4)
    save_data = write(save_data, len(data[0]), 4)
    for row in data:
        for item in row:
            save_data = write(save_data, item, 1)
    return save_data


def write_dict(save_data: list[int], data: dict[Any, Any]) -> list[int]:
    """
    Writes a dictionary to the save data

    Args:
        save_data (list[int]): The save data
        data (dict[Any, Any]): The dictionary

    Returns:
        list[int]: The save data
    """
    save_data = write(save_data, len(data), 4)
    for key, value in data.items():
        save_data = write(save_data, key, 4)
        if isinstance(value, str):
            save_data = serialise_utf8_string(save_data, value)
        elif isinstance(value, bool):
            save_data = write(save_data, value, 1)
        else:
            save_data = write(save_data, value, 4)

    return save_data


def serialise_zero_legends(save_data: list[int], data: list[Any]):
    """
    Serialises the zero legends data

    Args:
        save_data (list[int]): The save data
        data (list[Any]): The zero legends data
    """
    save_data = write(save_data, len(data), 2)
    for chapter in data:
        unknown_1 = chapter["unknown_1"]
        save_data = write(save_data, unknown_1, 1)
        save_data = write(save_data, len(chapter["stars"]), 1)
        for star in chapter["stars"]:
            selected_stage = star["selected_stage"]
            stages_cleared = star["stages_cleared"]
            unlock_next = star["unlock_next"]
            save_data = write(save_data, selected_stage, 1)
            save_data = write(save_data, stages_cleared, 1)
            save_data = write(save_data, unlock_next, 1)
            save_data = write(save_data, len(star["stages"]), 2)
            for clear_amount in star["stages"]:
                save_data = write(save_data, clear_amount, 2)
    return save_data


def serialize_save(save_stats: dict[str, Any]) -> bytes:
    """Serialises the save stats"""

    save_data: list[int] = []

    save_data = write(save_data, save_stats["game_version"])

    save_data = write(save_data, save_stats["unknown_1"])

    save_data = write(save_data, save_stats["mute_music"])
    save_data = write(save_data, save_stats["mute_sound_effects"])

    save_data = write(save_data, save_stats["cat_food"])
    save_data = write(save_data, save_stats["current_energy"])
    if save_stats["extra_time_data"]:
        if save_stats["extra_time_data"]["Value"] != 0:
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
    save_data = write(save_data, save_stats["upgrade_state"])

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
    save_data = write(save_data, save_stats["unknown_2"])
    save_data = write(save_data, save_stats["daily_reward_flag"])
    save_data = write_length_data(
        save_data, save_stats["unknown_116"], write_length=False
    )

    save_data = serialise_main_story(save_data, save_stats["story_chapters"])
    save_data = serialise_treasures(save_data, save_stats["treasures"])

    save_data = write_length_data(save_data, save_stats["enemy_guide"])

    save_data = write_length_data(save_data, save_stats["cats"])
    save_data = serialise_cat_upgrades(save_data, save_stats["cat_upgrades"])
    save_data = write_length_data(save_data, save_stats["current_forms"])

    save_data = serialise_blue_upgrades(save_data, save_stats["blue_upgrades"])

    save_data = write_length_data(save_data, save_stats["menu_unlocks"])
    save_data = write_length_data(save_data, save_stats["new_dialogs_1"])

    save_data = write_length_data(save_data, save_stats["battle_items"], 4, 4, False, 6)
    save_data = write_length_data(save_data, save_stats["new_dialogs_2"])

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

    save_data = set_variable_data(save_data, save_stats["unknown_10"])

    save_data = write_length_data(
        save_data, save_stats["unknown_11"], write_length=False
    )

    save_data = write(save_data, save_stats["normal_tickets"])
    save_data = write(save_data, save_stats["rare_tickets"])

    save_data = write_length_data(save_data, save_stats["gatya_seen_cats"])

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

    save_data = write_length_data(
        save_data, save_stats["unknown_107"], write_length=False, bytes_per_val=1
    )
    if save_stats["dst"]:
        save_data = serialise_utf8_string(save_data, save_stats["unknown_110"])
    unknown_108 = helper.format_text(save_stats["unknown_108"])
    save_data = write(save_data, len(unknown_108), 4)
    for i in range(len(unknown_108)):
        save_data = serialise_utf8_string(save_data, unknown_108[i])

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

    save_data = serialise_cat_upgrades(save_data, save_stats["catseye_related_data"])

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

    save_data = serialise_event_timed_scores(
        save_data, save_stats["event_timed_scores"]
    )

    save_data = serialise_utf8_string(save_data, save_stats["inquiry_code"])
    save_data = serialise_play_time(save_data, save_stats["play_time"])

    save_data = write(save_data, save_stats["unknown_25"])
    save_data = write(save_data, save_stats["backup_state"])
    if save_stats["dst"]:
        save_data = write(save_data, save_stats["unknown_119"])
    save_data = write(save_data, save_stats["gv_44"])
    save_data = write(save_data, save_stats["unknown_120"])

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

    save_data = serialise_login_bonuses(save_data, save_stats["login_bonuses"])
    save_data = write(save_data, save_stats["unknown_49"])
    save_data = write_length_data(
        save_data, save_stats["announcment"], write_length=False
    )
    save_data = write(save_data, save_stats["backup_counter"])

    save_data = write_length_data(
        save_data, save_stats["unknown_131"], write_length=False
    )

    save_data = write(save_data, save_stats["gv_55"])

    save_data = write(save_data, save_stats["unknown_51"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_113"])

    save_data = serialise_dojo(save_data, save_stats["dojo_data"])
    save_data = write(save_data, save_stats["dojo_item_lock"])
    save_data = write_length_data(
        save_data, save_stats["dojo_locks"], write_length=False, bytes_per_val=1
    )

    save_data = write(save_data, save_stats["unknown_114"])

    save_data = write(save_data, save_stats["gv_58"])

    save_data = write(save_data, save_stats["unknown_115"])

    save_data = serialise_outbreaks(save_data, save_stats["outbreaks"])

    save_data = write_double(save_data, save_stats["unknown_52"])
    save_data = write_length_data(
        save_data, save_stats["item_schemes"]["to_obtain_ids"]
    )
    save_data = write_length_data(save_data, save_stats["item_schemes"]["received_ids"])

    save_data = serialise_outbreaks(save_data, save_stats["current_outbreaks"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_55"])

    save_data = write_double(save_data, save_stats["time_stamp_4"])
    save_data = write(save_data, save_stats["gv_60"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_117"])

    save_data = write(save_data, save_stats["gv_61"])

    save_data = serialise_unlock_popups(
        save_data, save_stats["unlock_popups"], save_stats["unknown_118"]
    )

    save_data = write_length_data(save_data, save_stats["base_materials"])

    save_data = write(save_data, save_stats["unknown_56"])
    save_data = write(save_data, save_stats["unknown_57"])
    save_data = write(save_data, save_stats["unknown_58"])

    save_data = write(save_data, save_stats["engineers"])
    save_data = serialise_ototo_cat_cannon(save_data, save_stats["ototo_cannon"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_59"])
    save_data = serialise_tower(save_data, save_stats["tower"])
    save_data = serialise_missions(save_data, save_stats["missions"])
    save_data = serialise_tower_item_obtained(
        save_data, save_stats["tower_item_obtained"]
    )
    save_data = serialise_dumped_data(save_data, save_stats["unknown_61"])
    save_data = write(save_data, save_stats["challenge"]["Score"])
    save_data = write(save_data, save_stats["challenge"]["Cleared"])

    save_data = write(save_data, save_stats["gv_67"])

    save_data = write_dict(save_data, save_stats["weekly_event_missions"])
    save_data = write(save_data, save_stats["won_dojo_reward"])
    save_data = write(save_data, save_stats["event_flag_update_flag"])

    save_data = write(save_data, save_stats["gv_68"])

    save_data = write_dict(save_data, save_stats["completed_one_level_in_chapter"])
    save_data = write_dict(save_data, save_stats["displayed_cleared_limit_text"])
    save_data = write_dict(save_data, save_stats["event_start_dates"])
    save_data = write_length_data(save_data, save_stats["stages_beaten_twice"])

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

    save_data = serialise_gold_pass(save_data, save_stats["gold_pass"])

    save_data = serialise_talent_data(save_data, save_stats["talents"])
    save_data = write(save_data, save_stats["np"])

    save_data = write(save_data, save_stats["unknown_70"])

    save_data = write(save_data, save_stats["gv_80000"])

    save_data = write(save_data, save_stats["unknown_71"])

    save_data = write(save_data, save_stats["leadership"])

    save_data = write(save_data, save_stats["officer_pass_cat_id"])
    save_data = write(save_data, save_stats["officer_pass_cat_form"])

    save_data = write(save_data, save_stats["gv_80200"])

    save_data = write(save_data, save_stats["filibuster_stage_id"])
    save_data = write(save_data, save_stats["filibuster_stage_enabled"])

    save_data = write(save_data, save_stats["gv_80300"])

    save_data = write_length_data(save_data, save_stats["unknown_74"])

    save_data = write(save_data, save_stats["gv_80500"])

    save_data = write_length_data(save_data, save_stats["unknown_75"], 2)

    save_data = serialise_legend_quest_current(
        save_data, save_stats["legend_quest_current"]
    )
    save_data = serialise_legend_quest_progress(save_data, save_stats["legend_quest"])
    save_data = write_length_data(
        save_data, save_stats["unknown_133"], bytes_per_val=1, write_length=False
    )
    save_data = write_length_data(
        save_data, save_stats["legend_quest_ids"], write_length=False
    )

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
    save_data = serialise_enigma_data(
        save_data, save_stats["enigma_data"], save_stats["game_version"]["Value"]
    )
    save_data = serialise_cleared_slots(save_data, save_stats["cleared_slot_data"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_121"])
    save_data = serialise_gauntlet_current(
        save_data, save_stats["collab_gauntlets_current"]
    )
    save_data = serialise_gauntlet_progress(save_data, save_stats["collab_gauntlets"])
    save_data = write_length_data(
        save_data, save_stats["unknown_84"], bytes_per_val=1, write_length=False
    )

    save_data = serialise_dumped_data(save_data, save_stats["unknown_85"])

    save_data = serialise_talent_orbs(
        save_data, save_stats["talent_orbs"], save_stats["game_version"]
    )

    save_data = serialise_dumped_data(save_data, save_stats["unknown_86"])

    save_data = serialise_cat_shrine(save_data, save_stats["cat_shrine"])

    save_data = write(save_data, save_stats["unknown_130"])

    save_data = write(save_data, save_stats["gv_90900"])

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

    save_data = write(save_data, save_stats["gv_100000"])
    data = check_gv(save_data, save_stats, 100100)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = write(save_data, save_stats["date_int"])

    save_data = write(save_data, save_stats["gv_100100"])
    data = check_gv(save_data, save_stats, 100300)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = write_length_data(
        save_data, save_stats["unknown_93"], bytes_per_val=19, write_length=False
    )

    save_data = write(save_data, save_stats["gv_100300"])
    data = check_gv(save_data, save_stats, 100700)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_94"])
    save_data = write(save_data, save_stats["platinum_shards"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_100"])

    save_data = write(save_data, save_stats["gv_100700"])
    data = check_gv(save_data, save_stats, 100900)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_aku(save_data, save_stats["aku"])

    save_data = write(save_data, save_stats["unknown_95"])
    save_data = serialise_dumped_data(save_data, save_stats["unknown_96"])

    save_data = write(save_data, save_stats["gv_100900"])
    data = check_gv(save_data, save_stats, 101000)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = write(save_data, save_stats["unknown_97"])

    save_data = write(save_data, save_stats["gv_101000"])
    data = check_gv(save_data, save_stats, 110000)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_98"])

    save_data = write(save_data, save_stats["gv_110000"])
    data = check_gv(save_data, save_stats, 110500)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_gauntlet_current(
        save_data, save_stats["behemoth_culling_current"]
    )
    save_data = serialise_gauntlet_progress(save_data, save_stats["behemoth_culling"])
    save_data = write_length_data(
        save_data, save_stats["unknown_124"], bytes_per_val=1, write_length=False
    )

    save_data = write(save_data, save_stats["unknown_125"])

    save_data = write(save_data, save_stats["gv_110500"])
    data = check_gv(save_data, save_stats, 110600)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = write(save_data, save_stats["unknown_126"])

    save_data = write(save_data, save_stats["gv_110600"])
    data = check_gv(save_data, save_stats, 110700)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_127"])

    if save_stats["dst"]:
        save_data = write(save_data, save_stats["unknown_128"])

    save_data = write(save_data, save_stats["gv_110700"])
    data = check_gv(save_data, save_stats, 110800)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = write(save_data, save_stats["shrine_dialogs"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_129"])

    save_data = write(save_data, save_stats["dojo_3x_speed"])

    save_data = serialise_dumped_data(save_data, save_stats["unknown_132"])

    save_data = write(save_data, save_stats["gv_110800"])
    data = check_gv(save_data, save_stats, 110900)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_135"])

    save_data = write(save_data, save_stats["gv_110900"])
    data = check_gv(save_data, save_stats, 120000)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_zero_legends(save_data, save_stats["zero_legends"])

    save_data = write(save_data, save_stats["unknown_136"])

    save_data = write(save_data, save_stats["gv_120000"])
    data = check_gv(save_data, save_stats, 120100)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_137"])

    save_data = write(save_data, save_stats["gv_120100"])
    data = check_gv(save_data, save_stats, 120200)
    save_data = data["save_data"]
    if data["exit"]:
        return bytes(save_data)

    save_data = serialise_dumped_data(save_data, save_stats["unknown_138"])

    save_data = write(save_data, save_stats["gv_120200"])

    extra_data = base64.b64decode(save_stats["extra_data"])

    save_data += extra_data

    save_data = exit_serialiser(save_data, save_stats)

    return bytes(save_data)
