"""Checks if the editor is updated and if not, updates it"""

import subprocess
import sys
from typing import Union
import requests
from . import helper, user_input_handler

PKG_NAME = "battle-cats-save-editor"


def get_local_version() -> str:
    """Get the local version of the program"""

    return helper.read_file_string(helper.get_file("version.txt"))


def get_pypi_version() -> Union[None, str]:
    """Get latest pypi version of the program"""

    try:
        response = requests.get(f"https://pypi.python.org/pypi/{PKG_NAME}/json")
        response.raise_for_status()
        return response.json()["info"]["version"]
    except requests.exceptions.RequestException:
        helper.colored_text(
            "Could not get latest version from pypi\nCheck your intnet connection\n",
            base=helper.RED,
        )
        return None


def update(command: str = "py"):
    """Update pypi package testing for py and python"""

    helper.colored_text("Updating...", base=helper.GREEN)
    try:
        subprocess.run(
            f"{command} -m pip install --upgrade {PKG_NAME}",
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
                f"Error: {err.stderr.decode('utf-8')}\nYou may need to manually update with py -m pip install -U {PKG_NAME}",
                base=helper.RED,
            )


def check_update():
    """Check for update and allow user to automatically update"""

    local_version = get_local_version()
    pypi_version = get_pypi_version()
    if pypi_version is not None and pypi_version > local_version:
        helper.colored_text(
            f"Update available: &{local_version}& -> &{pypi_version}&",
            base=helper.GREEN,
            new=helper.WHITE,
        )
        usr_update = user_input_handler.colored_input("Update now? (&y&/&n&):")
        if usr_update.lower()[0] == "y":
            update()
            helper.colored_text(
                "Please rerun the program to use the latest update", base=helper.GREEN
            )
            sys.exit()
    else:
        helper.colored_text(
            f"No update available (local: &{local_version}& pypi: &{pypi_version}&)",
            base=helper.GREEN,
            new=helper.WHITE,
        )
