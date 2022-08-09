"""Handler for user input"""

from typing import Any, Tuple, Union

from . import helper


def handle_all_at_once(
    ids: list[int],
    all_at_once: bool,
    data: list[int],
    names: list[Any],
    item_name: str,
    group_name: str,
    explain_text: str = "",
) -> list[int]:
    """Handle all at once option"""

    first = True
    value = None
    for item_id in ids:
        if all_at_once and first:
            value = helper.check_int(
                colored_input(f"Enter {item_name} {explain_text}:")
            )
            first = False
        elif not all_at_once:
            value = helper.check_int(
                colored_input(
                    f"Enter {item_name} for {group_name} &{names[item_id]}& {explain_text}:"
                )
            )
        if value is None:
            continue
        data[item_id] = value
    return data


def create_all_list(
    ids: list[str],
    max_val: int,
) -> dict[str, Any]:
    """Creates a list with an all at once option"""

    all_at_once = False
    if f"{max_val}" in ids:
        ids_s = list(range(1, max_val))
        ids = [format(x, "02d") for x in ids_s]
        all_at_once = True
    return {"ids": ids, "at_once": all_at_once}


def create_all_list_inc(ids: list[str], max_val: int) -> dict[str, Any]:
    """Creates a list with an all at once option and include all"""

    return create_all_list(ids, max_val)


def create_all_list_not_inc(ids: list[str], max_val: int) -> list[str]:
    """Creates a list with an all at once option and don't include all"""

    return create_all_list(ids, max_val)["ids"]


def get_range(
    usr_input: str,
    length: Union[int, None] = None,
    min_val: int = 0,
    all_ids: Union[list[int], None] = None,
) -> list[int]:
    """Get a range of numbers from user input"""

    ids: list[int] = []
    for item in usr_input.split(" "):
        if item.lower() == "all":
            if length is None and all_ids is None:
                helper.colored_text("You can't use &all& here", helper.RED)
                return []
            if all_ids:
                return all_ids
            if length is not None:
                return list(range(min_val, length))
        if "-" in item:
            start_s, end_s = item.split("-")
            start = helper.check_int(start_s)
            end = helper.check_int(end_s)
            if start is None or end is None:
                helper.colored_text(
                    "Invalid input. Please enter a valid range of numbers separated by a dash.",
                    helper.RED,
                )
                return ids
            if start > end:
                start, end = end, start
            ids.extend(list(range(start, end + 1)))
        else:
            item_id = helper.check_int(item)
            if item_id is None:
                helper.colored_text(
                    "Invalid input. Please enter a valid integer.", helper.RED
                )
                return ids
            ids.append(item_id)
    return ids


def colored_input(dialog: str) -> str:
    """Format dialog as a colored string"""

    helper.colored_text(dialog, end="")
    return input()


def get_range_ids(group_name: str, length: int) -> list[int]:
    """Get a range of ids from user input"""

    ids = get_range(
        colored_input(
            f"Enter {group_name} ids(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        length,
    )
    return ids


def select_options(
    options: list[str],
    mode: str = "edit",
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> Tuple[list[int], bool]:
    """Select an option or multiple options from a list"""

    helper.colored_list(options, extra_data=extra_data, offset=offset)
    total = len(options)
    helper.colored_text(f"{total+1}. &Select all&")
    ids_s = colored_input(
        f"What do you want to {mode} (You can enter multiple values separated by spaces to {mode} multiple at once):"
    ).split(" ")
    individual = True
    if str(total + 1) in ids_s:
        ids = list(range(1, total + 1))
        individual = False
        ids_s = helper.int_to_str_ls(ids)

    ids = helper.parse_int_list(ids_s, -1)
    return ids, individual


def select_inc(
    options: list[str],
    mode: str = "edit",
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> Tuple[list[int], bool]:
    """Select an option or multiple options from a list and include all"""

    return select_options(options, mode, extra_data, offset)


def select_not_inc(
    options: list[str],
    mode: str = "edit",
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> list[int]:
    """Select an option or multiple options from a list and don't include all"""
    return select_options(options, mode, extra_data, offset)[0]


def select_single(
    options: list[str],
    mode: str = "edit",
) -> int:
    "Select a single option from a list"

    helper.colored_list(options)
    return get_int(f"What do you want to {mode}:")


def get_int(dialog: str) -> int:
    """Get user input as an integer and keep asking until a valid integer is entered"""

    helper.colored_text(dialog, end="")
    while True:
        try:
            val = input()
            val = val.strip(" ")
            return int(val)
        except ValueError:
            helper.colored_text(
                "Invalid input. Please enter a valid integer.", helper.RED
            )


def ask_if_individual(item_name: str) -> bool:
    """Ask if the user wants to edit an individual item"""

    is_individual = (
        colored_input(
            f"Do you want to edit {item_name} individually (&1&), or all at once (&2&):"
        )
        == "1"
    )
    return is_individual
