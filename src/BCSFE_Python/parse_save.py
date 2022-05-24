import collections
import datetime
import json
import traceback

import helper

address = 0
save_data_g = None

# move all unknown vals to the bottom of the json
def re_order(class_data):
        priority = json.loads(open(helper.get_files_path("order.json"), "r", encoding="utf-8").read())
        ordered_data = collections.OrderedDict(class_data)
        
        for item in ordered_data.copy():
            if "unknown" in item:
                ordered_data.move_to_end(item)

        for i in range(len(priority)):
            ordered_data.move_to_end(priority[len(priority)-1-i], False)
        return ordered_data
    
def Set_address(val):
    global address
    if address == None:
        raise Exception("Invalid address")
    address = val


def next(number, Length=False):
    if number < 0:
        return skip(number)
    if number > len(save_data_g):
        raise Exception("Byte length is greater than the length of the save data")
    val = ConvertLittle(save_data_g[address:address+number])
    data = {}
    Set_address(address + number)
    if Length:
        data["Value"] = val
        data["Length"] = number
    else:
        return val
    return data


def skip(number):
    Set_address(address + number)


def ConvertLittle(bytes):
    return int.from_bytes(bytes, byteorder='little', signed=False)


def get_time_data_skip(dst_flag):
    year = next(4)
    year_2 = next(4)

    month = next(4)
    month_2 = next(4)

    day = next(4)
    day_2 = next(4)
    float_val = next(8)
    hour = next(4)
    minute = next(4)
    second = next(4)
    dst = 0
    if dst_flag:
        dst = next(1)

    time = datetime.datetime(year, month, day, hour, minute, second)
    return {"time" : time.isoformat(), "float" : float_val, "dst" : dst, "duplicate" : {"yy" : year_2, "mm" : month_2, "dd" : day_2}}


def get_time_data(dst_flag):
    if dst_flag:
        dst = next(1)
    year = next(4)
    month = next(4)
    day = next(4)
    hour = next(4)
    minute = next(4)
    second = next(4)

    time = datetime.datetime(year, month, day, hour, minute, second)
    return time.isoformat()


def get_length_data(length_bytes=4, separator=4, length=None):
    data = []
    if length == None:
        length = next(length_bytes)
    if length > len(save_data_g):
        raise Exception("Length too large")
    for i in range(length):
        data.append(next(separator))
    return data


def filter_array(items, value):
    filtered_array = []
    for item in items:
        if item != value:
            filtered_array.append(item)
    return filtered_array


def get_equip_slots():
    length = next(1)
    data = get_length_data(1, length=length*10)
    slots = []
    for i in range(length):
        start_pos = 10*i
        end_pos = 10*(i+1)
        slots.append(data[start_pos:end_pos])

    data = slots
    return data


def get_main_story_levels():
    chapter_progress = []
    for i in range(10):
        chapter_progress.append(next(4))
    chapter_progress_dict = chapter_progress
    times_cleared = []
    for i in range(10):
        chapter_times = []
        for i in range(51):
            chapter_times.append(next(4))
        times_cleared.append(chapter_times)
    times_cleared_dict = times_cleared
    return {"Chapter Progress": chapter_progress_dict, "Times Cleared": times_cleared_dict}


def get_treasures():
    treasures = []
    for i in range(10):
        chapter = []
        for j in range(49):
            chapter.append(next(4))
        treasures.append(chapter)
    return treasures


def get_cat_upgrades():
    length = next(4)
    data = get_length_data(4, 2, length*2)
    base_levels = data[1::2]
    plus_levels = data[0::2]

    data_dict = {"Base": base_levels,"Plus": plus_levels}
    return data_dict


def get_blue_upgrades():
    length = 11
    data = get_length_data(4, 2, length*2)
    base_levels = data[1::2]
    plus_levels = data[0::2]
    data_dict = {"Base": base_levels,"Plus": plus_levels}
    return data_dict


def get_utf8_string(length=None):
    data = get_length_data(4, 1, length)
    data = bytes(data).decode("utf-8")
    return data


def skip_some_data(save_data, total_cats):
    pos = save_data.find(total_cats.to_bytes(4, "little"), address)
    if pos > address:
         pos -= 24

    length = pos - address
    return {"Value" : next(length), "Length" : length}


def skip_some_data_two():
    length = next(2)
    get_length_data(2, 4, length)


def get_event_stages_current():
    unknown_val = next(1)
    total_sub_chapters = next(2) * unknown_val
    stars_per_sub_chapter = next(1)
    stages_per_sub_chapter = next(1)

    clear_progress = get_length_data(
        1, 1, total_sub_chapters * stars_per_sub_chapter)
    clear_progress = list(helper.chunks(
        clear_progress, stars_per_sub_chapter))

    return {"Clear": clear_progress, "unknown" : unknown_val, "total": total_sub_chapters, "stages": stages_per_sub_chapter, "stars": stars_per_sub_chapter}


def get_event_stages(lengths):
    total_sub_chapters = lengths["total"]
    stars_per_sub_chapter = lengths["stars"]
    stages_per_sub_chapter = lengths["stages"]

    clear_progress = get_length_data(
        1, 1, total_sub_chapters * stars_per_sub_chapter)
    clear_amount = get_length_data(
        1, 2, total_sub_chapters * stages_per_sub_chapter * stars_per_sub_chapter)
    unlock_next = get_length_data(
        1, 1, total_sub_chapters * stars_per_sub_chapter)

    clear_progress = list(helper.chunks(
        clear_progress, stars_per_sub_chapter))
    clear_amount = list(helper.chunks(
        clear_amount, stages_per_sub_chapter*stars_per_sub_chapter))
    unlock_next = list(helper.chunks(
        unlock_next, stars_per_sub_chapter))

    clear_amount_sep = []

    for i in range(len(clear_amount)):
        sub_chapter_clears = []
        for j in range(stars_per_sub_chapter):
            sub_chapter_clears.append(
                clear_amount[i][j::stars_per_sub_chapter])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {"Value": {"clear_progress": clear_progress, "clear_amount": clear_amount, "unlock_next": unlock_next},"Lengths" : lengths}


def get_purchase_receipts():
    total_strs = next(4)
    data = []
    
    for i in range(total_strs):
        data_dict = {"unknown_4" : next(4)}

        strings = next(4)
        data_dict["item_packs"] = []
        for j in range(strings):
            strings_dict = {}

            strings_dict["Value"] = get_utf8_string()
            strings_dict["unknown_1"] = next(1)
            data_dict["item_packs"].append(strings_dict)

        data.append(data_dict)
    return data

def get_dojo_data_maybe():
    # everything here is speculative and might not be correct
    dojo_data = {}
    total_subchapters = next(4)
    for i in range(total_subchapters):
        subchapter_id = next(4)
        subchapter_data = {}

        total_stages = next(4)
        for j in range(total_stages):
            stage_id = next(4)

            score = next(4)
            subchapter_data[stage_id] = score
        dojo_data[subchapter_id] = subchapter_data
    return dojo_data

def get_data_before_outbreaks():
    data = []

    length = next(4, True)
    data.append(length)
    for i in range(length["Value"]):
        length_2 = next(4, True)
        data.append(length_2)

        length_3 = next(4, True)
        data.append(length_3)

        for j in range(length_3["Value"]):
            val_1 = next(4, True)
            data.append(val_1)

            val_2 = next(1, True)
            data.append(val_2)


    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        val_1 = next(4, True)
        data.append(val_1)

        val_2 = next(1, True)
        data.append(val_2)

    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        val_1 = next(4, True)
        data.append(val_1)

        val_2 = next(4, True)
        data.append(val_2)
    
    length = next(4, True)
    data.append(length)

    val_1 = next(4, True)
    data.append(val_1)

    for i in range(length["Value"]):
        val_2 = next(8, True)
        data.append(val_2)

        val_3 = next(4, True)
        data.append(val_3)

    gv_56 = next(4, True) # 0x38
    data.append(gv_56)

    val_1 = next(1, True)
    data.append(val_1)

    length = next(4, True)
    data.append(length)

    val_2 = next(4, True)
    data.append(val_2)

    for i in range(length["Value"]):
        val_3 = next(1, True)
        data.append(val_3)

        val_4 = next(4, True)
        data.append(val_4)

    return data


def get_outbreaks():
    chapters_count = next(4)
    outbreaks = {}
    stages_counts = {}
    for i in range(chapters_count):
        chapter_id = next(4)
        stages_count = next(4)
        stages_counts[chapter_id] = stages_count
        chapter = {}
        for j in range(stages_count):
            stage_id = next(4)
            outbreak_cleared_flag = next(1)
            chapter[stage_id] = outbreak_cleared_flag
        outbreaks[chapter_id] = chapter
    return {"outbreaks" : outbreaks, "stages_counts" : stages_counts}

def get_mission_data_maybe():
    data = []

    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        val_1 = next(4, True)
        data.append(val_1)

        length_2 = next(4, True)
        data.append(length_2)

        for j in range(length_2["Value"]):
            val_2 = next(4, True)
            data.append(val_2)

            val_3 = next(1, True)
            data.append(val_3)

    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        val_1 = next(4, True)
        data.append(val_1)

        val_2 = next(1, True)
        data.append(val_2)

    unknown_val_1 = next(8, True)
    data.append(unknown_val_1)

    gv_60 = next(4, True) # 0x3c
    data.append(gv_60)

    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        length_2 = next(4, True)
        data.append(length_2)

        val_1 = next(4, True)
        data.append(val_1)

    unknown_val_2 = next(1, True)
    data.append(unknown_val_2)

    length = next(4, True)
    data.append(length)

    for i in range(length["Value"]):
        val_1 = next(4, True)
        data.append(val_1)

        val_2 = next(1, True)
        data.append(val_2)

    gv_61 = next(4, True) # 0x3d
    data.append(gv_61)

    length = next(4, True)
    data.append(length)

    val_1 = next(4, True)
    data.append(val_1)

    for i in range(length["Value"]):
        val_2 = next(1, True)
        data.append(val_2)

        val_3 = next(4, True)
        data.append(val_3)
    return data

def get_cat_cannon_data():
    length = next(4)
    cannon_data = {}
    for i in range(length):
        cannon = {"level" : 0, "unlock_flag" : 0}
        cannon_id = next(4)
        len_val = next(4)
        unlock_flag = next(4)
        level = next(4)
        cannon["level"] = level
        cannon["unlock_flag"] = unlock_flag
        cannon["len_val"] = len_val
        cannon_data[cannon_id] = cannon
    return cannon_data

def get_data_near_ht():
    data = []

    val = next(1, True)
    data.append(val)

    unknown_val_1 = next(val["Value"], True)
    data.append(unknown_val_1)

    for i in range(10):
        unknown_val_2 = next(3, True)
        data.append(unknown_val_2)

    unknown_val_3 = next(8, True)
    data.append(unknown_val_3)

    gv_64 = next(4, True) # 0x40
    data.append(gv_64)

    length = next(4, True)
    data.append(length)

    val_1 = next(4, True)
    data.append(val_1)

    val_3 = {"Value" : 0}
    for i in range(length["Value"]):
        val_2 = next(4, True)
        data.append(val_2)

        val_3 = next(4, True)
        data.append(val_3)

    val_1 = next(4, True)
    data.append(val_1)

    val_4 = {"Value" : 0}
    for i in range(val_3["Value"]):
        length = next(4, True)
        data.append(length)

        for i in range(length["Value"]):
            val_2 = next(4, True)
            data.append(val_2)

        val_4 = next(4, True)
        data.append(val_4)
    
    val_1 = next(4, True)
    data.append(val_1)

    for i in range(val_4["Value"]):
        val_2 = next(1, True)
        data.append(val_2)

        val_3 = next(4, True)
        data.append(val_3)
    return data

def get_ht_it_data():
    total = next(4)
    stars = next(4)

    current_data = {"total" : total, "stars" : stars, "selected" : []}

    for i in range(total):
        for j in range(stars):
            current_data["selected"].append(next(4))
    
    current_data["selected"] = list(helper.chunks(current_data["selected"], 4))

    total = next(4)
    stars = next(4)

    progress_data = {"total" : total, "stars" : stars, "clear_progress" : [], "clear_amount" : [], "unlock_next" : []}

    for i in range(total):
        for j in range(stars):
            progress_data["clear_progress"].append(next(4))
    
    progress_data["clear_progress"] = list(helper.chunks(progress_data["clear_progress"], 4))

    total = next(4)
    stages = next(4)
    progress_data["stages"] = stages
    
    stars = next(4)

    clear_amount = get_length_data(4, 4, total * stages * stars)

    clear_amount = list(helper.chunks(clear_amount, stages*stars))

    clear_amount_sep = []

    for i in range(len(clear_amount)):
        sub_chapter_clears = []
        for j in range(stars):
            sub_chapter_clears.append(
                clear_amount[i][j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    progress_data["clear_amount"] = clear_amount_sep

    data = []
    length = next(4, True)
    data.append(length)

    length_2 = next(4, True)
    data.append(length_2)

    for i in range(length["Value"]):
        for j in range(length_2["Value"]):
            data.append(next(4, True))
    return {"data" : data, "current" : current_data, "progress" : progress_data}

def get_mission_segment():
    missions = {}
    length = next(4)
    for i in range(length):
        mission_id = next(4)
        mission_value = next(4)
        missions[mission_id] = mission_value
    return missions

def get_mission_data():
    missions = {}
    missions["flags"] = get_mission_segment() # 4 = claimed, 3 = unlocked, 2 = completed 0/1 = not unlocked
    missions["values"] = get_mission_segment() # e.g number of gamatoto expeditions, stages cleared etc
    return missions

def get_looped_data():
    data = []
    val_114 = next(4, True)
    data.append(val_114)

    
    val_118 = next(4, True)
    data.append(val_118)

    for i in range(val_114["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_118 = next(4, True)
        data.append(val_118)

    
    val_114 = next(4, True)
    data.append(val_114)
    for i in range(val_118["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_114 = next(4, True)
        data.append(val_114)
    
    val_118 = next(4, True)
    data.append(val_118)

    for i in range(val_114["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_118 = next(4, True)
        data.append(val_118)
    
    val_114 = next(4, True)
    data.append(val_114)
    for i in range(val_118["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_114 = next(4, True)
        data.append(val_114)
    
    val_118 = next(4, True)
    data.append(val_118)

    for i in range(val_114["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_118 = next(4, True)
        data.append(val_118)
    
    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_118["Value"]):
        val_24 = next(4, True)
        data.append(val_24)

        val_54 = next(4, True)
        data.append(val_54)


    val_61 = next(4, True)
    data.append(val_61)

    for i in range(val_54["Value"]):
        for j in range(val_61["Value"]):
            val_15 = next(1, True)
            data.append(val_15)

    return data

def get_data_after_challenge():
    data = []
    gv_67 = next(4, True) # 0x43
    data.append(gv_67)

    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_54["Value"]):
        val_57 = next(4, True)
        data.append(val_57)

        val_15 = next(1, True)
        data.append(val_15)

    
    data.append(next(1, True))
    data.append(next(1, True))
    gv_68 = next(4, True) # 0x44
    data.append(gv_68)


    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_54["Value"]):
        val_57 = next(4, True)
        data.append(val_57)

        val_22 = next(4, True)
        data.append(val_22)
    
    val_54 = next(4, True)
    data.append(val_54)

    val_118 = next(4, True)
    data.append(val_118)
    for i in range(val_54["Value"]):
        val_15 = next(1, True)
        data.append(val_15)

        val_118 = next(4, True)
        data.append(val_118)

    
    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_118["Value"]):
        val_22 = next(4, True)
        data.append(val_22)

        val_54 = next(4, True)
        data.append(val_54)
    
    for i in range(val_54["Value"]):
        val_24 = next(4, True)
        data.append(val_24)

    val_22 = next(4, True)
    data.append(val_22)

    gv_69 = next(4, True) # 0x45
    data.append(gv_69)

    val_54 = next(4, True)
    data.append(val_54)

    val_118 = next(4, True)
    data.append(val_118)

    for i in range(val_54["Value"]):
        val_15 = next(1, True)
        data.append(val_15)

        val_118 = next(4, True)
        data.append(val_118)

    
    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_118["Value"]):
        val_65 = next(8, True)
        data.append(val_65)

        val_54 = next(4, True)
        data.append(val_54)

    #line 4905
    return data

def get_data_after_tower():
    data = []

    gv_66 = next(4, True) # 0x42
    data.append(gv_66)

    data.append(next(4*2, True))
    data.append(next(1*3, True))
    data.append(next(4*3, True))
    data.append(next(1*3, True))
    data.append(next(1, True))
    data.append(next(8, True))

    val_54 = next(4, True)
    data.append(val_54)

    val_61 = next(4, True)
    data.append(val_61)

    for i in range(val_54["Value"]):
        for j in range(val_61["Value"]):
            val_22 = next(4, True)
            data.append(val_22)
    
    val_54 = next(4, True)
    data.append(val_54)

    val_61 = next(4, True)
    data.append(val_61)

    for i in range(val_54["Value"]):
        for j in range(val_61["Value"]):
            val_22 = next(4, True)
            data.append(val_22)

    val_54 = next(4, True)
    data.append(val_54)

    val_61 = next(4, True)
    data.append(val_61)

    val_57 = next(4, True)
    data.append(val_57)
    for i in range(val_54["Value"]):
        for j in range(val_61["Value"]):
            for k in range(val_57["Value"]):
                val_22 = next(4, True)
                data.append(val_22)
    
    val_54 = next(4, True)
    data.append(val_54)

    val_61 = next(4, True)
    data.append(val_61)

    for i in range(val_54["Value"]):
        for j in range(val_61["Value"]):
            val_22 = next(4, True)
            data.append(val_22)
    
    val_54 = next(4, True)
    data.append(val_54)

    for i in range(val_54["Value"] - 1):
        val_22 = next(4, True)
        data.append(val_22)
    
    return data

def get_uncanny_current():
    total_subchapters = next(4)
    stages_per_subchapter = next(4)
    stars = next(4)
    if total_subchapters < 1:
        next(4)
    else:
        clear_progress = get_length_data(4, 4, total_subchapters * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    return {"Clear": clear_progress, "total": total_subchapters, "stages": stages_per_subchapter, "stars": stars}

def get_uncanny_progress(lengths):
    total = lengths["total"]
    stars = lengths["stars"]
    stages = lengths["stages"]

    clear_progress = get_length_data(4, 4, total * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    clear_amount = get_length_data(4, 4, total * stages * stars)
    unlock_next = get_length_data(4, 4, total * stars)

    clear_amount = list(helper.chunks(clear_amount, stages*stars))
    unlock_next = list(helper.chunks(unlock_next, stars))

    clear_amount_sep = []

    for i in range(len(clear_amount)):
        sub_chapter_clears = []
        for j in range(stars):
            sub_chapter_clears.append(
                clear_amount[i][j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {"Value": {"clear_progress": clear_progress, "clear_amount": clear_amount, "unlock_next": unlock_next}, "Lengths" : lengths}


def get_data_after_uncanny():
    lengths = get_uncanny_current()
    return {"current" : lengths, "progress" : get_uncanny_progress(lengths)}

def get_talent_data():
    data = []

    data.append(next(4*2, True))
    data.append(next(8*7, True))
    data.append(next(4, True))
    data.append(next(8, True))

    val_4 = next(4, True)
    data.append(val_4)
    for i in range(val_4["Value"]):
        val_7 = next(4, True)
        data.append(val_7)
        val_3 = next(4, True)
        data.append(val_3)
    
    data.append(next(8, True))
    data.append(next(1, True))
    data.append(next(1, True))

    total_cats = next(4)

    talents = {}
    for i in range(total_cats):
        cat_id = next(4)
        cat_data = []

        number_of_talents = next(4)

        for j in range(number_of_talents):
            talent_id = next(4)
            talent_level = next(4)
            talent = {"id" : talent_id, "level" : talent_level}
            cat_data.append(talent)
        talents[cat_id] = cat_data
    return {"talents" : talents, "dump" : data}

    #line 5136

def get_medals():
    medal_data_1 = get_length_data(2, 2)

    total_medals = next(2)
    medals = {}

    for i in range(total_medals):
        medal_id = next(2)
        medal_flag = next(1)
        medals[medal_id] = medal_flag
    return {"medal_data_1" : medal_data_1, "medal_data_2" : medals}

def get_data_after_medals():
    data = []
    data.append(next(1, True))

    val_2 = next(2, True)
    data.append(val_2)

    val_3 = next(2, True)
    data.append(val_3)

    for i in range(val_2["Value"]):
        val_1 = next(1, True)
        data.append(val_1)

        val_3 = next(2, True)
        data.append(val_3)

    val_2 = next(2, True)
    data.append(val_2)

    val_6c = val_3
    for i in range(val_6c["Value"]):
        val_2 = next(2, True)
        data.append(val_2)
        for j in range(val_2["Value"]):
            val_3 = next(2, True)
            data.append(val_3)

            val_4 = next(2, True)
            data.append(val_4)

        val_2 = next(2, True)
        data.append(val_2)

    val_7c = val_2
    for i in range(val_7c["Value"]):
        val_2 = next(2, True)
        data.append(val_2)

        val_12 = next(4, True)
        data.append(val_12)

    
    data.append(next(4, True)) # 90000

    data.append(next(4, True))
    data.append(next(4, True))
    data.append(next(8, True))
    data.append(next(4, True)) # 90100

    val_18 = next(2, True)
    data.append(val_18)
    for i in range(val_18["Value"]):
        data.append(next(4, True))
        data.append(next(4, True))
        data.append(next(2, True))
        data.append(next(4, True))
        data.append(next(4, True))
        data.append(next(4, True))
        data.append(next(2, True))

    val_18 = next(2, True)
    data.append(val_18)
    for i in range(val_18["Value"]):
        val_32 = next(4, True)
        data.append(val_32)

        val_48 = next(8, True)
        data.append(val_48)


    #line 5434
    return data

def get_data_after_after_leadership(dst):
    data = []
    data.append(next(4, True))
    if not dst:
        data.append(next(5, True))

    if dst:
        data.append(next(12, True))
    else:
        data.append(next(7, True))
    return data

def get_data_after_leadership():
    data = []
    val_16 = next(1, True)
    data.append(val_16)

    val_45 = next(1, True)
    data.append(val_45)

    val_18 = next(1, True)
    data.append(val_18)


    for i in range(val_16["Value"]):
        for j in range(val_18["Value"]):
            val_15 = next(1, True)
            data.append(val_15)

    for i in range(val_16["Value"]):
        for j in range(val_18["Value"]):
            val_15 = next(1, True)
            data.append(val_15)

    for i in range(val_16["Value"]):
        for j in range(val_45["Value"]):
            for k in range(val_18["Value"]):
                val_20 = next(2, True)
                data.append(val_20)

    for i in range(val_16["Value"]):
        for j in range(val_45["Value"]):
            for k in range(val_18["Value"]):
                val_20 = next(2, True)
                data.append(val_20)

    for i in range(val_16["Value"]):
        for j in range(val_18["Value"]):
            val_15 = next(1, True)
            data.append(val_15)


    for i in range(val_16["Value"]):
        data.append(next(1, True))
    for i in range(48):
        data.append(next(4, True))

    data.append(next(2, True))
    data.append(next(1, True))
    data.append(next(4, True)) # 80600

    val_54 = next(4, True)
    data.append(val_54)

    if val_54["Value"] > 0:
        val_118 = next(4, True)
        data.append(val_118)

        val_55 = next(4, True)
        data.append(val_55)

        for i in range(val_55["Value"]):
            val_61 = next(4, True)
            data.append(val_61)
        
        for i in range(val_54["Value"] - 1):
            val_61 = next(4, True)
            data.append(val_61)

            val_61 = next(4, True)
            data.append(val_61)
    return data

def get_gauntlet_current():
    total_subchapters = next(2)
    stages_per_subchapter = next(1)
    stars = next(1)

    clear_progress = get_length_data(4, 1, total_subchapters * stars)
    clear_progress = list(helper.chunks(clear_progress, stars))

    return {"Clear": clear_progress, "total": total_subchapters, "stages": stages_per_subchapter, "stars": stars}

def get_gauntlet_progress(lengths, unlock=True):
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

    clear_amount = list(helper.chunks(clear_amount, stages*stars))

    clear_amount_sep = []

    for i in range(len(clear_amount)):
        sub_chapter_clears = []
        for j in range(stars):
            sub_chapter_clears.append(
                clear_amount[i][j::stars])
        clear_amount_sep.append(sub_chapter_clears)

    clear_amount = clear_amount_sep
    return {"Value": {"clear_progress": clear_progress, "clear_amount": clear_amount, "unlock_next": unlock_next}, "Lengths" : lengths}


def get_data_after_gauntlets():
    data = []
    
    data.append(next(4*2, True))
    data.append(next(1*3, True))

    val_4 = next(1, True)
    data.append(val_4)
    for i in range(val_4["Value"]):
        data.append(next(4, True))
        data.append(next(4, True))
        data.append(next(1, True))
        data.append(next(8, True))
    
    val_20 = next(2, True)
    data.append(val_20)

    val_18 = next(2, True)
    data.append(val_18)

    for i in range(val_20["Value"]):
        data.append(next((2+1) * 10, True))
        data.append(next(3, True))
        val_18 = next(2, True)
        data.append(val_18)
    
    val_20 = next(2, True)
    data.append(val_20)

    for i in range(val_18["Value"]):
        val_30 = next(2, True)
        data.append(val_30)

        for j in range(val_30["Value"]):
            val_33 = next(4, True)
            data.append(val_33)

        val_20 = next(2, True)
        data.append(val_20)

    
    for i in range(val_20["Value"]):
        val_18 = next(2, True)
        data.append(val_18)
        
        val_4 = next(1, True)
        data.append(val_4)


    data.append(next(4, True)) # 90400
    return data

def get_data_after_orbs():
    data = []
    val_31 = next(2, True)
    data.append(val_31)
    for i in range(val_31["Value"]):
        val_18 = next(2, True)
        data.append(val_18)

        val_5 = next(1, True)
        data.append(val_5)

        for j in range(val_5["Value"]):
            val_6 = next(1, True)
            data.append(val_6)

            val_18 = next(2, True)
            data.append(val_18)
    data.append(next(1, True))
    data.append(next(4, True)) # 90700

    length = next(2, True)
    data.append(length)
    for i in range(length["Value"]):
        data.append(next(4, True))

    data.append(next(1*10, True))
    data.append(next(4, True)) # 90800

    data.append(next(1, True))
    data.append(next(8*2, True))
    data.append(next(1, True))

    length = next(1, True)
    data.append(length)
    for i in range(length["Value"]):
        data.append(next(1, True))

    data.append(next(8*3, True))
    data.append(next(4, True)) # 90900
    return data
    
    

def get_slot_names(total_slots):
    names = []
    for i in range(total_slots):
        names.append(get_utf8_string())
    return names
def get_talent_orbs(game_version):
    talent_orb_data = {}

    total_orbs = next(2)    
    for i in range(total_orbs):
        orb_id = next(2)
        if game_version["Value"] < 110400:
            amount = next(1)
        else:
            amount = next(2)
        talent_orb_data[orb_id] = amount

    
    return talent_orb_data


def data_after_after_gauntlets():
    data = []

    data.append(next(1, True))
    data.append(next(8 * 2, True))
    data.append(next(4, True))
    data.append(next(1*2, True))
    data.append(next(8*2, True))
    data.append(next(4, True)) # 90500
    return data    

def get_data_near_end_after_shards():
    data = []
    data.append(next(1, True))
    data.append(next(4, True)) # 100600

    val_2 = next(2, True)
    data.append(val_2)

    val_3 = next(2, True)
    data.append(val_3)

    for i in range(val_2["Value"]):
        val_1 = next(1, True)
        data.append(val_1)

        val_3 = next(2, True)
        data.append(val_3)
    val_6c = val_3

    val_2 = next(2, True)
    data.append(val_2)

    for i in range(val_6c["Value"]):
        val_2 = next(2, True)
        data.append(val_2)

        for j in range(val_2["Value"]):
            val_3 = next(2, True)
            data.append(val_3)

            val_4 = next(2, True)
            data.append(val_4)

        val_2 = next(2, True)
        data.append(val_2)
    val_7c = val_2
    for i in range(val_7c["Value"]):
        val_2 = next(2, True)
        data.append(val_2)

        val_12 = next(4, True)
        data.append(val_12)
    return data

def get_data_near_end():
    data = []
    val_5 = next(1, True)
    data.append(val_5)
    if 0 < val_5["Value"]:
        val_33 = next(4, True)
        data.append(val_33)
        if val_5["Value"] != 1:
            val_33 = next(4, True)
            data.append(val_33)
            if val_5["Value"] != 2:
                val_32 = val_5["Value"] + 2
                for i in range(val_32):
                    data.append(next(4, True))

    data.append(next(1, True))
    data.append(next(4, True)) # 100400
    data.append(next(8, True))
    return data

def get_aku():
    total = next(2)
    stages = next(1)
    stars = next(1)
    return get_gauntlet_progress({"total" : total, "stages" : stages, "stars" : stars}, False)                

def get_data_after_aku():
    data_1 = []

    val_6 = next(2, True)
    data_1.append(val_6)

    val_7 = next(2, True)
    data_1.append(val_7)

    for i in range(val_6["Value"]):
        val_7 = next(2, True)
        data_1.append(val_7)

        for j in range(val_7["Value"]):
            data_1.append(next(2, True))
        val_7 = next(2, True)
        data_1.append(val_7)

    val_4c = val_7
    for i in range(val_4c["Value"]):
        data_1.append(next(2, True))
        data_1.append(next(8, True))
    
    val_5 = next(2, True)
    data_1.append(val_5)

    for i in range(val_5["Value"]):
        data_1.append(next(2, True))
        data_1.append(next(8, True))
        
    data_1.append(next(1, True))
    return data_1
def get_data_near_end_after_aku():  
    data_2 = []
    val_4 = next(2, True)
    data_2.append(val_4)

    for i in range(val_4["Value"]):
        data_2.append(next(4, True))
        data_2.append(next(1, True))
        data_2.append(next(1, True))
    return data_2

def exit_parser(save_stats):
    save_stats["hash"] = get_utf8_string(32)
    return save_stats

def check_gv(save_stats, game_version):
    if save_stats["game_version"]['Value'] < game_version:
        save_stats = exit_parser(save_stats)
        save_stats["exit"] = True
    else:
        save_stats["exit"] = False
    return save_stats

def get_play_time():
    raw_val = next(4, True)
    frames = raw_val["Value"]

    play_time_data = helper.frames_hmsf(frames)

    return play_time_data

def start_parse(save_data, game_version_country):
    try:
        save_stats = parse_save(save_data, game_version_country)
    except Exception:
        helper.coloured_text(f"\nError: An error has occurred while parsing your save data ({address=}):", base=helper.red)
        traceback.print_exc()
        game_version = get_game_version(save_data)
        if game_version < 110000:
            helper.coloured_text(f"\nThis save is from before &11.0.0& (current save version is &{helper.gv_to_str(game_version)}&), so this is likely the cause for the issue. &The save editor is not designed to work with saves from before 11.0.0&")
        else:
            helper.coloured_text("\nPlease report this to &#bug-reports&, and/or &dm me your save& on discord")
        helper.coloured_text("Press enter to exit:", is_input=True)
        exit()
    return save_stats

def get_game_version(save_data):
    return ConvertLittle(save_data[0:3])

def find_date():
    for i in range(100):
        val = next(4)
        if val >= 2000 and val <= 3000:
            return address - 4
    return None

def get_dst(save_data, address):
    dst = False
    if save_data[address] == 15:
        dst = True
    elif save_data[address-1] == 15:
        dst = False  # Offset in jp due to no dst
    return dst


def parse_save(save_data, game_version_country):
    Set_address(0)
    global save_data_g
    save_data_g = save_data
    save_stats = {}
    save_stats["editor_version"] = helper.get_version()

    save_stats["game_version"] = next(4, True)
    save_stats["version"] = game_version_country

    save_stats["unknown_1"] = next(3, True)

    save_stats["cat_food"] = next(4, True)
    save_stats["current_energy"] = next(4, True)

    old_address = address
    new_address = find_date()
    Set_address(old_address)
    extra = new_address-old_address
    save_stats["extra_time_data"] = next(extra, True)
    
    dst = get_dst(save_data, address+118)
    save_stats["dst"] = dst
    data = get_time_data_skip(save_stats["dst"])

    save_stats["time"] = data["time"]
    save_stats["dst_val"] = data["dst"]
    save_stats["float_val_1"] = data["float"]
    save_stats["duplicate_time"] = data["duplicate"]

    save_stats["unknown_flags_1"] = get_length_data(length=4)
    save_stats["xp"] = next(4, True)

    save_stats["tutorial_cleared"] = next(4, True)
    save_stats["unknown_flags_2"] = get_length_data(length=12)
    save_stats["unknown_flag_1"] = next(1, True)
    save_stats["slots"] = get_equip_slots()

    save_stats["cat_stamp_current"] = next(4, True)

    save_stats["cat_stamp_collected"] = get_length_data(length=30)
    save_stats["unknown_2"] = get_length_data(length=12)

    save_stats["story_chapters"] = get_main_story_levels()
    save_stats["treasures"] = get_treasures()
    save_stats["enemy_guide"] = get_length_data()
    save_stats["cats"] = get_length_data()
    save_stats["cat_upgrades"] = get_cat_upgrades()
    save_stats["current_forms"] = get_length_data()

    save_stats["blue_upgrades"] = get_blue_upgrades()

    save_stats["menu_unlocks"] = get_length_data()
    save_stats["unknown_5"] = get_length_data()

    save_stats["battle_items"] = get_length_data(4, 4, 6)
    save_stats["new_dialogs"] = get_length_data()
    save_stats["unknown_6"] = next(4, True)
    save_stats["unknown_7"] = get_length_data(length=21)

    save_stats["lock_item"] = next(1, True)
    save_stats["locked_items"] = get_length_data(1, 1, 6)
    save_stats["second_time"] = get_time_data(save_stats["dst"])

    save_stats["unknown_8"] = get_length_data(length=50)
    save_stats["third_time"] = get_time_data(save_stats["dst"])
    
    save_stats["unknown_9"] = next(6*4, True)

    save_stats["thirty2_code"] = get_utf8_string()
    save_stats["unknown_10"] = skip_some_data(save_data, len(save_stats["cats"]))
    save_stats["unknown_11"] = get_length_data(length=4)
    save_stats["normal_tickets"] = next(4, True)
    save_stats["rare_tickets"] = next(4, True)
    save_stats["other_cat_data"] = get_length_data()
    save_stats["unknown_12"] = get_length_data(length=10)
    length = next(2)
    cat_storage_len = True
    if length != 128: 
        skip(-2)
        cat_storage_len = False
        length = 100

    cat_storage_id = get_length_data(2, 4, length)
    cat_storage_type = get_length_data(2, 4, length)
    save_stats["cat_storage"] = {"ids" : cat_storage_id, "types" : cat_storage_type, "len" : cat_storage_len}
    current_sel = get_event_stages_current()
    save_stats["event_current"] = current_sel

    save_stats["event_stages"] = get_event_stages(current_sel)

    save_stats["unknown_15"] = get_length_data(length=38)
    save_stats["unit_drops"] = get_length_data()
    save_stats["rare_gacha_seed"] = next(4, True)
    save_stats["unknown_17"] = next(12, True)
    save_stats["unknown_18"] = next(4, True)

    save_stats["fourth_time"] = get_time_data(save_stats["dst"])
    save_stats["unknown_105"] = get_length_data(length=5)
    save_stats["unknown_108"] = {}
    save_stats["unknown_107"] = next(3, True)
    if save_stats["game_version"]["Value"] < 110500 or save_stats["dst"]:
        save_stats["unknown_110"] = get_utf8_string()
    total_strs = next(4)
    save_stats["unknown_108"] = []
    for i in range(total_strs):
        save_stats["unknown_108"].append(get_utf8_string())
    if save_stats["dst"]:
        save_stats["unknown_112"] = {}
        floats = []
        floats.append(next(8, True))
        floats.append(next(8, True))
        floats.append(next(8, True))
        save_stats["unknown_112"]["floats"] = floats

        length = next(4)
        strs = []
        for i in range(length):
            strs.append(get_utf8_string())
        save_stats["unknown_112"]["strs"] = strs
        data = []
        data.append(next(1, True))
        data.append(next(4, True))
        data.append(next(4, True))
        save_stats["unknown_112"]["data"] = data
    if not save_stats["dst"]:
        save_stats["unknown_111"] = next(4, True)
    save_stats["unlocked_slots"] = next(1, True)
    length_1 = next(4)
    length_2 = next(4)
    save_stats["unknown_20"] = {"Value": get_length_data(4, 4, length_1 * length_2)}
    save_stats["unknown_20"]["Length_1"] = length_1
    save_stats["unknown_20"]["Length_2"] = length_2

    save_stats["unknown_21"] = get_length_data(length=8)
    save_stats["trade_progress"] = next(4, True)
    
    if save_stats["dst"]:
        save_stats["unknown_24"] = get_length_data(length=2)
    else:
        save_stats["unknown_24"] = get_length_data(length=1)

    save_stats["catseye_related_data"] = get_length_data()
    save_stats["unknown_22"] = get_length_data(length=11)
    save_stats["user_rank_rewards"] = get_length_data(4, 1)

    if save_stats["dst"]:
        save_stats["unknown_23"] = next(0, True)
    else:
        save_stats["unknown_23"] = next(8, True)

    save_stats["unlocked_forms"] = get_length_data()
    save_stats["transfer_code"] = get_utf8_string()
    save_stats["confirmation_code"] = get_utf8_string()
    save_stats["transfer_flag"] = next(1, True)

    lengths = [next(4), next(4), next(4)]
    length = lengths[0] * lengths[1] * lengths[2]

    save_stats["stage_data_related_1"] = {"Value": get_length_data(4, 1, length), "Lengths" : lengths}

    lengths = [next(4), next(4), next(4)]
    length = lengths[0] * lengths[1] * lengths[2]

    save_stats["event_timed_scores"] = {"Value": get_length_data(4, 4, length), "Lengths" : lengths}

    save_stats["inquiry_code"] = get_utf8_string()
    save_stats["play_time"] = get_play_time()
    save_stats["unknown_25"] = next(14, True)

    save_stats["itf_timed_scores"] = list(helper.chunks(get_length_data(4, 4, 51*3), 51))

    if save_stats["dst"]:
        save_stats["unknown_27"] = next(4, True)
    else:
        save_stats["unknown_27"] = next(3, True)

    save_stats["cat_related_data_1"] = get_length_data()
    save_stats["unknown_28"] = next(1, True)

    save_stats["gv_45"] = next(4, True)
    save_stats["gv_46"] = next(4, True)

    save_stats["unknown_29"] = next(8, True)
    save_stats["unknown_30"] = next(4, True)
    save_stats["lucky_tickets_1"] = get_length_data(length=20)
    save_stats["unknown_32"] = get_length_data(length=20)

    save_stats["gv_47"] = next(4, True)
    save_stats["gv_48"] = next(4, True)

    if save_stats["dst"]:
        save_stats["unknown_34"] = next(8, True)
    else:
        save_stats["unknown_34"] = next(9, True)

    save_stats["unknown_35"] = get_length_data()
    save_stats["unknown_36"] = next(15, True)

    save_stats["user_rank_popups"] = next(3, True)

    save_stats["unknown_37"] = next(1, True)

    save_stats["gv_49"] = next(4, True)
    save_stats["gv_50"] = next(4, True)
    save_stats["gv_51"] = next(4, True)

    save_stats["cat_guide_collected"] = get_length_data(4, 1)


    save_stats["gv_52"] = next(4, True)

    save_stats["unknown_40"] = get_length_data(4, 8, 5)
    save_stats["cat_fruit"] = get_length_data()
    save_stats["cat_related_data_3"] = get_length_data()
    save_stats["catseye_cat_data"] = get_length_data()
    save_stats["catseyes"] = get_length_data()
    save_stats["catamins"] = get_length_data()

    save_stats["unknown_42"] = next(9, True)

    save_stats["gamatoto_xp"] = next(4, True)
    save_stats["unknown_43"] = get_length_data(length=4)
    save_stats["unknown_44"] = get_length_data(4, 1)
    save_stats["unknown_45"] = get_length_data(4, 12*4)
    save_stats["gv_53"] = next(4, True)

    save_stats["helpers"] = get_length_data()
    save_stats["unknown_47"] = next(1, True)
    save_stats["gv_54"] = next(4, True)

    save_stats["purchases"] = get_purchase_receipts()
    save_stats["gv_54"] = next(4, True)
    save_stats["gamatoto_skin"] = next(4, True)
    save_stats["platinum_tickets"] = next(4, True)

    save_stats["unknown_48"] = get_length_data(4, 8)
    save_stats["unknown_49"] = next(16, True)
    save_stats["unknown_50"] = get_length_data(length=36)

    save_stats["gv_55"] = next(4, True)

    save_stats["unknown_51"] = next(1, True)

    save_stats["unknown_113"] = get_data_before_outbreaks()
    
    save_stats["dojo_data"] = get_dojo_data_maybe()

    save_stats["unknown_114"] = next(7, True)

    save_stats["gv_58"] = next(4, True) # 0x3a
    
    save_stats["unknown_115"] = next(8, True)
    save_stats["outbreaks"] = get_outbreaks()

    save_stats["unknown_52"] = next(8, True)
    save_stats["unknown_53"] = get_length_data()
    save_stats["unknown_54"] = get_length_data()

    save_stats["unknown_55"] = get_mission_data_maybe()

    save_stats["base_materials"] = get_length_data()

    save_stats["unknown_56"] = next(8, True)
    save_stats["unknown_57"] = next(1, True)
    save_stats["unknown_58"] = next(4, True)

    save_stats["engineers"] = next(4, True)
    save_stats["ototo_cannon"] = get_cat_cannon_data()

    save_stats["unknown_59"] = get_data_near_ht()

    save_stats["tower"] = get_ht_it_data()
    save_stats["missions"] = get_mission_data()

    save_stats["unknown_60"] = get_looped_data()
    save_stats["unknown_61"] = get_data_after_tower()

    save_stats["challenge"] = {"Score" : next(4, True), "Cleared" : next(1, True)}

    save_stats["unknown_102"] = get_data_after_challenge()

    lengths = get_uncanny_current()
    save_stats["uncanny_current"] = lengths
    save_stats["uncanny"] = get_uncanny_progress(lengths)

    total = lengths["total"]
    save_stats["unknown_62"] = next(4, True)
    save_stats["unknown_63"] = get_length_data(length=total)

    save_stats["unknown_64"] = get_data_after_uncanny()

    total = save_stats["unknown_64"]["progress"]["Lengths"]["total"]
    save_stats["unknown_65"] = next(4, True)
    val_61 = save_stats["unknown_65"]

    save_stats["unknown_66"] = []
    for i in range(total):
        val_61 = next(4, True)
        save_stats["unknown_66"].append(val_61)

    val_54 = 0x37
    if val_61["Value"] < 0x38:
        val_54 = val_61

    save_stats["lucky_tickets_2"] = get_length_data(length=val_54["Value"])

    save_stats["unknown_67"] = []
    if 0x37 < val_61["Value"]:
        save_stats["unknown_67"] = get_length_data(4, 4, val_61)

    save_stats["unknown_68"] = next(1, True)

    save_stats["gv_77"] = next(4, True) # 0x4d

    data = get_talent_data()
    save_stats["unknown_69"] = data["dump"]
    save_stats["talents"] = data["talents"]

    save_stats["np"] = next(4, True)

    save_stats["unknown_70"] = next(1, True)

    save_stats["gv_80000"] = next(4, True) # 80000

    save_stats["unknown_71"] = next(1, True)

    save_stats["leadership"] = next(2, True)

    save_stats["unknown_72"] = next(4, True)

    save_stats["gv_80200"] = next(4, True) # 80200

    save_stats["unknown_73"] = next(2, True)

    save_stats["gv_80300"] = next(4, True) # 80300

    save_stats["unknown_74"] = get_length_data()

    save_stats["gv_80500"] = next(4, True) # 80500
    
    save_stats["unknown_75"] = get_length_data(2, 4)
    save_stats["unknown_76"] = get_data_after_leadership()
    save_stats["gv_80700"] = next(4, True) # 80700
    if save_stats["dst"]:
        save_stats["unknown_104"] = next(1, True)
        save_stats["gv_100600"] = next(4, True)
        if save_stats["gv_100600"]["Value"] != 100600:
            skip(-5)
    save_stats["restart_pack"] = next(1, True)

    save_stats["unknown_101"] = get_data_after_after_leadership(save_stats["dst"])

    save_stats["medals"] = get_medals()

    save_stats["unknown_103"] = get_data_after_medals()

    lengths = get_gauntlet_current()
    save_stats["gauntlet_current"] = lengths
    save_stats["gauntlets"] = get_gauntlet_progress(lengths)

    save_stats["unknown_77"] = get_length_data(4, 1, lengths["total"])

    save_stats["gv_90300"] = next(4, True) # 90300

    lengths = get_gauntlet_current()
    save_stats["unknown_78"] = lengths
    save_stats["unknown_79"] = get_gauntlet_progress(lengths)

    save_stats["unknown_80"] = get_length_data(4, 1, lengths["total"])

    save_stats["unknown_81"] = get_data_after_gauntlets()

    lengths = get_gauntlet_current()
    save_stats["unknown_82"] = lengths
    save_stats["unknown_83"] = get_gauntlet_progress(lengths)
    save_stats["unknown_84"] = get_length_data(4, 1, lengths["total"])


    save_stats["unknown_85"] = data_after_after_gauntlets()

    save_stats["talent_orbs"] = get_talent_orbs(save_stats["game_version"])

    save_stats["unknown_86"] = get_data_after_orbs()

    save_stats["slot_names"] = get_slot_names(len(save_stats["slots"]))
    save_stats["gv_91000"] = next(4, True)
    save_stats["legend_tickets"] = next(4, True)

    save_stats["unknown_87"] = get_length_data(1, 5)
    save_stats["unknown_88"] = next(2, True)

    save_stats["token"] = get_utf8_string()

    save_stats["unknown_89"] = next(1*3, True)
    save_stats["unknown_90"] = next(8, True)
    save_stats["unknown_91"] = next(8, True)

    save_stats = check_gv(save_stats, 100000)
    if save_stats["exit"]: return save_stats
    save_stats["gv_100000"] = next(4, True) # 100000

    save_stats["date_int"] = next(4, True)

    save_stats = check_gv(save_stats, 100100)
    if save_stats["exit"]: return save_stats
    save_stats["gv_100100"] = next(4, True) # 100100

    save_stats["unknown_93"] = get_length_data(4, 19, 6)
    
    save_stats = check_gv(save_stats, 100300)
    if save_stats["exit"]: return save_stats
    save_stats["gv_100300"] = next(4, True) # 100300

    save_stats["unknown_94"] = get_data_near_end()

    save_stats["platinum_shards"] = next(4, True)

    save_stats["unknown_100"] = get_data_near_end_after_shards()

    save_stats = check_gv(save_stats, 100700)
    if save_stats["exit"]: return save_stats
    save_stats["gv_100700"] = next(4, True) # 100700

    save_stats["aku"] = get_aku()

    save_stats["unknown_95"] = next(1*2, True)
    save_stats["unknown_96"] = get_data_after_aku()

    save_stats = check_gv(save_stats, 100900)
    if save_stats["exit"]: return save_stats
    save_stats["gv_100900"] = next(4, True) # 100900

    save_stats["unknown_97"] = next(1, True)

    save_stats = check_gv(save_stats, 101000)
    if save_stats["exit"]: return save_stats
    save_stats["gv_101000"] = next(4, True) # 101000

    save_stats["unknown_98"] = get_data_near_end_after_aku()

    save_stats = check_gv(save_stats, 110000)
    if save_stats["exit"]: return save_stats
    save_stats["gv_110000"] = next(4, True) # 110000

    length = len(save_data) - address - 32
    save_stats["extra_data"] = next(length, True)
    
    save_stats = exit_parser(save_stats)

    return save_stats

