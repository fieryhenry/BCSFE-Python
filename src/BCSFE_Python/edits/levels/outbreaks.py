import helper
from edits.levels import main_story


def encode_ls(list):
    out_dict = {}
    for i in range(len(list)):
        out_dict[i] = list[i]
    return out_dict


def edit_outbreaks(save_stats):
    outbreaks = save_stats["outbreaks"]["outbreaks"]

    available_chapters = []
    for chapter in outbreaks.keys():
        index = chapter
        if index > 2:
            index -= 1
        available_chapters.append(main_story.chapters[index])

    print("What chapter do you want to edit:")
    ids = helper.selection_list(
        available_chapters, "clear the outbreaks for?", True)
    ids = helper.validate_clamp(ids, len(available_chapters), 1, -1)
    ids = main_story.format_story_ids(ids)
    for id in ids:
        outbreaks[id] = encode_ls([1] * len(outbreaks[id]))
    save_stats["outbreaks"]["outbreaks"] = outbreaks
    print("Successfully set outbreaks")
    return save_stats
