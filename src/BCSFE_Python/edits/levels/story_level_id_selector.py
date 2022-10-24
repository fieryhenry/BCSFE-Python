"""Handler for selecting story levels"""
from typing import Optional

from ... import user_input_handler, helper
from . import main_story

def select_specific_chapters() -> list[int]:
    """Select specific levels"""

    print("What chapters do you want to select?")
    ids = user_input_handler.select_not_inc(
        main_story.CHAPTERS, "clear"
    )
    return ids


def select_level_progress(chapter_id: Optional[int], total: int) -> int:
    """Select level progress"""

    print("What level do you want to clear up to and including?")
    if chapter_id is not None:
        helper.colored_text(
            f"Chapter: &{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    progress = user_input_handler.get_int(
        f"Enter the stage id that you want to clear/unclear (e.g &1&=korea cleared, &2&=korea &and& mongolia cleared, &{total}&=all, &0&=unclear all)?:"
    )
    progress = helper.clamp(progress, 0, total)
    return progress
