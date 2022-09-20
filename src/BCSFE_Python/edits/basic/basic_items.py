"""Handler for basic, items that work in a common way"""
from typing import Any
from ... import helper, item, managed_item


def edit_cat_food(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing cat food"""

    cat_food = item.Item(
        name="Cat Food",
        value=save_stats["cat_food"]["Value"],
        max_value=45000,
        edit_name="value",
        bannable=item.BannableItem(
            is_bannable=True,
            has_workaround=False,
            managed_item_type=managed_item.ManagedItemType.CATFOOD,
        ),
    )
    cat_food.edit()
    save_stats["cat_food"]["Value"] = cat_food.value
    return save_stats


def edit_xp(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing xp"""

    experience = item.Item(
        name="XP",
        value=save_stats["xp"]["Value"],
        max_value=99999999,
        edit_name="value",
    )
    experience.edit()
    save_stats["xp"]["Value"] = experience.value
    return save_stats


def edit_normal_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing normal tickets"""

    normal_tickets = item.Item(
        name="Normal Tickets",
        value=save_stats["normal_tickets"]["Value"],
        max_value=2999,
        edit_name="value",
    )
    normal_tickets.edit()
    save_stats["normal_tickets"]["Value"] = normal_tickets.value
    return save_stats


def edit_rare_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing rare tickets"""

    rare_tickets = item.Item(
        name="Rare Tickets",
        value=save_stats["rare_tickets"]["Value"],
        max_value=299,
        edit_name="value",
        bannable=item.BannableItem(
            is_bannable=True,
            has_workaround=True,
            work_around_text='&Instead of editing rare tickets directly, use the "Normal Ticket Max Trade Progress" conversion feature instead! It is much more safe.',
            managed_item_type=managed_item.ManagedItemType.RARE_TICKET,
        ),
    )
    rare_tickets.edit()
    save_stats["rare_tickets"]["Value"] = rare_tickets.value
    return save_stats


def edit_platinum_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing platinum tickets"""

    platinum_tickets = item.Item(
        name="Platinum Tickets",
        value=save_stats["platinum_tickets"]["Value"],
        max_value=9,
        edit_name="value",
        bannable=item.BannableItem(
            is_bannable=True,
            has_workaround=True,
            work_around_text="&Instead of editing platinum tickets, edit platinum shards instead! They are much more safe. 10 platinum shards = 1 platinum ticket",
            managed_item_type=managed_item.ManagedItemType.PLATINUM_TICKET,
        ),
    )
    platinum_tickets.edit()
    save_stats["platinum_tickets"]["Value"] = platinum_tickets.value
    return save_stats


def edit_platinum_shards(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing platinum shards"""

    ticket_amount = save_stats["platinum_tickets"]["Value"]
    max_value = 99 - (ticket_amount * 10)
    platinum_shards = item.Item(
        name="Platinum Shards",
        value=save_stats["platinum_shards"]["Value"],
        max_value=max_value,
        edit_name="value",
    )
    platinum_shards.edit()
    save_stats["platinum_shards"]["Value"] = platinum_shards.value
    return save_stats


def edit_np(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing np"""

    nyanko_points = item.Item(
        name="NP",
        value=save_stats["np"]["Value"],
        max_value=9999,
        edit_name="value",
    )
    nyanko_points.edit()
    save_stats["np"]["Value"] = nyanko_points.value
    return save_stats


def edit_leadership(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing leadership"""

    leadership = item.Item(
        name="Leadership",
        value=save_stats["leadership"]["Value"],
        max_value=9999,
        edit_name="value",
    )
    leadership.edit()
    save_stats["leadership"]["Value"] = leadership.value
    return save_stats


def edit_battle_items(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing battle items"""

    battle_items = item.create_item_group(
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
        edit_name="value",
        group_name="Battle Items",
    )
    battle_items.edit()
    save_stats["battle_items"] = battle_items.values

    return save_stats


def edit_catseyes(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing catseyes"""

    catseyes = item.create_item_group(
        names=[
            "Special",
            "Rare",
            "Super Rare",
            "Uber Super Rare",
            "Legend Rare",
        ],
        values=save_stats["catseyes"],
        maxes=9999,
        edit_name="value",
        group_name="Catseyes",
    )
    catseyes.edit()
    save_stats["catseyes"] = catseyes.values
    return save_stats


def edit_engineers(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing ototo engineers"""

    engineers = item.Item(
        name="Ototo Engineers",
        value=save_stats["engineers"]["Value"],
        max_value=5,
        edit_name="value",
    )
    engineers.edit()
    save_stats["engineers"]["Value"] = engineers.value
    return save_stats


def edit_base_materials(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing ototo base materials"""

    base_materials = item.create_item_group(
        names=[
            "Bricks",
            "Feathers",
            "Coal",
            "Sprockets",
            "Gold",
            "Meteorite",
            "Beast Bones",
            "Ammonite",
        ],
        values=save_stats["base_materials"],
        maxes=9999,
        edit_name="value",
        group_name="Base Materials",
    )
    base_materials.edit()
    save_stats["base_materials"] = base_materials.values
    return save_stats


def edit_catamins(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing catamins"""

    catamins = item.create_item_group(
        names=[
            "Catamin A",
            "Catamin B",
            "Catamin C",
        ],
        values=save_stats["catamins"],
        maxes=9999,
        edit_name="value",
        group_name="Catamins",
    )
    catamins.edit()
    save_stats["catamins"] = catamins.values
    return save_stats


def edit_inquiry_code(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the inquiry code"""

    print(
        "WARNING: Editing your inquiry code should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!"
    )
    inquiry_code = item.Item(
        name="Inquiry Code",
        value=save_stats["inquiry_code"],
        max_value=None,
        edit_name="value",
    )
    inquiry_code.edit()
    save_stats["inquiry_code"] = inquiry_code.value
    return save_stats


def edit_rare_gacha_seed(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the rare gacha seed"""

    rare_gacha_seed = item.Item(
        name="Rare Gacha Seed",
        value=save_stats["rare_gacha_seed"]["Value"],
        max_value=None,
        edit_name="value",
    )
    rare_gacha_seed.edit()
    save_stats["rare_gacha_seed"]["Value"] = rare_gacha_seed.value
    return save_stats


def edit_unlocked_slots(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the amount of unlocked slots"""

    unlocked_slots = item.Item(
        name="Unlocked Slots",
        value=save_stats["unlocked_slots"]["Value"],
        max_value=len(save_stats["slots"]),
        edit_name="value",
    )
    unlocked_slots.edit()
    save_stats["unlocked_slots"]["Value"] = unlocked_slots.value
    return save_stats


def edit_token(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the password-refresh-token"""

    print(
        "WARNING: Editing your token should only be done if you know what you are doing! Because it will lead to an elsewhere error in-game if not done correctly!"
    )
    token = item.Item(
        name="Token",
        value=save_stats["token"],
        max_value=None,
        edit_name="value",
    )
    token.edit()
    save_stats["token"] = token.value
    return save_stats


def edit_restart_pack(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for giving the restart pack"""

    save_stats["restart_pack"]["Value"] = 1
    print("Successfully gave the restart pack")
    return save_stats


def edit_challenge_battle(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the score of the challenge battle"""

    challenge_battle = item.Item(
        name="Challenge Battle",
        value=save_stats["challenge"]["Score"]["Value"],
        max_value=None,
        edit_name="score",
    )
    challenge_battle.edit()
    save_stats["challenge"]["Score"]["Value"] = challenge_battle.value
    save_stats["challenge"]["Cleared"]["Value"] = 1
    return save_stats


def edit_legend_tickets(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing legend tickets"""

    legend_tickets = item.Item(
        name="Legend Tickets",
        value=save_stats["legend_tickets"]["Value"],
        max_value=4,
        edit_name="value",
        bannable=item.BannableItem(
            is_bannable=True,
            has_workaround=False,
            managed_item_type=managed_item.ManagedItemType.LEGEND_TICKET,
        ),
    )
    legend_tickets.edit()
    save_stats["legend_tickets"]["Value"] = legend_tickets.value
    return save_stats


def edit_dojo_score(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing the dojo score"""

    if not save_stats["dojo_data"]:
        helper.colored_text(
            "No catclaw dojo data found\nPlease enter the catclaw dojo menu and try again",
            base=helper.RED,
        )
        return save_stats

    dojo_score = item.Item(
        name="Dojo Score",
        value=save_stats["dojo_data"][0][0],
        max_value=None,
        edit_name="value",
    )
    dojo_score.edit()
    save_stats["dojo_data"][0][0] = dojo_score.value
    return save_stats
