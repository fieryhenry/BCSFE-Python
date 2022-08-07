"""Handler for claiming all user rank rewards"""

from typing import Any

from ... import helper


def claim(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Claim all user rank rewards"""

    save_stats["user_rank_rewards"] = [1] * len(save_stats["user_rank_rewards"])

    helper.colored_text("Claimed all user rank rewards", helper.GREEN)

    return save_stats