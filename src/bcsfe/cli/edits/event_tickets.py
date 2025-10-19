from __future__ import annotations
from bcsfe import cli, core
from bcsfe.core.game.catbase.gatya import GatyaEventType
from bcsfe.core.server.event_data import split_hhmm, split_yyyymmdd


class EventTickets:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.gatya_item_buy = core.core_data.get_gatya_item_buy(self.save_file)
        self.gatya_item_names = core.core_data.get_gatya_item_names(self.save_file)
        self.gatya_option_n = core.GatyaDataOption.read(
            self.save_file, GatyaEventType.NORMAL
        )
        self.gatya_option_r = core.GatyaDataOption.read(
            self.save_file, GatyaEventType.RARE
        )
        self.gatya_option_e = core.GatyaDataOption.read(
            self.save_file, GatyaEventType.EVENT
        )

        cli.color.ColoredText.localize("downloading_gatya_data")
        temp_save_file = core.SaveFile(cc=save_file.cc, gv=save_file.game_version)
        gatya_event_data = core.ServerHandler(temp_save_file).download_gatya_data()

        if gatya_event_data is None:
            cli.color.ColoredText.localize("download_gatya_data_fail")
            self.gatya_event_data = None
        else:
            cli.color.ColoredText.localize("download_gatya_data_success")
            self.gatya_event_data = core.ServerGatyaData.from_data(gatya_event_data)

    @staticmethod
    def edit(save_file: core.SaveFile):
        event_tickets = EventTickets(save_file)

        if event_tickets.gatya_event_data is None:
            return

        event_ticket_items: list[
            tuple[
                core.ServerGatyaDataItem, core.ServerGatyaDataSet, core.GatyaItemBuyItem
            ]
        ] = []

        if (
            event_tickets.gatya_option_n is None
            or event_tickets.gatya_option_r is None
            or event_tickets.gatya_option_e is None
        ):
            return

        for item in event_tickets.gatya_event_data.items:
            for gset in item.sets:
                if gset.number == -1:
                    continue

                gset_opt = None

                if item.get_normal_flag():
                    gset_opt = event_tickets.gatya_option_n.get(gset.number)
                elif item.get_rare_flag():
                    gset_opt = event_tickets.gatya_option_r.get(gset.number)
                elif item.get_collab_flag():
                    gset_opt = event_tickets.gatya_option_e.get(gset.number)

                if gset_opt is None:
                    continue

                gatya_item = event_tickets.gatya_item_buy.get(gset_opt.ticket_item_id)
                if gatya_item is None:
                    continue

                category = gatya_item.category
                if category in [
                    core.GatyaItemCategory.EVENT_TICKETS.value,
                    core.GatyaItemCategory.LUCKY_TICKETS_1.value,
                    core.GatyaItemCategory.LUCKY_TICKETS_2.value,
                ]:
                    event_ticket_items.append((item, gset, gatya_item))

        event_names: list[str] = []
        values: list[int] = []

        for event_item, gset, gatya_item in event_ticket_items:
            start_y, start_m, start_d = split_yyyymmdd(event_item.filter.start_yyyymmdd)
            start_h, start_min = split_hhmm(event_item.filter.start_hhmm)
            end_y, end_m, end_d = split_yyyymmdd(event_item.filter.end_yyyymmdd)
            end_h, end_min = split_hhmm(event_item.filter.end_hhmm)
            time_str = f"{start_y}-{start_m:02}-{start_d:02} {start_h:02}:{start_min:02} -> {end_y}-{end_m:02}-{end_d:02} {end_h:02}:{end_min:02}"
            event_message = gset.message.replace("<br>", "\n")

            base_msg = f"{time_str}"
            item_name = event_tickets.gatya_item_names.get_name(gatya_item.id)
            if item_name is not None:
                base_msg += f" - {item_name}"

            if event_message:
                base_msg += f" - {event_message}"

            current_amount = event_tickets.get_ticket(gatya_item.id)

            if current_amount is not None:
                event_names.append(base_msg)
                values.append(current_amount)

        values = cli.dialog_creator.MultiEditor.from_reduced(
            "event_tickets",
            event_names,
            ints=values,
            max_values=core.core_data.max_value_manager.get("event_tickets"),
            group_name_localized=True,
        ).edit()

        for (event_item, gset, gatya_item), value in zip(event_ticket_items, values):
            event_tickets.edit_ticket(gatya_item.id, value)

    def get_ticket(self, item_id: int) -> int | None:
        item = self.gatya_item_buy.get(item_id)
        if item is None:
            return

        if item.category == core.GatyaItemCategory.EVENT_TICKETS.value:
            if item.index < len(self.save_file.event_capsules):
                return self.save_file.event_capsules[item.index]
        if item.category == core.GatyaItemCategory.LUCKY_TICKETS_1.value:
            if item.index < len(self.save_file.lucky_tickets):
                return self.save_file.lucky_tickets[item.index]
        if item.category == core.GatyaItemCategory.LUCKY_TICKETS_2.value:
            if item.index < len(self.save_file.event_capsules_2):
                return self.save_file.event_capsules_2[item.index]

        return None

    def edit_ticket(self, item_id: int, amount: int):
        item = self.gatya_item_buy.get(item_id)
        if item is None:
            return

        if item.category == core.GatyaItemCategory.EVENT_TICKETS.value:
            if item.index < len(self.save_file.event_capsules):
                self.save_file.event_capsules[item.index] = amount
        if item.category == core.GatyaItemCategory.LUCKY_TICKETS_1.value:
            if item.index < len(self.save_file.lucky_tickets):
                self.save_file.lucky_tickets[item.index] = amount
        if item.category == core.GatyaItemCategory.LUCKY_TICKETS_2.value:
            if item.index < len(self.save_file.event_capsules_2):
                self.save_file.event_capsules_2[item.index] = amount
