"""Handler for clearing main story chapters"""
from typing import Any


from ... import helper
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
    save_stats: dict[str, Any], chapter_id: int, progress: int
) -> dict[str, Any]:
    """Clear specific levels in a chapter"""
    story_chapters = save_stats["story_chapters"]
    progress = helper.clamp(progress, 0, 48)
    if progress == 0:
        story_chapters["Chapter Progress"][chapter_id] = 0
        story_chapters["Times Cleared"][chapter_id] = [0] * 51
    else:
        stage_index = progress - 1
        story_chapters["Chapter Progress"][chapter_id] = progress
        # set all levels before the one being cleared to 1
        story_chapters["Times Cleared"][chapter_id][stage_index] = 1
        for i in range(stage_index):
            story_chapters["Times Cleared"][chapter_id][i] = 1
        # set all levels after the one being cleared to 0
        for i in range(stage_index + 1, get_total_stages(save_stats, chapter_id) + 3):
            story_chapters["Times Cleared"][chapter_id][i] = 0

    save_stats["story_chapters"] = story_chapters
    return save_stats


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


def get_total_stages(save_stats: dict[str, Any], chapter_id: int) -> int:
    """Get the total number of stages in a chapter"""

    return len(save_stats["story_chapters"]["Times Cleared"][chapter_id]) - 3


def clear_each(save_stats: dict[str, Any]):
    """Clear stages for each chapter"""

    chapter_ids = story_level_id_selector.select_specific_chapters()

    for chapter_id in chapter_ids:
        helper.colored_text(f"Chapter: &{chapter_id+1}& : &{CHAPTERS[chapter_id]}&")
        formatted_id = format_story_id(chapter_id)
        progress = story_level_id_selector.select_level_progress(
            chapter_id, get_total_stages(save_stats, formatted_id)
        )
        save_stats = clear_specific_level_ids(save_stats, formatted_id, progress)
    helper.colored_text("Successfully set main story chapters")
    return save_stats


def clear_all(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear whole chapters"""

    chapter_ids = story_level_id_selector.select_specific_chapters()
    text = ""
    for chapter_id in chapter_ids:
        text += f"Chapter: &{chapter_id+1}& : &{CHAPTERS[chapter_id]}&\n"
    helper.colored_text(text.strip("\n"))
    progress = story_level_id_selector.select_level_progress(
        None, get_total_stages(save_stats, 0)
    )
    for chapter_id in chapter_ids:
        chapter_id = format_story_id(chapter_id)
        save_stats = clear_specific_level_ids(save_stats, chapter_id, progress)
    helper.colored_text("Successfully set main story chapters")
    return save_stats
