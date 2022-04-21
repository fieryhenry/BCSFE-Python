from edits.levels import main_story
import helper

def treasures(save_stats):
    treasures = save_stats["treasures"]
    helper.create_list(main_story.chapters)
    ids = helper.coloured_text("10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    all_at_once = False
    if "10" in ids:
        ids = range(1, 10)
        all_at_once = True
        ids = [format(x, '02d') for x in ids]
    first = True
    level = 0
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue
        id = helper.clamp(id, 1, 10)
        id -= 1

        if all_at_once and first:
            level = helper.validate_int(helper.coloured_text("Enter treasure level (&0& = none, &1&=inferior, &2&=normal, &3&=superior):", is_input=True))
            first = False
        elif not all_at_once:
            level = helper.validate_int(helper.coloured_text(f"Enter treasure level for chapter &{main_story.chapters[id]}& (&0& = none, &1&=inferior, &2&=normal, &3&=superior):", is_input=True))
        if not level: continue
        if id > 2: id+=1
        treasures[id] = [level] * 48 + [0]
    save_stats["treasures"] = treasures
    print("Successfully set treasures")
    return save_stats