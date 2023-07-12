from bcsfe.core import io, game
from bcsfe.cli import color


def clear_tutorial(save_file: "io.save.SaveFile", display_already_cleared: bool = True):
    if not game.map.story.is_tutorial_clear(save_file):
        game.map.story.clear_tutorial(save_file)
        color.ColoredText.localize("tutorial_cleared")
    else:
        if display_already_cleared:
            color.ColoredText.localize("tutorial_already_cleared")
