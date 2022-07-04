"""Handler for cat upgrades"""

from ... import helper, user_input_handler, csv_file_handler


def upgrade_cats(save_stats: dict) -> dict:
    """Upgrade specific cats"""

    cats = save_stats["cat_upgrades"]
    base = cats["Base"]
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        len(base),
    )
    return upgrade_cats_ids(save_stats, ids)


def upgrade_current_cats(save_stats: dict) -> dict:
    """Upgrade current cats"""

    cats = save_stats["cats"]
    cat_ids = []
    for i, cat_val in enumerate(cats):
        if cat_val == 1:
            cat_ids.append(i)
    save_stats = upgrade_cats_ids(save_stats, cat_ids)

    return save_stats


def get_rarities() -> list:
    """Get all cat ids of each rarity"""

    path = helper.get_file("game_data/rarity/unitbuy.csv")
    data = csv_file_handler.parse_csv(path)
    rarity_ids = helper.copy_first_n(data, 13)
    return rarity_ids


def get_rarity(rarity_ids: list) -> list:
    """Get all cat ids of a certain rarity"""

    rarities = get_rarities()
    cat_ids = []
    for rarity_id in rarity_ids:
        rarity_id = helper.check_int(rarity_id)
        if rarity_id is None:
            print("Please input a valid number")
            continue
        rarity_id -= 1
        for i, rarity_val in enumerate(rarities):
            if int(rarity_val) == rarity_id:
                cat_ids.append(i)
    return cat_ids


types = [
    "Normal",
    "Special",
    "Rare",
    "Super Rare",
    "Uber Super Rare",
    "Legend Rare",
]


def upgrade_cat_rarity(save_stats: dict) -> dict:
    """Upgrade all cats of a certain rarity"""

    ids = user_input_handler.select_options(
        options=types,
        mode="upgrade",
    )

    cat_ids = get_rarity(ids)
    save_stats = upgrade_cats_ids(save_stats, cat_ids)

    return save_stats


def upgrade_handler(data: dict, ids: list, item_name: str, save_stats: dict) -> dict:
    """Handler for cat upgrades"""

    ids = helper.check_cat_ids(ids, save_stats)

    base = data["Base"]
    plus = data["Plus"]
    individual = "1"
    if len(ids) > 1:
        individual = user_input_handler.colored_input(
            f"Do you want to upgrade each {item_name} individually(&1&), or all at once(&2&):"
        )
    first = True
    base_lvl = None
    plus_lvl = None
    for cat_id in ids:
        if individual == "2" and first:
            levels = get_plus_base(
                user_input_handler.colored_input(
                    'Enter the base level followed by a "&+&" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n'
                )
            )
            base_lvl = levels[0]
            plus_lvl = levels[1]
            first = False
        elif individual == "1":
            helper.colored_text(f"The current upgrade level of id &{cat_id}& is &{base[cat_id]+1}&+&{plus[cat_id]}&")
            levels = get_plus_base(
                user_input_handler.colored_input(
                    f'Enter the base level for {item_name}: &{cat_id}& followed by a "&+&" then the plus level, e.g 5&+&12. If you want to ignore the base level do &+&12, if you want to ignore the plus level do 5&+&:\n'
                )
            )
            base_lvl = levels[0]
            plus_lvl = levels[1]
        else:
            return data
        if base_lvl is not None:
            base[cat_id] = base_lvl - 1
        if plus_lvl is not None:
            plus[cat_id] = plus_lvl

    data["Base"] = base
    data["Plus"] = plus

    return data


def set_user_popups(save_stats: dict) -> dict:
    """Set user popups, stops the user rank popups from spamming up the screen"""

    save_stats["user_rank_popups"]["Value"] = 0xFFFFFF
    return save_stats


def upgrade_cats_ids(save_stats: dict, ids: list) -> dict:
    """Upgrade cats by ids"""

    save_stats["cat_upgrades"] = upgrade_handler(
        data=save_stats["cat_upgrades"],
        ids=ids,
        item_name="cat",
        save_stats=save_stats,
    )
    save_stats = set_user_popups(save_stats)
    print("Successfully set cat levels")
    return save_stats


def get_plus_base(usr_input: str) -> tuple:
    """Get the base and plus level of an input"""

    split = usr_input.split("+")
    base = None
    plus = None
    if split[0]:
        base = helper.check_int(split[0])
    if split[1]:
        plus = helper.check_int(split[1])
    return base, plus
