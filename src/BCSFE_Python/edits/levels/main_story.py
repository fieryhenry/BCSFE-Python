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
    
    if "10" in ids:
        ids = range(1, 10)
        ids = [format(x, '02d') for x in ids]
    
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue

        id = helper.clamp(id, 1, 10)
        id -= 1
        helper.coloured_text(f"{chapters[id]}:")
        if id > 2: id+=1
        max_stage_id = helper.validate_int(helper.coloured_text("Enter the stage id that you want to clear up to (and including) (e.g &1&=korea cleared, &2&=korea &and& mongolia cleared)?:", is_input=True))
        if not max_stage_id: continue

        max_stage_id = helper.clamp(max_stage_id, 1, 48)
        
        story_chapters["Chapter Progress"][id] = max_stage_id
        story_chapters["Times Cleared"][id] = ([1] * max_stage_id) + ([0] * (48 - max_stage_id)) + ([0] * 3)

    save_stats["story_chapters"] = story_chapters
    print("Successfully cleared story levels")

    return save_stats
def main_story(save_stats):
    whole = helper.coloured_text("Do you want to edit whole chapters at once &(1)& or specific stages &(2)&?:", is_input=True)
    if whole == "2": return specific_levels(save_stats)
    story_chapters = save_stats["story_chapters"]


    print("What chapters do you want to beat completely?")
    helper.create_list(chapters)
    ids = helper.coloured_text("10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")

    if "10" in ids:
        ids = range(1, 10)
        ids = [format(x, '02d') for x in ids]
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue

        id = helper.clamp(id, 1, 10)
        id -= 1
        if id > 2: id+=1

        story_chapters["Chapter Progress"][id] = 48
        story_chapters["Times Cleared"][id] = ([1] * 48) + ([0] * 3)
    save_stats["story_chapters"] = story_chapters
    print("Successfully cleared story chapters")
    return save_stats