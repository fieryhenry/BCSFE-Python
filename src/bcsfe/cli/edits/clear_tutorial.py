from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color


def clear_tutorial(
    save_file: core.SaveFile, display_already_cleared: bool = True
):
    core.StoryChapters.clear_tutorial(save_file)
    if display_already_cleared:
        color.ColoredText.localize("tutorial_cleared")
