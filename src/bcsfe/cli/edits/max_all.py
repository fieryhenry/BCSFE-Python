from __future__ import annotations

from collections.abc import Callable
from bcsfe import core


def max_catfood(save_file: core.SaveFile):
    orig = save_file.catfood
    save_file.catfood = core.core_data.max_value_manager.catfood
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.catfood - orig, core.ManagedItemType.CATFOOD
        )
    )


def max_rare_tickets(save_file: core.SaveFile):
    orig = save_file.rare_tickets
    save_file.rare_tickets = core.core_data.max_value_manager.rare_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.rare_tickets - orig, core.ManagedItemType.RARE_TICKET
        )
    )


def max_plat_tickets(save_file: core.SaveFile):
    orig = save_file.platinum_tickets
    save_file.platinum_tickets = core.core_data.max_value_manager.platinum_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.platinum_tickets - orig, core.ManagedItemType.PLATINUM_TICKET
        )
    )


def max_plat_shards(save_file: core.SaveFile):
    save_file.platinum_shards = 10 * core.core_data.max_value_manager.platinum_tickets


def max_legend_tickets(save_file: core.SaveFile):
    orig = save_file.legend_tickets
    save_file.legend_tickets = core.core_data.max_value_manager.legend_tickets
    core.BackupMetaData(save_file).add_managed_item(
        core.ManagedItem.from_change(
            save_file.legend_tickets - orig, core.ManagedItemType.LEGEND_TICKET
        )
    )


def max_xp(save_file: core.SaveFile):
    save_file.xp = core.core_data.max_value_manager.xp


def max_np(save_file: core.SaveFile):
    save_file.np = core.core_data.max_value_manager.np


def max_100_million_ticket(save_file: core.SaveFile):
    save_file.hundred_million_ticket = (
        core.core_data.max_value_manager.hundred_million_tickets
    )


def max_leadership(save_file: core.SaveFile):
    save_file.leadership = core.core_data.max_value_manager.leadership


def max_battle_items(save_file: core.SaveFile):
    for item in save_file.battle_items.items:
        item.amount = core.core_data.max_value_manager.battle_items


def max_catseyes(save_file: core.SaveFile):
    for id in range(len(save_file.catseyes)):
        save_file.catseyes[id] = core.core_data.max_value_manager.catseyes


def max_treasure_chests(save_file: core.SaveFile):
    for id in range(len(save_file.treasure_chests)):
        save_file.treasure_chests[id] = core.core_data.max_value_manager.treasure_chests


def max_catamins(save_file: core.SaveFile):
    for id in range(len(save_file.catseyes)):
        save_file.catamins[id] = core.core_data.max_value_manager.catamins


def max_labyrinth_medals(save_file: core.SaveFile):
    for id in range(len(save_file.labyrinth_medals)):
        save_file.labyrinth_medals[id] = (
            core.core_data.max_value_manager.labyrinth_medals
        )


# def max_catfruit(save_file: core.SaveFile):
#     for id in range(len(save_file.catfruit)):
#         save_file.catfruit[id] = core.core_data.max_value_manager.get_new(
#             core.MaxValueType.CATFRUIT
#         )


def max_normal_tickets(save_file: core.SaveFile):
    save_file.normal_tickets = core.core_data.max_value_manager.normal_tickets


def max_all(save_file: core.SaveFile):
    maxes = core.core_data.max_value_manager
    features: dict[str, Callable[[core.SaveFile], None]] = {
        "catfood": max_catfood,
        "xp": max_xp,
        "normal_tickets": max_normal_tickets,
        "rare_tickets": max_rare_tickets,
        "platinum_tickets": max_plat_tickets,
        "legend_tickets": max_legend_tickets,
        "platinum_shards": max_plat_shards,
        "np": max_np,
        "leadership": max_leadership,
        "battle_items": max_battle_items,
        "catseyes": max_catseyes,
        "catamins": max_catamins,
        "labyrinth_medals": max_labyrinth_medals,
        "100_million_ticket": max_100_million_ticket,
        "treasure_chests": max_treasure_chests,
    }
    # TODO: finish
