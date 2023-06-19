"""Handler for basic, items that work in a common way"""
from typing import Any
from ... import item, managed_item


def edit_cat_food(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing cat food"""

    cat_food = item.IntItem(
        name="Cat Food",
        value=item.Int(save_stats["cat_food"]["Value"]),
        max_value=45000,
        bannable=item.Bannable(
            managed_item.ManagedItemType.CATFOOD, save_stats["inquiry_code"]
        ),
    )
    cat_food.edit()
    save_stats["cat_food"]["Value"] = cat_food.get_value()
    return save_stats


def edit_xp(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing xp"""

    experience = item.IntItem(
        name="XP",
        value=item.Int(save_stats["xp"]["Value"]),
        max_value=99999999,
    )
    experience.edit()
    save_stats["xp"]["Value"] = experience.get_value()
    return save_stats


def edit_normal_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing normal tickets"""

    normal_tickets = item.IntItem(
        name="Normal Tickets",
        value=item.Int(save_stats["normal_tickets"]["Value"]),
        max_value=2999,
    )
    normal_tickets.edit()
    save_stats["normal_tickets"]["Value"] = normal_tickets.get_value()
    return save_stats


def edit_rare_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing rare tickets"""

    rare_tickets = item.IntItem(
        name="Rare Tickets",
        value=item.Int(save_stats["rare_tickets"]["Value"]),
        max_value=299,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            work_around='&Instead of editing rare tickets directly, use the "Normal Ticket Max Trade Progress" conversion feature instead! It is much more safe.',
            type=managed_item.ManagedItemType.RARE_TICKET,
        ),
    )
    rare_tickets.edit()
    save_stats["rare_tickets"]["Value"] = rare_tickets.get_value()
    return save_stats


def edit_platinum_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing platinum tickets"""

    platinum_tickets = item.IntItem(
        name="Platinum Tickets",
        value=item.Int(save_stats["platinum_tickets"]["Value"]),
        max_value=9,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            work_around="&Instead of editing platinum tickets, edit platinum shards instead! They are much more safe. 10 platinum shards = 1 platinum ticket",
            type=managed_item.ManagedItemType.PLATINUM_TICKET,
        ),
    )
    platinum_tickets.edit()
    save_stats["platinum_tickets"]["Value"] = platinum_tickets.get_value()
    return save_stats


def edit_platinum_shards(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing platinum shards"""

    ticket_amount = save_stats["platinum_tickets"]["Value"]
    max_value = 99 - (ticket_amount * 10)
    platinum_shards = item.IntItem(
        name="Platinum Shards",
        value=item.Int(save_stats["platinum_shards"]["Value"]),
        max_value=max_value,
    )
    platinum_shards.edit()
    save_stats["platinum_shards"]["Value"] = platinum_shards.get_value()
    return save_stats


def edit_np(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing np"""

    nyanko_points = item.IntItem(
        name="NP",
        value=item.Int(save_stats["np"]["Value"]),
        max_value=9999,
    )
    nyanko_points.edit()
    save_stats["np"]["Value"] = nyanko_points.get_value()
    return save_stats


def edit_leadership(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing leadership"""

    leadership = item.IntItem(
        name="Leadership",
        value=item.Int(save_stats["leadership"]["Value"]),
        max_value=9999,
    )
    leadership.edit()
    save_stats["leadership"]["Value"] = leadership.get_value()
    return save_stats


def edit_battle_items(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing battle items"""

    battle_items = item.IntItemGroup.from_lists(
        names=[
            "Speed Up",
            "Treasure Radar",
            "Rich Cat",
            "Cat CPU",
            "Cat Jobs",
            "Sniper the Cat",
        ],
        values=save_stats["battle_items"],
        maxes=9999,
        group_name="Battle Items",
    )
    battle_items.edit()
    save_stats["battle_items"] = battle_items.get_values()

    return save_stats


def edit_engineers(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing ototo engineers"""

    engineers = item.IntItem(
        name="Ototo Engineers",
        value=item.Int(save_stats["engineers"]["Value"]),
        max_value=5,
    )
    engineers.edit()
    save_stats["engineers"]["Value"] = engineers.get_value()
    return save_stats


def edit_catamins(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing catamins"""

    catamins = item.IntItemGroup.from_lists(
        names=[
            "Catamin A",
            "Catamin B",
            "Catamin C",
        ],
        values=save_stats["catamins"],
        maxes=9999,
        group_name="Catamins",
    )
    catamins.edit()
    save_stats["catamins"] = catamins.get_values()
    return save_stats


def edit_inquiry_code(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the inquiry code"""

    print(
        "WARNING: Editing your inquiry code should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!"
    )
    inquiry_code = item.StrItem(
        name="Inquiry Code",
        value=save_stats["inquiry_code"],
    )
    inquiry_code.edit()
    save_stats["inquiry_code"] = inquiry_code.get_value()
    return save_stats


def edit_rare_gacha_seed(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the rare gacha seed"""

    rare_gacha_seed = item.IntItem(
        name="Rare Gacha Seed",
        value=item.Int(save_stats["rare_gacha_seed"]["Value"], signed=False),
        max_value=None,
    )
    rare_gacha_seed.edit()
    save_stats["rare_gacha_seed"]["Value"] = rare_gacha_seed.get_value()
    return save_stats


def edit_unlocked_slots(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the amount of unlocked slots"""

    unlocked_slots = item.IntItem(
        name="Unlocked Slots",
        value=item.Int(save_stats["unlocked_slots"]["Value"]),
        max_value=len(save_stats["slot_names"]),
    )
    unlocked_slots.edit()
    save_stats["unlocked_slots"]["Value"] = unlocked_slots.get_value()
    return save_stats


def edit_token(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the password-refresh-token"""

    print(
        "WARNING: Editing your token should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!"
    )
    token = item.StrItem(
        name="Token",
        value=save_stats["token"],
    )
    token.edit()
    save_stats["token"] = token.get_value()
    return save_stats


def edit_restart_pack(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for giving the restart pack"""

    save_stats["restart_pack"]["Value"] = 1
    print("Successfully gave the restart pack")
    return save_stats


def edit_challenge_battle(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the score of the challenge battle"""

    challenge_battle = item.IntItem(
        name="Challenge Battle",
        value=item.Int(save_stats["challenge"]["Score"]["Value"]),
        max_value=None,
    )
    challenge_battle.edit()
    save_stats["challenge"]["Score"]["Value"] = challenge_battle.get_value()
    save_stats["challenge"]["Cleared"]["Value"] = 1
    return save_stats


def edit_legend_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing legend tickets"""

    legend_tickets = item.IntItem(
        name="Legend Tickets",
        value=item.Int(save_stats["legend_tickets"]["Value"]),
        max_value=4,
        bannable=item.Bannable(
            inquiry_code=save_stats["inquiry_code"],
            type=managed_item.ManagedItemType.LEGEND_TICKET,
        ),
    )
    legend_tickets.edit()
    save_stats["legend_tickets"]["Value"] = legend_tickets.get_value()
    return save_stats


def edit_dojo_score(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the dojo score"""

    if not save_stats["dojo_data"]:
        save_stats["dojo_data"] = {0: {0: 0}}

    dojo_score = item.IntItem(
        name="Dojo Score",
        value=item.Int(save_stats["dojo_data"][0][0]),
        max_value=None,
    )
    dojo_score.edit()
    save_stats["dojo_data"][0][0] = dojo_score.get_value()
    return save_stats
