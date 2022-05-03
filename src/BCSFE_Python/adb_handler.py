import helper
import subprocess
import os

def adb_pull(game_version):
    detect_adb()
    if game_version == "jp": game_version = ""
    path = f"/data/data/jp.co.ponos.battlecats{game_version}/files/SAVE_DATA"
    helper.coloured_text(f"Pulling save data from &{path}", new=helper.green)
    data = subprocess.run(f"adb pull {path}", capture_output=True)
    return data

def adb_error_handler(output : subprocess.CompletedProcess, game_version, success="SAVE_DATA"):
    return_code = output.returncode
    error = bytes.decode(output.stderr, "utf-8")
    if return_code == 0:
        helper.coloured_text(f"Success", new=helper.green)
        return success
        
    elif "device '(null)' not found" in error:
        helper.coloured_text(f"Error: No device with an adb connection can be found, please connect one and try again.", base=helper.red)
        return
    elif "does not exist" in error:
        helper.coloured_text(f"Error: You don't seem to have game version: &\"{game_version}\"& installed on this device please try again.", base=helper.red)
        return
    elif "daemon started successfully;" in error:
        helper.coloured_text(f"Adb daemon has now started, re-trying")
        return "retry"
    else:
        helper.coloured_text(f"Error: an unknown error has occurred: {error}")
        return

def find_adb_path():
    drive_letters =["C", "D", "E"]
    for drive_letter in drive_letters:
        if os.path.exists(f"{drive_letter}:\\LDPlayer\\LDPlayer4.0"):
            return f"{drive_letter}:\\LDPlayer\\LDPlayer4.0"
        elif os.path.exists(f"{drive_letter}:\Program Files (x86)\\Nox\\bin"):
            return f"{drive_letter}:\Program Files (x86)\\Nox\\bin"

def add_to_path():
    adb_path = find_adb_path()
    if not adb_path:
        adb_path = input("Please enter the path to the folder than contains adb:")
        if os.path.isfile(adb_path):
            adb_path = os.path.dirname(adb_path)
    subprocess.run(f"setx PATH \"%PATH%{adb_path}\"")
    subprocess.run(f"set PATH=%PATH%{adb_path}", shell=True)
    print("Successfully added adb to path")

def adb_pull_handler(game_version=None):
    if not game_version:
        game_version = input("Enter your game version (en, jp, kr, tw):")
    detect_adb()
    output = adb_pull(game_version)
    success = adb_error_handler(output, game_version)
    if success == "retry":
        return adb_pull_handler(game_version)
    return success

def detect_adb():
    try:
        subprocess.run(f"adb", capture_output=True)
    except FileNotFoundError:
        add_adb = helper.valdiate_bool(helper.coloured_text("Error, adb is not in your Path environment variable. There is a tutorial in the github's readme. Would you like to try to add adb to your path now?(&y&/&n&):", is_input=True), "y")
        if add_adb:
            add_to_path()
            print("Please re-run the editor to try again")
        exit()

def adb_clear(game_version):
    if game_version == "jp": game_version = ""
    package_name = f"jp.co.ponos.battlecats{game_version}"
    path = f"/data/data/{package_name}"
    detect_adb()

    data = subprocess.run(f"adb shell rm {path}/shared_prefs -r -f", capture_output=True)

    success = adb_error_handler(data, game_version, True)
    if not success:
        return
    if success == "retry":
        adb_clear(game_version)
    subprocess.run(f"adb shell rm {path}/files/*SAVE_DATA*", capture_output=True)
    adb_rerun(package_name)

def adb_rerun(package_name):
    print("Re-opening game...")
    subprocess.run(f"adb shell am force-stop {package_name}")
    subprocess.run(f"adb shell monkey -p {package_name} -v 1", stdout=subprocess.DEVNULL)

def adb_push(game_version, save_data_path, rerun):
    detect_adb()
    version = game_version
    if version == "jp": version = ""
    package_name = f"jp.co.ponos.battlecats{version}"
    path = f"/data/data/{package_name}/files/SAVE_DATA"
    helper.coloured_text(f"Pushing save data to &{path}&", new=helper.green)
    
    data = subprocess.run(f"adb push \"{save_data_path}\" \"{path}\"", capture_output=True)

    success = adb_error_handler(data, game_version, True)
    if not success:
        return
    if success == "retry":
        return adb_push(game_version, save_data_path, rerun)
    if rerun: adb_rerun(package_name)