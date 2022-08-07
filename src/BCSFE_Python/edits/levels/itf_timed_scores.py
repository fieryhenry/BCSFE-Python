"""Handler for setting into the future timed scores"""
from typing import Any

from ... import item
from . import main_story

def set_scores(scores: list[list[int]], usr_scores: list[int]) -> list[list[int]]:
    """Set the scores for a stage"""

    for i, usr_score in enumerate(usr_scores):
        if usr_score is not None:
            scores[i] = ([usr_score] * 48) + ([0] * 3)
    return scores


def timed_scores(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for setting into the future timed scores"""

    scores = save_stats["itf_timed_scores"]

    usr_scores = item.create_item_group(
        names=main_story.CHAPTERS[3:6],
        values=None,
        maxes=9999,
        edit_name="score",
        group_name="Into The Future Timed Scores",
    )
    usr_scores.edit()
    save_stats["itf_timed_scores"] = set_scores(
        scores, usr_scores.values
    )

    print("Successfully set timed scores")
    return save_stats
