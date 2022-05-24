import patcher
import json
import os
import secrets
import colored
import requests
import serialise_save
import parse_save
import tkinter
from tkinter import filedialog

root = tkinter.Tk()
root.withdraw()

green = "#008000"
dark_yellow = "#d7c32a"
red = "#ff0000"
cyan = "#00ffff"

def gv_to_str(game_version):
    gv = str(game_version)
    gv_formatted = ""
    for i in range(0, len(gv), 2):
        val = int(gv[i:i+2])
        gv_formatted += (str(val)) + "."
        
    return gv_formatted.strip(".")

def to_little(number, bytes):
    val_b = int.to_bytes(number, bytes, "little")
    return val_b

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def load_save_file(path):
    save_data = open_file_b(path)
    game_version_c = get_game_version(save_data)
    coloured_text(f"Game version: &{game_version_c}&")
    save_stats = parse_save.start_parse(save_data, game_version_c)
    write_file(save_data, path + "_backup", False)
    coloured_text(f"Backup successfully created at &{os.path.abspath(path) + '_backup'}", new=green)
    return {"save_data" : save_data, "save_stats" : save_stats, "game_version" : game_version_c}

def load_json_handler(json_path):
    save_stats = load_json(json_path)
    save_data = serialise_save.start_serialize(save_stats)
    save_data = patcher.patch_save_data(save_data, save_stats["version"])
    path = write_file(save_data, "SAVE_DATA", True)
    if path:
        print("Successfully loaded save data")
    else:
        print("Please select a place to write the save data to")
    return path
def load_json(json_path):
    data = open(json_path, "r", encoding="utf-8").read()
    save_stats = json.loads(data)
    return save_stats

def sel_file(title, filetypes):
    path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    if not path:
        input("Please select a file")
        return
    return path

def sel_save():
    print("Select your battle cats save")
    path = sel_file("Select A Battle Cats Save", [("Battle Cats Save", "*SAVE_DATA*"), ("All Files", "*.*")])
    return path

def write_file(data, path, prompt):
    if prompt:
        path = filedialog.asksaveasfile("w", confirmoverwrite=True, initialfile=os.path.basename(
            path), filetypes=[("Battle Cats Save", "*.*")])
        if not path:
            print("Please save the file")
            return
        path = path.name
    f = open(path, "wb")
    f.write(data)
    if prompt:
        coloured_text(f"Successfully wrote save data to: &{path}&", new=green)
    return path


def frames_hmsf(frames):
    ss, frames = divmod(frames, 30)
    mm, ss = divmod(ss, 60)
    hh, mm = divmod(mm, 60)
    return {"hh" : hh, "mm" : mm, "ss" : ss, "frames" : frames}

def parse_csv_file(path, lines=None, min_length=0, black_list=None, parse=False, separator=","):
    if not lines:
        lines = open(path, "r", encoding="utf-8").readlines()
    data = []
    for line in lines:
        line_data = line.split(separator)
        if len(line_data) < min_length:
            continue
        if black_list:
            line_data = filter_list(line_data, black_list)
        if parse:
            line_data = ls_int(line_data)
        data.append(line_data)
    return data

def copy_first_n(list, number):
    new_list = []
    for item in list:
        new_list.append(item[number])
    return new_list

def ls_int(ls, offset=0):
    data = []
    for item in ls:
        try:
            data.append(int(item) + offset)
        except:
            data.append(item)
    return data

def filter_list(data : list, black_list : list):
    trimmed_data = data
    for i in range(len(data)):
        item = data[i]
        for banned in black_list:
            if banned in item:
                index = item.index(banned)
                item = item[:index]
                trimmed_data[i] = item
    return trimmed_data
    
def hmsf_seconds(hmsf):
    total_frames = hmsf["frames"]
    total_frames += hmsf["ss"] * 30
    total_frames += hmsf["mm"] * 60 * 30
    total_frames += hmsf["hh"] * 60 * 60 * 30
    return total_frames

def validate_int(string):
    string = string.strip(" ")
    if string.isdigit():
        return int(string)
    else:
        return None

def get_version():
    path = get_files_path("version.txt")
    version = open_file_s(path)
    return version

def get_latest_version():
    package_name = "battle-cats-save-editor"
    r = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if not r.ok:
        coloured_text("An error has occurred while checking for a new version", base=red)
        return
    return r.json()["info"]["version"]

def check_update():
    installed_version = get_version()
    coloured_text(f"\nYou currently have version &{installed_version}& installed", new=green)
    latest_version = get_latest_version()
    if not latest_version:
        return
    coloured_text(f"The latest version available is &{latest_version}&\n", new=green)
    if installed_version != latest_version:
        coloured_text(f"&A new version is available!&\n&Please run &py -m pip install -U battle-cats-save-editor& to install it&",base=cyan, new=green)
        coloured_text(f"&See the changelog here: &https://github.com/fieryhenry/BCSFE-Python/blob/master/changelog.md\n", base=cyan, new=green)

def get_range_input(input, length=None, min=0, all_ids=None):
    ids = []
    flag = length != None or all_ids != None
    if flag and input.lower() == "all":
        if all_ids:
            return all_ids
        else:
            return range(min, length)
    if "-" in input:
        content = input.split('-')
        first = validate_int(content[0])
        second = validate_int(content[1])
        if first == None or second == None:
            print(f"Please enter 2 valid numbers when making a range : {first} | {second}")
            return []
        ids = range(first, second+1)
    else:
        content = input.split(" ")
        for id in content:
            item_id = validate_int(id)
            if item_id == None:
                print(f"Please enter a valid number : {id}")
                continue
            ids.append(item_id)
    return ids
def edit_item_str(item, name):
    coloured_text(f"Your {name} is : &{item}&")
    item = coloured_text(f"Enter new {name}:", is_input=True)
    coloured_text(f"Successfully set {name} to &{item}&")
    return item

def get_real_path(path):
    base_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(base_path, path)
    return path

def open_file_s(path):
    return open(path, "r", encoding="utf-8").read()

def get_files_path(path):
    base_path = get_real_path("files/")
    path = os.path.join(base_path, path)
    return path
def create_list(list, index=True, extra_values=None, offset=None, color=True):
    output = ""
    for i in range(len(list)):
        if index:
            output += f"{i+1}. &{list[i]}&"
        else:
            output += str(list[i])
        if extra_values:
            if offset != None:
                output += f" &:& {extra_values[i]+offset}"
            else:
                output += f" &:& {extra_values[i]}"
        output += "\n"
    output = output.removesuffix("\n")
    if not color:
        output = output.replace("&", "")
    coloured_text(output)
def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

def selection_list(names, mode, index_flag, include_at_once=False):
    create_list(names, index_flag)

    total = len(names)+1
    ids = coloured_text(f"{total}. &All at once&\nWhat do you want to {mode} (You can enter multiple values separated by spaces to edit multiple at once):", is_input=True).split(" ")
    individual = True
    if str(total) in ids:
        ids = range(1, total)
        ids = [format(x, '02d') for x in ids]
        individual = False
    if include_at_once:
        return {"ids" : ids, "individual" : individual}
    return ids

def handle_all_at_once(ids, all_at_once, data, names, item_name, group_name, explain_text=""):
    first = True
    value = 0
    for id in ids:
        if all_at_once and first:
            value = validate_int(coloured_text(f"Enter {item_name} {explain_text}:", is_input=True))
            first = False
        elif not all_at_once:
            value = validate_int(coloured_text(f"Enter {item_name} for {group_name} &{names[id]}& {explain_text}:", is_input=True))
        if value == None: continue
        data[id] = value
    return data

def validate_clamp(values, max, min=0, offset=-1):
    if type(values) == str: values = [values]
    int_vals = []
    for value in values:
        value = f"{value}".strip(" ")
        value = validate_int(value)
        if value == None: continue
        value = clamp(value, min, max)
        value += offset
        int_vals.append(value)
    return int_vals

def create_all_list(ids, max_val, include_all_at_once=False):
    all_at_once = False
    if f"{max_val}" in ids:
        ids = range(1, max_val)
        ids = [format(x, '02d') for x in ids]
        all_at_once = True
    if include_all_at_once:
        return {"ids" : ids, "at_once" : all_at_once}
    else:
        return ids
def edit_array_user(names, data, maxes, name, type_name="level", range=False, length=None, item_name=None, offset=0, custom_text=""):
    individual = True
    min_length = min(len(names), len(data))
    names = names[0:min_length]
    data = data[0:min_length]
    if type(maxes) == int:
        maxes = [maxes] * len(data)
    if range:
        ids = get_range_input(coloured_text(f"Enter {name} ids(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), length)
        if len(ids) > 1:
            individual = coloured_text(f"Do you want to set the {name} for each {item_name} individually(&1&), or all at once(&2&):", is_input=True)
    else:
        ids = selection_list(names, "edit", True, True)
        individual = ids["individual"]
        ids = ids["ids"]
    first = True
    val = None
    for id in ids:
        id = validate_int(id)
        if id == None:
            print("Please enter a number")
            continue
        id -= 1
        max_str = ""
        if maxes:
            if not individual:
                max_str = f" (Max &{max(maxes)+offset}&)"
            else:
                max_str = f" (Max &{maxes[id]+offset}&)"

        if not individual and first:
            if custom_text:
                val = validate_int(coloured_text(f"{custom_text}", is_input=True))
            else:
                val = validate_int(coloured_text(f"What {type_name} do you want to set your &{name}& to?{max_str}:", is_input=True))
            if val == None:
                print("Please enter a valid number")
                continue
            first = False
        if individual:
            if custom_text:
                val = validate_int(coloured_text(f"{custom_text} : {names[id]}:", is_input=True))
            else:
                val = validate_int(coloured_text(f"What &{type_name}& do you want to set your &{names[id]}& to?{max_str}:", is_input=True))
            if val == None:
                print("Please enter a valid number")
                continue
        if maxes:
            val = clamp(val, 0, maxes[id]+offset)
        data[id] = val - offset
    return data

def valdiate_bool(value, true_text):
    if value.lower() == true_text.lower():
        return True
    else:
        return False

def edit_items_list(names, item, name, maxes, type_name="level", offset=0):
    item = edit_array_user(names, item, maxes, name, type_name, offset=offset)
    
    coloured_text(f"Successfully edited &{name}")
    return item   
def edit_item(item, max, name, warning=False, add_plural=False, custom_text=None):
    plural = ""
    if type(item) == dict:
        item = item.copy()
        item_val = item["Value"]
    else: item_val = item
    if warning:
        coloured_text(f"&WARNING: Editing in catfood, rare tickets, platinum tickets or legend tickets will most likely lead to a ban!", new=red)
        if name == "Platinum Tickets": coloured_text("&Instead of editing platinum tickets, edit platinum shards instead! They are much more safe. 10 platinum shards = 1 platinum ticket", new=red)
        elif name == "Rare Tickets": coloured_text("&Instead of editing rare tickets directly, use the \"Normal Ticket Max Trade Progress\" conversion feature instead! It is much more safe.", new=red)
        input("Press enter to accept the risk:")
    if add_plural:
        plural = "s"

    if custom_text:
        coloured_text(f"{custom_text[0]}&{item_val}")
    else:
        coloured_text(f"You currently have &{item_val}& {name}{plural}")
    max_str = f"(max &{max}&)"
    if not max: max_str = ""
    text = f"Enter amount of {name}{plural} to set{max_str}:"
    if custom_text:
        if max_str:
            max_str += ":"
        text = f"{custom_text[1]}{max_str}"
    val = validate_int(coloured_text(text, is_input=True))
    if val == None:
        print("Please enter a valid number")
        return
    if max:
        val = clamp(val, 0, max)
    if type(item) == dict: item["Value"] = val
    else: item = val
    coloured_text(f"Successfully set {name} to &{val}&")
    return item

def download_save():
    country_code = input("Enter your game version (en, ja, kr, tw):")
    if country_code == "jp": country_code = "ja"
    transfer_code = input("Enter transfer code:")
    confirmation_code = input("Enter confirmation code:")
    game_version = input("Enter game version (e.g 110300, 906000, 100400):")

    url = f"https://nyanko-save.ponosgames.com/v1/transfers/{transfer_code}/reception"
    data = {
        "clientInfo" : {
            "client" : {
                "countryCode" : country_code,
                "version" : game_version
            },
            "device" : {
                "model" : "SM-G973N"
            },
            "os" : {
                "type" : "android",
                "version" : "7.1.2"
            }
        },
        "nonce" : secrets.token_hex(16),
        "pin" : confirmation_code
    }
    json_text = json.dumps(data).encode("utf-8")
    response = requests.post(url, data=json_text, headers={"content-type" : "application/json", "accept-encoding" : "gzip"})
    content = response.content
    if len(content) > 50:
        print("Successfully downloaded save data")
    else:
        print("Incorrect transfer code / confirmation code / game version")
        return
    write_file(response.content, "SAVE_DATA", False)
    return "SAVE_DATA"

def set_range(list_original, values, start_point):
    list_original = list(list_original)
    list_original[start_point:start_point+len(values)] = values
    return bytes(list_original)

def get_game_version(save_data):
    game_version = patcher.detect_game_version(save_data)
    if not game_version:
        game_version = input("Enter your game version (en, jp, kr, tw):")
    return game_version
    
def write_save_data(save_data, game_version, path, prompt=True):
    save_data = patcher.patch_save_data(save_data, game_version)
    write_file(save_data, path, prompt)
    exit()


def open_file_b(path):
    f = open(path, "rb").read()
    return f
def coloured_text(text, base="#ffffff", new=dark_yellow, chr="&", is_input=False):
    color_new = colored.fg(new)
    color_base = colored.fg(base)
    color_reset = colored.fg("#ffffff")

    text_split = text.split(chr)
    for i in range(len(text_split)):
        if i % 2:
            print(f"{color_new}{text_split[i]}{color_base}", end="")
        else:
            print(f"{color_base}{text_split[i]}{color_base}", end="")
    print(color_reset, end="")
    if is_input:
        return input()
    else:
        print()
