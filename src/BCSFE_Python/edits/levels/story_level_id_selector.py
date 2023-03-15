"""Handler for selecting story levels"""
from typing import Optional

from ... import user_input_handler, helper
from . import main_story


def select_specific_chapters() -> list[int]:
    """Select specific levels"""

    print("What chapters do you want to select?")
    ids = user_input_handler.select_not_inc(main_story.CHAPTERS, "clear")
    return ids


def get_option():
    """Get option"""

    options = [
        "Select specific levels with stage ids",
        "Select all levels up to a certain stage",
        "Select all levels",
    ]
    return user_input_handler.select_single(options)


def select_levels(
    chapter_id: Optional[int], forced_option: Optional[int] = None, total: int = 48
) -> list[int]:
    """Select levels"""

    if forced_option is None:
        choice = get_option()
    else:
        choice = forced_option
    if choice == 1:
        return select_specific_levels(chapter_id, total)
    if choice == 2:
        return select_levels_up_to(chapter_id, total)
    if choice == 3:
        return select_all(total)
    return []


def select_specific_levels(chapter_id: Optional[int], total: int) -> list[int]:
    """Select specific levels"""

    print("What levels do you want to select?")
    if chapter_id is not None:
        helper.colored_text(
            f"Chapter: &{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    ids = user_input_handler.get_range_ids(
        "Level ids (e.g &1&=korea, &2&=mongolia)", total
    )
    ids = helper.check_clamp(ids, total, 1, -1)
    return ids


def select_levels_up_to(chapter_id: Optional[int], total: int) -> list[int]:
    """Select levels up to a certain level"""

    print("What levels do you want to select?")
    if chapter_id is not None:
        helper.colored_text(
            f"Chapter: &{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    stage_id = user_input_handler.get_int(
        f"Enter the stage id that you want to clear/unclear up to (and including) (e.g &1&=korea cleared, &2&=korea &and& mongolia cleared, &{total}&=all)?:"
    )
    stage_id = helper.clamp(stage_id, 1, total)
    return list(range(0, stage_id))


def select_all(total: int) -> list[int]:
    """Select all levels"""

    return list(range(0, total))


def select_level_progress(
    chapter_id: Optional[int], total: int, examples: Optional[list[str]] = None
) -> int:
    """Select level progress"""

    if examples is None:
        examples = [
            "korea",
            "mongolia",
        ]

    print("What level do you want to clear up to and including?")
    if chapter_id is not None:
        helper.colored_text(
            f"Chapter: &{chapter_id+1}& : &{main_story.CHAPTERS[chapter_id]}&"
        )
    progress = user_input_handler.get_int(
        f"Enter the stage id that you want to clear/unclear (e.g &1&={examples[0]} cleared, &2&={examples[0]} &and& {examples[1]} cleared, &{total}&=all, &0&=unclear all)?:"
    )
    progress = helper.clamp(progress, 0, total)
    return progress
