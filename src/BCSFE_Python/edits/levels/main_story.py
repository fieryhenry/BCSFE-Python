"""Handler for clearing main story chapters"""
from typing import Any


from ... import helper, user_input_handler
from . import story_level_id_selector

CHAPTERS = [
    "Empire of Cats 1",
    "Empire of Cats 2",
    "Empire of Cats 3",
    "Into the Future 1",
    "Into the Future 2",
    "Into the Future 3",
    "Cats of the Cosmos 1",
    "Cats of the Cosmos 2",
    "Cats of the Cosmos 3",
]

def clear_specific_level_ids(
    story_chapters: dict[str, Any], chapter_id: int, ids: list[int], val: int
) -> dict[str, Any]:
    """Clear specific levels in a chapter"""

    if val >= 1:
        story_chapters["Chapter Progress"][chapter_id] = max(ids)
    else:
        story_chapters["Chapter Progress"][chapter_id] = min(ids) - 1

    for level_id in ids:
        story_chapters["Times Cleared"][chapter_id][level_id] = val
    return story_chapters

def has_cleared_chapter(save_stats: dict[str, Any], chapter_id: int) -> bool:
    """
    Check if a chapter has been cleared

    Args:
        save_stats (dict[str, Any]): Save stats
        chapter_id (int): Chapter ID

    Returns:
        bool: True if cleared, False if not
    """
    chapter_id = format_story_id(chapter_id)

    return save_stats["story_chapters"]["Chapter Progress"][chapter_id] >= 48


def format_story_ids(ids: list[int]) -> list[int]:
    """For some reason there is a gap after EoC 3. This adds that"""

    formatted_ids: list[int] = []
    for story_id in ids:
        formatted_ids.append(format_story_id(story_id))
    return formatted_ids


def format_story_id(chapter_id: int) -> int:
    """For some reason there is a gap after EoC 3. This adds that"""

    if chapter_id > 2:
        chapter_id += 1
    return chapter_id


def clear_levels(
    story_chapters: dict[str, Any],
    treasures: list[list[int]],
    ids: list[int],
    val: int,
    chapter_progress: int,
    clear: bool,
) -> tuple[dict[str, Any], list[list[int]]]:
    """Clear levels in a chapter"""

    for chapter_id in ids:
        story_chapters["Chapter Progress"][chapter_id] = chapter_progress
        story_chapters["Times Cleared"][chapter_id] = (
            ([val] * chapter_progress) + ([0] * (48 - chapter_progress)) + ([0] * 3)
        )
        if not clear:
            treasures[chapter_id] = [0] * 49
    return story_chapters, treasures


def clear_each(save_stats: dict[str, Any]):
    """Clear stages for each chapter"""

    clear = user_input_handler.colored_input("Do you want to clear or unclear (c/u)?:") == "c"

    chapter_ids = story_level_id_selector.select_specific_chapters()

    for chapter_id in chapter_ids:
        helper.colored_text(f"Chapter: &{chapter_id+1}& : &{CHAPTERS[chapter_id]}&")
        ids = story_level_id_selector.select_levels(chapter_id)
        chapter_id = format_story_id(chapter_id)
        save_stats["story_chapters"] = clear_specific_level_ids(
            save_stats["story_chapters"], chapter_id, ids, 1 if clear else 0
        )
    helper.colored_text("Successfully cleared main story chapters")
    return save_stats


def clear_all(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear whole chapters"""

    clear = user_input_handler.colored_input("Do you want to clear or unclear (c/u)?:") == "c"
    chapter_ids = story_level_id_selector.select_specific_chapters()
    text = ""
    for chapter_id in chapter_ids:
        text += f"Chapter: &{chapter_id+1}& : &{CHAPTERS[chapter_id]}&\n"
    helper.colored_text(text.strip("\n"))
    ids = story_level_id_selector.select_levels(None)
    for chapter_id in chapter_ids:
        chapter_id = format_story_id(chapter_id)
        save_stats["story_chapters"] = clear_specific_level_ids(
            save_stats["story_chapters"], chapter_id, ids, 1 if clear else 0
        )
    helper.colored_text("Successfully cleared main story chapters")
    return save_stats
