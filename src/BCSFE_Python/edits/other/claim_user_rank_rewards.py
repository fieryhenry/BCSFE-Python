"""Handler for claiming all user rank rewards"""

from typing import Any

from ... import helper, user_input_handler


def claim(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Claim all user rank rewards"""

    save_stats["user_rank_rewards"] = [1] * len(save_stats["user_rank_rewards"])

    helper.colored_text("Claimed all user rank rewards", helper.GREEN)

    return save_stats


def edit_rewards(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Edit all user rank rewards"""

    option = user_input_handler.select_single(
        [
            "Claim all user rank rewards",
            "Clear all user rank rewards",
            "Back",
        ],
    )
    if option == 1:
        save_stats = claim(save_stats)
    elif option == 2:
        save_stats = clear(save_stats)
    return save_stats


def clear(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Clear all user rank rewards"""

    save_stats["user_rank_rewards"] = [0] * len(save_stats["user_rank_rewards"])

    helper.colored_text("Unclaimed all user rank rewards", helper.GREEN)

    return save_stats
