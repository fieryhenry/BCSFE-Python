"""Update the editor"""

import subprocess
from typing import Any, Optional

import requests

from . import config_manager, helper


def update(latest_version: str, command: str = "py") -> bool:
    """Update pypi package testing for py and python"""

    helper.colored_text("Updating...", base=helper.GREEN)
    try:
        full_cmd = f"{command} -m pip install --upgrade battle-cats-save-editor=={latest_version}"
        subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            check=True,
        )
        helper.colored_text("Update successful", base=helper.GREEN)
        return True
    except subprocess.CalledProcessError:
        return False


def try_update(latest_version: str):
    """
    Try to update the editor

    Args:
        latest_version (str): The latest version of the editor
    """
    success = update(latest_version, "py")
    if success:
        return
    success = update(latest_version, "python3")
    if success:
        return
    success = update(latest_version, "python")
    if success:
        return
    helper.colored_text(
        "Update failed\nYou may need to manually update with py -m pip install -U battle-cats-save-editor",
        base=helper.RED,
    )


def get_local_version() -> str:
    """Returns the local version of the editor"""

    return helper.read_file_string(helper.get_file("version.txt"))


def get_version_info() -> Optional[tuple[str, str]]:
    """Gets the latest version of the program"""

    package_name = "battle-cats-save-editor"
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        return None

    info = (
        get_pypi_version(data),
        get_latest_prerelease_version(data),
    )
    return info


def get_pypi_version(data: dict[str, Any]) -> str:
    """Get latest pypi version of the program"""
    return data["info"]["version"]


def get_latest_prerelease_version(data: dict[str, Any]) -> str:
    """Get latest prerelease version of the program"""
    releases = list(data["releases"])
    releases.reverse()
    for release in releases:
        if "b" in release:
            return release
    return ""


def pypi_is_newer(local_version: str, pypi_version: str, remove_b: bool = True) -> bool:
    """Checks if the local version is newer than the pypi version"""
    if remove_b:
        if "b" in pypi_version:
            pypi_version = pypi_version.split("b")[0]
        if "b" in local_version:
            local_version = local_version.split("b")[0]

    return pypi_version > local_version


def check_update(version_info: tuple[str, str]) -> tuple[bool, str]:
    """Checks if the editor is updated"""

    local_version = get_local_version()
    pypi_version, latest_prerelease_version = version_info

    check_pre = "b" in local_version or config_manager.get_config_value_category(
        "START_UP", "UPDATE_TO_BETAS"
    )
    if check_pre and pypi_is_newer(
        local_version, latest_prerelease_version, remove_b=False
    ):
        helper.colored_text("Prerelease update available\n", base=helper.GREEN)
        return True, latest_prerelease_version

    if pypi_is_newer(local_version, pypi_version):
        helper.colored_text("Stable update available\n", base=helper.GREEN)
        return True, pypi_version

    helper.colored_text("No update available\n", base=helper.GREEN)
    return False, local_version
