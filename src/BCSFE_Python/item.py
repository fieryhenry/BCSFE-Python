"""Item object"""

from typing import Any, Union

from . import helper, user_input_handler, managed_item, config_manager, tracker


class BannableItem:
    """BannableItem object"""

    def __init__(
        self,
        is_bannable: bool = False,
        has_workaround: bool = False,
        work_around_text: str = "",
        managed_item_type: Union[None, managed_item.ManagedItemType] = None,
    ) -> None:
        self.is_bannable = is_bannable
        self.has_workaround = has_workaround
        self.work_around_text = work_around_text
        self.managed_item_type = managed_item_type


class Item:
    """An item"""

    def __init__(
        self,
        name: str,
        value: Union[int, str],
        max_value: Union[int, None],
        edit_name: str,
        bannable: BannableItem = BannableItem(False, False, ""),
        offset: int = 0,
        length: int = 4,
        set_name: str = "set",
    ) -> None:
        self.name = name
        self.value = value
        self.max_value = max_value
        self.offset = offset
        self.edit_name = edit_name
        self.bannable = bannable
        self.length = length
        self.set_name = set_name

        if config_manager.get_config_value_category("EDITOR", "DISABLE_MAXES"):
            self.max_value = None

    def clamp(self) -> None:
        """Clamp the value to the max value"""

        if self.max_value is not None:
            self.value = helper.clamp(
                value=int(self.value),
                min_value=0,
                max_value=self.max_value,
            )
        else:
            # Make sure the value is not negative and fits in the byte length
            self.value = helper.clamp(
                value=int(self.value),
                min_value=0,
                max_value=256**self.length - 1,
            )

    def ban_warning(self) -> bool:
        """Warning for editing a bannable item"""

        if not config_manager.get_config_value_category("EDITOR", "SHOW_BAN_WARNING"):
            return False

        helper.colored_text(
            text=f"WARNING: Editing in {self.name} will most likely lead to a ban!",
            base=helper.RED,
        )
        if self.bannable.has_workaround:
            helper.colored_text(
                text=self.bannable.work_around_text,
                new=helper.RED,
            )
        leave = (
            user_input_handler.colored_input("Do you want to continue? (&y&/&n&):")
            == "n"
        )
        return leave

    def edit_int(self) -> None:
        """Handler for editing an integer value"""

        if self.bannable.is_bannable:
            leave = self.ban_warning()
            if leave:
                return
        if self.value is not None:
            helper.colored_text(
                f"The current {self.edit_name} of {self.name} is : &{int(self.value)+self.offset}&"
            )
        if self.max_value is None:
            max_str = "(max &None&)"
        else:
            max_str = f"(max &{self.max_value+self.offset}&)"

        text = f"Enter the {self.edit_name} of {self.name} you want to {self.set_name} {max_str}:"
        self.value = user_input_handler.get_int(text) - self.offset
        self.clamp()
        helper.colored_text(
            f"Successfully {self.set_name} the {self.edit_name} of {self.name} to &{self.value+self.offset}&"
        )

    def edit_str(self) -> None:
        """Handler for editing a string value"""

        helper.colored_text(
            f"The current {self.edit_name} of {self.name} is : &{self.value}&"
        )
        text = f"Enter the {self.edit_name} of {self.name} you want to {self.set_name}:"
        self.value = user_input_handler.colored_input(text)
        helper.colored_text(
            f"Successfully {self.set_name} the {self.edit_name} of {self.name} to &{self.value}&"
        )

    def edit(self) -> None:
        """Handler for editing an item"""

        original_val = self.value

        if isinstance(self.value, int):
            self.edit_int()
        elif self.value is None:
            self.edit_int()
        else:
            self.edit_str()
            return

        if self.bannable.is_bannable and original_val != self.value:
            new_val = self.value
            if not self.bannable.managed_item_type or isinstance(original_val, str):
                return
            item_tracker = tracker.Tracker()
            item_tracker.update_tracker(
                new_val - original_val, self.bannable.managed_item_type
            )


class ItemGroup:
    """A group of items"""

    def __init__(self, name: str, items: list[Item]):
        self.name = name
        self.items = items
        self.selected_items: list[Item] = []

    @property
    def max_value(self) -> Union[int, None]:
        """Get the maximum value of the selected items"""
        if config_manager.get_config_value_category("EDITOR", "DISABLE_MAXES"):
            return None
        try:
            return max(
                [
                    item.max_value
                    for item in self.selected_items
                    if item.max_value is not None
                ]
            )
        except (ValueError, TypeError):
            return None

    @property
    def selected_names(self) -> list[str]:
        """Get the names of the selected items"""
        return [item.name for item in self.selected_items]

    @property
    def names(self) -> list[str]:
        """Get the names of the items"""
        return [item.name for item in self.items]

    @property
    def selected_values(self) -> list[Union[int, str]]:
        """Get the values of the selected items"""
        return [item.value for item in self.selected_items]

    @property
    def values(self) -> list[Any]:
        """Get the values of the items"""
        return [item.value for item in self.items]

    def select(self) -> bool:
        """Select items from the group"""

        helper.colored_text(f"What &{self.name}& do you want to set?")
        ids = user_input_handler.select_inc(
            self.names,
            offset=self.items[0].offset,
            extra_data=self.values,
        )
        for option_id in ids[0]:
            if option_id < 0:
                helper.colored_text(
                    "You can't select options less than 1!",
                    base=helper.RED,
                )
                continue
            if option_id >= len(self.items):
                helper.colored_text(
                    "You can't select options greater than the last option!",
                    base=helper.RED,
                )
                continue
            self.selected_items.append(self.items[option_id])
        return ids[1]

    def edit(self) -> None:
        """Edit items from the group"""

        individual = self.select()
        if not individual:
            self.edit_all()
        else:
            for item in self.selected_items:
                print()
                item.edit()

    def edit_all(self) -> None:
        """Handler for editing all selected items at once"""

        if self.max_value is None:
            max_str = ""
        else:
            max_str = f" (max &{self.max_value+self.selected_items[0].offset}&)"
        text = f"Enter the {self.selected_items[0].edit_name} of {self.name} you want to set{max_str}:"
        value = user_input_handler.get_int(text) - self.selected_items[0].offset
        display_val = value
        for item in self.selected_items:
            item.value = value
            if self.max_value is not None:
                item.clamp()
                display_val = item.value

        helper.colored_text(
            f"Successfully set the {self.selected_items[0].edit_name} of {self.name} to &{display_val + self.selected_items[0].offset}&"
        )


def create_item_group(
    names: list[str],
    values: Any,
    maxes: Any,
    edit_name: str,
    group_name: str,
    offset: int = 0,
) -> ItemGroup:
    """Create a list of items"""

    if isinstance(maxes, int) or maxes is None:
        maxes = [maxes] * len(names)
    if values is None:
        values = [None] * len(names)

    items = [
        Item(
            name=name,
            value=value,
            max_value=max_value,
            edit_name=edit_name,
            offset=offset,
        )
        for name, value, max_value in zip(names, values, maxes)
    ]

    item_group = ItemGroup(name=group_name, items=items)

    return item_group
