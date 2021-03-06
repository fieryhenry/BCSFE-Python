"""Handler for clearing the tutorial"""


def clear_tutorial(save_stats: dict) -> dict:
    """Handler for clearing the tutorial"""

    save_stats["tutorial_cleared"]["Value"] = 1
    if save_stats["story_chapters"]["Chapter Progress"][0] == 0:
        save_stats["story_chapters"]["Chapter Progress"][0] = 1
    save_stats["story_chapters"]["Times Cleared"][0][0] = 1
    print("Successfully cleared the tutorial")
    return save_stats
