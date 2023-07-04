from bcsfe.core import io, game, server
from bcsfe.cli import dialog_creator, color


class BasicItems:
    @staticmethod
    def edit_catfood(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(22)
        original_amount = save_file.catfood
        save_file.catfood = dialog_creator.SingleEditor(
            name, save_file.catfood, 45000
        ).edit()
        change = save_file.catfood - original_amount
        server.managed_item.BackupMetaData(save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.CATFOOD
            )
        )

    @staticmethod
    def edit_xp(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(6)
        save_file.xp = dialog_creator.SingleEditor(name, save_file.xp, 99999999).edit()

    @staticmethod
    def edit_normal_tickets(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(20)
        save_file.normal_tickets = dialog_creator.SingleEditor(
            name, save_file.normal_tickets, 2999
        ).edit()

    @staticmethod
    def edit_rare_tickets(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(21)
        original_amount = save_file.rare_tickets
        save_file.rare_tickets = dialog_creator.SingleEditor(
            name, save_file.rare_tickets, 299
        ).edit()
        change = save_file.rare_tickets - original_amount
        server.managed_item.BackupMetaData(save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.RARE_TICKET
            )
        )

    @staticmethod
    def edit_platinum_tickets(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(29)
        original_amount = save_file.platinum_tickets
        save_file.platinum_tickets = dialog_creator.SingleEditor(
            name, save_file.platinum_tickets, 9
        ).edit()
        change = save_file.platinum_tickets - original_amount
        server.managed_item.BackupMetaData(save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.PLATINUM_TICKET
            )
        )

    @staticmethod
    def edit_legend_tickets(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(145)
        original_amount = save_file.legend_tickets
        save_file.legend_tickets = dialog_creator.SingleEditor(
            name, save_file.legend_tickets, 4
        ).edit()
        change = save_file.legend_tickets - original_amount
        server.managed_item.BackupMetaData(save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.LEGEND_TICKET
            )
        )

    @staticmethod
    def edit_platinum_shards(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(157)
        platinum_ticket_amount = save_file.platinum_tickets
        max_value = 99 - (platinum_ticket_amount * 10)
        save_file.platinum_shards = dialog_creator.SingleEditor(
            name, save_file.platinum_shards, max_value
        ).edit()

    @staticmethod
    def edit_np(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(7)
        save_file.np = dialog_creator.SingleEditor(name, save_file.np, 9999).edit()

    @staticmethod
    def edit_leadership(save_file: "io.save.SaveFile"):
        name = game.catbase.gatya_item.GatyaItemNames(save_file).get_name(105)
        save_file.leadership = dialog_creator.SingleEditor(
            name, save_file.leadership, 9999
        ).edit()

    @staticmethod
    def edit_battle_items(save_file: "io.save.SaveFile"):
        save_file.battle_items.edit(save_file)

    @staticmethod
    def edit_catamins(save_file: "io.save.SaveFile"):
        names = game.catbase.gatya_item.GatyaItemNames(save_file).names
        items = game.catbase.gatya_item.GatyaItemBuy(save_file).get_by_category(6)
        names = [names[item.id] for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catamins",
            names,
            save_file.catamins,
            9999,
            group_name_localized=True,
        ).edit()
        save_file.catamins = values

    @staticmethod
    def edit_catseyes(save_file: "io.save.SaveFile"):
        names = game.catbase.gatya_item.GatyaItemNames(save_file).names
        items = game.catbase.gatya_item.GatyaItemBuy(save_file).get_by_category(5)
        names = [names[item.id] for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catseyes",
            names,
            save_file.catseyes,
            9999,
            group_name_localized=True,
        ).edit()
        save_file.catseyes = values

    @staticmethod
    def edit_catfruit(save_file: "io.save.SaveFile"):
        names = game.catbase.matatabi.Matatabi(save_file).get_names()

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
    def set_restart_pack(save_file: "io.save.SaveFile"):
        save_file.restart_pack = 1
        names = game.catbase.gatya_item.GatyaItemNames(save_file).names
        name = names[123]
        color.ColoredText.localize("value_gave", name=name)

    @staticmethod
    def edit_inquiry_code(save_file: "io.save.SaveFile"):
        item_name = save_file.get_localizable().get("autoSave_txt5").strip()
        save_file.inquiry_code = dialog_creator.StringEditor(
            item_name, save_file.inquiry_code
        ).edit()

    @staticmethod
    def edit_password_refresh_token(save_file: "io.save.SaveFile"):
        save_file.password_refresh_token = dialog_creator.StringEditor(
            "password_refresh_token", save_file.password_refresh_token
        ).edit()

    @staticmethod
    def edit_scheme_items(save_file: "io.save.SaveFile"):
        save_file.scheme_items.edit(save_file)
