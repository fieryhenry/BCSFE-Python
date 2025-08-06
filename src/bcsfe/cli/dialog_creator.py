from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color


class RangeInput:
    def __init__(self, max: int | None = None, min: int = 0):
        self.max = max
        self.min = min

    def clamp_value(self, value: int) -> int:
        if self.max is None:
            return max(value, self.min)
        return max(min(value, self.max), self.min)

    def get_input_locale(
        self,
        dialog: str,
        perameters: dict[str, int | str],
        escape: bool = True,
    ) -> list[int] | None:
        user_input = color.ColoredInput(end="").localize(
            dialog, escape=escape, **perameters
        )
        return self.parse(user_input)

    def parse(self, user_input: str) -> list[int] | None:
        if user_input == "":
            return []
        if user_input == core.core_data.local_manager.get_key("quit_key"):
            return None
        parts = user_input.split(" ")
        ids: list[int] = []
        all_text = core.core_data.local_manager.get_key("all")
        for part in parts:
            if "-" in part and len(part.split("-")) == 2:
                lower, upper = part.split("-")
                try:
                    lower = int(lower)
                    upper = int(upper)
                except ValueError:
                    continue
                if lower > upper:
                    lower, upper = upper, lower
                if self.max is not None:
                    lower = max(lower, self.min)
                    upper = min(upper, self.max)
                else:
                    lower = max(lower, self.min)
                ids.extend(range(lower, upper + 1))
            elif part.lower() == all_text.lower() and self.max is not None:
                ids.extend(range(self.min, self.max + 1))
            else:
                try:
                    part = int(part)
                except ValueError:
                    continue
                if self.max is not None:
                    part = max(part, self.min)
                    part = min(part, self.max)
                else:
                    part = max(part, self.min)
                ids.append(part)
        return ids


class IntInput:
    def __init__(
        self,
        max: int | None = None,
        min: int = 0,
        default: int | None = None,
        signed: bool = True,
    ):
        self.signed = signed
        self.max = self.get_max_value(max, signed)
        self.min = min
        self.default = default

    @staticmethod
    def get_max_value(max: int | None, signed: bool = True) -> int:
        disable_maxes = core.core_data.config.get_bool(core.ConfigKey.DISABLE_MAXES)
        if signed:
            max_int = 2**31 - 1
        else:
            max_int = 2**32 - 1
        if disable_maxes or max is None:
            return max_int
        return min(max, max_int)

    def clamp_value(self, value: int) -> int:
        return max(min(value, self.max), self.min)

    def get_input(
        self,
        localization_key: str,
        perameters: dict[str, int | str],
        escape: bool = True,
    ) -> tuple[int | None, str]:
        user_input = color.ColoredInput(end="").localize(
            localization_key, escape=escape, **perameters
        )
        if user_input == "" and self.default is not None:
            return self.default, user_input
        try:
            user_input_i = int(user_input)
        except ValueError:
            return None, user_input

        return self.clamp_value(user_input_i), user_input

    def get_input_locale_while(
        self, dialog: str, perameters: dict[str, int | str], escape: bool = True
    ) -> int | None:
        while True:
            int_val, user_input = self.get_input(dialog, perameters, escape=escape)
            if int_val is not None:
                return int_val
            if user_input == core.core_data.local_manager.get_key("quit_key"):
                return None

    def get_input_locale(
        self, localization_key: str | None, perameters: dict[str, int | str]
    ) -> tuple[int | None, str]:
        if localization_key is None:
            if self.default is not None:
                perameters = {
                    "min": self.min,
                    "max": self.max,
                    "default": self.default,
                }
                localization_key = "input_int_default"
            else:
                perameters = {"min": self.min, "max": self.max}
                localization_key = "input_int"
        return self.get_input(localization_key, perameters)

    def get_basic_input_locale(self, localization_key: str, perameters: dict[str, Any]):
        try:
            user_input = int(
                color.ColoredInput(end="").localize(localization_key, **perameters)
            )
        except ValueError:
            return None
        return user_input


class ListOutput:
    def __init__(
        self,
        strings: list[str],
        ints: list[int],
        dialog: str | None = None,
        perameters: dict[str, Any] | None = None,
        start_index: int = 1,
        localize_elements: bool = True,
    ):
        self.strings = strings
        self.ints = ints
        self.dialog = dialog
        if perameters is None:
            perameters = {}
        self.perameters = perameters
        self.start_index = start_index
        self.localize_elements = localize_elements

    def get_output(self, dialog: str | None, strings: list[str]) -> str:
        end_string = ""
        if dialog is not None:
            end_string = core.core_data.local_manager.get_key(dialog, **self.perameters)
        end_string += "\n"
        for i, string in enumerate(strings):
            try:
                int_string = str(self.ints[i])
            except IndexError:
                int_string = ""

            string = string.replace("{int}", int_string)
            end_string += f" <@s>{i + self.start_index}.</> <@t>{string}</>\n"
        end_string = end_string.strip("\n")
        return end_string

    def display(self, dialog: str | None, strings: list[str]) -> None:
        output = self.get_output(dialog, strings)
        color.ColoredText(output)

    def display_locale(self, remove_alias: bool = False) -> None:
        dialog = ""
        if self.dialog is not None:
            dialog = core.core_data.local_manager.get_key(self.dialog)
        new_strings: list[str] = []
        for string in self.strings:
            if self.localize_elements:
                string_ = core.core_data.local_manager.get_key(string)
            else:
                string_ = string
            if remove_alias:
                string_ = core.core_data.local_manager.get_all_aliases(string_)[0]
            new_strings.append(string_)

        self.display(dialog, new_strings)

    def display_non_locale(self) -> None:
        self.display(self.dialog, self.strings)


class ChoiceInput:
    def __init__(
        self,
        items: list[str],
        strings: list[str],
        ints: list[int],
        perameters: dict[str, int | str],
        dialog: str,
        single_choice: bool = False,
        remove_alias: bool = False,
        display_all_at_once: bool = True,
        start_index: int = 1,
        localize_options: bool = True,
    ):
        self.items = items
        self.strings = strings
        self.ints = ints
        self.perameters = perameters
        self.dialog = dialog
        self.is_single_choice = single_choice
        self.remove_alias = remove_alias
        self.display_all_at_once = display_all_at_once
        self.start_index = start_index
        self.localize_options = localize_options

    @staticmethod
    def from_reduced(
        items: list[str],
        ints: list[int] | None = None,
        perameters: dict[str, int | str] | None = None,
        dialog: str | None = None,
        single_choice: bool = False,
        remove_alias: bool = False,
        display_all_at_once: bool = True,
        start_index: int = 1,
        localize_options: bool = True,
    ) -> ChoiceInput:
        if perameters is None:
            perameters = {}
        if ints is None:
            ints = []
        if dialog is None:
            dialog = ""
        return ChoiceInput(
            items.copy(),
            items.copy(),
            ints.copy(),
            perameters.copy(),
            dialog,
            single_choice,
            remove_alias,
            display_all_at_once,
            start_index,
            localize_options,
        )

    def get_input(self) -> tuple[int | None, str]:
        if len(self.strings) == 0:
            return None, ""
        if len(self.strings) == 1:
            return self.get_min_value(), ""
        ListOutput(
            self.strings,
            self.ints,
            start_index=self.start_index,
            localize_elements=self.localize_options,
        ).display_locale(self.remove_alias)
        return IntInput(self.get_max_value(), self.get_min_value()).get_input_locale(
            self.dialog, self.perameters
        )

    def get_input_while(self) -> int | None:
        if len(self.strings) == 0:
            return None
        while True:
            int_val, user_input = self.get_input()
            if int_val is not None:
                return int_val
            if user_input == core.core_data.local_manager.get_key("quit_key"):
                return None
            for i, string in enumerate(self.strings):
                if self.localize_options:
                    string = core.core_data.local_manager.get_key(string)
                if string.lower().strip() == user_input.lower().strip():
                    return i + self.start_index

    def get_max_value(self) -> int:
        return len(self.strings) + self.start_index - 1

    def get_min_value(self) -> int:
        return self.start_index

    def get_input_locale(self, localized: bool = True) -> tuple[list[int] | None, bool]:
        if len(self.strings) == 0:
            return [], False
        if len(self.strings) == 1:
            return [self.get_min_value()], False
        if not self.is_single_choice and self.display_all_at_once:
            if localized:
                self.strings.append("all_at_once")
            else:
                self.strings.append(core.core_data.local_manager.get_key("all_at_once"))
        if localized:
            ListOutput(
                self.strings,
                self.ints,
                start_index=self.start_index,
                localize_elements=self.localize_options,
            ).display_locale()
        else:
            ListOutput(
                self.strings,
                self.ints,
                start_index=self.start_index,
                localize_elements=self.localize_options,
            ).display_non_locale()
        key = "input_many"
        if self.is_single_choice:
            key = "input_single"
        dialog = core.core_data.local_manager.get_key(key).format(
            min=self.get_min_value(), max=self.get_max_value()
        )
        usr_input = color.ColoredInput().get(dialog).split(" ")
        int_vals: list[int] = []
        for inp in usr_input:
            try:
                value = int(inp)
                if value > self.get_max_value() or value < self.get_min_value():
                    raise ValueError
                int_vals.append(value)
            except ValueError:
                if inp == core.core_data.local_manager.get_key("quit_key"):
                    return None, False

                cont = False
                for i, string in enumerate(self.strings):
                    if self.localize_options:
                        string = core.core_data.local_manager.get_key(string)
                    if string.lower().strip() == inp.lower().strip():
                        int_vals.append(i + self.start_index)
                        cont = True
                        break

                if cont:
                    continue

                color.ColoredText.localize(
                    "invalid_input_int",
                    min=self.get_min_value(),
                    max=self.get_max_value(),
                )
        if (
            self.get_max_value() in int_vals
            and not self.is_single_choice
            and self.display_all_at_once
        ):
            return list(range(self.get_min_value(), self.get_max_value())), True

        if self.is_single_choice and len(int_vals) > 1:
            int_vals = [int_vals[0]]

        return int_vals, False

    def get_input_locale_while(self) -> list[int] | None:
        if len(self.strings) == 0:
            return []
        if len(self.strings) == 1:
            return [self.get_min_value()]
        while True:
            int_vals, all_at_once = self.get_input_locale()
            if int_vals is None:
                return None
            if all_at_once:
                return int_vals
            if len(int_vals) == 0:
                continue
            if len(int_vals) == 1 and int_vals[0] == 0:
                return []
            return int_vals

    def multiple_choice(
        self, localized_options: bool = True
    ) -> tuple[list[int] | None, bool]:
        color.ColoredText.localize(self.dialog, True, **self.perameters)
        user_input, all_at_once = self.get_input_locale(localized_options)
        if user_input is None:
            return None, all_at_once
        return [i - self.start_index for i in user_input], all_at_once

    def single_choice(self) -> int | None:
        return self.get_input_while()

    def get(self) -> tuple[int | None | list[int], bool]:
        if self.is_single_choice:
            return self.single_choice(), False
        return self.multiple_choice()


class MultiEditor:
    def __init__(
        self,
        group_name: str,
        items: list[str],
        strings: list[str],
        ints: list[int] | None,
        max_values: list[int] | int | None,
        perameters: dict[str, int | str] | None,
        dialog: str,
        single_choice: bool = False,
        signed: bool = True,
        group_name_localized: bool = False,
        cumulative_max: bool = False,
    ):
        self.items = items
        self.strings = strings
        self.ints = ints
        if self.ints is not None:
            total_ints = len(self.ints)
        else:
            total_ints = len(self.strings)
        if max_values is None:
            max_values_ = [None] * total_ints
        elif isinstance(max_values, int):
            max_values_ = [max_values] * total_ints
        else:
            max_values_ = max_values
        self.max_values = max_values_
        if perameters is None:
            perameters = {}
        self.perameters = perameters
        if group_name_localized:
            self.perameters["group_name"] = core.core_data.local_manager.get_key(
                group_name
            )
        else:
            self.perameters["group_name"] = group_name
        self.dialog = dialog
        self.is_single_choice = single_choice
        self.signed = signed
        self.cumulative_max = cumulative_max

    @staticmethod
    def from_reduced(
        group_name: str,
        items: list[str],
        ints: list[int] | None,
        max_values: list[int] | int | None,
        group_name_localized: bool = False,
        dialog: str = "input",
        cumulative_max: bool = False,
        items_localized: bool = False,
    ):
        if items_localized:
            for i, item in enumerate(items):
                items[i] = core.core_data.local_manager.get_key(item)
        text: list[str] = []
        for item_name in items:
            if ints is not None:
                text.append(f"{item_name} <@q>: {{int}}</>")
            else:
                text.append(f"{item_name}")
        return MultiEditor(
            group_name,
            items,
            text,
            ints,
            max_values,
            None,
            dialog,
            group_name_localized=group_name_localized,
            cumulative_max=cumulative_max,
        )

    def edit(self) -> list[int]:
        choices, all_at_once = ChoiceInput(
            self.items,
            self.strings,
            self.ints or [],
            self.perameters,
            "select_edit",
        ).get()
        if choices is None:
            return self.ints or []
        if isinstance(choices, int):
            choices = [choices]
        if all_at_once:
            return self.edit_all(choices)
        return self.edit_one(choices)

    def edit_all(self, choices: list[int]) -> list[int]:
        max_max_value = 0
        for choice in choices:
            if choice >= len(self.max_values):
                max_value = None
            else:
                max_value = self.max_values[choice]
            if max_value is None:
                max_value = IntInput.get_max_value(max_value, self.signed)
            max_max_value = max(max_max_value, max_value)
        if self.cumulative_max:
            max_max_value = max_max_value // len(choices)
        usr_input = IntInput(max_max_value, default=None).get_input_locale_while(
            self.dialog + "_all",
            {
                "name": self.perameters["group_name"],
                "max": max_max_value,
            },
        )
        if usr_input is None:
            return self.ints or []
        ints = self.ints or [0] * len(self.strings)

        for choice in choices:
            if choice >= len(self.max_values):
                max_value = None
            else:
                max_value = self.max_values[choice]
            max_value = IntInput.get_max_value(max_value, self.signed)
            value = min(usr_input, max_value)
            ints[choice] = value
            if self.ints is not None:
                color.ColoredText.localize(
                    "value_changed",
                    name=self.items[choice],
                    value=value,
                )

        return ints

    def edit_one(self, choices: list[int]) -> list[int]:
        ints = self.ints or [0] * len(self.strings)

        for choice in choices:
            if choice >= len(self.max_values):
                max_value = None
            else:
                max_value = self.max_values[choice]
            if max_value is None:
                max_value = IntInput.get_max_value(max_value, self.signed)

            if self.cumulative_max:
                max_value -= sum(ints) - ints[choice]
                max_value = max(max_value, 0)

            item = self.items[choice]
            usr_input = IntInput(
                max_value, default=ints[choice]
            ).get_input_locale_while(
                self.dialog,
                {"name": item, "value": ints[choice], "max": max_value},
                escape=False,
            )
            if usr_input is None:
                continue
            ints[choice] = usr_input
            color.ColoredText.localize(
                "value_changed", name=item, value=ints[choice], escape=False
            )
        return ints


class SingleEditor:
    def __init__(
        self,
        item: str,
        value: int,
        max_value: int | None = None,
        min_value: int = 0,
        signed: bool = True,
        localized_item: bool = False,
        remove_alias: bool = False,
    ):
        if localized_item:
            item = core.core_data.local_manager.get_key(item)
        if remove_alias:
            item = core.core_data.local_manager.get_all_aliases(item)[0]
        self.item = item
        self.value = value
        self.max_value = max_value
        self.min_value = min_value
        self.signed = signed

    def edit(self, escape_text: bool = True) -> int:
        max_value = self.max_value
        if max_value is None:
            max_value = IntInput.get_max_value(max_value, self.signed)
        if self.max_value is None:
            dialog = "input_non_max"
        elif self.min_value != 0:
            dialog = "input_min"
        else:
            dialog = "input"
        usr_input = IntInput(
            max_value, self.min_value, default=self.value, signed=self.signed
        ).get_input_locale_while(
            dialog,
            {
                "name": self.item,
                "value": self.value,
                "max": max_value,
                "min": self.min_value,
            },
            escape=escape_text,
        )
        if usr_input is None:
            return self.value
        print()
        color.ColoredText.localize(
            "value_changed", name=self.item, value=usr_input, escape=escape_text
        )
        return usr_input


class StringInput:
    def __init__(self, default: str = ""):
        self.default = default

    def get_input_locale_while(
        self, key: str, perameters: dict[str, Any]
    ) -> str | None:
        while True:
            usr_input = self.get_input_locale(key, perameters)
            if usr_input is None:
                return None
            if usr_input == "":
                return self.default
            if usr_input == " ":
                continue
            return usr_input

    def get_input_locale(
        self,
        key: str,
        perameters: dict[str, Any] | None = None,
        escape: bool = True,
    ) -> str | None:
        if perameters is None:
            perameters = {}
        usr_input = color.ColoredInput().localize(key, escape, **perameters)
        quit_key = core.core_data.local_manager.get_key("quit_key")
        if usr_input == "" or usr_input == quit_key:
            return None
        if usr_input == f"\\{quit_key}":
            return quit_key
        return usr_input


class StringEditor:
    def __init__(self, item: str, value: str, item_localized: bool = False):
        if item_localized:
            item = core.core_data.local_manager.get_key(item)
        self.item = item
        self.value = value

    def edit(self) -> str:
        usr_input = StringInput(default=self.value).get_input_locale_while(
            "input_non_max",
            {"name": self.item, "value": self.value},
        )
        if usr_input is None:
            return self.value
        color.ColoredText.localize(
            "value_changed",
            name=self.item,
            value=usr_input,
        )
        return usr_input


class YesNoInput:
    def __init__(self, default: bool = False):
        self.default = default

    def get_input_once(
        self, key: str, perameters: dict[str, Any] | None = None
    ) -> bool | None:
        if perameters is None:
            perameters = {}
        usr_input = color.ColoredInput().localize(key, **perameters)
        if usr_input == "":
            return self.default

        if usr_input == core.core_data.local_manager.get_key("quit_key"):
            return None
        return usr_input == core.core_data.local_manager.get_key("yes_key")


class DialogBuilder:
    def __init__(self, dialog_structure: dict[Any, Any]):
        self.dialog_structure = dialog_structure
