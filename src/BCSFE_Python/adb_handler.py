"""Handler for adb commands"""

import subprocess
import os
import sys
from typing import Union
from . import user_input_handler, helper


def adb_pull(game_version: str) -> subprocess.CompletedProcess:
    """Pull save data from specific version from a device using adb"""

    if game_version == "jp":
        game_version = ""
    path = f"/data/data/jp.co.ponos.battlecats{game_version}/files/SAVE_DATA"
    helper.colored_text(f"Pulling save data from &{path}", new=helper.GREEN)
    return adb_cmd_handler(f"adb pull \"{path}\" SAVE_DATA")


def adb_error_handler(error: str) -> None:
    """Handle adb errors, and display message if there is an error"""

    if "device '(null)' not found" in error or "device not found" in error:
        helper.colored_text(
            "Error: No device with an adb connection can be found, please connect one and try again.",
            base=helper.RED,
        )
        return None

    if "does not exist" in error:
        helper.colored_text(
            "Error: You don't seem to have this game version installed on this device please try again.",
            base=helper.RED,
        )
        return None

    if "'adb' is not recognized as an internal or external command" in error:
        add_adb = (
            user_input_handler.colored_input(
                "Error, adb is not in your Path environment variable. There is a tutorial in the github's readme. Would you like to try to add adb to your path now?(&y&/&n&):"
            )
            == "y"
        )
        if add_adb:
            add_to_path()
            print("Please re-run the editor to try again")
        sys.exit()

    helper.colored_text(f"Error: an unknown error has occurred: {error}")
    return None


def find_adb_path() -> Union[str, None]:
    """Find adb path automatically in common locations"""

    drive_letters = ["C", "D", "E"]
    for drive_letter in drive_letters:
        if os.path.exists(f"{drive_letter}:\\LDPlayer\\LDPlayer4.0"):
            return f"{drive_letter}:\\LDPlayer\\LDPlayer4.0"
        if os.path.exists(f"{drive_letter}:\\Program Files (x86)\\Nox\\bin"):
            return f"{drive_letter}:\\Program Files (x86)\\Nox\\bin"
        if os.path.exists(f"{drive_letter}:\\adb"):
            return f"{drive_letter}:\\adb"
    return None


def add_to_path() -> None:
    """Try to add adb to path environment variable automatically"""

    adb_path = find_adb_path()
    if not adb_path:
        adb_path = input(
            "Please enter the path to the folder than contains adb: download link here: https://dl.google.com/android/repository/platform-tools-latest-windows.zip:"
        )
        if os.path.isfile(adb_path):
            adb_path = os.path.dirname(adb_path)

    subprocess.run(f'setx PATH "{adb_path};%PATH%"', shell=True, check=True)
    subprocess.run(f"set PATH={adb_path};%PATH%", shell=True, check=True)
    print("Successfully added adb to path")


def adb_pull_handler(game_version: str = None) -> Union[None, str]:
    """Pull save data from device and return the path to the save data"""

    if not game_version:
        game_version = input("Enter your game version (en, jp, kr, tw):")
    if adb_pull(game_version) is None:
        return None
    return "SAVE_DATA"


def start_adb() -> None:
    """Start adb server"""

    helper.colored_text("Starting adb...", helper.GREEN)
    subprocess.run(
        "adb devices",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def adb_clear(game_version: str) -> None:
    """Delete save data and other required files from device for a fresh install without having to re-download any assets"""

    if game_version == "jp":
        game_version = ""
    package_name = f"jp.co.ponos.battlecats{game_version}"
    path = f"/data/data/{package_name}"

    if adb_cmd_handler(f"adb shell rm {path}/shared_prefs -r -f") is None:
        return
    if adb_cmd_handler(f"adb shell rm {path}/files/*SAVE_DATA*") is None:
        return
    adb_rerun(package_name)


def adb_rerun(package_name: str):
    """Close and open the game"""

    print("Re-opening game...")
    if adb_cmd_handler(f"adb shell am force-stop {package_name}") is None:
        return
    if adb_cmd_handler(f"adb shell monkey -p {package_name} -v 1") is None:
        return


def adb_cmd_handler(cmd: str) -> Union[subprocess.CompletedProcess, None]:
    """Handle adb commands"""

    start_adb()
    try:
        return subprocess.run(cmd, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        adb_error_handler(exc.stderr.decode("utf-8"))
        return None


def adb_push(game_version: str, save_data_path: str, rerun: bool):
    """Push save data to a specific game version on device using adb"""

    version = game_version
    if version == "jp":
        version = ""
    package_name = f"jp.co.ponos.battlecats{version}"
    path = f"/data/data/{package_name}/files/SAVE_DATA"
    helper.colored_text(f"Pushing save data to &{path}&", new=helper.GREEN)

    if adb_cmd_handler(f'adb push "{save_data_path}" "{path}"') is None:
        return

    if rerun:
        adb_rerun(package_name)
