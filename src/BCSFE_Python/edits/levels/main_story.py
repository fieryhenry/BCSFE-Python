"""Handler for clearing main story chapters"""

from ... import helper, user_input_handler

chapters = [
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


def specific_levels(save_stats: dict) -> dict:
    """Clear whole chapters"""

    story_chapters = save_stats["story_chapters"]

    print("What chapters do you want to select?")
    helper.colored_list(chapters)
    ids = user_input_handler.colored_input(
        "10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")
    ids = helper.check_clamp(ids, 10, 1, -1)
    story_chapters = specific_handler(ids, story_chapters)
    save_stats["story_chapters"] = story_chapters

    print("Successfully cleared story levels")

    return save_stats


def specific_handler(ids: list, data: dict) -> dict:
    """Clear specific stages in a chapter"""

    for chapter_id in ids:
        max_level = user_input_handler.colored_input(
            "Enter the stage id that you want to clear up to (and including) (e.g &1&=korea cleared, &2&=korea &and& mongolia cleared)?:"
        )
        max_level = helper.check_int(max_level)
        if max_level is None:
            print("Please input a number")
            return data
        max_level = helper.clamp(max_level, 1, 48)
        data["Chapter Progress"][chapter_id] = max_level
        data["Times Cleared"][chapter_id] = (
            ([1] * max_level) + ([0] * (48 - max_level)) + ([0] * 3)
        )

    return data


def main_story(save_stats: dict) -> dict:
    """Handler for editing story chapters"""

    whole = user_input_handler.colored_input(
        "Do you want to edit whole chapters at once &(1)& or specific stages &(2)&?:"
    )
    if whole == "2":
        return specific_levels(save_stats)
    story_chapters = save_stats["story_chapters"]

    print("What chapters do you want to beat completely?")
    helper.colored_list(chapters)

    ids = user_input_handler.colored_input(
        "10. &All at once&\nEnter a number from 1 to 10 (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")
    ids = user_input_handler.create_all_list(ids, 10)
    ids = helper.check_clamp(ids, 10, 1, -1)

    story_chapters = edit_story(ids, story_chapters, 48)
    save_stats["story_chapters"] = story_chapters

    print("Successfully cleared story chapters")
    return save_stats


def format_story_ids(ids: list) -> list:
    """For some reason there is a gap after EoC 3. This adds that"""

    formatted_ids = []
    for story_id in ids:
        if story_id > 2:
            story_id += 1
        formatted_ids.append(story_id)
    return formatted_ids


def edit_story(ids: list, data: dict, chapter_progress: int) -> dict:
    """Edit story chapters for a set of ids"""

    ids = format_story_ids(ids)
    for chapter_id in ids:
        data["Chapter Progress"][chapter_id] = chapter_progress
        data["Times Cleared"][chapter_id] = (
            ([1] * chapter_progress) + ([0] * (48 - chapter_progress)) + ([0] * 3)
        )
    return data
