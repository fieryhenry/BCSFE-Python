from bcsfe.core import io, game, server
from bcsfe.cli import dialog_creator


class BasicItems:
    def __init__(self, save_file: io.save.SaveFile):
        self.save_file = save_file

    def edit_catfood(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(22)
        original_amount = self.save_file.catfood
        self.save_file.catfood = dialog_creator.SingleEditor(
            name, self.save_file.catfood, 45000
        ).edit()
        change = self.save_file.catfood - original_amount
        server.managed_item.BackupMetaData(self.save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.CATFOOD
            )
        )

    def edit_xp(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(6)
        self.save_file.xp = dialog_creator.SingleEditor(
            name, self.save_file.xp, 99999999
        ).edit()

    def edit_normal_tickets(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(20)
        self.save_file.normal_tickets = dialog_creator.SingleEditor(
            name, self.save_file.normal_tickets, 2999
        ).edit()

    def edit_rare_tickets(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(21)
        original_amount = self.save_file.rare_tickets
        self.save_file.rare_tickets = dialog_creator.SingleEditor(
            name, self.save_file.rare_tickets, 299
        ).edit()
        change = self.save_file.rare_tickets - original_amount
        server.managed_item.BackupMetaData(self.save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.RARE_TICKET
            )
        )

    def edit_platinum_tickets(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(29)
        original_amount = self.save_file.platinum_tickets
        self.save_file.platinum_tickets = dialog_creator.SingleEditor(
            name, self.save_file.platinum_tickets, 9
        ).edit()
        change = self.save_file.platinum_tickets - original_amount
        server.managed_item.BackupMetaData(self.save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.PLATINUM_TICKET
            )
        )

    def edit_legend_tickets(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(145)
        original_amount = self.save_file.legend_tickets
        self.save_file.legend_tickets = dialog_creator.SingleEditor(
            name, self.save_file.legend_tickets, 4
        ).edit()
        change = self.save_file.legend_tickets - original_amount
        server.managed_item.BackupMetaData(self.save_file).add_managed_item(
            server.managed_item.ManagedItem.from_change(
                change, server.managed_item.ManagedItemType.LEGEND_TICKET
            )
        )

    def edit_platinum_shards(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(157)
        platinum_ticket_amount = self.save_file.platinum_tickets
        max_value = 99 - (platinum_ticket_amount * 10)
        self.save_file.platinum_shards = dialog_creator.SingleEditor(
            name, self.save_file.platinum_shards, max_value
        ).edit()

    def edit_np(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(7)
        self.save_file.np = dialog_creator.SingleEditor(
            name, self.save_file.np, 9999
        ).edit()

    def edit_leadership(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(105)
        self.save_file.leadership = dialog_creator.SingleEditor(
            name, self.save_file.leadership, 9999
        ).edit()

    def edit_engineers(self):
        name = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).get_name(92)
        self.save_file.ototo.engineers = dialog_creator.SingleEditor(
            name, self.save_file.ototo.engineers, 5
        ).edit()

    def edit_catamins(self):
        names = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).names
        items = game.catbase.gatya_item.GatyaItemBuy(self.save_file.cc).get_by_category(
            6
        )
        names = [names[item.id] for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catamins",
            names,
            self.save_file.catamins,
            9999,
            group_name_localized=True,
        ).edit()
        self.save_file.catamins = values

    def edit_catseyes(self):
        names = game.catbase.gatya_item.GatyaItemNames(self.save_file.cc).names
        items = game.catbase.gatya_item.GatyaItemBuy(self.save_file.cc).get_by_category(
            5
        )
        names = [names[item.id] for item in items]
        values = dialog_creator.MultiEditor.from_reduced(
            "catseyes",
            names,
            self.save_file.catseyes,
            9999,
            group_name_localized=True,
        ).edit()
        self.save_file.catseyes = values

    def edit_catfruit(self):
        names = game.catbase.matatabi.Matatabi(self.save_file.cc).get_names()

        max_value = 998
        if self.save_file.game_version < 110400:
            max_value = 128

        values = dialog_creator.MultiEditor.from_reduced(
            "catfruit",
            names,
            self.save_file.catfruit,
            max_value,
            group_name_localized=True,
            cumulative_max=True,
        ).edit()
        self.save_file.catfruit = values
