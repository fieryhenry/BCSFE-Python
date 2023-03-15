"""Handler for user input"""

from typing import Any, Optional, Tuple, Union

from . import helper, locale_handler


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
    locale_manager = locale_handler.LocalManager.from_config()
    first = True
    value = None
    for item_id in ids:
        if all_at_once and first:
            value = helper.check_int(
                colored_input(
                    locale_manager.search_key("enter_item_name_explain")
                    % (item_name, explain_text)
                )
            )
            first = False
        elif not all_at_once:
            value = helper.check_int(
                colored_input(
                    locale_manager.search_key("enter_item_name_group_explain")
                    % (item_name, group_name, names[item_id], explain_text)
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
    locale_manager = locale_handler.LocalManager.from_config()
    ids: list[int] = []
    for item in usr_input.split(" "):
        if item.lower() == locale_manager.search_key("all_text").lower():
            if length is None and all_ids is None:
                helper.colored_text(
                    locale_manager.search_key("invalid_all"), helper.RED
                )
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
                    locale_manager.search_key("invalid_range_format"),
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
                    locale_manager.search_key("invalid_int"), helper.RED
                )
                return ids
            ids.append(item_id)
    return ids


def colored_input(
    dialog: str, base: Optional[str] = None, new: Optional[str] = None
) -> str:
    """Format dialog as a colored string"""
    if base is None:
        base = helper.WHITE
    if new is None:
        new = helper.DARK_YELLOW
    helper.colored_text(dialog, end="", base=base, new=new)
    return input()


def get_range_ids(group_name: str, length: int) -> list[int]:
    """Get a range of ids from user input"""

    locale_manager = locale_handler.LocalManager.from_config()
    ids = get_range(
        colored_input(locale_manager.search_key("enter_range_text") % (group_name)),
        length,
    )
    return ids


def select_options(
    options: list[str],
    mode: Optional[str] = None,
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> Tuple[list[int], bool]:
    """Select an option or multiple options from a list"""

    if len(options) == 1:
        return [0], True

    locale_manager = locale_handler.LocalManager.from_config()
    if mode is None:
        mode = locale_manager.search_key("edit_text")

    helper.colored_list(options, extra_data=extra_data, offset=offset)
    total = len(options)
    helper.colored_text(f"{total+1}. {locale_manager.search_key('select_all')}")
    ids_s = colored_input(
        locale_manager.search_key("select_list") % (mode, mode)
    ).split(" ")
    individual = True
    if str(total + 1) in ids_s:
        ids = list(range(1, total + 1))
        individual = False
        ids_s = helper.int_to_str_ls(ids)

    ids = helper.parse_int_list(ids_s, -1)
    for item_id in ids:
        if item_id < 0 or item_id > total - 1:
            helper.colored_text(
                locale_manager.search_key("invalid_range") % (total + 1),
                helper.RED,
            )
            return select_options(options, mode, extra_data, offset)
    return ids, individual


def select_inc(
    options: list[str],
    mode: Optional[str] = None,
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> Tuple[list[int], bool]:
    """Select an option or multiple options from a list and include all"""

    return select_options(options, mode, extra_data, offset)


def select_not_inc(
    options: list[str],
    mode: Optional[str] = None,
    extra_data: Union[list[Any], None] = None,
    offset: int = 0,
) -> list[int]:
    """Select an option or multiple options from a list and don't include all"""
    return select_options(options, mode, extra_data, offset)[0]


def select_single(
    options: list[str],
    mode: Optional[str] = None,
    title: str = "",
    allow_text: bool = False,
) -> int:
    "Select a single option from a list"
    locale_manager = locale_handler.LocalManager.from_config()
    if not options:
        raise ValueError(locale_manager.search_key("error_no_options"))
    if len(options) == 1:
        return 1
    helper.colored_list(options)
    if not title:
        title = locale_manager.search_key("select_option_to") % (mode)
    val = colored_input(title)
    if allow_text:
        if val in options:
            return options.index(val) + 1
    val = helper.check_int(val)
    if val is None:
        helper.colored_text(locale_manager.search_key("invalid_int"), helper.RED)
        return select_single(options, mode, title, allow_text)
    if val < 1 or val > len(options):
        helper.colored_text(
            locale_manager.search_key("invalid_range") % (len(options)),
            helper.RED,
        )
        return select_single(options, mode, title, allow_text)
    return val


def get_int(dialog: str, default: Optional[int] = None) -> int:
    """Get user input as an integer and keep asking until a valid integer is entered"""

    helper.colored_text(dialog, end="")
    locale_manager = locale_handler.LocalManager.from_config()
    while True:
        try:
            val = input()
            val = val.strip(" ")
            return int(val)
        except ValueError:
            if default is not None:
                return default
            helper.colored_text(locale_manager.search_key("invalid_int"), helper.RED)


def ask_if_individual(item_name: str) -> bool:
    """Ask if the user wants to edit an individual item"""
    locale_manager = locale_handler.LocalManager.from_config()
    is_individual = (
        colored_input(
            locale_manager.search_key("ask_individual") % (item_name),
        )
        == "1"
    )
    return is_individual


def get_yes_no(dialog: str) -> bool:
    """Get user input as a yes or no"""
    locale_manager = locale_handler.LocalManager.from_config()
    while True:
        val = colored_input(dialog)
        if val:
            if val.lower()[0] == "y":
                return True
            if val.lower()[0] == "n":
                return False
        helper.colored_text(locale_manager.search_key("invalid_yes_no"), helper.RED)
