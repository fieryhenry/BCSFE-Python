from typing import Any, Optional, Union
from bcsfe import core
from bcsfe.cli import color


class RangeInput:
    def __init__(self, max: Optional[int] = None, min: int = 0):
        self.max = max
        self.min = min

    def clamp_value(self, value: int) -> int:
        if self.max is None:
            return max(value, self.min)
        return max(min(value, self.max), self.min)

    def get_input_locale(
        self,
        dialog: str,
        perameters: dict[str, Union[int, str]],
        escape: bool = True,
    ) -> Optional[list[int]]:
        user_input = color.ColoredInput(end="").localize(
            dialog, escape=escape, **perameters
        )
        return self.parse(user_input)

    def parse(self, user_input: str) -> Optional[list[int]]:
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
        max: Optional[int] = None,
        min: int = 0,
        default: Optional[int] = None,
        signed: bool = True,
    ):
        self.signed = signed
        self.max = self.get_max_value(max, signed)
        self.min = min
        self.default = default

    @staticmethod
    def get_max_value(max: Optional[int], signed: bool = True) -> int:
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
        perameters: dict[str, Union[int, str]],
        escape: bool = True,
    ) -> tuple[Optional[int], str]:
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
        self, dialog: str, perameters: dict[str, Union[int, str]]
    ) -> Optional[int]:
        while True:
            int_val, user_input = self.get_input(dialog, perameters)
            if int_val is not None:
                return int_val
            if user_input == core.core_data.local_manager.get_key("quit_key"):
                return None

    def get_input_locale(
        self, localization_key: Optional[str], perameters: dict[str, Union[int, str]]
    ) -> tuple[Optional[int], str]:
        if localization_key is None:
            if self.default is not None:
                perameters = {"min": self.min, "max": self.max, "default": self.default}
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
        dialog: Optional[str] = None,
        perameters: Optional[dict[str, Any]] = None,
    ):
        self.strings = strings
        self.ints = ints
        self.dialog = dialog
        if perameters is None:
            perameters = {}
        self.perameters = perameters

    def get_output(self, dialog: Optional[str], strings: list[str]) -> str:
        end_string = ""
        if dialog is not None:
            end_string = core.core_data.local_manager.get_key(dialog, **self.perameters)
        end_string += "\n"
        for i, string in enumerate(strings):
            try:
                int_string = str(self.ints[i])
            except IndexError:
                int_string = ""
            string = string.format(int=int_string)
            end_string += f" <@s>{i+1}.</> <@t>{string}</>\n"
        end_string = end_string.strip("\n")
        return end_string

    def display(self, dialog: Optional[str], strings: list[str]) -> None:
        output = self.get_output(dialog, strings)
        color.ColoredText(output)

    def display_locale(self, remove_alias: bool = False) -> None:
        dialog = ""
        if self.dialog is not None:
            dialog = core.core_data.local_manager.get_key(self.dialog)
        new_strings: list[str] = []
        for string in self.strings:
            string_ = core.core_data.local_manager.get_key(string)
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
        perameters: dict[str, Union[int, str]],
        dialog: str,
        single_choice: bool = False,
        remove_alias: bool = False,
        display_all_at_once: bool = True,
    ):
        self.items = items
        self.strings = strings
        self.ints = ints
        self.perameters = perameters
        self.dialog = dialog
        self.is_single_choice = single_choice
        self.remove_alias = remove_alias
        self.display_all_at_once = display_all_at_once

    @staticmethod
    def from_reduced(
        items: list[str],
        ints: Optional[list[int]] = None,
        perameters: Optional[dict[str, Union[int, str]]] = None,
        dialog: Optional[str] = None,
        single_choice: bool = False,
        remove_alias: bool = False,
        display_all_at_once: bool = True,
    ) -> "ChoiceInput":
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
        )

    def get_input(self) -> tuple[Optional[int], str]:
        if len(self.strings) == 0:
            return None, ""
        if len(self.strings) == 1:
            return 1, ""
        ListOutput(self.strings, self.ints).display_locale(self.remove_alias)
        return IntInput(len(self.strings), 1).get_input_locale(
            self.dialog, self.perameters
        )

    def get_input_while(self) -> Optional[int]:
        if len(self.strings) == 0:
            return None
        while True:
            int_val, user_input = self.get_input()
            if int_val is not None:
                return int_val
            if user_input == core.core_data.local_manager.get_key("quit_key"):
                return None

    def get_input_locale(
        self, localized: bool = True
    ) -> tuple[Optional[list[int]], bool]:
        if len(self.strings) == 0:
            return [], False
        if len(self.strings) == 1:
            return [1], False
        if not self.is_single_choice and self.display_all_at_once:
            if localized:
                self.strings.append("all_at_once")
            else:
                self.strings.append(core.core_data.local_manager.get_key("all_at_once"))
        if localized:
            ListOutput(self.strings, self.ints).display_locale()
        else:
            ListOutput(self.strings, self.ints).display_non_locale()
        key = "input_many"
        if self.is_single_choice:
            key = "input_single"
        dialog = core.core_data.local_manager.get_key(key).format(
            min=1, max=len(self.strings)
        )
        usr_input = color.ColoredInput().get(dialog).split(" ")
        int_vals: list[int] = []
        for i in usr_input:
            try:
                value = int(i)
                if value > len(self.strings) or value < 1:
                    raise ValueError
                int_vals.append(value)
            except ValueError:
                if i == core.core_data.local_manager.get_key("quit_key"):
                    return None, False
                if i in self.strings:
                    int_vals.append(self.strings.index(i) + 1)
                    continue
                color.ColoredText.localize(
                    "invalid_input_int", min=1, max=len(self.strings)
                )
        if (
            len(self.strings) in int_vals
            and not self.is_single_choice
            and self.display_all_at_once
        ):
            return list(range(1, len(self.strings))), True

        if self.is_single_choice and len(int_vals) > 1:
            int_vals = [int_vals[0]]

        return int_vals, False

    def get_input_locale_while(self) -> Optional[list[int]]:
        if len(self.strings) == 0:
            return []
        if len(self.strings) == 1:
            return [1]
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
    ) -> tuple[Optional[list[int]], bool]:
        color.ColoredText.localize(self.dialog, True, **self.perameters)
        user_input, all_at_once = self.get_input_locale(localized_options)
        if user_input is None:
            return None, all_at_once
        return [i - 1 for i in user_input], all_at_once

    def single_choice(self) -> Optional[int]:
        return self.get_input_while()

    def get(self) -> tuple[Union[Optional[int], list[int]], bool]:
        if self.is_single_choice:
            return self.single_choice(), False
        return self.multiple_choice()


class MultiEditor:
    def __init__(
        self,
        group_name: str,
        items: list[str],
        strings: list[str],
        ints: Optional[list[int]],
        max_values: Optional[Union[list[int], int]],
        perameters: Optional[dict[str, Union[int, str]]],
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
        ints: Optional[list[int]],
        max_values: Optional[Union[list[int], int]],
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
            self.items, self.strings, self.ints or [], self.perameters, "select_edit"
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
            max_value = IntInput.get_max_value(self.max_values[choice], self.signed)
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
            max_value = self.max_values[choice]
            if max_value is None:
                max_value = IntInput.get_max_value(max_value, self.signed)

            if self.cumulative_max:
                max_value -= sum(ints) - ints[choice]

            item = self.items[choice]
            usr_input = IntInput(
                max_value, default=ints[choice]
            ).get_input_locale_while(
                self.dialog,
                {"name": item, "value": ints[choice], "max": max_value},
            )
            if usr_input is None:
                continue
            ints[choice] = usr_input
            color.ColoredText.localize(
                "value_changed",
                name=item,
                value=ints[choice],
            )
        return ints


class SingleEditor:
    def __init__(
        self,
        item: str,
        value: int,
        max_value: Optional[int] = None,
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

    def edit(self) -> int:
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
        )
        if usr_input is None:
            return self.value
        print()
        color.ColoredText.localize(
            "value_changed",
            name=self.item,
            value=usr_input,
        )
        return usr_input


class StringInput:
    def __init__(self, default: str = ""):
        self.default = default

    def get_input_locale_while(
        self, key: str, perameters: dict[str, Any]
    ) -> Optional[str]:
        while True:
            usr_input = self.get_input_locale(key, perameters)
            if usr_input is None:
                return None
            if usr_input == "":
                return self.default
            if usr_input == " ":
                continue
            return usr_input

    def get_input_locale(self, key: str, perameters: dict[str, Any]) -> Optional[str]:
        usr_input = color.ColoredInput().localize(key, **perameters)
        if usr_input == "" or usr_input == core.core_data.local_manager.get_key(
            "quit_key"
        ):
            return None
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

    def get_input_locale_while(self, key: str, perameters: dict[str, Any]) -> bool:
        while True:
            usr_input = self.get_input_locale(key, perameters)
            if usr_input is None:
                return self.default
            if usr_input == "" or usr_input == core.core_data.local_manager.get_key(
                "quit_key"
            ):
                return self.default
            if usr_input == " ":
                continue
            return usr_input == core.core_data.local_manager.get_key("yes_key")

    def get_input_locale(self, key: str, perameters: dict[str, Any]) -> Optional[str]:
        usr_input = color.ColoredInput().get(key, **perameters)
        if usr_input == "" or usr_input == core.core_data.local_manager.get_key(
            "quit_key"
        ):
            return None
        return usr_input

    def get_input_once(
        self, key: str, perameters: Optional[dict[str, Any]] = None
    ) -> bool:
        if perameters is None:
            perameters = {}
        usr_input = color.ColoredInput().localize(key, **perameters)
        if usr_input == "" or usr_input == core.core_data.local_manager.get_key(
            "quit_key"
        ):
            return self.default
        return usr_input == core.core_data.local_manager.get_key("yes_key")


class DialogBuilder:
    def __init__(self, dialog_structure: dict[Any, Any]):
        self.dialog_structure = dialog_structure
