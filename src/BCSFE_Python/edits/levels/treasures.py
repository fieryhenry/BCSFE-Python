from edits.levels import main_story
import helper

def get_stages():
    treasures_values = []
    eoc_treasures = helper.parse_csv_file(helper.get_files_path("game_data/treasures/treasureData0.csv"), min_length=1, black_list=["//", "\n", "\t"], parse=True)[11:22]
    itf_treasures = helper.parse_csv_file(helper.get_files_path("game_data/treasures/treasureData1.csv"), min_length=1, black_list=["//", "\n", "\t"], parse=True)[11:22]
    cotc_treasures = helper.parse_csv_file(helper.get_files_path("game_data/treasures/treasureData2_0.csv"), min_length=1, black_list=["//", "\n", "\t"], parse=True)[11:22]
    
    treasures_values.append(remove_negative_1(eoc_treasures))
    treasures_values.append(remove_negative_1(itf_treasures))
    treasures_values.append(remove_negative_1(cotc_treasures))
    return treasures_values

def get_treasure_groups():
    treasure_stages = get_stages()
    treasure_names = get_names()
    return {"names": treasure_names, "stages" : treasure_stages}

def get_names():
    names = []
    eoc_names = helper.parse_csv_file(helper.get_files_path("game_data/treasures/Treasure3_0_en.csv"), min_length=3, black_list=["//", "\n", "\t"], separator="|")[:11]
    itf_names = helper.parse_csv_file(helper.get_files_path("game_data/treasures/Treasure3_1_AfterFirstEncounter_en.csv"), min_length=3, black_list=["//", "\n", "\t"], separator="|")[:11]
    cotc_names = helper.parse_csv_file(helper.get_files_path("game_data/treasures/Treasure3_2_0_en.csv"), min_length=3, black_list=["//", "\n", "\t"], separator="|")[:11]
    
    names.append(helper.copy_first_n(eoc_names, 0))
    names.append(helper.copy_first_n(itf_names, 0))
    names.append(helper.copy_first_n(cotc_names, 0))

    return names

def remove_negative_1(data):
    new_data = data.copy()
    for i in range(len(data)):
        if -1 in data[i]:
            new_data[i] = new_data[i][:-1]
    return new_data

def treasure_groups(save_stats):
    treasure_groups = get_treasure_groups()
    treasures = save_stats["treasures"]

    helper.create_list(main_story.chapters)
    ids = helper.coloured_text("Enter a number from 1 to 9 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    
    ids = helper.validate_clamp(ids, 9, 1, -1)

    for chapter_id in ids:
        print(f"Chapter: {main_story.chapters[chapter_id]}")
        type_id = chapter_id // 3
        if chapter_id > 2: chapter_id+=1
        names = treasure_groups["names"][type_id]
        treasure_levels = [-1] * len(names)
        treasure_levels = helper.edit_array_user(names, treasure_levels, None, "treasures", "treasure level", custom_text="What do you want to set your treasure level to? (&0&=none, &1&=inferior, &2&=normal, &3&=superior)")
        
        for i in range(len(treasure_levels)):
            treasure_level = treasure_levels[i]
            if treasure_level == -1: continue
            stages = treasure_groups["stages"][type_id][i]
            for stage in stages:
                treasures[chapter_id][stage] = treasure_level
    save_stats["treasures"] = treasures

    return save_stats
def specific_treasures(save_stats):
    individual = helper.valdiate_bool(helper.coloured_text("Do you want to edit the treasures for individual levels &(1)&, or groups of treasures (e.g energy drink, aqua crystal) &(2)&?:",is_input=True), "1")
    if not individual:
        return treasure_groups(save_stats)
    treasures = save_stats["treasures"]

    helper.create_list(main_story.chapters)
    ids = helper.coloured_text("Enter a number from 1 to 9 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    
    ids = helper.create_all_list(ids, 9)
    ids = helper.validate_clamp(ids, 9, 1, -1)

    for chapter_id in ids:
        stage_ids = helper.get_range_input(helper.coloured_text(f"Enter stage ids for chapter {main_story.chapters[chapter_id]}(e.g 1=korea, 2=mongolia)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), 49)
        stage_ids_data = helper.create_all_list(stage_ids, 49, True)

        stage_ids = stage_ids_data["ids"]
        stage_ids = helper.validate_clamp(stage_ids, 49, 1, -1)
        all_at_once = stage_ids_data["at_once"]

        treasure_data = [-1] * 49
        treasure_data = helper.handle_all_at_once(stage_ids, all_at_once, treasure_data, range(1, 50), "treasure level", "stage", "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)")
        if chapter_id > 2: chapter_id+=1
        for i in range(len(treasure_data)):
            stage = treasure_data[i]
            if stage == -1: continue
            if i > 45:
                id = i
            else:
                id = 45 - i
            treasures[chapter_id][id] = stage

    save_stats["treasures"] = treasures
    print("Successfully set treasures")
    return save_stats

def treasures(save_stats):
    treasures = save_stats["treasures"]

    helper.create_list(main_story.chapters)
    ids = helper.coloured_text("10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    
    data = helper.create_all_list(ids, 10, True)
    ids = data["ids"]
    ids = helper.validate_clamp(ids, 10, 1, -1)
    all_at_once = data["at_once"]
    usr_levels = [-1] * 9
    usr_levels = helper.handle_all_at_once(ids, all_at_once, usr_levels, main_story.chapters, "treasure level", "chapter", "(&0&=none, &1&=inferior, &2&=normal, &3&=superior)")
    for i in range(len(usr_levels)):
        level = usr_levels[i]
        if level == -1: continue
        if i > 2: i+=1
        treasures[i] = [level] * 48 + [0]

    save_stats["treasures"] = treasures
    print("Successfully set treasures")
    return save_stats