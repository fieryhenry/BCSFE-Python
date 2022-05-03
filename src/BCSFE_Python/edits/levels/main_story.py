import helper


chapters = ["Empire of Cats 1", "Empire of Cats 2", "Empire of Cats 3",
                "Into the Future 1", "Into the Future 2", "Into the Future 3",
                "Cats of the Cosmos 1", "Cats of the Cosmos 2", "Cats of the Cosmos 3"
            ]

def specific_levels(save_stats):
    story_chapters = save_stats["story_chapters"]

    print("What chapters do you want to select?")
    helper.create_list(chapters)
    ids = helper.coloured_text("10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    ids = helper.validate_clamp(ids, 10, 1, -1)
    story_chapters = specific_handler(ids, story_chapters)
    save_stats["story_chapters"] = story_chapters

    print("Successfully cleared story levels")

    return save_stats

def specific_handler(ids, data):
    for id in ids:
        max_level = helper.coloured_text("Enter the stage id that you want to clear up to (and including) (e.g &1&=korea cleared, &2&=korea &and& mongolia cleared)?:", is_input=True)
        max_level = helper.validate_int(max_level)
        if max_level == None:
            print("Please input a number")
            return data
        max_level = helper.clamp(max_level, 1, 48)
        data["Chapter Progress"][id] = max_level
        data["Times Cleared"][id] = ([1] * max_level) + ([0] * (48 - max_level)) + ([0] * 3)
            
    return data

def main_story(save_stats):
    whole = helper.coloured_text("Do you want to edit whole chapters at once &(1)& or specific stages &(2)&?:", is_input=True)
    if whole == "2": return specific_levels(save_stats)
    story_chapters = save_stats["story_chapters"]

    print("What chapters do you want to beat completely?")
    helper.create_list(chapters)
    
    ids = helper.coloured_text("10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    ids = helper.create_all_list(ids, 10)
    ids = helper.validate_clamp(ids, 10, 1, -1)

    story_chapters = edit_story(ids, story_chapters, 48)
    save_stats["story_chapters"] = story_chapters

    print("Successfully cleared story chapters")
    return save_stats

def format_story_ids(ids):
    formatted_ids = []
    for id in ids:
        if id > 2:
            id+=1
        formatted_ids.append(id)
    return formatted_ids

def edit_story(ids, data, chapter_progress):
    ids = format_story_ids(ids)
    for id in ids:
        data["Chapter Progress"][id] = chapter_progress
        data["Times Cleared"][id] = ([2] * chapter_progress) + ([0] * (48 - chapter_progress)) + ([0] * 3)
    return data