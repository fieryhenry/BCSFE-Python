from __future__ import annotations
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from bcsfe import core
from bcsfe.cli import color

T = TypeVar("T")

ActionFunc = Callable[[int], T]


class NoAssignedActionException(Exception):
    def __init__(self, index: int):
        super().__init__(f"No assigned action to index {index}")


class Action(Generic[T]):
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


class Actions(Generic[T]):
    def __init__(self, actions: list[Action[T]]):
        self.actions = actions

    def len(self) -> int:
        return len(self.actions)

    def is_empty(self) -> bool:
        return self.len() == 0

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
        color.color_print(self.to_string())


def display_options_key(
    options: list[str], dialog: str, escape: bool = True, **kwargs: Any
):
    display_options_raw(options, core.localize(dialog, escape, **kwargs))


def display_options_raw(options: list[str], dialog: str):
    lines: list[str] = []

    color.color_print(dialog)
    for i, opt in enumerate(options):
        lines.append(f" {i + 1}. <@t>{opt}</>")

    color.color_print("\n".join(lines))


def yes_no_raw(dialog: str) -> bool | None:
    inp = str_input_raw(dialog)
    if inp is None:
        return None
    return inp.lower().strip() == core.localize("yes_key").strip().lower()


def range_multi_input_key(
    dialog: str, max: MaxValue, min: int = 0, escape: bool = True, **kwargs: Any
) -> list[int] | None:
    return range_multi_input_raw(core.localize(dialog, escape, **kwargs), max, min)


def range_basic_parse(usr_input: str, max: MaxValue, min: int = 0) -> list[int] | None:
    nums: list[int] = []
    for part in usr_input.split(" "):
        if part.isdigit():
            int_i = int(part)
            if int_i > max.max or int_i < min:
                color.color_print_key("invalid_input_int", min=min, max=max.max)
                return None
            nums.append(int(part))
        elif "-" in part:
            min_v, max_v = part.split("-", 1)
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


def range_multi_input_raw(dialog: str, max: MaxValue, min: int = 0) -> list[int] | None:
    usr_input = color.color_input(dialog)
    if usr_input == core.localize("quit_key"):
        return None

    nums: list[int] = []
    for part in usr_input.split(" "):
        if part.isdigit():
            int_i = int(part)
            if int_i > max.max or int_i < min:
                color.color_print_key("invalid_input_int", min=min, max=max.max)
                continue
            nums.append(int(part))
        elif "-" in part:
            min_v, max_v = part.split("-", 1)
            if not min_v.isdigit() or not max_v.isdigit():
                color.color_print_key("invalid_range", val=part)
                continue
            min_i = int(min_v)
            max_i = int(max_v)
            if max_i < min_i:
                color.color_print_key("invalid_range", val=part)
                continue
            if max_i > max.max or min_i < min:
                color.color_print_key("invalid_input_int", min=min, max=max.max)
                continue

            nums.extend(list(range(min_i, max_i + 1)))
        else:
            color.color_print_key("invalid_range", val=part)

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
    if not options:
        return None
    if len(options) == 1:
        return [(0, options[0])]

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
        inp = color.color_input(dialog)
        if inp == quit_key:
            return None

        inps = inp.split(" ")

        for inp in inps:
            if not inp.isdigit():
                color.color_print_key("invalid_input_int", min=min, max=actions.max())
                continue

            inp_i = int(inp)
            inp_i -= offset
            if inp_i < 0:
                color.color_print_key("invalid_input_int", min=min, max=actions.max())
                break

            action = actions.get_rebase(inp_i)
            if action is None:
                color.color_print_key("invalid_input_int", min=min, max=actions.max())
                break

            ids.extend(action[0].run(action[1]))
        else:
            return ids


def single_select_raw(actions: Actions[T], dialog: str) -> T | None:
    if actions.max() == 0:
        return None
    if actions.len() == 1 and actions.actions[0].len() == 1:
        return actions.actions[0].run(0)
    offset = 1

    min = offset

    quit_key = core.localize("quit_key")

    while True:
        actions.display()
        inp = color.color_input(dialog)
        if inp == quit_key:
            return None
        if not inp.isdigit():
            for act in actions.actions:
                for i, o in enumerate(act.options):
                    if o.lower().strip() == inp.lower().strip():
                        return act.run(i)
            color.color_print_key("invalid_input_int", min=min, max=actions.max())
            continue

        inp_i = int(inp)
        inp_i -= offset
        if inp_i < 0:
            color.color_print_key("invalid_input_int", min=min, max=actions.max())
            continue

        action = actions.get_rebase(inp_i)
        if action is None:
            color.color_print_key("invalid_input_int", min=min, max=actions.max())
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


def basic_keys_pick_key(
    keys: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> str | None:
    return basic_pick_key(
        [core.localize(key) for key in keys], dialog, escape, **kwargs
    )


def basic_keys_pick_key_index(
    keys: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> int | None:
    return basic_pick_key_index(
        [core.localize(key) for key in keys], dialog, escape, **kwargs
    )


def basic_keys_pick_key_entry(
    keys: list[str], dialog: str, escape: bool = True, **kwargs: Any
) -> tuple[int, str] | None:
    return basic_pick_key_entry(
        [core.localize(key) for key in keys], dialog, escape, **kwargs
    )


class MaxValue:
    def __init__(self, max: int, bits: int, show: bool = True):
        self.max = max
        self.show = show
        self.bits = bits

    def hide_max(self) -> MaxValue:
        self.show = False
        return self

    @staticmethod
    def always_cap(max: int) -> MaxValue:
        return MaxValue(max, 32)

    @staticmethod
    def specific(max: int, bits: int) -> MaxValue:
        if core.core_data.config.get_bool(core.ConfigKey.DISABLE_MAXES):
            return MaxValue.none(bits).hide_max()
        return MaxValue(max, bits)

    @staticmethod
    def none(bits: int) -> MaxValue:
        return MaxValue((2**bits) - 1, bits)

    @staticmethod
    def new_bits(max: int | None, bits: int) -> MaxValue:
        if max is None:
            return MaxValue.none(bits)
        return MaxValue.specific(max, bits)

    @staticmethod
    def i32(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 31)

    @staticmethod
    def u32(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 32)

    @staticmethod
    def i16(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 15)

    @staticmethod
    def u16(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 16)

    @staticmethod
    def i8(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 7)

    @staticmethod
    def u8(max: int | None = None) -> MaxValue:
        return MaxValue.new_bits(max, 8)

    def clamp(self, v: int) -> int:
        return min(self.max, v)


def edit_int_raw(item_name: str, current_value: int, max: MaxValue) -> int:
    if max.show:
        key = "input"
    else:
        key = "input_no_max"

    dialog = core.localize(
        key, name=item_name, value=current_value, max=max.max, escape=False
    )

    val = int_input_raw(dialog, max, auto_clamp=True)
    if val is None:
        val = current_value
    color.color_print_key("value_changed", name=item_name, value=val, escape=False)
    return val


def edit_str_raw(item_name: str, current_value: str) -> str:
    dialog = core.localize("input_no_max", name=item_name, value=current_value)

    val = str_input_raw(dialog) or current_value
    color.color_print_key("value_changed", name=item_name, value=val)
    return val


def int_input_key(
    dialog: str,
    _max: MaxValue,
    min: int = 0,
    default: int | None = None,
    auto_clamp: bool = False,
    escape: bool = True,
    **kwargs: Any,
) -> int | None:
    return int_input_raw(
        core.localize(dialog, escape, **kwargs), _max, min, default, auto_clamp
    )


def str_input_key(dialog: str, escape: bool = True, **kwargs: Any) -> str | None:
    return str_input_raw(core.localize(dialog, escape, **kwargs))


def int_input_raw(
    dialog: str,
    _max: MaxValue,
    _min: int = 0,
    default: int | None = None,
    auto_clamp: bool = False,
) -> int | None:
    quit_key = core.localize("quit_key")
    while True:
        inp = color.color_input(dialog)
        if not inp and default is not None:
            return default
        if inp == quit_key:
            return None
        try:
            inp_i = int(inp)
        except ValueError:
            color.color_print_key("invalid_input_int", max=_max.max, min=_min)
            continue

        if inp_i < _min or inp_i > _max.max:
            if auto_clamp:
                inp_i = min(max(_min, inp_i), _max.max)
            else:
                color.color_print_key("invalid_input_int", max=_max.max, min=_min)
                continue

        return inp_i


def str_input_raw(dialog: str) -> str | None:
    quit_key = core.localize("quit_key")
    inp = color.color_input(dialog)
    if inp == quit_key:
        return None
    if inp == f"\\{quit_key}":
        inp = quit_key
    return inp


def edit_int_key(
    item_key: str,
    current_value: int,
    max: MaxValue,
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
    def specific(max: int, bits: int) -> CumulativeMax:
        return CumulativeMax(MaxValue.specific(max, bits))

    @staticmethod
    def new(max: MaxValue):
        return CumulativeMax(max)

    def get(self, current_values: list[int], ids: list[int] | int) -> MaxValue:
        if isinstance(ids, int):
            ids = [ids]

        v = 0
        for id in ids:
            v += current_values[id]

        return MaxValue.specific(self.max.max - sum(current_values) + v, self.max.bits)


class MultiMax:
    def __init__(self, maxes: list[MaxValue]):
        self.maxes = maxes

    @staticmethod
    def new(maxes: list[MaxValue]) -> MultiMax:
        return MultiMax(maxes)

    def get(self, id: int) -> MaxValue | None:
        if id < 0 or id >= len(self.maxes):
            return None
        return self.maxes[id]

    def maximal(self, ids: list[int]) -> MaxValue:
        m = MaxValue.specific(0, 0)
        for id in ids:
            m_v = self.get(id)
            if m_v is None:
                continue
            if m_v.max > m.max:
                m = m_v

        return m


def edit_ints_key(
    group_name: str,
    item_names: list[str],
    current_values: list[int],
    max: MultiMax | CumulativeMax | MaxValue,
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
    max: MultiMax | CumulativeMax | MaxValue,
) -> list[int]:
    entries = multi_select_indexes_key(
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

    if len(entries) == 1:
        edit_individual(current_values, max, entries, item_names)
        return current_values

    single_select_key(
        Actions[None]
        .new()
        .add_new_key(
            "individually",
            lambda _: edit_individual(current_values, max, entries, item_names),
        )
        .add_new_key(
            "edit_all_at_once",
            lambda _: edit_many(current_values, max, entries, group_name, item_names),
        ),
        "individual_or_all_at_once",
        group=group_name,
    )

    return current_values


def edit_individual(
    current_values: list[int],
    max: MaxValue | MultiMax | CumulativeMax,
    entries: list[int],
    names: list[str],
):
    entries_c = entries.copy()
    for id in entries:
        if isinstance(max, MultiMax):
            _max = max.get(id)
            if _max is None:
                return
        elif isinstance(max, CumulativeMax):
            _max = max.get(current_values, entries_c)
        else:
            _max = max
        new_val = edit_int_raw(names[id], current_values[id], _max)
        current_values[id] = new_val
        entries_c.pop(0)


def edit_many(
    current_values: list[int],
    max: MaxValue | MultiMax | CumulativeMax,
    entries: list[int],
    group_name: str,
    names: list[str],
):
    if isinstance(max, MultiMax):
        _max = max.maximal(entries)
    elif isinstance(max, CumulativeMax):
        _max = MaxValue.specific(
            max.get(current_values, entries).max // len(entries), max.max.bits
        )
    else:
        _max = max
    val = int_input_key(
        "input_generic", _max, name=group_name, auto_clamp=True, max=_max.max
    )
    if val is None:
        return

    for id in entries:
        if isinstance(max, MultiMax):
            maxm = max.get(id)
            if maxm is None:
                continue
            _max = maxm
        val_ = _max.clamp(val)
        current_values[id] = val_
        color.color_print_key("value_changed", name=names[id], value=val_, escape=False)
