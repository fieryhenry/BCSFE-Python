from bcsfe import core
from bcsfe.cli import dialog_creator, color, edits


class BasicItems:
    @staticmethod
    def edit_catfood(save_file: "core.SaveFile"):
        should_exit = not dialog_creator.YesNoInput().get_input_once("catfood_warning")
        if should_exit:
            return

        name = core.get_gatya_item_names(save_file).get_name(22)
        original_amount = save_file.catfood
        save_file.catfood = dialog_creator.SingleEditor(
            name, save_file.catfood, 45000
        ).edit()
        change = save_file.catfood - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.CATFOOD)
        )

    @staticmethod
    def edit_xp(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(6)
        save_file.xp = dialog_creator.SingleEditor(name, save_file.xp, 99999999).edit()

    @staticmethod
    def edit_normal_tickets(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(20)
        save_file.normal_tickets = dialog_creator.SingleEditor(
            name, save_file.normal_tickets, 2999
        ).edit()

    @staticmethod
    def get_bannable_feature_options(feature_name: str, safe_feature_name: str) -> int:
        feature_name = core.local_manager.get_key(feature_name)
        safe_feature_name = core.local_manager.get_key(safe_feature_name)

        options = [
            color.ColoredText.get_localized_text(
                "continue_editing", feature_name=feature_name
            ),
            color.ColoredText.get_localized_text(
                "go_to_safe_feature", safer_feature_name=safe_feature_name
            ),
            color.ColoredText.get_localized_text(
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
    def edit_rare_tickets(save_file: "core.SaveFile"):
        color.ColoredText.localize("rare_ticket_warning")
        name = core.get_gatya_item_names(save_file).get_name(21)
        option = BasicItems.get_bannable_feature_options(
            "rare_tickets_l", "rare_ticket_trade_l"
        )
        if option == 2:
            return
        if option == 1:
            return edits.rare_ticket_trade.RareTicketTrade.rare_ticket_trade(save_file)

        original_amount = save_file.rare_tickets
        save_file.rare_tickets = dialog_creator.SingleEditor(
            name, save_file.rare_tickets, 299
        ).edit()
        change = save_file.rare_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.RARE_TICKET)
        )

    @staticmethod
    def edit_platinum_tickets(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(29)
        original_amount = save_file.platinum_tickets
        save_file.platinum_tickets = dialog_creator.SingleEditor(
            name, save_file.platinum_tickets, 9
        ).edit()
        change = save_file.platinum_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.PLATINUM_TICKET)
        )

    @staticmethod
    def edit_legend_tickets(save_file: "core.SaveFile"):
        should_exit = not dialog_creator.YesNoInput().get_input_once(
            "legend_ticket_warning"
        )
        if should_exit:
            return
        name = core.get_gatya_item_names(save_file).get_name(145)
        original_amount = save_file.legend_tickets
        save_file.legend_tickets = dialog_creator.SingleEditor(
            name, save_file.legend_tickets, 4
        ).edit()
        change = save_file.legend_tickets - original_amount
        core.BackupMetaData(save_file).add_managed_item(
            core.ManagedItem.from_change(change, core.ManagedItemType.LEGEND_TICKET)
        )

    @staticmethod
    def edit_platinum_shards(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(157)
        platinum_ticket_amount = save_file.platinum_tickets
        max_value = 99 - (platinum_ticket_amount * 10)
        save_file.platinum_shards = dialog_creator.SingleEditor(
            name, save_file.platinum_shards, max_value
        ).edit()

    @staticmethod
    def edit_np(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(7)
        save_file.np = dialog_creator.SingleEditor(name, save_file.np, 9999).edit()

    @staticmethod
    def edit_leadership(save_file: "core.SaveFile"):
        name = core.get_gatya_item_names(save_file).get_name(105)
        save_file.leadership = dialog_creator.SingleEditor(
            name, save_file.leadership, 9999
        ).edit()

    @staticmethod
    def edit_battle_items(save_file: "core.SaveFile"):
        save_file.battle_items.edit(save_file)

    @staticmethod
    def edit_catamins(save_file: "core.SaveFile"):
        names_o = core.get_gatya_item_names(save_file)
        items = core.get_gatya_item_buy(save_file).get_by_category(6)
        names = [names_o.get_name(item.id) for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catamins",
            names,
            save_file.catamins,
            9999,
            group_name_localized=True,
        ).edit()
        save_file.catamins = values

    @staticmethod
    def edit_catseyes(save_file: "core.SaveFile"):
        names_o = core.get_gatya_item_names(save_file)
        items = core.get_gatya_item_buy(save_file).get_by_category(5)
        names = [names_o.get_name(item.id) for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catseyes",
            names,
            save_file.catseyes,
            9999,
            group_name_localized=True,
        ).edit()
        save_file.catseyes = values

    @staticmethod
    def edit_catfruit(save_file: "core.SaveFile"):
        names = core.Matatabi(save_file).get_names()

        max_value = 998
        if save_file.game_version < 110400:
            max_value = 128

        values = dialog_creator.MultiEditor.from_reduced(
            "catfruit",
            names,
            save_file.catfruit,
            max_value,
            group_name_localized=True,
            cumulative_max=True,
        ).edit()
        save_file.catfruit = values

    @staticmethod
    def set_restart_pack(save_file: "core.SaveFile"):
        save_file.restart_pack = 1
        name = core.get_gatya_item_names(save_file).get_name(123)
        color.ColoredText.localize("value_gave", name=name)

    @staticmethod
    def edit_inquiry_code(save_file: "core.SaveFile"):
        item_name = save_file.get_localizable().get("autoSave_txt5").strip()
        save_file.inquiry_code = dialog_creator.StringEditor(
            item_name, save_file.inquiry_code
        ).edit()

    @staticmethod
    def edit_password_refresh_token(save_file: "core.SaveFile"):
        save_file.password_refresh_token = dialog_creator.StringEditor(
            "password_refresh_token", save_file.password_refresh_token
        ).edit()

    @staticmethod
    def edit_scheme_items(save_file: "core.SaveFile"):
        save_file.scheme_items.edit(save_file)

    @staticmethod
    def edit_engineers(save_file: "core.SaveFile"):
        save_file.ototo.edit_engineers(save_file)

    @staticmethod
    def edit_base_materials(save_file: "core.SaveFile"):
        save_file.ototo.base_materials.edit_base_materials(save_file)
