"""Helper script for usefull functions"""

import json
import os
import sys
from tkinter import Tk, filedialog
from typing import Union

import colored

from . import parse_save, patcher, serialise_save, user_input_handler

root = Tk()
root.withdraw()

GREEN = "#008000"
RED = "#FF0000"
DARK_YELLOW = "#D7C32A"
BLACK = "#000000"
WHITE = "#FFFFFF"
CYAN = "#00FFFF"


def str_to_gv(game_version: str) -> str:
    """Turn a game version with semantic versioning to integer representation"""

    split_gv = game_version.split(".")
    if len(split_gv) == 2:
        split_gv.append("0")
    final = ""
    for split in split_gv:
        final += split.zfill(2)
    return final


def gv_to_str(game_version: int) -> str:
    """Turn a game version integer into a string"""

    return f"{game_version[0:2]}.{game_version[2:4]}.{game_version[4:6]}"


def check_clamp(
    values: list, max_value: int, min_value: int = 0, offset: int = -1
) -> list:
    """# turn a list of strings into a list of ints and clamp them between a min and max"""

    if isinstance(values, str):
        values = [values]
    int_values = []
    for value in values:
        value = str(value).strip(" ")
        value = check_int(value)
        if value is None:
            continue
        value = clamp(value, min_value, max_value)
        value += offset
        int_values.append(value)
    return int_values


def num_to_bytes(num: int, length: int) -> bytes:
    """Turn number into little endian bytes"""

    return num.to_bytes(length, byteorder="little")


def load_json_handler(json_path: str) -> Union[None, str]:
    """Load a save_data json file and serialise it"""

    save_stats = load_json(json_path)
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    path = save_file(
        "Save file",
        get_save_file_filetype(),
        os.path.join(os.path.dirname(json_path), "SAVE_DATA"),
    )
    if not path:
        return None
    write_file_bytes(path, save_data)
    return path


def load_json(json_path: str) -> dict:
    """Load a json file"""

    return json.loads(read_file_string(json_path))

def check_cat_ids(cat_ids: list, save_stats: dict) -> list:
    """Check if a list of cat ids is valid"""

    for cat_id in cat_ids:
        if cat_id > len(save_stats["cats"]):
            print(
                colored_text(
                    f"Invalid cat id {cat_id}", base=RED
                )
            )
            cat_ids.remove(cat_id)
    return cat_ids


def check_int(value: str) -> Union[int, None]:
    """Check if a string is an integer"""

    value = str(value).strip(" ")
    try:
        return int(value)
    except ValueError:
        return None


def set_range(
    list_original: Union[bytes, list], values: list, start_point: int
) -> bytes:
    """Set a range of values in a list"""

    list_original = list(list_original)
    list_original[start_point : start_point + len(values)] = values
    return bytes(list_original)


def frames_to_time(frames: int) -> dict:
    """Turn frames into hours, minutes, seconds, frames"""

    seconds, frames = divmod(frames, 30)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return {"hh": hours, "mm": minutes, "ss": seconds, "frames": frames}


def seconds_to_time(seconds: int) -> dict:
    """Turn seconds into hours, minutes, seconds"""

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return {"hh": hours, "mm": minutes, "ss": seconds}


def time_to_seconds(time: dict) -> int:
    """Turn hours, minutes, seconds into seconds"""
    seconds = time["ss"]
    seconds += time["mm"] * 60
    seconds += time["hh"] * 60 * 60
    return seconds


def time_to_frames(time: dict) -> int:
    """Turn hours, minutes, seconds, frames into frames"""

    total_frames = time["frames"]
    total_frames += time["ss"] * 30
    total_frames += time["mm"] * 60 * 30
    total_frames += time["hh"] * 60 * 60 * 30
    return total_frames


def chunks(lst: list, chunk_len: int) -> list:
    """Split list into chunks of n"""

    for i in range(0, len(lst), chunk_len):
        yield lst[i : i + chunk_len]


def read_file_bytes(file_path: str) -> bytes:
    """Read file as bytes"""

    with open(file_path, "rb") as file:
        return file.read()


def write_file_bytes(file_path: str, data: bytes) -> bytes:
    """Write file as bytes"""

    try:
        with open(file_path, "wb") as file:
            file.write(data)
    except PermissionError:
        print(colored_text("Permission denied. Make sure the file is not in use", base=RED))
        sys.exit(1)
    return data


def write_file_string(file_path: str, data: str):
    """Write file as string"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


def clamp(value: int, min_value: int, max_value: int) -> int:
    """Clamp a value between two values"""

    return max(min(value, max_value), min_value)


def get_country_code(save_data: dict) -> str:
    """Ask the user for their country code if it cannot be detected"""

    country_code = patcher.detect_game_version(save_data)
    if not country_code:
        country_code = user_input_handler.colored_input(
            "Enter your game version (&en&, &jp&, &kr&, &tw&):"
        )
    return country_code


def load_save_file(path: str) -> dict:
    """Load a save file, get the country code, create a backup and parse the save data"""

    save_data = read_file_bytes(path)
    country_code = get_country_code(save_data)
    colored_text(f"Game version: &{country_code}&")
    save_stats = parse_save.start_parse(save_data, country_code)
    write_file_bytes(path + "_backup", save_data)
    colored_text(f"Backup created at: &{os.path.abspath(path + '_backup')}&", new=GREEN)
    return {
        "save_data": save_data,
        "country_code": country_code,
        "save_stats": save_stats,
    }


def offset_list(lst: list, offset: int) -> list:
    """Offset each value in an list by a certain amount"""

    new_list = []
    for item in lst:
        new_list.append(item + offset)
    return new_list


def copy_first_n(lst: list, number: int) -> list:
    """Get the nth item in a list of lists"""

    new_list = []
    for item in lst:
        new_list.append(item[number])
    return new_list


def write_save_data(save_data: dict, country_code: str, path: str, prompt: bool):
    """Patch the save data and write it"""

    save_data = patcher.patch_save_data(save_data, country_code)
    if prompt:
        path = save_file("Save File", get_save_file_filetype(), path)
        if not path:
            colored_text("Save cancelled", new=RED)
            return
    write_file_bytes(path, save_data)
    colored_text(f"Saved to: &{os.path.abspath(path)}&", new=GREEN)
    return save_data


def save_file(title: str, file_types: list[tuple[str]], path: str) -> str:
    """Save a file with tkinter"""

    try:
        path = filedialog.asksaveasfile(
            "w",
            confirmoverwrite=True,
            initialfile=os.path.basename(path),
            filetypes=file_types,
            title=title,
        )
    except PermissionError:
        print(colored_text("Permission denied. Make sure the file is not in use", base=RED))
        sys.exit(1)
    if not path:
        return ""
    return path.name


def select_file(title: str, file_types: list[tuple[str]], default_dir: str = "") -> str:
    """Select a file with tkinter"""
    file_path = filedialog.askopenfilename(
        initialdir=default_dir, title=title, filetypes=file_types
    )
    return file_path


def get_save_file_filetype() -> list[tuple[str]]:
    """Get the file types for the save file"""

    return [("Battle Cats Save Files", "*SAVE_DATA*"), ("All Files", "*.*")]


def colored_list(
    items: list, extra_data: list = None, index: bool = True, offset: int = None
):
    """Print a list with colors and extra data if provided"""

    final = ""
    for i, item in enumerate(items):
        if index:
            final += f"{i+1}. "
        final += f"&{item}&"
        if extra_data:
            if extra_data[i] is not None:
                if isinstance(offset, int):
                    final += f" &:& {extra_data[i]+offset}"
                else:
                    final += f" &:& {extra_data[i]}"
        final += "\n"
    final = final.rstrip("\n")
    colored_text(final)


def int_to_str_ls(int_list: list) -> list:
    """Turn list of ints to list of strings"""

    str_list = []
    for i in int_list:
        str_list.append(str(i))
    return str_list


def get_file(file_name: str) -> str:
    """Get file in files folder"""

    file_path = os.path.join(get_local_files_path(), file_name)
    return file_path


def read_file_string(file_path: str) -> str:
    """Read file as string"""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except UnicodeDecodeError:
        colored_text("Error: make sure the file is in UTF-8 encoding", base=RED)
        sys.exit(1)

def get_local_files_path() -> str:
    """Get the local files path"""

    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
    return dir_path


def colored_text(
    text: str,
    base: str = WHITE,
    new: str = DARK_YELLOW,
    split_char: str = "&",
    end: str = "\n",
):
    """Print text with colors"""
    color_new = colored.fg(new)
    color_base = colored.fg(base)
    color_reset = colored.fg(WHITE)

    text_split = text.split(split_char)
    for i, text_section in enumerate(text_split):
        if i % 2:
            print(f"{color_new}{text_section}{color_base}", end="")
        else:
            print(f"{color_base}{text_section}{color_base}", end="")
    print(color_reset, end=end)


def remove_empty_items(list_of_lists: list[list]) -> list[list]:
    """Remove empty items from list of lists"""

    for i, lst in enumerate(list_of_lists):
        list_of_lists[i] = list(filter(None, lst))
    list_of_lists = remove_empty_lists(list_of_lists)
    return list_of_lists


def remove_empty_lists(list_of_lists: list[list]) -> list[list]:
    """Remove empty lists from list of lists"""

    new_lists = []
    for lst in list_of_lists:
        if lst:
            new_lists.append(lst)
    return new_lists


def parse_int_list_list(list_of_lists: list[list[str]]) -> list[list[int]]:
    """Turn list of list of strings into list of list of ints"""

    for i, lst in enumerate(list_of_lists):
        for j, item in enumerate(lst):
            try:
                list_of_lists[i][j] = int(item)
            except ValueError:
                continue
    return list_of_lists


def parse_int_list(lst: list, offset: int) -> list[int]:
    """Turn string list to int list"""

    new_list = []
    for item in lst:
        try:
            new_list.append(int(item) + offset)
        except ValueError:
            pass
    return new_list
