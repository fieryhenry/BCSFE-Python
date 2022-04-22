import patcher
import json
import os
import secrets
import subprocess
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

def to_little(number, bytes):
    val_b = int.to_bytes(number, bytes, "little")
    return val_b

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def load_save_file(path):
    save_data = open_file_b(path)
    game_version_c = get_game_version(save_data)
    save_stats = parse_save.start_parse(save_data, game_version_c)
    write_file(save_data, path + "_backup", False)
    coloured_text(f"Backup successfully created at &{os.path.abspath(path) + '_backup'}", new=green)
    coloured_text(f"Game version: &{game_version_c}")
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
    data = open(json_path, "r").read()
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

def adb_pull(game_version):
    if game_version == "jp": game_version = ""
    path = f"/data/data/jp.co.ponos.battlecats{game_version}/files/SAVE_DATA"
    coloured_text(f"Pulling save data from &{path}", new=green)
    try:
        data = subprocess.run(f"adb pull {path}", capture_output=True)
    except FileNotFoundError:
        coloured_text("Error, please put adb into your Path environment variable\nTutorial in the help video's description", base=red)
        exit()
    return data

def adb_error_handler(output : subprocess.CompletedProcess, game_version, success="SAVE_DATA"):
    return_code = output.returncode
    error = bytes.decode(output.stderr, "utf-8")
    if return_code == 0:
        coloured_text(f"Success", new=green)
        return success
        
    elif "device '(null)' not found" in error:
        coloured_text(f"Error: No device with an adb connection can be found, please connect one and try again.", base=red)
        return
    elif "does not exist" in error:
        coloured_text(f"Error: You don't seem to have game version: &\"{game_version}\"& installed on this device please try again.", base=red)
        return
    elif "daemon started successfully;" in error:
        coloured_text(f"Adb daemon has now started, re-trying")
        return "retry"
    else:
        coloured_text(f"Error: an unknown error has occurred: {error}")
        return

def adb_pull_handler(game_version=None):
    if not game_version:
        game_version = input("Enter your game version (en, jp, kr, tw):")
        
    output = adb_pull(game_version)
    success = adb_error_handler(output, game_version)
    if success == "retry":
        return adb_pull_handler(game_version)
    return success

def adb_clear(game_version):
    if game_version == "jp": game_version = ""
    package_name = f"jp.co.ponos.battlecats{game_version}"
    path = f"/data/data/{package_name}"
    try:
        data = subprocess.run(f"adb shell rm {path}/shared_prefs -r -f", capture_output=True)
    except FileNotFoundError:
        coloured_text("Error, please put adb into your Path environment variable\nTutorial in the help video's description", base=red)
        exit()
    success = adb_error_handler(data, game_version, True)
    if not success:
        return
    if success == "retry":
        adb_clear(game_version)
    subprocess.run(f"adb shell rm {path}/files/*SAVE_DATA*", capture_output=True)
    adb_rerun(package_name)

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
        coloured_text(f"&A new version is available!&\n&Please run &python -m pip install -U battle-cats-save-editor& to install it&",base=cyan, new=green)
        coloured_text(f"&See the changelog here: &https://github.com/fieryhenry/BCSFE-Python/blob/master/changelog.md\n", base=cyan, new=green)

def get_range_input(input, length=None, min=0):
    ids = []
    if length != None and input.lower() == "all":
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
def edit_array_user(names, data, maxes, name, type_name="level", range=False, length=None, item_name=None, offset=0):
    individual = True
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
            val = validate_int(coloured_text(f"What {type_name} do you want to set your &{name}& to?{max_str}:", is_input=True))
            if val == None:
                print("Please enter a valid number")
                continue
            first = False
        if individual:
            val = validate_int(coloured_text(f"What &{type_name}& do you want to set your &{names[id]}& to?{max_str}:", is_input=True))
            if val == None:
                print("Please enter a valid number")
                continue
        if maxes:
            val = clamp(val, 0, maxes[id]+offset)
        data[id] = val - offset
    return data

def edit_items_list(names, item, name, maxes, type_name="level", offset=0):
    item = edit_array_user(names, item, maxes, name, type_name, offset=offset)
    
    coloured_text(f"Successfully edited &{name}")
    return item   
def edit_item(item, max, name, warning=False, add_plural=False, custom_text=None):
    plural = ""
    if type(item) == dict: item_val = item["Value"]
    else: item_val = item
    if warning:
        coloured_text(f"&WARNING: Editing in catfood, rare tickets, platinum tickets or legend tickets will most likely lead to a ban!", new=red)
        if name == "Platinum Tickets": coloured_text("&Instead of editing platinum tickets, edit platinum shards instead! They are much more safe. 10 platinum shards = 1 platinum ticket", new=red)
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
    if len(content) > 50000:
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

def adb_rerun(package_name):
    print("Re-opening game...")
    subprocess.run(f"adb shell am force-stop {package_name}")
    subprocess.run(f"adb shell monkey -p {package_name} -v 1", stdout=subprocess.DEVNULL)

def adb_push(game_version, save_data_path, rerun):
    version = game_version
    if version == "jp": version = ""
    package_name = f"jp.co.ponos.battlecats{version}"
    path = f"/data/data/{package_name}/files/SAVE_DATA"
    coloured_text(f"Pushing save data to &{path}&", new=green)
    try:
        data = subprocess.run(f"adb push \"{save_data_path}\" \"{path}\"", capture_output=True)
    except FileNotFoundError:
        coloured_text("Error, please put adb into your Path environment variable\nTutorial in the help video's description", base=red)
        exit()
    success = adb_error_handler(data, game_version, True)
    if not success:
        return
    if success == "retry":
        return adb_push(game_version, save_data_path, rerun)
    if rerun: adb_rerun(package_name)

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
