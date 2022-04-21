from edits.levels import main_story
import helper

def timed_scores(save_stats):
    scores = save_stats["itf_timed_scores"]
    helper.create_list(main_story.chapters[3:6])
    ids = helper.coloured_text("4. &All at once&\nEnter a number from 1 to 4 (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    all_at_once = False
    if "4" in ids:
        ids = range(1, 4)
        all_at_once = True
        ids = [format(x, '02d') for x in ids]
    first = True
    level = 0
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue
        id = helper.clamp(id, 1, 4)
        id -= 1

        if all_at_once and first:
            level = helper.validate_int(input("Enter timed score:"))
            first = False
        elif not all_at_once:
            level = helper.validate_int(helper.coloured_text(f"Enter timed score for chapter &{main_story.chapters[3:6][id]}&:", is_input=True))
        if not level: continue
        scores[id] = ([level] * 48) + ([0] * 3)
    save_stats["itf_timed_scores"] = scores
    print("Successfully set timed scores")
    return save_stats