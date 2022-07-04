"""Handler for editting outbreaks"""

from ... import helper, user_input_handler
from ..levels import main_story


def encode_ls(lst: list) -> dict:
    """Encode a list of integers into a dictionary"""
    return {i: lst[i] for i in range(len(lst))}


def edit_outbreaks(save_stats: dict) -> dict:
    """Handler for editting outbreaks"""

    outbreaks = save_stats["outbreaks"]["outbreaks"]

    available_chapters = []
    for chapter in outbreaks.keys():
        index = chapter
        if index > 2:
            index -= 1
        available_chapters.append(main_story.chapters[index])

    print("What chapter do you want to edit:")
    ids = user_input_handler.select_options(
        options=available_chapters,
        mode="clear the outbreaks for?",
    )
    ids = helper.check_clamp(ids, len(available_chapters), 1, -1)
    ids = main_story.format_story_ids(ids)
    for chapter_id in ids:
        outbreaks[chapter_id] = encode_ls([1] * len(outbreaks[chapter_id]))
    save_stats["outbreaks"]["outbreaks"] = outbreaks
    print("Successfully set outbreaks")
    return save_stats
