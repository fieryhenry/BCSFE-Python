"""Handler for setting into the future timed scores"""

from ..levels import main_story
from ... import item


def timed_scores(save_stats: dict) -> dict:
    """Handler for setting into the future timed scores"""

    scores = save_stats["itf_timed_scores"]

    usr_scores = item.create_item_group(
        names=main_story.chapters[3:6],
        values=None,
        maxes=9999,
        edit_name="score",
        group_name="Into The Future Timed Scores",
    )
    usr_scores.edit()
    for i, usr_score in enumerate(usr_scores.values):
        if usr_score is not None:
            scores[i] = ([usr_score] * 48) + ([0] * 3)
    save_stats["itf_timed_scores"] = scores

    print("Successfully set timed scores")
    return save_stats
