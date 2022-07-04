"""Handler for editing gamatoto helpers"""

from ... import helper as helper_module
from ... import item


def get_gamatoto_helpers() -> dict:
    """Get the rarities of all gamatoto helpers"""

    data = helper_module.read_file_string(
        helper_module.get_file(
            "game_data/gamatoto/GamatotoExpedition_Members_name_en.csv"
        )
    ).splitlines()
    helpers = {}
    for line in data:
        line_data = line.split("|")
        if len(line_data) < 5:
            break

        helper_id = line_data[0]
        rarity = int(line_data[1])
        type_str = line_data[4]
        helpers[helper_id] = {"Rarity_id": rarity, "Rarity_name": type_str}
    return helpers


def generate_helpers(user_input: list, helper_data: dict) -> list:
    """Generate unique helpers from amounts of each"""

    final_helpers = []
    values = list(helper_data.values())
    for i, usr_input in enumerate(user_input):
        for j, value in enumerate(values):
            if value["Rarity_id"] == i:
                final_helpers += list(range(j + 1, j + 1 + usr_input))
                break
    return final_helpers


def edit_helpers(save_stats: dict) -> dict:
    """Handler for gamatoto helpers"""

    helpers = save_stats["helpers"]

    helper_data = get_gamatoto_helpers()
    current_helpers = {}
    helper_count = {
        "Intern": 0,
        "Lackey": 0,
        "Underling": 0,
        "Assistant": 0,
        "Legend": 0,
    }
    for helper in helpers:
        if helper == 0xFFFFFFFF:
            break
        current_helpers[helper] = helper_data[str(helper)]
        helper_count[current_helpers[helper]["Rarity_name"]] += 1

    helpers_counts_input = item.create_item_group(
        names=list(helper_count.keys()),
        values=list(helper_count.values()),
        edit_name="amount",
        group_name="Gamatoto Helpers",
        maxes=10,
    )
    helpers_counts_input.edit()
    final_helpers = generate_helpers(helpers_counts_input.values, helper_data)
    extra_ls = [0xFFFFFFFF] * (len(helpers) - len(final_helpers))
    final_helpers += extra_ls

    helpers = final_helpers
    save_stats["helpers"] = helpers
    return save_stats
