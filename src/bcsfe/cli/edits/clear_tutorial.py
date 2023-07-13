from bcsfe import core
from bcsfe.cli import color


def clear_tutorial(save_file: "core.SaveFile", display_already_cleared: bool = True):
    if not core.StoryChapters.is_tutorial_clear(save_file):
        core.StoryChapters.clear_tutorial(save_file)
        color.ColoredText.localize("tutorial_cleared")
    else:
        if display_already_cleared:
            color.ColoredText.localize("tutorial_already_cleared")
