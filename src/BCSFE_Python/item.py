from typing import Optional, Union
from . import managed_item, user_input_handler, helper, locale_handler, tracker


class Bannable:
    def __init__(self, type: "managed_item.ManagedItemType", work_around: str = ""):
        self.type = type
        self.work_around = work_around


class Int:
    def __init__(self, value: Optional[int], byte_size: int = 4, signed: bool = True):
        self.value = value
        self.byte_size = byte_size
        self.signed = signed

    def get_max_value(self) -> int:
        if self.signed:
            return (2 ** (self.byte_size * 8 - 1)) - 1
        return (2 ** (self.byte_size * 8)) - 1


class IntItem:
    def __init__(
        self,
        name: str,
        value: Int,
        max_value: Optional[int],
        bannable: Optional[Bannable] = None,
        offset: int = 0,
    ):
        self.name = name
        self.__value = value
        self.max_value = max_value
        self.bannable = bannable
        self.offset = offset
        self.locale_manager = locale_handler.LocalManager.from_config()

    def get_max_value(self) -> int:
        if self.max_value is not None:
            return self.max_value
        return self.__value.get_max_value()

    def show_ban_warning(self) -> bool:
        if self.bannable is None:
            return True
        helper.colored_text(self.locale_manager.search_key("ban_warning") % self.name)
        if self.bannable.work_around:
            helper.colored_text(self.bannable.work_around)
        return user_input_handler.get_yes_no(
            self.locale_manager.search_key("ban_warning_leave")
        )

    def edit(self) -> None:
        end = not self.show_ban_warning()
        if end:
            return
        original_value = self.__value.value
        helper.colored_text(
            self.locale_manager.search_key("current_item_value")
            % (self.name, self.get_value_off())
        )
        max_str = ""
        if self.max_value is not None:
            max_str = " " + self.locale_manager.search_key("max_str") % self.max_value
        new_value = user_input_handler.get_int(
            self.locale_manager.search_key("enter_value_text") % (self.name, max_str),
        )
        new_value -= self.offset
        new_value = helper.clamp(new_value, 0, self.get_max_value())
        self.__value.value = new_value
        helper.colored_text(
            self.locale_manager.search_key("item_value_changed")
            % (
                self.name,
                0 if original_value is None else original_value,
                self.get_value_off(),
            )
        )
        if self.bannable is not None and self.__value.value != original_value:
            new_value = self.__value.value
            if original_value is None:
                original_value = 0
            item_tracker = tracker.Tracker()
            item_tracker.update_tracker(
                self.__value.value - original_value, self.bannable.type
            )

    def get_value_off(self) -> int:
        if self.__value.value is None:
            return 0
        return self.__value.value + self.offset

    def get_value(self) -> int:
        if self.__value.value is None:
            return 0
        return self.__value.value

    def get_value_none(self) -> Optional[int]:
        return self.__value.value

    def set_value(self, value: int) -> None:
        self.__value.value = value


class IntItemGroup:
    def __init__(self, group_name: str, items: list[IntItem]):
        self.items = items
        self.locale_manager = locale_handler.LocalManager.from_config()
        self.group_name = group_name

    def get_values(self) -> list[int]:
        return [item.get_value() for item in self.items]

    def get_values_none(self) -> list[Optional[int]]:
        return [item.get_value_none() for item in self.items]

    def get_values_off(self) -> list[int]:
        return [item.get_value_off() for item in self.items]

    def all_none(self) -> bool:
        return all([item.get_value_none() is None for item in self.items])

    def get_names(self) -> list[str]:
        return [item.name for item in self.items]

    def edit(self) -> None:
        if not self.items:
            return
        ids, individual = user_input_handler.select_options(
            self.get_names(),
            self.locale_manager.search_key("select_l"),
            self.get_values_off() if not self.all_none() else None,
        )
        if individual:
            for id in ids:
                self.items[id].edit()
        else:
            max_value = self.get_max_max_value()
            offset = self.items[ids[0]].offset
            max_str = ""
            if self.items[ids[0]].max_value is not None:
                max_str = " " + self.locale_manager.search_key("max_str") % (
                    max_value + offset
                )
            new_value = user_input_handler.get_int(
                self.locale_manager.search_key("enter_value_text")
                % (self.group_name, max_str)
            )
            new_value -= offset
            entered_value = helper.clamp(new_value, 0, max_value)
            for id in ids:
                max_value = self.items[id].get_max_value()
                new_value = helper.clamp(new_value, 0, max_value)
                self.items[id].set_value(new_value)

            helper.colored_text(
                self.locale_manager.search_key("success_set")
                % (self.group_name, entered_value + offset)
            )

    def get_max_max_value(self) -> int:
        return max([item.get_max_value() for item in self.items])

    @staticmethod
    def from_lists(
        names: list[str],
        values: Optional[list[int]],
        maxes: Union[list[int], int, None],
        group_name: str,
        offset: int = 0,
    ) -> "IntItemGroup":
        items: list[IntItem] = []
        for i in range(len(names)):
            max_value = maxes[i] if isinstance(maxes, list) else maxes
            items.append(
                IntItem(
                    names[i],
                    Int(values[i]) if values is not None else Int(None),
                    max_value,
                    offset=offset,
                )
            )
        return IntItemGroup(group_name, items)


class StrItem:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
        self.locale_manager = locale_handler.LocalManager.from_config()

    def edit(self) -> None:
        original_value = self.value
        helper.colored_text(
            self.locale_manager.search_key("current_item_value")
            % (self.name, self.value)
        )
        new_value = user_input_handler.colored_input(
            self.locale_manager.search_key("enter_value_text") % (self.name, "")
        )
        self.value = new_value
        helper.colored_text(
            self.locale_manager.search_key("item_value_changed")
            % (self.name, original_value, self.value)
        )

    def get_value(self) -> str:
        return self.value
