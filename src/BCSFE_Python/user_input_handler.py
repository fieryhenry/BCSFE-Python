"""Handler for user input"""

from typing import Tuple, Union

from . import helper


def handle_all_at_once(
    ids: list,
    all_at_once: bool,
    data: list,
    names: list,
    item_name: str,
    group_name: str,
    explain_text: str = "",
) -> list:
    """Handle all at once option"""

    first = True
    value = 0
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
    ids: list, max_val: int, include_all_at_once: bool = False
) -> Union[dict, list]:
    """Creates a list with an all at once option"""

    all_at_once = False
    if f"{max_val}" in ids:
        ids = range(1, max_val)
        ids = [format(x, "02d") for x in ids]
        all_at_once = True
    if include_all_at_once:
        return {"ids": ids, "at_once": all_at_once}
    return ids


def get_range(
    usr_input: str, length: int = None, min_val: int = 0, all_ids: list = None,
) -> list:
    """Get a range of numbers from user input"""

    ids = []
    if usr_input.lower() == "all":
        if length is None and all_ids is None:
            helper.colored_text("You can't use &all& here", helper.RED)
            return []
        if all_ids:
            return all_ids
        return range(min_val, length)
    if "-" in usr_input:
        start, end = usr_input.split("-")
        start = helper.check_int(start)
        end = helper.check_int(end)
        if start is None or end is None:
            helper.colored_text(
                "Invalid input. Please enter a valid range of numbers separated by a dash.",
                helper.RED,
            )
            return ids
        if start > end:
            start, end = end, start
        ids = range(start, end + 1)
    else:
        content = usr_input.split(" ")
        for item_id in content:
            item_id = helper.check_int(item_id)
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
    options: list,
    mode: str = "edit",
    extra_data: list = None,
    include: bool = False,
    offset: int = 0,
) -> Union[Tuple[list, bool], list]:
    """Select an option or multiple options from a list"""

    helper.colored_list(options, extra_data=extra_data, offset=offset)
    total = len(options)
    helper.colored_text(f"{total+1}. &Select all&")
    ids = colored_input(
        f"What do you want to {mode} (You can enter multiple values separated by spaces to {mode} multiple at once):"
    ).split(" ")
    individual = True
    if str(total + 1) in ids:
        ids = range(1, total + 1)
        individual = False
        ids = helper.int_to_str_ls(ids)
    ids = helper.parse_int_list(ids, -1)
    if include:
        return ids, individual
    return ids


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
