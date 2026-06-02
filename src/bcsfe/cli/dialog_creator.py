from __future__ import annotations
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

from bcsfe import core
from bcsfe.cli import color

T = TypeVar("T")

ActionFunc = Callable[[int], T]


class NoAssignedActionException(Exception):
    def __init__(self, index: int):
        super().__init__(f"No assigned action to index {index}")


class Action[T]:
    def __init__(self, options: list[str], func: ActionFunc[T]):
        self.options = options
        self.func = func

    def len(self) -> int:
        return len(self.options)

    @staticmethod
    def new_raw(options: str | list[str], func: ActionFunc[T]) -> Action[T]:
        if isinstance(options, str):
            options = [options]
        return Action(options, func)

    @staticmethod
    def new_key(
        options: str | list[str],
        func: ActionFunc[T],
        escape: bool = True,
        **kwargs: Any,
    ) -> Action[T]:
        if isinstance(options, str):
            options = [options]

        options_ls = [core.localize(opt, escape, **kwargs) for opt in options]

        return Action[T].new_raw(options_ls, func)

    def run(self, index: int) -> T:
        return self.func(index)


class Actions[T]:
    def __init__(self, actions: list[Action[T]]):
        self.actions = actions

    @staticmethod
    def new() -> Actions[T]:
        return Actions([])

    def add(self, action: Action[T]) -> Actions[T]:
        self.actions.append(action)

        return self

    def add_new_raw(self, options: str | list[str], func: ActionFunc[T]) -> Actions[T]:
        return self.add(Action[T].new_raw(options, func))

    def add_new_key(
        self,
        options: str | list[str],
        func: ActionFunc[T],
        escape: bool = True,
        **kwargs: Any,
    ) -> Actions[T]:
        return self.add(Action[T].new_key(options, func, escape, **kwargs))

    def get(self, index: int) -> Action[T] | None:
        current = 0
        for action in self.actions:
            if current >= index:
                return action
            current += action.len()
        return None

    def get_rebase(self, index: int) -> tuple[Action[T], int] | None:
        current = 0
        for action in self.actions:
            if index < current + action.len():
                return action, index - current
            current += action.len()
        return None

    def max(self) -> int:
        current = 0
        for action in self.actions:
            current += action.len()
        return current

    def run(self, index: int) -> T:
        action = self.get(index)
        if action is None:
            raise NoAssignedActionException(index)

        return action.run(index)

    def to_string(self) -> str:
        lines: list[str] = []

        i = 1
        for action in self.actions:
            for opt in action.options:
                lines.append(f" {i}. <@t>{opt}</>")
                i += 1

        return "\n".join(lines)

    def display(self):
        color.ColoredText(self.to_string())


def display_options_key(
    options: list[str], dialog: str, escape: bool = True, **kwargs: Any
):
    display_options_raw(options, core.localize(dialog, escape, **kwargs))


def display_options_raw(options: list[str], dialog: str):
    lines: list[str] = []

    for i, opt in enumerate(options):
        lines.append(f" {i + 1}. <@t>{opt}</>")

    color.ColoredText("\n".join(lines))
    color.ColoredText(dialog)


def yes_no_raw(dialog: str) -> bool | None:
    inp = str_input_raw(dialog)
    if inp is None:
        return None
    return inp.lower().strip() == core.localize("yes_key").strip().lower()


def range_multi_input_key(
    dialog: str, max: MaxValue | int, min: int = 0, escape: bool = True, **kwargs: Any
) -> list[int] | None:
    return range_multi_input_raw(core.localize(dialog, escape, **kwargs), max, min)


def range_basic_parse(
    usr_input: str, max: MaxValue | int, min: int = 0
) -> list[int] | None:
    if isinstance(max, int):
        max = MaxValue.specific(max)
    nums: list[int] = []
    for part in usr_input.split(" "):
        if part.isdigit():
            int_i = int(part)
            if int_i > max.max or int_i < min:
                color.ColoredText.localize("invalid_input_int", min=min, max=max.max)
                return None
            nums.append(int(part))
        elif "," in part:
            min_v, max_v = part.split(",", 1)
            if not min_v.isdigit() or not max_v.isdigit():
                return None
            min_i = int(min_v)
            max_i = int(max_v)
            if max_i < min_i:
                return None
            if max_i > max.max or min_i < min:
                return None

            nums.extend(list(range(min_i, max_i + 1)))
        else:
            return None

    return nums


def range_multi_input_raw(
    dialog: str, max: MaxValue | int, min: int = 0
) -> list[int] | None:
    if isinstance(max, int):
        max = MaxValue.specific(max)
    usr_input = color.ColoredInput().get(dialog)
    if usr_input == core.localize("quit_key"):
        return None

    nums: list[int] = []
    for part in usr_input.split(" "):
        if part.isdigit():
            int_i = int(part)
            if int_i > max.max or int_i < min:
                color.ColoredText.localize("invalid_input_int", min=min, max=max.max)
                continue
            nums.append(int(part))
        elif "," in part:
            min_v, max_v = part.split(",", 1)
            if not min_v.isdigit() or not max_v.isdigit():
                color.ColoredText.localize("invalid_range", val=part)
                continue
            min_i = int(min_v)
            max_i = int(max_v)
            if max_i < min_i:
                color.ColoredText.localize("invalid_range", val=part)
                continue
            if max_i > max.max or min_i < min:
                color.ColoredText.localize("invalid_input_int", min=min, max=max.max)
                continue

            nums.extend(list(range(min_i, max_i + 1)))
        else:
            color.ColoredText.localize("invalid_range", val=part)

    return nums


def yes_no_key(dialog: str, escape: bool = False, **kwargs: Any) -> bool | None:
    return yes_no_raw(core.localize(dialog, escape, **kwargs))


def multi_select_raw(options: list[str], dialog: str) -> list[str] | None:
    out = multi_select_entries_raw(options, dialog)
    if out is None:
        return None
    return [v[1] for v in out]


def multi_select_indexes_raw(options: list[str], dialog: str) -> list[int] | None:
    out = multi_select_entries_raw(options, dialog)
    if out is None:
        return None
    return [v[0] for v in out]


def multi_select_key(
    options: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> list[str] | None:
    return multi_select_raw(options, core.localize(dialog, escape, **kwargs))


def multi_select_indexes_key(
    options: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> list[int] | None:
    return multi_select_indexes_raw(options, core.localize(dialog, escape, **kwargs))


def multi_select_entries_key(
    options: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> list[tuple[int, str]] | None:
    return multi_select_entries_raw(options, core.localize(dialog, escape, **kwargs))


def multi_select_entries_raw(
    options: list[str], dialog: str
) -> list[tuple[int, str]] | None:
    offset = 1

    actions = (
        Actions[list[tuple[int, str]]]
        .new()
        .add_new_raw(options, lambda v: [(v, options[v])])
        .add_new_key("all", lambda _: list(enumerate(options)))
    )

    ids: list[tuple[int, str]] = []

    quit_key = core.localize("quit_key")

    while True:
        actions.display()
        inp = color.ColoredInput("").get(dialog)
        if inp == quit_key:
            return None

        inps = inp.split(" ")

        for inp in inps:
            if not inp.isdigit():
                color.ColoredText.localize(
                    "invalid_input_int", min=min, max=actions.max()
                )
                continue

            inp_i = int(inp)
            inp_i -= offset
            if inp_i < 0:
                color.ColoredText.localize(
                    "invalid_input_int", min=min, max=actions.max()
                )
                break

            action = actions.get_rebase(inp_i)
            if action is None:
                color.ColoredText.localize(
                    "invalid_input_int", min=min, max=actions.max()
                )
                break

            ids.extend(action[0].run(action[1]))
        else:
            return ids


def single_select_raw(actions: Actions[T], dialog: str) -> T | None:
    offset = 1

    min = offset

    quit_key = core.localize("quit_key")

    while True:
        actions.display()
        inp = color.ColoredInput("").get(dialog)
        if inp == quit_key:
            return None
        if not inp.isdigit():
            for act in actions.actions:
                for i, o in enumerate(act.options):
                    if o.lower().strip() == inp.lower().strip():
                        return act.run(i)
            color.ColoredText.localize("invalid_input_int", min=min, max=actions.max())
            continue

        inp_i = int(inp)
        inp_i -= offset
        if inp_i < 0:
            color.ColoredText.localize("invalid_input_int", min=min, max=actions.max())
            continue

        action = actions.get_rebase(inp_i)
        if action is None:
            color.ColoredText.localize("invalid_input_int", min=min, max=actions.max())
            continue

        return action[0].run(action[1])


def single_select_key(
    actions: Actions[T],
    dialog_key: str,
    escape: bool = True,
    **kwargs: Any,
) -> T | None:
    return single_select_raw(actions, core.localize(dialog_key, escape, **kwargs))


def basic_pick_raw_entry(items: list[str], dialog: str) -> tuple[int, str] | None:
    return single_select_raw(
        Actions[tuple[int, str]].new().add_new_raw(items, lambda v: (v, items[v])),
        dialog,
    )


def basic_pick_raw_index(items: list[str], dialog: str) -> int | None:
    return single_select_raw(
        Actions[int].new().add_new_raw(items, lambda v: v),
        dialog,
    )


def basic_pick_raw(items: list[str], dialog: str) -> str | None:
    return single_select_raw(
        Actions[str].new().add_new_raw(items, lambda v: items[v]),
        dialog,
    )


def basic_pick_key_entry(
    items: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> tuple[int, str] | None:
    return basic_pick_raw_entry(items, core.localize(dialog, escape, **kwargs))


def basic_pick_key_index(
    items: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> int | None:
    return basic_pick_raw_index(items, core.localize(dialog, escape, **kwargs))


def basic_pick_key(
    items: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> str | None:
    return basic_pick_raw(items, core.localize(dialog, escape, **kwargs))


class MaxValue:
    def __init__(self, max: int, show: bool = True):
        self.max = max
        self.show = show

    def hide_max(self) -> MaxValue:
        self.show = False
        return self

    @staticmethod
    def specific(max: int) -> MaxValue:
        return MaxValue(max)

    @staticmethod
    def none(bits: int) -> MaxValue:
        return MaxValue((2**bits) - 1)

    @staticmethod
    def i32() -> MaxValue:
        return MaxValue.none(31)

    @staticmethod
    def u32() -> MaxValue:
        return MaxValue.none(32)

    @staticmethod
    def i16() -> MaxValue:
        return MaxValue.none(15)

    @staticmethod
    def u16() -> MaxValue:
        return MaxValue.none(16)

    def clamp(self, v: int) -> int:
        return min(self.max, v)


def edit_int_raw(item_name: str, current_value: int, max: MaxValue | int) -> int:
    if isinstance(max, int):
        max = MaxValue.specific(max)
    if max.show:
        key = "input"
    else:
        key = "input_no_max"

    dialog = core.localize(key, name=item_name, value=current_value, max=max.max)

    val = int_input_raw(dialog, max) or current_value
    color.ColoredText.localize("value_changed", name=item_name, value=val)
    return val


def edit_str_raw(item_name: str, current_value: str) -> str:
    dialog = core.localize("input_no_max", name=item_name, value=current_value)

    val = str_input_raw(dialog) or current_value
    color.ColoredText.localize("value_changed", name=item_name, value=val)
    return val


def int_input_key(
    dialog: str,
    _max: MaxValue | int,
    min: int = 0,
    default: int | None = None,
    escape: bool = True,
    **kwargs: Any,
) -> int | None:
    return int_input_raw(core.localize(dialog, escape, **kwargs), _max, min, default)


def str_input_key(dialog: str, escape: bool = True, **kwargs: Any) -> str | None:
    return str_input_raw(core.localize(dialog, escape, **kwargs))


def int_input_raw(
    dialog: str, max: MaxValue | int, min: int = 0, default: int | None = None
) -> int | None:
    if isinstance(max, int):
        max = MaxValue.specific(max)
    quit_key = core.localize("quit_key")
    while True:
        inp = color.ColoredInput("").get(dialog)
        if not inp and default is not None:
            return default
        if inp == quit_key:
            return None
        try:
            inp_i = int(inp)
        except ValueError:
            color.ColoredText.localize("invalid_input_int", max=max.max, min=min)
            continue

        if inp_i < min or inp_i > max.max:
            color.ColoredText.localize("invalid_input_int", max=max.max, min=min)
            continue

        return inp_i


def str_input_raw(dialog: str) -> str | None:
    quit_key = core.localize("quit_key")
    inp = color.ColoredInput("").get(dialog)
    if inp == quit_key:
        return None
    if inp == f"\\{quit_key}":
        inp = quit_key
    return inp


def edit_int_key(
    item_key: str,
    current_value: int,
    max: MaxValue | int,
    escape: bool = True,
    **kwargs: Any,
) -> int:
    return edit_int_raw(core.localize(item_key, escape, **kwargs), current_value, max)


def edit_str_key(
    item_key: str,
    current_value: str,
    escape: bool = True,
    **kwargs: Any,
) -> str:
    return edit_str_raw(core.localize(item_key, escape, **kwargs), current_value)


class CumulativeMax:
    def __init__(self, max: MaxValue):
        self.max = max

    @staticmethod
    def specific(max: int) -> CumulativeMax:
        return CumulativeMax(MaxValue.specific(max))

    @staticmethod
    def new(max: int | MaxValue):
        if isinstance(max, int):
            return CumulativeMax.specific(max)
        return CumulativeMax(max)


class MultiMax:
    def __init__(self, maxes: list[MaxValue]):
        self.maxes = maxes

    @staticmethod
    def new(maxes: Sequence[MaxValue | int]) -> MultiMax:
        new: list[MaxValue] = []

        for m in maxes:
            if isinstance(m, int):
                new.append(MaxValue.specific(m))
            else:
                new.append(m)

        return MultiMax(new)


def edit_ints_key(
    group_name: str,
    item_names: list[str],
    current_values: list[int],
    max: MultiMax | CumulativeMax | MaxValue | int,
    escape: bool = True,
    **kwargs: Any,
) -> list[int]:
    return edit_ints_raw(
        core.localize(group_name, escape, **kwargs), item_names, current_values, max
    )


def edit_ints_raw(
    group_name: str,
    item_names: list[str],
    current_values: list[int],
    max: MultiMax | CumulativeMax | MaxValue | int,
) -> list[int]:
    entries = multi_select_entries_key(
        [
            core.localize("value", name=name, value=value)
            for name, value in zip(item_names, current_values)
        ],
        "input_many",
        min=1,
        max=len(item_names) + 1,
    )

    if not entries:
        return current_values

    individual = len(entries) == 1

    if isinstance(max, (MultiMax, CumulativeMax)):
        raise NotImplementedError()

    if individual:
        for id, name in entries:
            new_val = edit_int_raw(name, current_values[id], max)
            current_values[id] = new_val
    else:
        val = int_input_key("input_generic", max, name=group_name)
        if val is None:
            return current_values

        for id, name in entries:
            current_values[id] = val
            color.ColoredText.localize("value_changed", name=name, value=val)

    return current_values
