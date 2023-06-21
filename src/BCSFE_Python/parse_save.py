"""Handler for parsing the save file"""

import collections
import datetime
import enum
import json
import struct
import traceback
from typing import Any, Optional, Union


from . import helper
from . import updater

address = 0
save_data_g = None


def re_order(data: dict[str, Any]) -> collections.OrderedDict[str, Any]:
    """Move all unknown vals to the bottom of the json"""

    priority: list[str] = json.loads(
        helper.read_file_string(helper.get_file("order.json"))
    )
    ordered_data = collections.OrderedDict(data)

    for item in ordered_data.copy():
        if "unknown" in item:
            ordered_data.move_to_end(item)

    for i in range(len(priority)):
        ordered_data.move_to_end(priority[len(priority) - 1 - i], False)
    return ordered_data


def set_address(val: int):
    """Set the address to a specific value"""

    global address
    address = val


def next_int_len(number: int) -> dict[str, int]:
    """Get the next int of a specified byte length from the save file"""

    if number < 0:
        raise Exception("Invalid number")
    if save_data_g is None:
        raise Exception("Invalid save data")
    if number > len(save_data_g):
        raise Exception("Byte length is greater than the length of the save data")
    val = convert_little(save_data_g[address : address + number])
    data: dict[str, int] = {}
    set_address(address + number)
    data["Value"] = val
    data["Length"] = number
    return data


def generate_empty_len(length: int) -> dict[str, int]:
    """Generate an empty dict with a length and value of 0"""

    data: dict[str, int] = {}
    data["Length"] = length
    data["Value"] = 0
    return data


def next_int(number: int) -> int:
    return next_int_len(number)["Value"]


def skip(number: int):
    """Skip a number of bytes"""

    set_address(address + number)


def convert_little(byte_data: bytes) -> int:
    """Convert a byte array to an int in little endian"""

    return int.from_bytes(byte_data, byteorder="little", signed=False)


def get_time_data_skip(dst_flag: bool) -> dict[str, Any]:
    year = next_int(4)
    year_2 = next_int(4)

    month = next_int(4)
    month_2 = next_int(4)

    day = next_int(4)
    day_2 = next_int(4)

    time_stamp = get_double()

    hour = next_int(4)
    minute = next_int(4)
    second = next_int(4)
    dst = 0
    if dst_flag:
        dst = next_int(1)

    time = datetime.datetime(year, month, day, hour, minute, second)
    return {
        "time": time.isoformat(),
        "time_stamp": time_stamp,
        "dst": dst,
        "duplicate": {"yy": year_2, "mm": month_2, "dd": day_2},
    }


def get_time_data(dst_flag: bool) -> str:
    if dst_flag:
        _ = next_int(1)
    year = next_int(4)
    month = next_int(4)
    day = next_int(4)
    hour = next_int(4)
    minute = next_int(4)
    second = next_int(4)

    time = datetime.datetime(year, month, day, hour, minute, second)
    return time.isoformat()


def get_length_data(
    length_bytes: int = 4, separator: int = 4, length: Union[int, None] = None
) -> list[int]:
    data: list[int] = []
    if length is None:
        length = next_int(length_bytes)
    if save_data_g is None:
        raise Exception("Invalid save data")
    if length > len(save_data_g):
        raise Exception("Length too large")
    for _ in range(length):
        data.append(next_int(separator))
    return data


def get_length_doubles(
    length_bytes: int = 4, length: Union[int, None] = None
) -> list[float]:
    data: list[float] = []
    if length is None:
        length = next_int(length_bytes)
    if save_data_g is None:
        raise Exception("Invalid save data")
    if length > len(save_data_g):
        raise Exception("Length too large")
    for _ in range(length):
        data.append(get_double())
    return data


def get_equip_slots() -> list[list[int]]:
    length = next_int(1)
    data = get_length_data(1, length=length * 10)
    slots: list[list[int]] = []
    for i in range(length):
        start_pos = 10 * i
        end_pos = 10 * (i + 1)
        slots.append(data[start_pos:end_pos])

    data = slots
    return data


def get_main_story_levels() -> dict[str, Any]:
    chapter_progress: list[int] = []
    for _ in range(10):
        chapter_progress.append(next_int(4))
    times_cleared: list[list[int]] = []
    for _ in range(10):
        chapter_times: list[int] = []
        for _ in range(51):
            chapter_times.append(next_int(4))
        times_cleared.append(chapter_times)
    times_cleared_dict = times_cleared
    return {
        "Chapter Progress": chapter_progress,
        "Times Cleared": times_cleared_dict,
    }


def get_treasures() -> list[list[int]]:
    treasures: list[list[int]] = []
    for _ in range(10):
        chapter: list[int] = []
        for _ in range(49):
            chapter.append(next_int(4))
        treasures.append(chapter)
    return treasures


def get_cat_upgrades() -> dict[str, Any]:
    length = next_int(4)
    data = get_length_data(4, 2, length * 2)
    base_levels = data[1::2]
    plus_levels = data[0::2]

    data_dict = {"Base": base_levels, "Plus": plus_levels}
    return data_dict


def get_blue_upgrades() -> dict[str, Any]:
    length = 11
    data = get_length_data(4, 2, length * 2)
    base_levels = data[1::2]
    plus_levels = data[0::2]
    data_dict = {"Base": base_levels, "Plus": plus_levels}
    return data_dict


def get_utf8_string(length: Union[int, None] = None) -> str:
    data = get_length_data(4, 1, length)
    data = bytes(data).decode("utf-8")
    return data


def read_variable_length_int() -> int:
    """
    Read a variable length int from the save file

    Returns:
        int: The value of the variable length int
    """
    i = 0
    for _ in range(4):
        i_3 = i << 7
        read = next_int(1)
        i = i_3 | (read & 127)
        if (read & 128) == 0:
            return i
    return i


def load_bonus_hash() -> tuple[dict[int, int], dict[int, int]]:
    """
    Get the variable data from the save file

    Returns:
        tuple[dict[int, int], dict[int, int]]: The variable data
    """
    length_1 = read_variable_length_int()
    data_1: dict[int, int] = {}
    for _ in range(length_1):
        key = read_variable_length_int()
        val = read_variable_length_int()
        data_1[key] = val

    length_2 = read_variable_length_int()
    data_2: dict[int, int] = {}
    for _ in range(length_2):
        key = read_variable_length_int()
        val = next_int(1)
        data_2[key] = val

    return (data_1, data_2)


def get_event_stages_current() -> dict[str, Any]:
    unknown_val = next_int(1)
    total_sub_chapters = next_int(2) * unknown_val
    stars_per_sub_chapter = next_int(1)
    stages_per_sub_chapter = next_int(1)

    clear_progress = get_length_data(1, 1, total_sub_chapters * stars_per_sub_chapter)
    clear_progress = list(helper.chunks(clear_progress, stars_per_sub_chapter))

    return {
        "Clear": clear_progress,
        "unknown": unknown_val,
        "total": total_sub_chapters,
        "stages": stages_per_sub_chapter,
        "stars": stars_per_sub_chapter,
    }


def get_event_stages(lengths: dict[str, Any]) -> dict[str, Any]:
    total_sub_chapters = lengths["total"]
    stars_per_sub_chapter = lengths["stars"]
    stages_per_sub_chapter = lengths["stages"]

    clear_progress = get_length_data(1, 1, total_sub_chapters * stars_per_sub_chapter)
    clear_amount = get_length_data(
        1, 2, total_sub_chapters * stages_per_sub_chapter * stars_per_sub_chapter
    )
    unlock_next = get_length_data(1, 1, total_sub_chapters * stars_per_sub_chapter)

    clear_progress = list(helper.chunks(clear_progress, stars_per_sub_chapter))
    clear_amount = list(
        helper.chunks(clear_amount, stages_per_sub_chapter * stars_per_sub_chapter)
    )
    unlock_next = list(helper.chunks(unlock_next, stars_per_sub_chapter))

    clear_amount_sep: list[list[list[int]]] = []

    for clear_amount_val in clear_amount:
        sub_chapter_clears: list[list[int]] = []
        for j in range(stars_per_sub_chapter):
            sub_chapter_clears.append(clear_amount_val[j::stars_per_sub_chapter])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {
        "Value": {
            "clear_progress": clear_progress,
            "clear_amount": clear_amount,
            "unlock_next": unlock_next,
        },
        "Lengths": lengths,
    }


def get_purchase_receipts() -> list[dict[str, Any]]:
    total_strs = next_int(4)
    data: list[dict[Any, Any]] = []

    for _ in range(total_strs):
        data_dict: dict[str, Any] = {}
        data_dict["unknown_4"] = next_int(4)

        strings = next_int(4)
        item_packs: list[Any] = []
        for _ in range(strings):
            strings_dict = {}

            strings_dict["Value"] = get_utf8_string()
            strings_dict["unknown_1"] = next_int(1)
            item_packs.append(strings_dict)
        data_dict["item_packs"] = item_packs
        data.append(data_dict)
    return data


def get_dojo_data_maybe() -> dict[int, Any]:
    # everything here is speculative and might not be correct
    dojo_data: dict[int, Any] = {}
    total_subchapters = next_int(4)
    for _ in range(total_subchapters):
        subchapter_id = next_int(4)
        subchapter_data = {}

        total_stages = next_int(4)
        for _ in range(total_stages):
            stage_id = next_int(4)

            score = next_int(4)
            subchapter_data[stage_id] = score
        dojo_data[subchapter_id] = subchapter_data
    return dojo_data


def get_data_before_outbreaks() -> list[dict[str, Any]]:
    data: list[dict[str, Any]] = []

    length = next_int_len(4)
    data.append(length)
    for _ in range(length["Value"]):
        length_2 = next_int_len(4)
        data.append(length_2)

        length_3 = next_int_len(4)
        data.append(length_3)

        for _ in range(length_3["Value"]):
            val_1 = next_int_len(4)
            data.append(val_1)

            val_2 = next_int_len(1)
            data.append(val_2)

    length = next_int_len(4)
    data.append(length)

    for _ in range(length["Value"]):
        val_1 = next_int_len(4)
        data.append(val_1)

        val_2 = next_int_len(1)
        data.append(val_2)

    length = next_int_len(4)
    data.append(length)

    for _ in range(length["Value"]):
        val_1 = next_int_len(4)
        data.append(val_1)

        val_2 = next_int_len(4)
        data.append(val_2)

    length = next_int_len(4)
    data.append(length)

    val_1 = next_int_len(4)
    data.append(val_1)

    for _ in range(length["Value"]):
        val_2 = next_int_len(8)
        data.append(val_2)

        val_3 = next_int_len(4)
        data.append(val_3)

    gv_56 = next_int_len(4)  # 0x38
    data.append(gv_56)

    val_1 = next_int_len(1)
    data.append(val_1)

    length = next_int_len(4)
    data.append(length)

    val_2 = next_int_len(4)
    data.append(val_2)

    for _ in range(length["Value"]):
        val_3 = next_int_len(1)
        data.append(val_3)

        val_4 = next_int_len(4)
        data.append(val_4)

    return data


def get_outbreaks() -> dict[int, Any]:
    chapters_count = next_int(4)
    outbreaks: dict[int, Any] = {}
    for _ in range(chapters_count):
        chapter_id = next_int(4)
        stages_count = next_int(4)
        chapter = {}
        for _ in range(stages_count):
            stage_id = next_int(4)
            outbreak_cleared_flag = next_int(1)
            chapter[stage_id] = outbreak_cleared_flag
        outbreaks[chapter_id] = chapter
    return outbreaks


def get_mission_data_maybe() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    length = next_int_len(4)
    data.append(length)

    for _ in range(length["Value"]):
        val_1 = next_int_len(4)
        data.append(val_1)

        val_2 = next_int_len(1)
        data.append(val_2)
    return data


def get_unlock_popups() -> tuple[list[tuple[int, int]], dict[str, int]]:
    """Get unlock popups and unlock flags"""

    length = next_int_len(4)
    val_1 = next_int_len(4)

    data: list[tuple[int, int]] = []

    for _ in range(length["Value"]):
        flag = next_int(1)

        popup_id = next_int(4)
        data.append((popup_id, flag))
    return data, val_1


def get_unknown_data():
    data: list[dict[str, int]] = []
    length = next_int_len(4)
    data.append(length)

    for _ in range(length["Value"]):
        length_2 = next_int_len(4)
        data.append(length_2)

        val_1 = next_int_len(4)
        data.append(val_1)

    unknown_val_2 = next_int_len(1)
    data.append(unknown_val_2)

    length = next_int_len(4)
    data.append(length)

    for _ in range(length["Value"]):
        val_1 = next_int_len(4)
        data.append(val_1)

        val_2 = next_int_len(1)
        data.append(val_2)

    return data


def get_cat_cannon_data() -> dict[int, dict[str, Any]]:
    length = next_int(4)
    cannon_data: dict[int, dict[str, Any]] = {}
    for _ in range(length):
        cannon: dict[str, Any] = {}
        cannon_id = next_int(4)
        len_val = next_int(4)
        unlock_flag = next_int(4)
        effect_level = next_int(4)
        foundation_level = 0
        style_level = 0
        if len_val == 4:
            foundation_level = next_int(4)
            style_level = next_int(4)
        cannon["levels"] = {
            "effect": effect_level,
            "foundation": foundation_level,
            "style": style_level,
        }
        cannon["unlock_flag"] = unlock_flag
        cannon["len_val"] = len_val
        cannon_data[cannon_id] = cannon
    return cannon_data


def get_data_near_ht() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    val = next_int_len(1)
    data.append(val)

    for _ in range(val["Value"]):
        unknown_val_2 = next_int_len(3)
        data.append(unknown_val_2)

    unknown_val_3 = next_int_len(8)
    data.append(unknown_val_3)
    gv_64 = next_int_len(4)  # 0x40
    data.append(gv_64)

    length = next_int_len(4)
    data.append(length)

    val_1 = next_int_len(4)
    data.append(val_1)

    val_3 = {"Value": 0}
    for _ in range(length["Value"]):
        val_2 = next_int_len(4)
        data.append(val_2)

        val_3 = next_int_len(4)
        data.append(val_3)

    val_1 = next_int_len(4)
    data.append(val_1)

    val_4 = {"Value": 0}
    for _ in range(val_3["Value"]):
        length = next_int_len(4)
        data.append(length)

        for _ in range(length["Value"]):
            val_2 = next_int_len(4)
            data.append(val_2)

        val_4 = next_int_len(4)
        data.append(val_4)

    val_1 = next_int_len(4)
    data.append(val_1)

    for _ in range(val_4["Value"]):
        val_2 = next_int_len(1)
        data.append(val_2)

        val_3 = next_int_len(4)
        data.append(val_3)
    return data


def get_ht_it_data() -> dict[str, Any]:
    total = next_int(4)
    stars = next_int(4)

    current_data: dict[str, Any] = {}
    current_data = {"total": total, "stars": stars, "selected": []}

    for _ in range(total):
        for _ in range(stars):
            current_data["selected"].append(next_int(4))

    current_data["selected"] = list(helper.chunks(current_data["selected"], 4))

    total = next_int(4)
    stars = next_int(4)

    progress_data: dict[str, Any] = {}
    progress_data = {
        "total": total,
        "stars": stars,
        "clear_progress": [],
        "clear_amount": [],
        "unlock_next": [],
    }

    for _ in range(total):
        for _ in range(stars):
            progress_data["clear_progress"].append(next_int(4))

    progress_data["clear_progress"] = list(
        helper.chunks(progress_data["clear_progress"], 4)
    )

    total = next_int(4)
    stages = next_int(4)
    progress_data["stages"] = stages

    stars = next_int(4)

    clear_amount = get_length_data(4, 4, total * stages * stars)

    clear_amount = list(helper.chunks(clear_amount, stages * stars))

    clear_amount_sep: list[list[list[int]]] = []

    for clear_amount_val in clear_amount:
        sub_chapter_clears: list[list[int]] = []
        for j in range(stars):
            sub_chapter_clears.append(clear_amount_val[j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    progress_data["clear_amount"] = clear_amount_sep

    data: list[dict[str, int]] = []
    length = next_int_len(4)
    data.append(length)

    length_2 = next_int_len(4)
    data.append(length_2)

    for _ in range(length["Value"]):
        for _ in range(length_2["Value"]):
            data.append(next_int_len(4))
    return {"data": data, "current": current_data, "progress": progress_data}


def get_mission_segment() -> dict[int, int]:
    missions: dict[int, int] = {}
    length = next_int(4)
    for _ in range(length):
        mission_id = next_int(4)
        mission_value = next_int(4)
        missions[mission_id] = mission_value
    return missions


def get_mission_data() -> dict[str, Any]:
    missions: dict[str, dict[int, int]] = {}
    missions["states"] = get_mission_segment()
    missions["requirements"] = get_mission_segment()
    missions["clear_types"] = get_mission_segment()
    missions["gamatoto"] = get_mission_segment()
    missions["nyancombo"] = get_mission_segment()
    missions["user_rank"] = get_mission_segment()
    missions["expiry"] = get_mission_segment()
    missions["preparing"] = get_mission_segment()
    return missions


def get_data_after_challenge() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    val_22 = next_int_len(4)
    data.append(val_22)

    gv_69 = next_int_len(4)  # 0x45
    data.append(gv_69)

    val_54 = next_int_len(4)
    data.append(val_54)

    val_118 = next_int_len(4)
    data.append(val_118)

    for _ in range(val_54["Value"]):
        val_15 = next_int_len(1)
        data.append(val_15)

        val_118 = next_int_len(4)
        data.append(val_118)

    val_54 = next_int_len(4)
    data.append(val_54)

    for _ in range(val_118["Value"]):
        val_65 = next_int_len(8)
        data.append(val_65)

        val_54 = next_int_len(4)
        data.append(val_54)

    return data


def get_data_after_tower() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    gv_66 = next_int_len(4)  # 0x42
    data.append(gv_66)

    data.append(next_int_len(4 * 2))
    data.append(next_int_len(1 * 3))
    data.append(next_int_len(4 * 3))
    data.append(next_int_len(1 * 3))
    data.append(next_int_len(1))
    data.append(next_int_len(8))

    val_54 = next_int_len(4)
    data.append(val_54)

    val_61 = next_int_len(4)
    data.append(val_61)

    for _ in range(val_54["Value"]):
        for _ in range(val_61["Value"]):
            val_22 = next_int_len(4)
            data.append(val_22)

    val_54 = next_int_len(4)
    data.append(val_54)

    val_61 = next_int_len(4)
    data.append(val_61)

    for _ in range(val_54["Value"]):
        for _ in range(val_61["Value"]):
            val_22 = next_int_len(4)
            data.append(val_22)

    val_54 = next_int_len(4)
    data.append(val_54)

    val_61 = next_int_len(4)
    data.append(val_61)

    val_57 = next_int_len(4)
    data.append(val_57)
    for _ in range(val_54["Value"]):
        for _ in range(val_61["Value"]):
            for _ in range(val_57["Value"]):
                val_22 = next_int_len(4)
                data.append(val_22)

    val_54 = next_int_len(4)
    data.append(val_54)

    val_61 = next_int_len(4)
    data.append(val_61)

    for _ in range(val_54["Value"]):
        for _ in range(val_61["Value"]):
            val_22 = next_int_len(4)
            data.append(val_22)

    val_54 = next_int_len(4)
    data.append(val_54)

    for _ in range(val_54["Value"] - 1):
        val_22 = next_int_len(4)
        data.append(val_22)

    return data


def get_uncanny_current() -> dict[str, Any]:
    total_subchapters = next_int(4)
    stages_per_subchapter = next_int(4)
    stars = next_int(4)
    if total_subchapters < 1:
        next_int(4)
        raise Exception("Invalid total subchapters")
    else:
        clear_progress = get_length_data(4, 4, total_subchapters * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    return {
        "Clear": clear_progress,
        "total": total_subchapters,
        "stages": stages_per_subchapter,
        "stars": stars,
    }


def get_event_timed_scores() -> dict[str, Any]:
    total_subchapters = next_int(4)
    stages_per_subchapter = next_int(4)
    stars = next_int(4)

    score = get_length_data(4, 4, total_subchapters * stars * stages_per_subchapter)
    score = list(helper.chunks(score, stars * stages_per_subchapter))

    return {
        "Score": score,
        "total": total_subchapters,
        "stages": stages_per_subchapter,
        "stars": stars,
    }


def get_uncanny_progress(lengths: dict[str, Any]) -> dict[str, Any]:
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    clear_progress = get_length_data(4, 4, total * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    clear_amount = get_length_data(4, 4, total * stages * stars)
    unlock_next = get_length_data(4, 4, total * stars)

    clear_amount = list(helper.chunks(clear_amount, stages * stars))
    unlock_next = list(helper.chunks(unlock_next, stars))

    clear_amount_sep: list[list[list[int]]] = []

    for clear_amount_val in clear_amount:
        sub_chapter_clears: list[list[int]] = []
        for j in range(stars):
            sub_chapter_clears.append(clear_amount_val[j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {
        "Value": {
            "clear_progress": clear_progress,
            "clear_amount": clear_amount,
            "unlock_next": unlock_next,
        },
        "Lengths": lengths,
    }


def get_data_after_uncanny() -> dict[str, Any]:
    lengths = get_uncanny_current()
    return {"current": lengths, "progress": get_uncanny_progress(lengths)}


def get_gold_pass_data() -> dict[str, Any]:
    """Get gold pass related data"""

    data: dict[str, Any] = {}
    data["officer_id"] = next_int_len(4)
    data["renewal_times"] = next_int_len(4)
    data["start_date"] = get_double()
    data["expiry_date"] = get_double()
    data["unknown_2"] = get_length_doubles(length=2)
    data["start_date_2"] = get_double()
    data["expiry_date_2"] = get_double()
    data["unknown_3"] = get_double()
    data["flag_2"] = next_int_len(4)
    data["expiry_date_3"] = get_double()

    number_of_rewards = next_int(4)
    claimed_rewards: dict[int, int] = {}
    for _ in range(number_of_rewards):
        item_id = next_int(4)
        amount = next_int(4)
        claimed_rewards[item_id] = amount

    data["claimed_rewards"] = claimed_rewards
    data["unknown_4"] = next_int_len(8)
    data["unknown_5"] = next_int_len(1)
    data["unknown_6"] = next_int_len(1)

    return data


def get_talent_data() -> dict[int, list[dict[str, int]]]:
    total_cats = next_int(4)

    talents: dict[int, list[dict[str, int]]] = {}
    for _ in range(total_cats):
        cat_id = next_int(4)
        cat_data: list[dict[str, int]] = []

        number_of_talents = next_int(4)

        for _ in range(number_of_talents):
            talent_id = next_int(4)
            talent_level = next_int(4)
            talent = {"id": talent_id, "level": talent_level}
            cat_data.append(talent)
        talents[cat_id] = cat_data
    return talents


def get_medals() -> dict[str, Any]:
    medal_data_1 = get_length_data(2, 2)

    total_medals = next_int(2)
    medals = {}

    for _ in range(total_medals):
        medal_id = next_int(2)
        medal_flag = next_int(1)
        medals[medal_id] = medal_flag
    return {"medal_data_1": medal_data_1, "medal_data_2": medals}


def get_data_after_medals() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    data.append(next_int_len(1))

    val_2 = next_int_len(2)
    data.append(val_2)

    val_3 = next_int_len(2)
    data.append(val_3)

    for _ in range(val_2["Value"]):
        val_1 = next_int_len(1)
        data.append(val_1)

        val_3 = next_int_len(2)
        data.append(val_3)

    val_2 = next_int_len(2)
    data.append(val_2)

    val_6c = val_3
    for _ in range(val_6c["Value"]):
        val_2 = next_int_len(2)
        data.append(val_2)
        for _ in range(val_2["Value"]):
            val_3 = next_int_len(2)
            data.append(val_3)

            val_4 = next_int_len(2)
            data.append(val_4)

        val_2 = next_int_len(2)
        data.append(val_2)

    val_7c = val_2
    for _ in range(val_7c["Value"]):
        val_2 = next_int_len(2)
        data.append(val_2)

        val_12 = next_int_len(4)
        data.append(val_12)

    data.append(next_int_len(4))  # 90000

    data.append(next_int_len(4))
    data.append(next_int_len(4))
    data.append(next_int_len(8))
    data.append(next_int_len(4))  # 90100

    val_18 = next_int_len(2)
    data.append(val_18)
    for _ in range(val_18["Value"]):
        data.append(next_int_len(4))
        data.append(next_int_len(4))
        data.append(next_int_len(2))
        data.append(next_int_len(4))
        data.append(next_int_len(4))
        data.append(next_int_len(4))
        data.append(next_int_len(2))

    val_18 = next_int_len(2)
    data.append(val_18)
    for _ in range(val_18["Value"]):
        val_32 = next_int_len(4)
        data.append(val_32)

        val_48 = next_int_len(8)
        data.append(val_48)

    return data


def get_data_after_after_leadership(dst: bool) -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    data.append(next_int_len(4))
    if not dst:
        data.append(next_int_len(5))

    if dst:
        data.append(next_int_len(12))
    else:
        data.append(next_int_len(7))
    return data


def get_legend_quest_current() -> dict[str, Any]:
    total_subchapters = next_int(1)
    stages_per_subchapter = next_int(1)
    stars = next_int(1)

    clear_progress = get_length_data(4, 1, total_subchapters * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    return {
        "Clear": clear_progress,
        "total": total_subchapters,
        "stages": stages_per_subchapter,
        "stars": stars,
    }


def get_legend_quest_progress(lengths: dict[str, Any]):
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    clear_progress = get_length_data(4, 1, total * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))
    clear_amount = get_length_data(4, 2, total * stars * stages)
    tries = get_length_data(4, 2, total * stars * stages)

    unlock_next = get_length_data(4, 1, total * stars)
    unlock_next = list(helper.chunks(unlock_next, stars))

    clear_amount = list(helper.chunks(clear_amount, stages * stars))
    tries = list(helper.chunks(tries, stages * stars))

    clear_amount_sep: list[list[list[int]]] = []
    stage_ids_sep: list[list[list[int]]] = []

    for clear_amount_val in clear_amount:
        sub_chapter_clears: list[list[int]] = []
        for j in range(stars):
            sub_chapter_clears.append(clear_amount_val[j::stars])
        clear_amount_sep.append(sub_chapter_clears)
    clear_amount = clear_amount_sep

    for stage_id_val in tries:
        sub_chapter_ids: list[list[int]] = []
        for j in range(stars):
            sub_chapter_ids.append(stage_id_val[j::stars])
        stage_ids_sep.append(sub_chapter_ids)
    tries = stage_ids_sep

    return {
        "Value": {
            "clear_progress": clear_progress,
            "clear_amount": clear_amount,
            "tries": tries,
            "unlock_next": unlock_next,
        },
        "Lengths": lengths,
    }


def get_data_after_leadership() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    data.append(next_int_len(2))
    data.append(next_int_len(1))
    data.append(next_int_len(4))  # 80600

    val_54 = next_int_len(4)
    data.append(val_54)

    if val_54["Value"] > 0:
        val_118 = next_int_len(4)
        data.append(val_118)

        val_55 = next_int_len(4)
        data.append(val_55)

        for _ in range(val_55["Value"]):
            val_61 = next_int_len(4)
            data.append(val_61)

        for _ in range(val_54["Value"] - 1):
            val_61 = next_int_len(4)
            data.append(val_61)

            val_61 = next_int_len(4)
            data.append(val_61)
    return data


def get_gauntlet_current() -> dict[str, Any]:
    total_subchapters = next_int(2)
    stages_per_subchapter = next_int(1)
    stars = next_int(1)

    clear_progress = get_length_data(4, 1, total_subchapters * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    return {
        "Clear": clear_progress,
        "total": total_subchapters,
        "stages": stages_per_subchapter,
        "stars": stars,
    }


def get_gauntlet_progress(
    lengths: dict[str, Any], unlock: bool = True
) -> dict[str, Any]:
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    clear_progress = get_length_data(4, 1, total * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    clear_amount = get_length_data(4, 2, total * stages * stars)
    unlock_next = []
    if unlock:
        unlock_next = get_length_data(4, 1, total * stars)
        unlock_next = list(helper.chunks(unlock_next, stars))

    clear_amount = list(helper.chunks(clear_amount, stages * stars))

    clear_amount_sep: list[list[list[int]]] = []

    for clear_amount_val in clear_amount:
        sub_chapter_clears: list[list[int]] = []
        for j in range(stars):
            sub_chapter_clears.append(clear_amount_val[j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {
        "Value": {
            "clear_progress": clear_progress,
            "clear_amount": clear_amount,
            "unlock_next": unlock_next,
        },
        "Lengths": lengths,
    }


class ClearedSlots:
    class Slot:
        class Cat:
            def __init__(self, cat_id: int, cat_form: int):
                self.cat_id = cat_id
                self.cat_form = cat_form

            def to_dict(self) -> dict[str, Any]:
                return {
                    "cat_id": self.cat_id,
                    "cat_form": self.cat_form,
                }

            @staticmethod
            def from_dict(data: dict[str, Any]) -> "ClearedSlots.Slot.Cat":
                return ClearedSlots.Slot.Cat(data["cat_id"], data["cat_form"])

        def __init__(self, cats: list[Cat], slot_index: int, separator: int):
            self.cats = cats
            self.slot_index = slot_index
            self.separator = separator

        def to_dict(self) -> dict[str, Any]:
            return {
                "cats": [cat.to_dict() for cat in self.cats],
                "slot_index": self.slot_index,
                "separator": self.separator,
            }

        @staticmethod
        def from_dict(data: dict[str, Any]):
            return ClearedSlots.Slot(
                [ClearedSlots.Slot.Cat.from_dict(cat) for cat in data["cats"]],
                data["slot_index"],
                data["separator"],
            )

    class StageSlot:
        class Stage:
            def __init__(self, stage_id: int):
                self.stage_id = stage_id

            def to_dict(self) -> dict[str, Any]:
                return {
                    "stage_id": self.stage_id,
                }

            @staticmethod
            def from_dict(data: dict[str, Any]) -> "ClearedSlots.StageSlot.Stage":
                return ClearedSlots.StageSlot.Stage(data["stage_id"])

        def __init__(self, slot_index: int, stages: list[Stage]):
            self.slot_index = slot_index
            self.stages = stages

        def to_dict(self) -> dict[str, Any]:
            return {
                "slot_index": self.slot_index,
                "stages": [stage.to_dict() for stage in self.stages],
            }

        @staticmethod
        def from_dict(data: dict[str, Any]) -> "ClearedSlots.StageSlot":
            return ClearedSlots.StageSlot(
                data["slot_index"],
                [
                    ClearedSlots.StageSlot.Stage.from_dict(stage)
                    for stage in data["stages"]
                ],
            )

    def __init__(self, slots: list[Slot], slot_stages: list[StageSlot], end_index: int):
        self.slots = slots
        self.slot_stages = slot_stages
        self.end_index = end_index

    def to_dict(self) -> dict[str, Any]:
        return {
            "slots": [slot.to_dict() for slot in self.slots],
            "slot_stages": [stage.to_dict() for stage in self.slot_stages],
            "end_index": self.end_index,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ClearedSlots":
        return ClearedSlots(
            [ClearedSlots.Slot.from_dict(slot) for slot in data["slots"]],
            [ClearedSlots.StageSlot.from_dict(stage) for stage in data["slot_stages"]],
            data["end_index"],
        )


def get_enigma_stages() -> dict[str, Any]:
    """
    Gets the enigma stages

    Returns:
        dict[str, Any]: The enigma stages
    """
    enigma_data: dict[str, Any] = {}
    enigma_data["energy_since_1"] = next_int(4)
    enigma_data["energy_since_2"] = next_int(4)
    enigma_data["enigma_level"] = next_int(1)
    enigma_data["unknown_2"] = next_int(1)
    enigma_data["unknown_3"] = next_int(1)

    total_stages = next_int(1)
    stages: list[dict[str, Any]] = []
    for _ in range(total_stages):
        data = {}
        data["level"] = next_int(4)  # 0 = inferior, 1 = normal, 2 = superior
        data["stage_id"] = next_int(4)
        data["decoding_status"] = next_int(
            1
        )  # 0 = not decoded, 1 = decoded, 2 = revealed
        data["start_time"] = get_double()
        stages.append(data)
    enigma_data["stages"] = stages
    return enigma_data


def get_cleared_slots() -> tuple[dict[str, Any], list[dict[str, int]]]:
    """
    Returns the line ups of the cleared stages

    Returns:
        dict[str, Any]: The line ups of the cleared stages
    """
    total_slots = next_int(2)
    index = next_int(2)
    slots: list[ClearedSlots.Slot] = []

    for _ in range(total_slots):
        cats: list[ClearedSlots.Slot.Cat] = []
        for _ in range(10):
            cat_id = next_int(2)
            cat_form = next_int(1)
            cat_data = ClearedSlots.Slot.Cat(cat_id, cat_form)
            cats.append(cat_data)
        separator = next_int(3)
        slot = ClearedSlots.Slot(cats, index, separator)
        index = next_int(2)
        slots.append(slot)

    cleared_slot_data: list[ClearedSlots.StageSlot] = []
    index_2 = next_int(2)
    for _ in range(index):
        total_stages = next_int(2)
        stages: list[ClearedSlots.StageSlot.Stage] = []
        for _ in range(total_stages):
            stage_id = next_int(4)
            stage = ClearedSlots.StageSlot.Stage(stage_id)
            stages.append(stage)
        stages_data = ClearedSlots.StageSlot(index_2, stages)
        index_2 = next_int(2)
        cleared_slot_data.append(stages_data)

    data_2: list[dict[str, int]] = []
    data_2.append({"Value": index_2, "Length": 2})
    for _ in range(index_2):
        val_18 = next_int_len(2)
        data_2.append(val_18)

        val_4 = next_int_len(1)
        data_2.append(val_4)
    data_2.append(next_int_len(4))  # 90400

    cleared_slots = ClearedSlots(slots, cleared_slot_data, index)

    return cleared_slots.to_dict(), data_2


def get_data_after_gauntlets() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    data.append(next_int_len(4 * 2))
    data.append(next_int_len(1 * 3))

    val_4 = next_int_len(1)
    data.append(val_4)
    for _ in range(val_4["Value"]):
        data.append(next_int_len(4))
        data.append(next_int_len(4))
        data.append(next_int_len(1))
        data.append(next_int_len(8))

    return data


def get_data_after_orbs() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    val_31 = next_int_len(2)
    data.append(val_31)
    for _ in range(val_31["Value"]):
        val_18 = next_int_len(2)
        data.append(val_18)

        val_5 = next_int_len(1)
        data.append(val_5)

        for _ in range(val_5["Value"]):
            val_6 = next_int_len(1)
            data.append(val_6)

            val_18 = next_int_len(2)
            data.append(val_18)
    data.append(next_int_len(1))
    data.append(next_int_len(4))  # 90700

    length = next_int_len(2)
    data.append(length)
    for _ in range(length["Value"]):
        data.append(next_int_len(4))

    data.append(next_int_len(1 * 10))
    data.append(next_int_len(4))  # 90800

    data.append(next_int_len(1))
    return data


def get_cat_shrine_data() -> dict[str, Any]:
    """
    Gets the cat shrine data

    Returns:
        dict[str, Any]: The cat shrine data
    """
    stamp_1 = get_double()
    stamp_2 = get_double()
    shrine_gone = next_int(1)
    flags: list[int] = get_length_data(1, 1)
    xp_offering = next_int(4)
    return {
        "flags": flags,
        "xp_offering": xp_offering,
        "shrine_gone": shrine_gone,
        "stamp_1": stamp_1,
        "stamp_2": stamp_2,
    }


def get_slot_names(save_stats: dict[str, Any]) -> list[str]:
    total_slots = len(save_stats["slots"])
    if save_stats["game_version"]["Value"] >= 110600:
        total_slots = next_int(1)
    names: list[str] = []
    for _ in range(total_slots):
        names.append(get_utf8_string())
    return names


def get_talent_orbs(game_version: dict[str, Any]) -> dict[int, int]:
    talent_orb_data: dict[int, int] = {}

    total_orbs = next_int(2)
    for _ in range(total_orbs):
        orb_id = next_int(2)
        if game_version["Value"] < 110400:
            amount = next_int(1)
        else:
            amount = next_int(2)
        talent_orb_data[orb_id] = amount

    return talent_orb_data


def data_after_after_gauntlets() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    data.append(next_int_len(1))
    data.append(next_int_len(8 * 2))
    data.append(next_int_len(4))
    data.append(next_int_len(1 * 2))
    data.append(next_int_len(8 * 2))
    data.append(next_int_len(4))  # 90500
    return data


def get_data_near_end_after_shards() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    data.append(next_int_len(1))
    data.append(next_int_len(4))  # 100600

    val_2 = next_int_len(2)
    data.append(val_2)

    val_3 = next_int_len(2)
    data.append(val_3)

    for _ in range(val_2["Value"]):
        val_1 = next_int_len(1)
        data.append(val_1)

        val_3 = next_int_len(2)
        data.append(val_3)
    val_6c = val_3

    val_2 = next_int_len(2)
    data.append(val_2)

    for _ in range(val_6c["Value"]):
        val_2 = next_int_len(2)
        data.append(val_2)

        for _ in range(val_2["Value"]):
            val_3 = next_int_len(2)
            data.append(val_3)

            val_4 = next_int_len(2)
            data.append(val_4)

        val_2 = next_int_len(2)
        data.append(val_2)
    val_7c = val_2
    for _ in range(val_7c["Value"]):
        val_2 = next_int_len(2)
        data.append(val_2)

        val_12 = next_int_len(4)
        data.append(val_12)
    return data


def get_data_near_end() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    val_5 = next_int_len(1)
    data.append(val_5)
    if 0 < val_5["Value"]:
        val_33 = next_int_len(4)
        data.append(val_33)
        if val_5["Value"] != 1:
            val_33 = next_int_len(4)
            data.append(val_33)
            if val_5["Value"] != 2:
                val_32 = val_5["Value"] + 2
                for _ in range(val_32):
                    data.append(next_int_len(4))

    data.append(next_int_len(1))
    data.append(next_int_len(4))  # 100400
    data.append(next_int_len(8))
    return data


def get_aku() -> dict[str, Any]:
    total = next_int(2)
    stages = next_int(1)
    stars = next_int(1)
    return get_gauntlet_progress(
        {"total": total, "stages": stages, "stars": stars}, False
    )


def get_data_after_aku() -> list[dict[str, int]]:
    data_1: list[dict[str, int]] = []

    val_6 = next_int_len(2)
    data_1.append(val_6)

    val_7 = next_int_len(2)
    data_1.append(val_7)

    for _ in range(val_6["Value"]):
        val_7 = next_int_len(2)
        data_1.append(val_7)

        for _ in range(val_7["Value"]):
            data_1.append(next_int_len(2))
        val_7 = next_int_len(2)
        data_1.append(val_7)

    val_4c = val_7
    for _ in range(val_4c["Value"]):
        data_1.append(next_int_len(2))
        data_1.append(next_int_len(8))

    val_5 = next_int_len(2)
    data_1.append(val_5)

    for _ in range(val_5["Value"]):
        data_1.append(next_int_len(2))
        data_1.append(next_int_len(8))

    data_1.append(next_int_len(1))
    return data_1


def get_data_near_end_after_aku() -> list[dict[str, int]]:
    data_2: list[dict[str, int]] = []
    val_4 = next_int_len(2)
    data_2.append(val_4)

    for _ in range(val_4["Value"]):
        data_2.append(next_int_len(4))
        data_2.append(next_int_len(1))
        data_2.append(next_int_len(1))
    return data_2


def exit_parser(save_stats: dict[str, Any]) -> dict[str, Any]:
    save_stats["hash"] = get_utf8_string(32)
    return save_stats


def check_gv(save_stats: dict[str, Any], game_version: int) -> dict[str, Any]:
    if save_stats["game_version"]["Value"] < game_version:
        save_stats = exit_parser(save_stats)
        save_stats["exit"] = True
        save_stats["extra_data"] = next_int_len(0)
    else:
        save_stats["exit"] = False
    return save_stats


def get_play_time() -> dict[str, Any]:
    raw_val = next_int_len(4)
    frames = raw_val["Value"]

    play_time_data = helper.frames_to_time(frames)

    return play_time_data


def start_parse(save_data: bytes, country_code: str) -> dict[str, Any]:
    """Start the parser and handle any exceptions."""

    try:
        save_stats = parse_save(save_data, country_code)
    except Exception:  # pylint: disable=broad-except
        helper.colored_text(
            f"\nError: An error has occurred while parsing your save data (address = {address}):",
            base=helper.RED,
        )
        traceback.print_exc()
        game_version = get_game_version(save_data)
        if game_version < 110000:
            helper.colored_text(
                f"\nThis save is from before &11.0.0& (current save version is &{helper.gv_to_str(game_version)}&), so this is likely the cause for the issue. &The save editor is not designed to work with saves from before 11.0.0&"
            )
        else:
            helper.colored_text(
                "\nPlease report this to &#bug-reports&, and/or &dm me your save& on discord"
            )
        helper.exit_editor()
        return {}
    return save_stats


def get_game_version(save_data: bytes) -> int:
    """Get the game version from the save data."""

    return convert_little(save_data[0:3])


def find_date() -> int:
    """Find the date of the save, used because for some reason in some saves there is like 40 zero bytes before the main save data"""
    for _ in range(100):
        val = next_int(4)
        if val >= 2000 and val <= 3000:
            return address - 4
    raise Exception("Could not find date")


def get_dst(save_data: bytes, offset: int) -> bool:
    """Get if the save has daylight savings from the save data, this is used to handle jp differences."""

    dst = False
    if save_data[offset] >= 15 and save_data[offset] <= 20:
        dst = True
    elif save_data[offset - 1] >= 15 and save_data[offset - 1] <= 20:
        dst = False  # Offset in jp due to no dst
    return dst


def get_double() -> float:
    """Get a double from the save data."""

    if save_data_g is None:
        raise Exception("No save data loaded")
    data = save_data_g[address : address + 8]
    val = struct.unpack("d", data)[0]
    set_address(address + 8)
    return val


def get_110800_data() -> list[dict[str, int]]:
    """
    Get the data from 11.7.0

    Returns:
        list[dict[str, int]]: The data
    """
    data: list[dict[str, int]] = []

    u_var_38 = next_int_len(1)
    data.append(u_var_38)

    return data


def get_110800_data_2() -> list[dict[str, int]]:
    """
    Get the data from 11.7.0

    Returns:
        list[dict[str, int]]: The data
    """
    data: list[dict[str, int]] = []

    u_var_38 = next_int_len(1)
    data.append(u_var_38)

    u_var_38 = next_int_len(1)
    data.append(u_var_38)

    return data


def get_110700_data() -> list[dict[str, int]]:
    """
    Get the data from 110600

    Returns:
        list[dict[str, int]]: The data
    """
    data: list[dict[str, int]] = []

    i_var_32 = next_int_len(4)
    data.append(i_var_32)

    for _ in range(i_var_32["Value"]):
        pi_var_33 = next_int_len(4)
        data.append(pi_var_33)

        f_var_54 = next_int_len(8)
        data.append(f_var_54)

        f_var_54 = next_int_len(8)
        data.append(f_var_54)

    return data


def get_login_bonuses() -> dict[int, int]:
    """
    Get the login bonuses

    Returns:
        dict[int, int]: The login bonuses
    """
    length = next_int(4)
    data: dict[int, int] = {}
    for _ in range(length):
        login_id = next_int(4)
        data[login_id] = next_int(4)
    return data


def get_tower_item_obtained() -> list[list[int]]:
    total_stars = next_int(4)
    total_stages = next_int(4)
    data: list[list[int]] = []
    for _ in range(total_stars):
        star_data: list[int] = []
        for _ in range(total_stages):
            star_data.append(next_int(1))
        data.append(star_data)
    return data


def get_dict(
    key_type: type, value_type: type, length: Optional[int] = None
) -> dict[Any, Any]:
    if length is None:
        length = next_int(4)
    data: dict[Any, Any] = {}
    for _ in range(length):
        if key_type == int:
            key = next_int(4)
        else:
            raise Exception("Invalid key type")
        if value_type == int:
            data[key] = next_int(4)
        elif value_type == str:
            data[key] = get_utf8_string()
        elif value_type == bool:
            data[key] = next_int(1) == 1
        else:
            raise Exception("Invalid value type")
    return data


class BackupState(enum.Enum):
    IDLE = 0
    GO_TO_CAN_BACKUP = 1
    IN_CAN_BACKUP = 2
    GO_TO_CHECK_BAN = 3
    IN_CHECK_BAN = 4
    GO_TO_BACKUP = 5
    IN_BACKUP = 6
    FINISHED = 7


def get_110900_data() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []

    data.append(next_int_len(4))
    data.append(next_int_len(2))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))

    ivar_14 = next_int_len(1)
    data.append(ivar_14)

    for _ in range(ivar_14["Value"]):
        data.append(next_int_len(2))

    svar6 = next_int_len(2)
    data.append(svar6)

    for _ in range(svar6["Value"]):
        data.append(next_int_len(2))

    svar6 = next_int_len(2)
    data.append(svar6)

    for _ in range(svar6["Value"]):
        data.append(next_int_len(2))

    data.append(next_int_len(4))
    data.append(next_int_len(4))
    data.append(next_int_len(4))
    data.append(next_int_len(2))
    data.append(next_int_len(2))
    data.append(next_int_len(2))
    data.append(next_int_len(2))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    svar6 = next_int_len(2)
    data.append(svar6)

    for _ in range(svar6["Value"]):
        data.append(next_int_len(2))

    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))
    data.append(next_int_len(1))

    cvar4 = next_int_len(1)
    data.append(cvar4)
    if 0 < cvar4["Value"]:
        data.append(next_int_len(2))
        if cvar4["Value"] != 1:
            data.append(next_int_len(2))
            if cvar4["Value"] != 2:
                data.append(next_int_len(2))
                if cvar4["Value"] != 3:
                    data.append(next_int_len(2))
                    if cvar4["Value"] != 4:
                        ivar32 = cvar4["Value"] + 4
                        for _ in range(ivar32):
                            data.append(next_int_len(2))
    return data


def get_zero_legends() -> list[Any]:
    total_chapters = next_int(2)
    chapters: list[dict[str, Any]] = []
    for _ in range(total_chapters):
        unknown_1 = next_int(1)
        total_stars = next_int(1)
        stars: list[dict[str, Any]] = []
        for _ in range(total_stars):
            selected_stage = next_int(1)
            stages_cleared = next_int(1)
            unlock_next = next_int(1)
            total_stages = next_int(2)
            stages: list[Any] = []
            for _ in range(total_stages):
                clear_amount = next_int(2)
                stages.append(clear_amount)
            stars.append(
                {
                    "selected_stage": selected_stage,
                    "stages_cleared": stages_cleared,
                    "unlock_next": unlock_next,
                    "stages": stages,
                }
            )
        chapters.append(
            {
                "unknown_1": unknown_1,
                "stars": stars,
            }
        )
    return chapters


def get_120100_data() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    svar19 = next_int_len(2)
    data.append(svar19)
    for _ in range(svar19["Value"]):
        data.append(next_int_len(2))

    return data


def get_120200_data() -> list[dict[str, int]]:
    data: list[dict[str, int]] = []
    data.append(next_int_len(1))
    data.append(next_int_len(2))
    cvar4 = next_int_len(1)
    data.append(cvar4)
    for _ in range(cvar4["Value"]):
        data.append(next_int_len(2))
        data.append(next_int_len(2))

    return data


def parse_save(
    save_data: bytes,
    country_code: Union[str, None],
    dst: Optional[bool] = None,
) -> dict[str, Any]:
    """Parse the save data."""
    if country_code == "ja" or country_code == "":
        country_code = "jp"
    set_address(0)
    global save_data_g
    save_data_g = save_data
    save_stats: dict[str, Any] = {}
    save_stats["editor_version"] = updater.get_local_version()

    save_stats["game_version"] = next_int_len(4)
    save_stats["version"] = country_code

    save_stats["unknown_1"] = next_int_len(1)

    save_stats["mute_music"] = next_int_len(1)
    save_stats["mute_sound_effects"] = next_int_len(1)

    save_stats["cat_food"] = next_int_len(4)
    save_stats["current_energy"] = next_int_len(4)

    old_address = address
    new_address = find_date()
    set_address(old_address)
    extra = new_address - old_address
    save_stats["extra_time_data"] = next_int_len(extra)

    if dst is None:
        dst = get_dst(save_data, address + 118)
    save_stats["dst"] = dst
    if (
        save_stats["version"] == "jp"
        and dst
        or save_stats["version"] != "jp"
        and not dst
    ):
        helper.colored_text(
            "Warning: DST detected is not correct for this save version, this may cause issues with save parsing.",
            helper.RED,
        )

    data = get_time_data_skip(save_stats["dst"])

    save_stats["time"] = data["time"]
    save_stats["dst_val"] = data["dst"]
    save_stats["time_stamp"] = data["time_stamp"]
    save_stats["duplicate_time"] = data["duplicate"]

    save_stats["unknown_flags_1"] = get_length_data(length=3)
    save_stats["upgrade_state"] = next_int_len(4)
    save_stats["xp"] = next_int_len(4)

    save_stats["tutorial_cleared"] = next_int_len(4)
    save_stats["unknown_flags_2"] = get_length_data(length=12)
    save_stats["unknown_flag_1"] = next_int_len(1)
    save_stats["slots"] = get_equip_slots()

    save_stats["cat_stamp_current"] = next_int_len(4)

    save_stats["cat_stamp_collected"] = get_length_data(length=30)
    save_stats["unknown_2"] = next_int_len(4)
    save_stats["daily_reward_flag"] = next_int_len(4)
    save_stats["unknown_116"] = get_length_data(length=10)

    save_stats["story_chapters"] = get_main_story_levels()
    save_stats["treasures"] = get_treasures()
    try:
        save_stats["enemy_guide"] = get_length_data()
    except Exception:
        return parse_save(save_data, country_code, not dst)
    if len(save_stats["enemy_guide"]) == 0:
        return parse_save(save_data, country_code, not dst)
    save_stats["cats"] = get_length_data()
    save_stats["cat_upgrades"] = get_cat_upgrades()
    save_stats["current_forms"] = get_length_data()

    save_stats["blue_upgrades"] = get_blue_upgrades()

    save_stats["menu_unlocks"] = get_length_data()
    save_stats["new_dialogs_1"] = get_length_data()

    save_stats["battle_items"] = get_length_data(4, 4, 6)
    save_stats["new_dialogs_2"] = get_length_data()
    save_stats["unknown_6"] = next_int_len(4)
    save_stats["unknown_7"] = get_length_data(length=21)

    save_stats["lock_item"] = next_int_len(1)
    save_stats["locked_items"] = get_length_data(1, 1, 6)
    save_stats["second_time"] = get_time_data(save_stats["dst"])

    save_stats["unknown_8"] = get_length_data(length=50)
    save_stats["third_time"] = get_time_data(save_stats["dst"])

    save_stats["unknown_9"] = next_int_len(6 * 4)

    save_stats["thirty2_code"] = get_utf8_string()
    save_stats["unknown_10"] = load_bonus_hash()
    save_stats["unknown_11"] = get_length_data(length=4)
    save_stats["normal_tickets"] = next_int_len(4)
    save_stats["rare_tickets"] = next_int_len(4)
    save_stats["gatya_seen_cats"] = get_length_data()
    save_stats["unknown_12"] = get_length_data(length=10)
    length = next_int(2)
    cat_storage_len = True
    if length != 128:
        skip(-2)
        cat_storage_len = False
        length = 100

    cat_storage_id = get_length_data(2, 4, length)
    cat_storage_type = get_length_data(2, 4, length)
    save_stats["cat_storage"] = {
        "ids": cat_storage_id,
        "types": cat_storage_type,
        "len": cat_storage_len,
    }
    current_sel = get_event_stages_current()
    save_stats["event_current"] = current_sel

    save_stats["event_stages"] = get_event_stages(current_sel)

    save_stats["unknown_15"] = get_length_data(length=38)
    save_stats["unit_drops"] = get_length_data()
    save_stats["rare_gacha_seed"] = next_int_len(4)
    save_stats["unknown_17"] = next_int_len(12)
    save_stats["unknown_18"] = next_int_len(4)

    save_stats["fourth_time"] = get_time_data(save_stats["dst"])
    save_stats["unknown_105"] = get_length_data(length=5)
    save_stats["unknown_107"] = get_length_data(separator=1, length=3)

    if save_stats["dst"]:
        save_stats["unknown_110"] = get_utf8_string()
    else:
        save_stats["unknown_110"] = ""

    total_strs = next_int(4)
    unknown_108: list[str] = []
    for _ in range(total_strs):
        unknown_108.append(get_utf8_string())
    save_stats["unknown_108"] = unknown_108

    if save_stats["dst"]:
        save_stats["time_stamps"] = get_length_doubles(length=3)

        length = next_int(4)
        strs: list[str] = []
        for _ in range(length):
            strs.append(get_utf8_string())
        save_stats["unknown_112"] = strs
        save_stats["energy_notice"] = next_int_len(1)
        save_stats["game_version_2"] = next_int_len(4)
    else:
        save_stats["time_stamps"] = [0, 0, 0]
        save_stats["unknown_112"] = []
        save_stats["energy_notice"] = generate_empty_len(1)
        save_stats["game_version_2"] = generate_empty_len(4)

    save_stats["unknown_111"] = next_int_len(4)
    save_stats["unlocked_slots"] = next_int_len(1)

    length_1 = next_int(4)
    length_2 = next_int(4)
    unknown_20: dict[str, Any] = {}
    unknown_20 = {"Value": get_length_data(4, 4, length_1 * length_2)}
    unknown_20["Length_1"] = length_1
    unknown_20["Length_2"] = length_2
    save_stats["unknown_20"] = unknown_20

    save_stats["time_stamps_2"] = get_length_doubles(length=4)

    save_stats["trade_progress"] = next_int_len(4)

    if save_stats["dst"]:
        save_stats["time_stamps_2"].append(get_double())
        save_stats["unknown_24"] = generate_empty_len(4)
    else:
        save_stats["unknown_24"] = next_int_len(4)

    save_stats["catseye_related_data"] = get_cat_upgrades()
    save_stats["unknown_22"] = get_length_data(length=11)
    save_stats["user_rank_rewards"] = get_length_data(4, 1)

    if not save_stats["dst"]:
        save_stats["time_stamps_2"].append(get_double())

    save_stats["unlocked_forms"] = get_length_data()
    save_stats["transfer_code"] = get_utf8_string()
    save_stats["confirmation_code"] = get_utf8_string()
    save_stats["transfer_flag"] = next_int_len(1)

    lengths = [next_int(4), next_int(4), next_int(4)]
    length = lengths[0] * lengths[1] * lengths[2]

    save_stats["stage_data_related_1"] = {
        "Value": get_length_data(4, 1, length),
        "Lengths": lengths,
    }

    save_stats["event_timed_scores"] = get_event_timed_scores()
    save_stats["inquiry_code"] = get_utf8_string()
    save_stats["play_time"] = get_play_time()

    save_stats["unknown_25"] = next_int_len(1)

    save_stats["backup_state"] = next_int_len(4)

    if save_stats["dst"]:
        save_stats["unknown_119"] = next_int_len(1)
    else:
        save_stats["unknown_119"] = generate_empty_len(1)

    save_stats["gv_44"] = next_int_len(4)

    save_stats["unknown_120"] = next_int_len(4)

    save_stats["itf_timed_scores"] = list(
        helper.chunks(get_length_data(4, 4, 51 * 3), 51)
    )

    save_stats["unknown_27"] = next_int_len(4)
    save_stats["cat_related_data_1"] = get_length_data()
    save_stats["unknown_28"] = next_int_len(1)

    save_stats["gv_45"] = next_int_len(4)
    save_stats["gv_46"] = next_int_len(4)

    save_stats["unknown_29"] = next_int_len(4)
    save_stats["lucky_tickets_1"] = get_length_data()
    save_stats["unknown_32"] = get_length_data()

    save_stats["gv_47"] = next_int_len(4)
    save_stats["gv_48"] = next_int_len(4)

    if not save_stats["dst"]:
        save_stats["energy_notice"] = next_int_len(1)
    save_stats["account_created_time_stamp"] = get_double()

    save_stats["unknown_35"] = get_length_data()
    save_stats["unknown_36"] = next_int_len(15)

    save_stats["user_rank_popups"] = next_int_len(4)

    save_stats["gv_49"] = next_int_len(4)
    save_stats["gv_50"] = next_int_len(4)
    save_stats["gv_51"] = next_int_len(4)
    save_stats["cat_guide_collected"] = get_length_data(4, 1)

    save_stats["gv_52"] = next_int_len(4)

    save_stats["time_stamps_3"] = get_length_doubles(length=5)

    save_stats["cat_fruit"] = get_length_data()
    save_stats["cat_related_data_3"] = get_length_data()
    save_stats["catseye_cat_data"] = get_length_data()
    save_stats["catseyes"] = get_length_data()
    save_stats["catamins"] = get_length_data()

    save_stats["gamatoto_time_left"] = helper.seconds_to_time(int(get_double()))
    save_stats["gamatoto_exclamation"] = next_int_len(1)
    save_stats["gamatoto_xp"] = next_int_len(4)
    save_stats["gamamtoto_destination"] = next_int_len(4)
    save_stats["gamatoto_recon_length"] = next_int_len(4)

    save_stats["unknown_43"] = next_int_len(4)

    save_stats["gamatoto_complete_notification"] = next_int_len(4)

    save_stats["unknown_44"] = get_length_data(4, 1)
    save_stats["unknown_45"] = get_length_data(4, 12 * 4)
    save_stats["gv_53"] = next_int_len(4)

    save_stats["helpers"] = get_length_data()

    save_stats["unknown_47"] = next_int_len(1)

    save_stats["gv_54"] = next_int_len(4)

    save_stats["purchases"] = get_purchase_receipts()
    save_stats["gv_54"] = next_int_len(4)
    save_stats["gamatoto_skin"] = next_int_len(4)
    save_stats["platinum_tickets"] = next_int_len(4)

    save_stats["login_bonuses"] = get_login_bonuses()
    save_stats["unknown_49"] = next_int_len(16)
    save_stats["announcment"] = get_length_data(length=32)

    save_stats["backup_counter"] = next_int_len(4)

    save_stats["unknown_131"] = get_length_data(length=3)
    save_stats["gv_55"] = next_int_len(4)

    save_stats["unknown_51"] = next_int_len(1)

    save_stats["unknown_113"] = get_data_before_outbreaks()

    save_stats["dojo_data"] = get_dojo_data_maybe()
    save_stats["dojo_item_lock"] = next_int_len(1)
    save_stats["dojo_locks"] = get_length_data(1, 1, 2)

    save_stats["unknown_114"] = next_int_len(4)
    save_stats["gv_58"] = next_int_len(4)  # 0x3a
    save_stats["unknown_115"] = next_int_len(8)

    save_stats["outbreaks"] = get_outbreaks()

    save_stats["unknown_52"] = get_double()
    save_stats["item_schemes"] = {}
    save_stats["item_schemes"]["to_obtain_ids"] = get_length_data()
    save_stats["item_schemes"]["received_ids"] = get_length_data()

    save_stats["current_outbreaks"] = get_outbreaks()

    save_stats["unknown_55"] = get_mission_data_maybe()

    save_stats["time_stamp_4"] = get_double()
    save_stats["gv_60"] = next_int_len(4)

    save_stats["unknown_117"] = get_unknown_data()

    save_stats["gv_61"] = next_int_len(4)
    data = get_unlock_popups()
    save_stats["unlock_popups"] = data[0]

    save_stats["unknown_118"] = data[1]

    save_stats["base_materials"] = get_length_data()

    save_stats["unknown_56"] = next_int_len(8)
    save_stats["unknown_57"] = next_int_len(1)
    save_stats["unknown_58"] = next_int_len(4)

    save_stats["engineers"] = next_int_len(4)
    save_stats["ototo_cannon"] = get_cat_cannon_data()

    save_stats["unknown_59"] = get_data_near_ht()

    save_stats["tower"] = get_ht_it_data()
    save_stats["missions"] = get_mission_data()
    save_stats["tower_item_obtained"] = get_tower_item_obtained()
    save_stats["unknown_61"] = get_data_after_tower()

    save_stats["challenge"] = {"Score": next_int_len(4), "Cleared": next_int_len(1)}

    save_stats["gv_67"] = next_int_len(4)  # 0x43

    save_stats["weekly_event_missions"] = get_dict(int, bool)
    save_stats["won_dojo_reward"] = next_int_len(1)
    save_stats["event_flag_update_flag"] = next_int_len(1)

    save_stats["gv_68"] = next_int_len(4)  # 0x44

    save_stats["completed_one_level_in_chapter"] = get_dict(int, int)
    save_stats["displayed_cleared_limit_text"] = get_dict(int, bool)
    save_stats["event_start_dates"] = get_dict(int, int)
    save_stats["stages_beaten_twice"] = get_length_data()

    save_stats["unknown_102"] = get_data_after_challenge()

    lengths = get_uncanny_current()
    save_stats["uncanny_current"] = lengths
    save_stats["uncanny"] = get_uncanny_progress(lengths)

    total = lengths["total"]
    save_stats["unknown_62"] = next_int_len(4)
    save_stats["unknown_63"] = get_length_data(length=total)

    save_stats["unknown_64"] = get_data_after_uncanny()

    total = save_stats["unknown_64"]["progress"]["Lengths"]["total"]
    save_stats["unknown_65"] = next_int_len(4)
    val_61 = save_stats["unknown_65"]

    save_stats["unknown_66"] = []
    unknown_66: list[Any] = []
    for _ in range(total):
        val_61 = next_int_len(4)
        unknown_66.append(val_61)
    save_stats["unknown_66"] = unknown_66

    val_54 = 0x37
    if val_61["Value"] < 0x38:
        val_54 = val_61["Value"]

    save_stats["lucky_tickets_2"] = get_length_data(length=val_54)

    save_stats["unknown_67"] = []
    if 0x37 < val_61["Value"]:
        save_stats["unknown_67"] = get_length_data(4, 4, val_61["Value"])

    save_stats["unknown_68"] = next_int_len(1)

    save_stats["gv_77"] = next_int_len(4)  # 0x4d

    save_stats["gold_pass"] = get_gold_pass_data()

    save_stats["talents"] = get_talent_data()
    save_stats["np"] = next_int_len(4)

    save_stats["unknown_70"] = next_int_len(1)

    save_stats["gv_80000"] = next_int_len(4)  # 80000

    save_stats["unknown_71"] = next_int_len(1)

    save_stats["leadership"] = next_int_len(2)
    save_stats["officer_pass_cat_id"] = next_int_len(2)
    save_stats["officer_pass_cat_form"] = next_int_len(2)

    save_stats["gv_80200"] = next_int_len(4)  # 80200
    save_stats["filibuster_stage_id"] = next_int_len(1)
    save_stats["filibuster_stage_enabled"] = next_int_len(1)

    save_stats["gv_80300"] = next_int_len(4)  # 80300

    save_stats["unknown_74"] = get_length_data()

    save_stats["gv_80500"] = next_int_len(4)  # 80500

    save_stats["unknown_75"] = get_length_data(2, 4)

    lengths = get_legend_quest_current()
    save_stats["legend_quest_current"] = lengths
    save_stats["legend_quest"] = get_legend_quest_progress(lengths)

    save_stats["unknown_133"] = get_length_data(4, 1, lengths["total"])
    save_stats["legend_quest_ids"] = get_length_data(4, 4, lengths["stages"])

    save_stats["unknown_76"] = get_data_after_leadership()
    save_stats["gv_80700"] = next_int_len(4)  # 80700
    if save_stats["dst"]:
        save_stats["unknown_104"] = next_int_len(1)
        save_stats["gv_100600"] = next_int_len(4)
        if save_stats["gv_100600"]["Value"] != 100600:
            skip(-5)
    else:
        save_stats["unknown_104"] = generate_empty_len(1)
        save_stats["gv_100600"] = generate_empty_len(4)
    save_stats["restart_pack"] = next_int_len(1)

    save_stats["unknown_101"] = get_data_after_after_leadership(save_stats["dst"])

    save_stats["medals"] = get_medals()

    save_stats["unknown_103"] = get_data_after_medals()

    lengths = get_gauntlet_current()
    save_stats["gauntlet_current"] = lengths
    save_stats["gauntlets"] = get_gauntlet_progress(lengths)

    save_stats["unknown_77"] = get_length_data(4, 1, lengths["total"])

    save_stats["gv_90300"] = next_int_len(4)  # 90300

    lengths = get_gauntlet_current()
    save_stats["unknown_78"] = lengths
    save_stats["unknown_79"] = get_gauntlet_progress(lengths)

    save_stats["unknown_80"] = get_length_data(4, 1, lengths["total"])

    save_stats["enigma_data"] = get_enigma_stages()
    data = get_cleared_slots()
    save_stats["cleared_slot_data"] = data[0]

    save_stats["unknown_121"] = data[1]

    lengths = get_gauntlet_current()
    save_stats["collab_gauntlets_current"] = lengths
    save_stats["collab_gauntlets"] = get_gauntlet_progress(lengths)
    save_stats["unknown_84"] = get_length_data(4, 1, lengths["total"])

    save_stats["unknown_85"] = data_after_after_gauntlets()

    save_stats["talent_orbs"] = get_talent_orbs(save_stats["game_version"])

    save_stats["unknown_86"] = get_data_after_orbs()

    save_stats["cat_shrine"] = get_cat_shrine_data()

    save_stats["unknown_130"] = next_int_len(4 * 5)

    save_stats["gv_90900"] = next_int_len(4)  # 90900

    save_stats["slot_names"] = get_slot_names(save_stats)
    save_stats["gv_91000"] = next_int_len(4)
    save_stats["legend_tickets"] = next_int_len(4)

    save_stats["unknown_87"] = get_length_data(1, 5)
    save_stats["unknown_88"] = next_int_len(2)

    save_stats["token"] = get_utf8_string()

    save_stats["unknown_89"] = next_int_len(1 * 3)
    save_stats["unknown_90"] = next_int_len(8)
    save_stats["unknown_91"] = next_int_len(8)

    save_stats["gv_100000"] = next_int_len(4)  # 100000
    save_stats = check_gv(save_stats, 100100)
    if save_stats["exit"]:
        return save_stats

    save_stats["date_int"] = next_int_len(4)

    save_stats["gv_100100"] = next_int_len(4)  # 100100
    save_stats = check_gv(save_stats, 100300)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_93"] = get_length_data(4, 19, 6)

    save_stats["gv_100300"] = next_int_len(4)  # 100300
    save_stats = check_gv(save_stats, 100700)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_94"] = get_data_near_end()

    save_stats["platinum_shards"] = next_int_len(4)

    save_stats["unknown_100"] = get_data_near_end_after_shards()

    save_stats["gv_100700"] = next_int_len(4)  # 100700
    save_stats = check_gv(save_stats, 100900)
    if save_stats["exit"]:
        return save_stats

    save_stats["aku"] = get_aku()

    save_stats["unknown_95"] = next_int_len(1 * 2)
    save_stats["unknown_96"] = get_data_after_aku()

    save_stats["gv_100900"] = next_int_len(4)  # 100900
    save_stats = check_gv(save_stats, 101000)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_97"] = next_int_len(1)

    save_stats["gv_101000"] = next_int_len(4)  # 101000
    save_stats = check_gv(save_stats, 110000)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_98"] = get_data_near_end_after_aku()

    save_stats["gv_110000"] = next_int_len(4)  # 110000
    save_stats = check_gv(save_stats, 110500)
    if save_stats["exit"]:
        return save_stats

    data = get_gauntlet_current()
    save_stats["behemoth_culling_current"] = data
    save_stats["behemoth_culling"] = get_gauntlet_progress(data)
    save_stats["unknown_124"] = get_length_data(4, 1, data["total"])

    save_stats["unknown_125"] = next_int_len(1)

    save_stats["gv_110500"] = next_int_len(4)  # 110500
    save_stats = check_gv(save_stats, 110600)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_126"] = next_int_len(1)

    save_stats["gv_110600"] = next_int_len(4)  # 110600
    save_stats = check_gv(save_stats, 110700)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_127"] = get_110700_data()

    if save_stats["dst"]:
        save_stats["unknown_128"] = next_int_len(1)
    else:
        save_stats["unknown_128"] = generate_empty_len(1)

    save_stats["gv_110700"] = next_int_len(4)  # 110700
    save_stats = check_gv(save_stats, 110800)
    if save_stats["exit"]:
        return save_stats

    save_stats["shrine_dialogs"] = next_int_len(4)

    save_stats["unknown_129"] = get_110800_data()

    save_stats["dojo_3x_speed"] = next_int_len(1)

    save_stats["unknown_132"] = get_110800_data_2()

    save_stats["gv_110800"] = next_int_len(4)  # 110800
    save_stats = check_gv(save_stats, 110900)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_135"] = get_110900_data()
    save_stats["gv_110900"] = next_int_len(4)  # 110900
    save_stats = check_gv(save_stats, 120000)
    if save_stats["exit"]:
        return save_stats

    save_stats["zero_legends"] = get_zero_legends()
    save_stats["unknown_136"] = next_int_len(1)
    save_stats["gv_120000"] = next_int_len(4)  # 120000
    save_stats = check_gv(save_stats, 120100)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_137"] = get_120100_data()
    save_stats["gv_120100"] = next_int_len(4)  # 120100
    save_stats = check_gv(save_stats, 120200)
    if save_stats["exit"]:
        return save_stats

    save_stats["unknown_138"] = get_120200_data()
    save_stats["gv_120200"] = next_int_len(4)  # 120200
    save_stats = check_gv(save_stats, 120200)
    if save_stats["exit"]:
        return save_stats

    length = len(save_data) - address - 32
    save_stats["extra_data"] = next_int_len(length)

    save_stats = exit_parser(save_stats)

    return save_stats
