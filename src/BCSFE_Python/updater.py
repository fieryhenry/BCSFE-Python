"""Update the editor"""

import subprocess

import requests

from . import helper


def update(command: str = "py") -> None:
    """Update pypi package testing for py and python"""

    helper.colored_text("Updating...", base=helper.GREEN)
    try:
        subprocess.run(
            f"{command} -m pip install --upgrade battle-cats-save-editor",
            shell=True,
            capture_output=True,
            check=True,
        )
        helper.colored_text("Update successful", base=helper.GREEN)
    except subprocess.CalledProcessError as err:
        helper.colored_text("Update failed", base=helper.RED)
        if command == "py":
            helper.colored_text("Trying with python instead", base=helper.RED)
            update("python")
        else:
            helper.colored_text(
                f"Error: {err.stderr.decode('utf-8')}\nYou may need to manually update with py -m pip install -U battle-cats-save-editor",
                base=helper.RED,
            )


def get_local_version() -> str:
    """Returns the local version of the editor"""

    return helper.read_file_string(helper.get_file("version.txt"))


def get_pypi_version():
    """Get latest pypi version of the program"""
    package_name = "battle-cats-save-editor"
    try:
        response = requests.get(
            f"https://pypi.python.org/pypi/{package_name}/json"
        )
        response.raise_for_status()
        return response.json()["info"]["version"]
    except requests.exceptions.RequestException as err:
        raise Exception("Error getting pypi version") from err

def get_latest_prerelease_version() -> str:
    """Get latest prerelease version of the program"""
    package_name = "battle-cats-save-editor"
    try:
        response = requests.get(
            f"https://pypi.python.org/pypi/{package_name}/json"
        )
        response.raise_for_status()
        releases = list(response.json()["releases"])
        releases.reverse()
        for release in releases:
            if "b" in release:
                return release
        return ""
    except requests.exceptions.RequestException as err:
        raise Exception("Error getting pypi version") from err

def check_update() -> bool:
    """Checks if the editor is updated"""

    local_version = get_local_version()
    pypi_version = get_pypi_version()
    if local_version < pypi_version:
        return True
    return False
