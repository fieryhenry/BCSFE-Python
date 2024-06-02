from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator


class EquipSlot:
    def __init__(self, cat_id: int):
        self.cat_id = cat_id

    @staticmethod
    def read(stream: core.Data) -> EquipSlot:
        return EquipSlot(stream.read_int())

    def write(self, stream: core.Data):
        stream.write_int(self.cat_id)

    def serialize(self) -> int:
        return self.cat_id

    @staticmethod
    def deserialize(data: int) -> EquipSlot:
        return EquipSlot(data)

    def __repr__(self):
        return f"EquipSlot({self.cat_id})"

    def __str__(self):
        return f"EquipSlot({self.cat_id})"


class EquipSlots:
    def __init__(self, slots: list[EquipSlot]):
        self.slots = slots
        self.name = ""

    @staticmethod
    def read(stream: core.Data) -> EquipSlots:
        length = 10
        slots = [EquipSlot.read(stream) for _ in range(length)]
        return EquipSlots(slots)

    @staticmethod
    def init() -> EquipSlots:
        length = 10
        slots = [EquipSlot(-1) for _ in range(length)]
        return EquipSlots(slots)

    def write(self, stream: core.Data):
        for slot in self.slots:
            slot.write(stream)

    def read_name(self, stream: core.Data):
        length = stream.read_int()
        try:
            self.name = stream.read_string(length)
        except UnicodeDecodeError:
            stream.pos -= length
            self.name = stream.read_utf8_string_by_char_length(length)

    def write_name(self, stream: core.Data):
        stream.write_string(self.name)

    def serialize(self) -> dict[str, Any]:
        return {
            "slots": [slot.serialize() for slot in self.slots],
            "name": self.name,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EquipSlots:
        slots = EquipSlots(
            [EquipSlot.deserialize(slot) for slot in data.get("slots", [])]
        )
        slots.name = data.get("name")
        return slots

    def __repr__(self):
        return f"EquipSlots({self.slots}, {self.name})"

    def __str__(self):
        return self.__repr__()


class LineUps:
    def __init__(self, slots: list[EquipSlots], total_slots: int = 15):
        self.slots = slots
        self.selected_slot = 0
        self.unlocked_slots = 0
        self.slot_names_length = total_slots

    @staticmethod
    def init(gv: core.GameVersion) -> LineUps:
        if gv < 90700:
            length = 10
        else:
            length = 15
        slots = [EquipSlots.init() for _ in range(length)]
        return LineUps(slots, length)

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> LineUps:
        if gv < 90700:
            length = 10
        else:
            length = stream.read_byte()
        slots = [EquipSlots.read(stream) for _ in range(length)]
        return LineUps(slots)

    def write(self, stream: core.Data, gv: core.GameVersion):
        if gv >= 90700:
            stream.write_byte(len(self.slots))
            length = len(self.slots)
        else:
            length = 10
        if length > len(self.slots):
            self.slots += [EquipSlots.init() for _ in range(length)]
        else:
            self.slots = self.slots[:length]
        for slot in self.slots:
            slot.write(stream)

    def read_2(self, stream: core.Data, gv: core.GameVersion):
        self.selected_slot = stream.read_int()
        if gv < 90700:
            unlocked_slots_l = stream.read_bool_list(10)
            unlocked_slots = sum(unlocked_slots_l)
        else:
            unlocked_slots = stream.read_byte()
        self.unlocked_slots = unlocked_slots

    def write_2(self, stream: core.Data, gv: core.GameVersion):
        stream.write_int(self.selected_slot)
        if gv < 90700:
            unlocked_slots_l = [False] * 10
            unlocked_slots = min(self.unlocked_slots, 10)
            for i in range(unlocked_slots):
                unlocked_slots_l[i] = True
            stream.write_bool_list(unlocked_slots_l, write_length=False)
        else:
            stream.write_byte(self.unlocked_slots)

    def read_slot_names(self, stream: core.Data, gv: core.GameVersion):
        if gv >= 110600:
            total_slots = stream.read_byte()
        else:
            total_slots = 15
        for i in range(total_slots):
            try:
                self.slots[i].read_name(stream)
            except IndexError:
                slot = EquipSlots.init()
                slot.read_name(stream)
                self.slots.append(slot)

        self.slot_names_length = total_slots

    def write_slot_names(self, stream: core.Data, gv: core.GameVersion):
        if gv >= 110600:
            stream.write_byte(self.slot_names_length)
        for i in range(self.slot_names_length):
            try:
                self.slots[i].write_name(stream)
            except IndexError:
                slot = EquipSlots.init()
                slot.write_name(stream)
                self.slots.append(slot)

    def serialize(self) -> dict[str, Any]:
        return {
            "slots": [slot.serialize() for slot in self.slots],
            "selected_slot": self.selected_slot,
            "unlocked_slots": self.unlocked_slots,
            "slot_names_length": self.slot_names_length,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> LineUps:
        line_ups = LineUps(
            [EquipSlots.deserialize(slot) for slot in data.get("slots", [])]
        )
        line_ups.selected_slot = data.get("selected_slot", 0)
        line_ups.unlocked_slots = data.get("unlocked_slots", 0)
        line_ups.slot_names_length = data.get("slot_names_length", 0)
        return line_ups

    def __repr__(self):
        return f"LineUps({self.slots}, {self.selected_slot}, {self.unlocked_slots})"

    def __str__(self):
        return self.__repr__()

    def edit_unlocked_slots(self):
        self.unlocked_slots = dialog_creator.SingleEditor(
            "unlocked_slots",
            self.unlocked_slots,
            self.slot_names_length,
            localized_item=True,
            remove_alias=True,
        ).edit()
