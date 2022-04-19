from BCSFE_Python import helper
from BCSFE_Python.edits.levels import main_story


def edit_outbreaks(save_stats):
    outbreaks = save_stats["outbreaks"]["outbreaks"]

    available_chapters = []
    for chapter in outbreaks.keys():
        index = chapter
        if index > 2: index -= 1
        available_chapters.append(main_story.chapters[index])


    print("What chapter do you want to edit:")
    ids = helper.selection_list(available_chapters, "clear the outbreaks for?", True)
    for id in ids:
        id = helper.validate_int(id)
        if not id: continue
        id = helper.clamp(id, 1, len(available_chapters))
        id -= 1
        if id > 2: id+=1
        outbreaks[id] = [1] * len(outbreaks[id])
    save_stats["outbreaks"]["outbreaks"] = outbreaks
    print("Successfully set outbreaks")
    return save_stats