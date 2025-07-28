from __future__ import annotations
import random
from bcsfe import core
from bcsfe.cli import dialog_creator, color, edits
from bcsfe.core.game.catbase.gatya_item import GatyaItemCategory


class BasicItems:
    @staticmethod
    def get_name(name: str | None, key: str) -> str:
        if name is None:
            return core.core_data.local_manager.get_key(key)
        return name.strip()

    @staticmethod
    def edit_catfood(save_file: core.SaveFile):
        should_exit = not dialog_creator.YesNoInput().get_input_once("catfood_warning")
        if should_exit:
            return

        name = core.core_data.get_gatya_item_names(save_file).get_name(22)
        original_amount = save_file.catfood
        save_file.catfood = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "catfood"),
            save_file.catfood,
            core.core_data.max_value_manager.get("catfood"),
        ).edit()
        change = save_file.catfood - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.CATFOOD)
        )

    @staticmethod
    def edit_xp(save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(6)
        save_file.xp = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "xp"),
            save_file.xp,
            core.core_data.max_value_manager.get("xp"),
        ).edit()

    @staticmethod
    def edit_normal_tickets(save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(20)
        save_file.normal_tickets = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "normal_tickets"),
            save_file.normal_tickets,
            core.core_data.max_value_manager.get("normal_tickets"),
        ).edit()

    @staticmethod
    def edit_100_million_ticket(save_file: core.SaveFile):
        color.ColoredText.localize("100_million_warn")
        name = core.core_data.get_gatya_item_names(save_file).get_name(212)
        save_file.hundred_million_ticket = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "100_million_tickets"),
            save_file.hundred_million_ticket,
            core.core_data.max_value_manager.get("100_million_tickets"),
        ).edit()

    @staticmethod
    def get_bannable_feature_options(feature_name: str, safe_feature_name: str) -> int:
        feature_name = core.core_data.local_manager.get_key(feature_name)
        safe_feature_name = core.core_data.local_manager.get_key(safe_feature_name)

        options = [
            core.core_data.local_manager.get_key(
                "continue_editing", feature_name=feature_name
            ),
            core.core_data.local_manager.get_key(
                "go_to_safe_feature", safer_feature_name=safe_feature_name
            ),
            core.core_data.local_manager.get_key(
                "cancel_editing", feature_name=feature_name
            ),
        ]
        option = dialog_creator.ChoiceInput(
            options,
            options,
            [],
            {"feature_name": feature_name},
            "select_an_option_to_continue",
        ).single_choice()
        if option is None:
            return 2
        option -= 1
        return option

    @staticmethod
    def edit_rare_tickets(save_file: core.SaveFile):
        color.ColoredText.localize("rare_ticket_warning")
        name = core.core_data.get_gatya_item_names(save_file).get_name(21)
        option = BasicItems.get_bannable_feature_options(
            "rare_tickets_l", "rare_ticket_trade_l"
        )
        if option == 2:
            return
        if option == 1:
            return edits.rare_ticket_trade.RareTicketTrade.rare_ticket_trade(save_file)

        original_amount = save_file.rare_tickets
        save_file.rare_tickets = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "rare_tickets"),
            save_file.rare_tickets,
            core.core_data.max_value_manager.get("rare_tickets"),
        ).edit()
        change = save_file.rare_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.RARE_TICKET)
        )

    @staticmethod
    def edit_platinum_tickets(save_file: core.SaveFile):
        color.ColoredText.localize("platinum_ticket_warning")
        name = core.core_data.get_gatya_item_names(save_file).get_name(29)
        option = BasicItems.get_bannable_feature_options(
            "platinum_tickets_l", "platinum_shards_l"
        )
        if option == 2:
            return
        if option == 1:
            return edits.basic_items.BasicItems.edit_platinum_shards(save_file)

        original_amount = save_file.platinum_tickets
        save_file.platinum_tickets = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "platinum_tickets"),
            save_file.platinum_tickets,
            core.core_data.max_value_manager.get("platinum_tickets"),
        ).edit()
        change = save_file.platinum_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.PLATINUM_TICKET)
        )

    @staticmethod
    def edit_legend_tickets(save_file: core.SaveFile):
        should_exit = not dialog_creator.YesNoInput().get_input_once(
            "legend_ticket_warning"
        )
        if should_exit:
            return
        name = core.core_data.get_gatya_item_names(save_file).get_name(145)
        original_amount = save_file.legend_tickets
        save_file.legend_tickets = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "legend_tickets"),
            save_file.legend_tickets,
            core.core_data.max_value_manager.get("legend_tickets"),
        ).edit()
        change = save_file.legend_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.LEGEND_TICKET)
        )

    @staticmethod
    def edit_platinum_shards(save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(157)
        platinum_ticket_amount = save_file.platinum_tickets
        max_value = (
            core.core_data.max_value_manager.get("platinum_tickets")
            - platinum_ticket_amount
        ) * 10 + 9
        save_file.platinum_shards = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "platinum_shards"),
            save_file.platinum_shards,
            max_value,
        ).edit()

    @staticmethod
    def edit_np(save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(7)
        save_file.np = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "np"),
            save_file.np,
            core.core_data.max_value_manager.get("np"),
        ).edit()

    @staticmethod
    def edit_leadership(save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(105)
        save_file.leadership = dialog_creator.SingleEditor(
            BasicItems.get_name(name, "leadership"),
            save_file.leadership,
            core.core_data.max_value_manager.get("leadership"),
        ).edit()

    @staticmethod
    def edit_battle_items(save_file: core.SaveFile):
        save_file.battle_items.edit(save_file)

    @staticmethod
    def edit_catamins(save_file: core.SaveFile):
        names_o = core.core_data.get_gatya_item_names(save_file)
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(6)
        if items is None:
            return
        names: list[str] = []
        for item in items:
            name = names_o.get_name(item.id)
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_catamin_name", id=item.id
                )
            names.append(name)
        values = dialog_creator.MultiEditor.from_reduced(
            "catamins",
            names,
            save_file.catamins,
            core.core_data.max_value_manager.get("catamins"),
            group_name_localized=True,
        ).edit()
        save_file.catamins = values

    @staticmethod
    def edit_catseyes(save_file: core.SaveFile):
        names_o = core.core_data.get_gatya_item_names(save_file)
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(5)
        if items is None:
            return
        names: list[str] = []
        for item in items:
            name = names_o.get_name(item.id)
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_catseye_name", id=item.id
                )
            names.append(name)

        values = dialog_creator.MultiEditor.from_reduced(
            "catseyes",
            names,
            save_file.catseyes,
            core.core_data.max_value_manager.get("catseyes"),
            group_name_localized=True,
        ).edit()
        save_file.catseyes = values

    @staticmethod
    def edit_treasure_chests(save_file: core.SaveFile):
        names_o = core.core_data.get_gatya_item_names(save_file)
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(
            GatyaItemCategory.TREASURE_CHESTS
        )
        if items is None:
            return
        names: list[str] = []
        for item in items:
            name = names_o.get_name(item.id)
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_treasure_chest_name", id=item.id
                )
            names.append(name)

        values = dialog_creator.MultiEditor.from_reduced(
            "treasure_chests",
            names,
            save_file.treasure_chests,
            core.core_data.max_value_manager.get("treasure_chests"),
            group_name_localized=True,
        ).edit()
        save_file.treasure_chests = values

    @staticmethod
    def edit_catfruit(save_file: core.SaveFile):
        names = core.Matatabi(save_file).get_names()
        if names is None:
            return
        new_names: list[str] = []
        for i, name in enumerate(names):
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_catfruit_name", id=i
                )
            new_names.append(name)
        names = new_names

        extra = len(save_file.catfruit) - len(names)
        if extra > 0:
            for i in range(extra):
                names.append(
                    core.core_data.local_manager.get_key(
                        "unknown_catfruit_name", id=i + len(names)
                    )
                )

        if save_file.game_version < 110400:
            max_value = core.core_data.max_value_manager.get_old("catfruit")
            cumulative_max = True
        else:
            max_value = core.core_data.max_value_manager.get_new("catfruit")
            cumulative_max = False

        names = names[: len(save_file.catfruit)]

        values = dialog_creator.MultiEditor.from_reduced(
            "catfruit",
            names,
            save_file.catfruit,
            max_value,
            group_name_localized=True,
            cumulative_max=cumulative_max,
        ).edit()
        save_file.catfruit = values

    @staticmethod
    def set_restart_pack(save_file: core.SaveFile):
        save_file.restart_pack = 1
        name = core.core_data.get_gatya_item_names(save_file).get_name(123)
        color.ColoredText.localize("value_gave", name=name)

    @staticmethod
    def edit_inquiry_code(save_file: core.SaveFile):
        should_exit = not dialog_creator.YesNoInput().get_input_once(
            "inquiry_code_warning"
        )
        if should_exit:
            return
        item_name = save_file.get_localizable().get("autoSave_txt5")
        save_file.inquiry_code = dialog_creator.StringEditor(
            BasicItems.get_name(item_name, "inquiry_code"),
            save_file.inquiry_code,
        ).edit()

    @staticmethod
    def edit_password_refresh_token(save_file: core.SaveFile):
        should_exit = not dialog_creator.YesNoInput().get_input_once(
            "password_refresh_token_warning"
        )
        if should_exit:
            return
        save_file.password_refresh_token = dialog_creator.StringEditor(
            "password_refresh_token",
            save_file.password_refresh_token,
            item_localized=True,
        ).edit()

    @staticmethod
    def edit_scheme_items(save_file: core.SaveFile):
        save_file.scheme_items.edit(save_file)

    @staticmethod
    def edit_engineers(save_file: core.SaveFile):
        save_file.ototo.edit_engineers(save_file)

    @staticmethod
    def edit_base_materials(save_file: core.SaveFile):
        save_file.ototo.base_materials.edit_base_materials(save_file)

    @staticmethod
    def edit_rare_gatya_seed(save_file: core.SaveFile):
        save_file.gatya.edit_rare_gatya_seed()

    @staticmethod
    def edit_normal_gatya_seed(save_file: core.SaveFile):
        save_file.gatya.edit_normal_gatya_seed()

    @staticmethod
    def edit_event_gatya_seed(save_file: core.SaveFile):
        save_file.gatya.edit_event_gatya_seed()

    @staticmethod
    def edit_unlocked_slots(save_file: core.SaveFile):
        save_file.lineups.edit_unlocked_slots()

    @staticmethod
    def edit_labyrinth_medals(save_file: core.SaveFile):
        names_o = core.core_data.get_gatya_item_names(save_file)
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(11)
        if items is None:
            return
        names: list[str] = []
        for item in items:
            name = names_o.get_name(item.id)
            if name is None:
                name = core.core_data.local_manager.get_key(
                    "unknown_labyrinth_medal_name", id=item.id
                )
            names.append(name)

        values = dialog_creator.MultiEditor.from_reduced(
            "labyrinth_medals",
            names,
            save_file.labyrinth_medals,
            core.core_data.max_value_manager.get("labyrinth_medals"),
            group_name_localized=True,
        ).edit()
        save_file.labyrinth_medals = values

    @staticmethod
    def edit_special_skills(save_file: core.SaveFile):
        save_file.special_skills.edit(save_file)

    @staticmethod
    def unlock_equip_menu(save_file: core.SaveFile):
        save_file.unlock_equip_menu()
        color.ColoredText.localize("equip_menu_unlocked")

    @staticmethod
    def allow_filibuster_stage_reclearing(save_file: core.SaveFile):
        save_file.filibuster_stage_enabled = True
        save_file.filibuster_stage_id = random.randint(0, 47)
        color.ColoredText.localize("filibuster_stage_reclearing_allowed")
