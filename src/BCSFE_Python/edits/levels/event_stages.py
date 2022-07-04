"""Handler for clearing event stages"""
from ... import helper, user_input_handler


def stage_handler(
    stage_data: dict, ids: list, offset: int, unlock_next: bool = True
) -> dict:
    """Clear stages from a set of ids"""

    lengths = stage_data["Lengths"]

    individual = True
    if len(ids) > 1:
        individual = user_input_handler.colored_input(
            "Do you want to set the stars/crowns for each subchapter individually(&1&), or all at once(&2&):"
        ) == "1"
    first = True
    stars = None
    for stage_id in ids:
        if not individual and first:
            stars = helper.check_int(
                user_input_handler.colored_input(
                    f"Enter the number of stars/cowns (max &{lengths['stars']}&):"
                )
            )
            if stars is None:
                print("Please enter a valid number")
                continue
            stars = helper.clamp(stars, 0, lengths["stars"])
            first = False
        elif individual:
            stars = helper.check_int(
                user_input_handler.colored_input(
                    f"Enter the number of stars/cowns for subchapter &{stage_id}& (max &{lengths['stars']}&):"
                )
            )
            if stars is None:
                print("Please enter a valid number")
                continue
            stars = helper.clamp(stars, 0, lengths["stars"])
        stage_id += offset
        stage_data_edit = stage_data
        if stage_id >= len(stage_data_edit["Value"]["clear_progress"]):
            continue
        stage_data_edit["Value"]["clear_progress"][stage_id] = (
            [lengths["stages"]] * stars
        ) + ([0] * (lengths["stars"] - stars))
        if unlock_next and stage_id + 1 < len(
            stage_data_edit["Value"]["clear_progress"]
        ):
            stage_data_edit["Value"]["unlock_next"][stage_id + 1] = (
                [lengths["stars"] - 1] * stars
            ) + ([0] * (lengths["stars"] - stars))
        stage_data_edit["Value"]["clear_amount"][stage_id] = (
            [[1] * lengths["stages"]] * stars
        ) + ([[0] * lengths["stages"]] * (lengths["stars"] - stars))

    print("Successfully set subchapters")

    return stage_data_edit


def stories_of_legend(save_stats: dict) -> dict:
    """Handler for clearing stories of legend"""

    stage_data = save_stats["event_stages"]

    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter subchapter ids (e.g &1& = legend begins, &2& = passion land)(You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):"
        ),
        50,
    )
    offset = -1
    save_stats["event_stages"] = stage_handler(stage_data, ids, offset)
    return save_stats


def event_stages(save_stats: dict) -> dict:
    """Handler for clearing event stages"""

    stage_data = save_stats["event_stages"]
    lengths = stage_data["Lengths"]

    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter subchapter ids (Look up &Event Release Order battle cats& to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths["total"] - 400,
    )
    offset = 400
    save_stats["event_stages"] = stage_handler(stage_data, ids, offset)
    return save_stats
