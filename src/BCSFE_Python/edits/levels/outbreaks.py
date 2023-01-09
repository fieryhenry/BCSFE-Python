"""Handler for editting outbreaks"""
from typing import Any, Optional

from ... import user_input_handler, helper
from . import main_story


def get_available_chapters(outbreaks: dict[int, Any]) -> list[str]:
    """Get available chapters"""

    available_chapters: list[str] = []
    for chapter_index in outbreaks:
        if chapter_index > 2:
            chapter_index -= 1
        if chapter_index > 6:
            continue
        available_chapters.append(main_story.CHAPTERS[chapter_index])
    return available_chapters


def set_outbreak(
    chapter_data: dict[int, int], val_to_set: int, total: Optional[int] = None
) -> dict[int, int]:
    """Set a chapter of an outbreak"""
    if total is None:
        total = len(chapter_data)

    for level_id in range(total):
        chapter_data[level_id] = val_to_set
    return chapter_data


def set_outbreaks(
    outbreaks: dict[int, Any],
    current_outbreaks: dict[int, Any],
    ids: list[int],
    clear: bool = True,
) -> tuple[dict[int, Any], dict[int, Any]]:
    """Set outbreaks"""
    for chapter_id in ids:
        outbreaks[chapter_id] = set_outbreak(
            outbreaks[chapter_id], 1 if clear else 0, 48
        )
        if chapter_id in current_outbreaks:
            if clear:
                current_outbreaks[chapter_id] = {}
    return outbreaks, current_outbreaks


def edit_outbreaks(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting outbreaks"""

    outbreaks = save_stats["outbreaks"]
    current_outbreaks = save_stats["current_outbreaks"]

    clear = (
        user_input_handler.colored_input(
            "Do you want to clear or un-clear outbreaks? (&c&/&u&): "
        )
        == "c"
    )

    available_chapters = get_available_chapters(outbreaks)

    print("What chapter do you want to edit:")
    ids = user_input_handler.select_not_inc(
        options=available_chapters,
        mode="clear the outbreaks for?",
    )
    ids = helper.check_clamp(ids, len(available_chapters) + 1, 0, 0)
    ids = main_story.format_story_ids(ids)
    outbreaks, current_outbreaks = set_outbreaks(
        outbreaks, current_outbreaks, ids, clear
    )
    save_stats["outbreaks"] = outbreaks
    save_stats["current_outbreaks"] = current_outbreaks
    print("Successfully set outbreaks")
    return save_stats
