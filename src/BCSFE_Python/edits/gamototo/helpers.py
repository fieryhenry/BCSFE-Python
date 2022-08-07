"""Handler for editing gamatoto helpers"""
from typing import Any

from ... import item, game_data_getter, helper

def get_gamatoto_helpers(is_jp: bool) -> dict[str, Any]:
    """Get the rarities of all gamatoto helpers"""

    data = (
        game_data_getter.get_file_latest(
            "resLocal", "GamatotoExpedition_Members_name_en.csv", is_jp
        )
        .decode("utf-8")
        .splitlines()
    )
    helpers: dict[str, Any] = {}
    for line in data:
        line_data = line.split("|")
        if len(line_data) < 5:
            break

        helper_id = line_data[0]
        rarity = int(line_data[1])
        type_str = line_data[4]
        helpers[helper_id] = {"Rarity_id": rarity, "Rarity_name": type_str}
    return helpers


def generate_helpers(user_input: list[int], helper_data: dict[str, Any]) -> list[int]:
    """Generate unique helpers from amounts of each"""

    final_helpers: list[int] = []
    values = list(helper_data.values())
    for i, usr_input in enumerate(user_input):
        for j, value in enumerate(values):
            if value["Rarity_id"] == i:
                final_helpers += list(range(j + 1, j + 1 + usr_input))
                break
    return final_helpers


def get_helpers(helpers: list[int], helper_data: dict[str, Any]) -> dict[str, Any]:
    """Get the amount of each type of helper"""

    current_helpers: dict[int, Any] = {}
    helper_count = {
        "Intern": 0,
        "Lackey": 0,
        "Underling": 0,
        "Assistant": 0,
        "Legend": 0,
    }
    for helper_id in helpers:
        if helper_id == 0xFFFFFFFF:
            break
        current_helpers[helper_id] = helper_data[str(helper_id)]
        helper_count[current_helpers[helper_id]["Rarity_name"]] += 1
    return helper_count


def add_empty_helper_slots(helpers: list[int], final_helpers: list[int]):
    """Add empty helper slots to the end of the list"""

    empty_slots = len(final_helpers) - len(helpers)
    if empty_slots > 0:
        helpers += [0xFFFFFFFF] * empty_slots
    return helpers


def edit_helpers(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for gamatoto helpers"""

    helpers = save_stats["helpers"]
    helper_data = get_gamatoto_helpers(helper.is_jp(save_stats))

    helper_count = get_helpers(helpers, helper_data)

    helpers_counts_input = item.create_item_group(
        names=list(helper_count.keys()),
        values=list(helper_count.values()),
        edit_name="amount",
        group_name="Gamatoto Helpers",
        maxes=10,
    )
    helpers_counts_input.edit()
    final_helpers = generate_helpers(
        helpers_counts_input.values, helper_data
    )
    helpers = add_empty_helper_slots(
        helpers, final_helpers
    )
    save_stats["helpers"] = helpers
    return save_stats
