from typing import Any, Optional, Union
from bcsfe.core import io, locale_handler
from bcsfe.cli import color

"""
ChoiceInput(battle_item_names, battle_item_values, True)
"""


class IntInput:
    def __init__(
        self,
        max: Optional[int],
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
        disable_maxes = io.config.Config().get(io.config.Key.DISABLE_MAXES)
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
        self, dialog: str, perameters: dict[str, Union[int, str]]
    ) -> tuple[Optional[int], str]:
        user_input = color.ColoredInput(end="").get(dialog.format(**perameters))
        if user_input == "" and self.default is not None:
            return self.default, user_input
        try:
            user_input_i = int(user_input)
        except ValueError:
            return None, user_input

        return self.clamp_value(user_input_i), user_input

    def get_input_while(
        self, dialog: str, perameters: dict[str, Union[int, str]]
    ) -> Optional[int]:
        while True:
            int_val, user_input = self.get_input(dialog, perameters)
            if int_val is not None:
                return int_val
            if user_input == "q":
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
        dialog = locale_handler.LocalManager().get_key(localization_key)
        return self.get_input(dialog, perameters)

    def get_input_locale_while(
        self, localization_key: str, perameters: dict[str, Union[int, str]]
    ) -> Optional[int]:
        dialog = locale_handler.LocalManager().get_key(localization_key)
        return self.get_input_while(dialog, perameters)


class IntOutput:
    def __init__(self, dialog: str, perameters: dict[str, Union[int, str]]):
        self.dialog = dialog
        self.perameters = perameters

    def get_output(self, dialog: str) -> str:
        return dialog.format(**self.perameters)

    def display(self) -> None:
        color.ColoredText(self.get_output(self.dialog))

    def display_locale(self) -> None:
        dialog = locale_handler.LocalManager().get_key(self.dialog)
        color.ColoredText(self.get_output(dialog))


class ListOutput:
    def __init__(
        self,
        strings: list[str],
        ints: list[int],
        dialog: str,
        perameters: dict[str, Union[int, str]],
    ):
        self.strings = strings
        self.ints = ints
        self.dialog = dialog
        self.perameters = perameters

    def get_output(self, dialog: str, strings: list[str]) -> str:
        end_string = dialog.format(**self.perameters)
        end_string += "\n"
        for i, string in enumerate(strings):
            string = string.format(int=self.ints[i])
            end_string += f" <w>{i+1}.</> <g>{string}</>\n"
        end_string = end_string.strip("\n")
        return end_string

    def display(self, dialog: str, strings: list[str]) -> None:
        output = self.get_output(dialog, strings)
        color.ColoredText(output)

    def display_locale(self) -> None:
        dialog = locale_handler.LocalManager().get_key(self.dialog)
        new_strings: list[str] = []
        for string in self.strings:
            new_strings.append(locale_handler.LocalManager().get_key(string))
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
    ):
        self.items = items
        self.strings = strings
        self.ints = ints
        self.perameters = perameters
        self.dialog = dialog
        self.is_single_choice = single_choice

    def get_input(self) -> tuple[Optional[int], str]:
        ListOutput(
            self.strings, self.ints, self.dialog, self.perameters
        ).display_non_locale()
        return IntInput(len(self.strings), 1).get_input(self.dialog, self.perameters)

    def get_input_while(self) -> Optional[int]:
        while True:
            int_val, user_input = self.get_input()
            if int_val is not None:
                return int_val
            if user_input == "q":
                return None

    def get_input_locale(self) -> list[int]:
        ListOutput(
            self.strings, self.ints, self.dialog, self.perameters
        ).display_locale()
        dialog = (
            locale_handler.LocalManager()
            .get_key("input_many")
            .format(min=1, max=len(self.strings))
        )
        usr_input = color.ColoredInput().get(dialog).split(" ")
        int_vals: list[int] = []
        for i in usr_input:
            try:
                int_vals.append(int(i))
            except ValueError:
                continue
        return int_vals

    def multiple_choice(self) -> list[int]:
        user_input = self.get_input_locale()
        return [i - 1 for i in user_input]

    def single_choice(self) -> Optional[int]:
        return self.get_input_while()

    def get(self) -> Union[Optional[int], list[int]]:
        if self.is_single_choice:
            return self.single_choice()
        return self.multiple_choice()


class MultiEditor:
    def __init__(
        self,
        group_name: str,
        items: list[str],
        strings: list[str],
        ints: list[int],
        max_values: Optional[Union[list[int], int]],
        perameters: Optional[dict[str, Union[int, str]]],
        dialog: str,
        single_choice: bool = False,
        signed: bool = True,
    ):
        self.items = items
        self.strings = strings
        self.ints = ints
        if max_values is None:
            max_values_ = [None] * len(ints)
        elif isinstance(max_values, int):
            max_values_ = [max_values] * len(ints)
        else:
            max_values_ = max_values
        self.max_values = max_values_
        if perameters is None:
            perameters = {}
        self.perameters = perameters
        self.perameters["group_name"] = group_name
        self.dialog = dialog
        self.is_single_choice = single_choice
        self.signed = signed

    def edit(self) -> list[int]:
        choices = ChoiceInput(
            self.items, self.strings, self.ints, self.perameters, "select_edit"
        ).get()
        if choices is None:
            return self.ints
        if isinstance(choices, int):
            choices = [choices]
        for choice in choices:
            max_value = self.max_values[choice]
            if max_value is None:
                max_value = IntInput.get_max_value(max_value, self.signed)
            item = self.items[choice]
            usr_input = IntInput(
                max_value, default=self.ints[choice]
            ).get_input_locale_while(
                self.dialog,
                {"name": item, "value": self.ints[choice], "max": max_value},
            )
            if usr_input is None:
                continue
            self.ints[choice] = usr_input
            color.ColoredText.localize(
                "value_changed",
                name=item,
                value=self.ints[choice],
            )
        return self.ints


class DialogBuilder:
    def __init__(self, dialog_structure: dict[Any, Any]):
        self.dialog_structure = dialog_structure
