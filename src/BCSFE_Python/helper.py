"""Helper script for usefull functions"""

import json
import os
import shutil
import sys
from tkinter import Tk, filedialog
from typing import Any, Generator, Union
import colored  # type: ignore

from . import (
    user_input_handler,
    server_handler,
    patcher,
    serialise_save,
    parse_save,
    tracker,
    config_manager
)

GREEN = "#008000"
RED = "#FF0000"
DARK_YELLOW = "#D7C32A"
BLACK = "#000000"
WHITE = "#FFFFFF"
CYAN = "#00FFFF"

def print_line_seperator(base: str, char: str = "-", length: int = 80):
    """Print a line of a char"""
    width = shutil.get_terminal_size().columns
    if width < length:
        length = width
    colored_text(char * length, base)

def get_dirs(path: str) -> list[str]:
    """Get all directories in a path"""

    if not os.path.exists(path):
        return []

    return [dir for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir))]


def delete_dir(path: str) -> None:
    """Delete a directory and all of its contents"""

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(path)


def create_dirs(path: str) -> None:
    """Create directories if they don't exist"""

    if not os.path.exists(path):
        os.makedirs(path)


def offset_list(lst: list[int], offset: int) -> list[int]:
    """Offset each value in an list by a certain amount"""

    new_list: list[int] = []
    for item in lst:
        new_list.append(item + offset)
    return new_list


def copy_first_n(lst: list[Any], number: int) -> list[Any]:
    """Get the nth item in a list of lists"""

    new_list: list[Any] = []
    for item in lst:
        new_list.append(item[number])
    return new_list


def get_file(file_name: str) -> str:
    """Get file in files folder"""

    file_path = os.path.join(get_local_files_path(), file_name)
    return file_path


def get_local_files_path() -> str:
    """Get the local files path"""

    dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "files")
    return dir_path


def read_file_string(file_path: str) -> str:
    """Reads a file and returns its contents as a string"""

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as err:
        raise Exception("File not found: " + file_path) from err
    except UnicodeDecodeError as err:
        raise Exception("Error reading file: " + file_path + ": " + str(err)) from err


def chunks(lst: list[Any], chunk_len: int) -> Generator[Any, Any, Any]:
    """Split list into chunks of n"""

    for i in range(0, len(lst), chunk_len):
        yield lst[i : i + chunk_len]


def frames_to_time(frames: int) -> dict[str, Any]:
    """Turn frames into hours, minutes, seconds, frames"""

    seconds, frames = divmod(frames, 30)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return {"hh": hours, "mm": minutes, "ss": seconds, "frames": frames}


def num_to_bytes(num: int, length: int) -> bytes:
    """Turn number into little endian bytes"""

    return num.to_bytes(length, byteorder="little")


def seconds_to_time(seconds: int) -> dict[str, Any]:
    """Turn seconds into hours, minutes, seconds"""

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return {"hh": hours, "mm": minutes, "ss": seconds}


def time_to_seconds(time: dict[str, Any]) -> int:
    """Turn hours, minutes, seconds into seconds"""
    seconds = time["ss"]
    seconds += time["mm"] * 60
    seconds += time["hh"] * 60 * 60
    return seconds


def time_to_frames(time: dict[str, Any]) -> int:
    """Turn hours, minutes, seconds, frames into frames"""

    total_frames = time["frames"]
    total_frames += time["ss"] * 30
    total_frames += time["mm"] * 60 * 30
    total_frames += time["hh"] * 60 * 60 * 30
    return total_frames


def check_int(value: str) -> Union[int, None]:
    """Check if a string is an integer"""

    value = str(value).strip(" ")
    try:
        return int(value)
    except ValueError:
        return None


def int_to_str_ls(int_list: list[int]) -> list[str]:
    """Turn list of ints to list of strings"""

    str_list: list[str] = []
    for i in int_list:
        str_list.append(str(i))
    return str_list


def parse_int_list(lst: list[str], offset: int) -> list[int]:
    """Turn string list to int list"""

    new_list: list[int] = []
    for item in lst:
        try:
            new_list.append(int(item) + offset)
        except ValueError:
            pass
    return new_list


def clamp(value: int, min_value: int, max_value: int) -> int:
    """Clamp a value between two values"""

    return max(min(value, max_value), min_value)


def write_file_bytes(file_path: str, data: bytes) -> bytes:
    """Write file as bytes"""

    try:
        with open(file_path, "wb") as file:
            file.write(data)
    except PermissionError as err:
        raise Exception("Permission denied: " + file_path) from err
    return data


def get_save_file_filetype() -> list[tuple[str, str]]:
    """Get the file types for the save file"""

    return [("Battle Cats Save Files", "*SAVE_DATA*"), ("All Files", "*.*")]


def read_file_bytes(file_path: str) -> bytes:
    """Read file as bytes"""

    with open(file_path, "rb") as file:
        return file.read()


def write_file_string(file_path: str, data: str):
    """Write file as string"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


def check_clamp(
    values: Any, max_value: int, min_value: int = 0, offset: int = -1
) -> list[int]:
    """turn a list of strings into a list of ints and clamp them between a min and max"""

    if isinstance(values, str):
        values = [values]
    int_values: list[int] = []
    for value in values:
        value = str(value).strip(" ")
        value = check_int(value)
        if value is None:
            continue
        value = clamp(value, min_value, max_value)
        value += offset
        int_values.append(value)
    return int_values


def encode_ls(lst: list[int]) -> dict[int, Any]:
    """Encode a list of integers into a dictionary"""
    return {i: lst[i] for i in range(len(lst))}


def parse_int_list_list(list_of_lists: list[list[str]]) -> list[list[int]]:
    """Turn list of list of strings into list of list of ints"""
    new_lists: list[list[int]] = []

    for lst in list_of_lists:
        new_list: list[int] = []
        for item in lst:
            try:
                new_list.append(int(item))
            except ValueError:
                continue
        new_lists.append(new_list)
    new_lists = [line for line in new_lists if line != []]
    return new_lists


def check_hex(value: str) -> Union[str, None]:
    """Check if a string is a hex number"""

    value = str(value).strip(" ")
    try:
        int(value, 16)
        return value
    except ValueError:
        return None


def check_dec(value: str) -> Union[str, None]:
    """Check if a string is a decimal number"""

    value = str(value).strip(" ")
    try:
        int(value)
        return value
    except ValueError:
        return None


def str_to_gv(game_version: str) -> str:
    """Turn a game version with semantic versioning to integer representation"""

    split_gv = game_version.split(".")
    if len(split_gv) == 2:
        split_gv.append("0")
    final = ""
    for split in split_gv:
        final += split.zfill(2)
    
    return final.lstrip("0")


def gv_to_str(game_version: int) -> str:
    """Turn a game version with integer representation to semantic versioning"""

    split_gv = str(game_version).zfill(6)
    split_gv = [str(int(split_gv[i : i + 2])) for i in range(0, len(split_gv), 2)]
    return ".".join(split_gv)


def load_json(json_path: str) -> Any:
    """Load a json file"""

    return json.loads(read_file_string(json_path))


def is_jp(save_stats: dict[str, Any]) -> bool:
    """Check if the save is a Japanese save"""

    return save_stats["version"] == "jp"


def check_tracker(save_stats: dict[str, Any], path: str) -> None:
    """Check if the tracker is enabled"""
    item_tracker = tracker.Tracker()

    if item_tracker.has_data():
        upload = (
            user_input_handler.colored_input(
                "You have untracked bannable items that need to be uploaded. Do you want to upload them now? (&y&/&n&) (You will be unable to do so after exiting unless you have WIPE_TRACKED_ITEMS_ON_START set to False):"
            )
            == "y"
        )
        if upload:
            server_handler.meta_data_upload_handler(save_stats, path)
            colored_text("Uploaded meta data", new=GREEN)


def exit_editor():
    """Exit the editor"""

    input("Press enter to exit:")
    sys.exit(0)


def check_cat_ids(cat_ids: list[int], save_stats: dict[str, Any]) -> list[int]:
    """Check if a list of cat ids is valid"""

    for cat_id in cat_ids:
        if cat_id > len(save_stats["cats"]):
            colored_text(f"Invalid cat id {cat_id}", base=RED)
            cat_ids.remove(cat_id)
    return cat_ids


def colored_text(
    text: str,
    base: str = WHITE,
    new: str = DARK_YELLOW,
    split_char: str = "&",
    end: str = "\n",
):
    """Print text with colors"""
    color_new = colored.fg(new)  # type: ignore
    color_base = colored.fg(base)  # type: ignore
    color_reset = colored.fg(WHITE)  # type: ignore

    text_split = text.split(split_char)
    for i, text_section in enumerate(text_split):
        if i % 2:
            print(f"{color_new}{text_section}{color_base}", end="")
        else:
            print(f"{color_base}{text_section}{color_base}", end="")
    print(color_reset, end=end)


def colored_list(
    items: list[str],
    extra_data: Any = None,
    index: bool = True,
    offset: Union[None, int] = None,
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


def calculate_user_rank(save_stats: dict[str, Any]):
    """Calculate the user rank"""

    user_rank = 10 # blue upgrade base level (1 each)
    user_rank += sum(save_stats["cats"])
    user_rank += sum(save_stats["cat_upgrades"]["Base"])
    user_rank += sum(save_stats["cat_upgrades"]["Plus"])
    user_rank += sum(save_stats["blue_upgrades"]["Base"])
    user_rank += sum(save_stats["blue_upgrades"]["Plus"])
    return user_rank


def write_save_data(save_data: bytes, country_code: str, path: str, prompt: bool):
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


def setup_tk():
    """Setup tkinter"""

    root = Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)


def save_file(title: str, file_types: list[tuple[str, str]], path: str) -> str:
    """Save a file with tkinter"""
    setup_tk()

    try:
        path_d = filedialog.asksaveasfile(
            mode="w",
            confirmoverwrite=True,
            initialfile=os.path.basename(path),
            filetypes=file_types,
            title=title,
        )
        if not path_d:
            return ""
    except PermissionError:
        print(
            colored_text(
                "Permission denied. Make sure the file is not in use", base=RED
            )
        )
        exit_editor()
    if not path:
        return ""
    return path_d.name


def select_file(
    title: str, file_types: list[tuple[str, str]], default_dir: str = "", initial_file: str = ""
) -> str:
    """Select a file with tkinter"""
    setup_tk()
    file_path = filedialog.askopenfilename(
        initialdir=default_dir, title=title, filetypes=file_types, initialfile=initial_file
    )
    return file_path

def get_default_save_name() -> str:
    """Get the default save name"""

    return config_manager.get_config_value("DEFAULT_SAVE_FILE_PATH")

def load_save_file(path: str) -> dict[str, Any]:
    """Load a save file, get the country code, create a backup and parse the save data"""

    save_data = read_file_bytes(path)
    country_code = get_country_code(save_data)
    colored_text(f"Game version: &{country_code}&")
    save_stats = parse_save.start_parse(save_data, country_code)
    if config_manager.get_config_value_category("START_UP", "CREATE_BACKUP"):
        write_file_bytes(path + "_backup", save_data)
        colored_text(f"Backup created at: &{os.path.abspath(path + '_backup')}&", new=GREEN)
    return {
        "save_data": save_data,
        "country_code": country_code,
        "save_stats": save_stats,
    }


def get_country_code(save_data: bytes) -> str:
    """Ask the user for their country code if it cannot be detected"""

    country_code = patcher.detect_game_version(save_data)
    if country_code is None:
        country_code = ask_cc()
    return country_code


def ask_cc():
    """Ask the user for their country code"""
    default_gv = config_manager.get_config_value("DEFAULT_GAME_VERSION")
    if default_gv:
        colored_text(f"Using default game version: &{default_gv}&")
        return default_gv

    country_code = user_input_handler.colored_input(
        "Enter your game version (&en&, &jp&, &kr&, &tw&):"
    )
    return country_code


def export_json(save_stats: dict[str, Any], path: str) -> None:
    """Export the save stats to a json file"""

    ordered_data = parse_save.re_order(save_stats)
    if os.path.isdir(path):
        path = os.path.join(path, f"{get_default_save_name()}.json")
    write_file_string(path, json.dumps(ordered_data, indent=4))
    colored_text(f"Successfully wrote json to &{os.path.abspath(path)}&")


def load_json_handler(json_path: str) -> Union[None, str]:
    """Load a save_data json file and serialise it"""

    save_stats = load_json(json_path)
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    path = save_file(
        "Save file",
        get_save_file_filetype(),
        os.path.join(os.path.dirname(json_path), get_default_save_name()),
    )
    if not path:
        return None
    write_file_bytes(path, save_data)
    return path
