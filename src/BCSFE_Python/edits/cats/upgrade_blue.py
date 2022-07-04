"""Handler for upgrading the blue upgrades"""

from ... import helper, user_input_handler
from ..cats import upgrade_cats

types = [
    "Power",
    "Range",
    "Charge",
    "Efficiency",
    "Wallet",
    "Health",
    "Research",
    "Accounting",
    "Study",
    "Energy",
]


def upgrade_blue_ids(save_stats: dict, ids: list) -> dict:
    """Upgrade blue upgrades for a set of ids"""

    save_stats["blue_upgrades"] = upgrade_cats.upgrade_handler(
        data=save_stats["blue_upgrades"],
        ids=ids,
        item_name="upgrade",
        save_stats=save_stats,
    )
    save_stats = upgrade_cats.set_user_popups(save_stats)
    print("Successfully set special skills")
    return save_stats


def upgrade_blue(save_stats: dict) -> dict:
    """Handler for editing blue upgrades"""

    levels = save_stats["blue_upgrades"]
    levels_removed = {
        "Base": [levels["Base"][0]] + levels["Base"][2:],
        "Plus": [levels["Plus"][0]] + levels["Plus"][2:],
    }

    levels_removed_formated = []
    for base, plus in zip(levels_removed["Base"], levels_removed["Plus"]):
        levels_removed_formated.append(
            f"{base + 1}+{plus}"
        )

    print("What do you want to upgrade:")
    helper.colored_list(types, extra_data=levels_removed_formated)

    total = len(types) + 1
    ids = user_input_handler.colored_input(
        f"{total}. &All at once&\nEnter a number from 1 to {total} (You can enter multiple values separated by spaces to edit multiple at once):"
    ).split(" ")
    ids = user_input_handler.create_all_list(ids, 11)
    ids = helper.parse_int_list(ids, -1)
    new_ids = []
    for blue_id in ids:
        if blue_id > 0:
            blue_id += 1
        new_ids.append(blue_id)
    ids = new_ids
    save_stats = upgrade_blue_ids(save_stats, ids)
    return save_stats
