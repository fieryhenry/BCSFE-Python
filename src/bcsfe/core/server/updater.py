from __future__ import annotations
import sys
from typing import Any
from bcsfe import core
import bcsfe


class Updater:
    package_name = "bcsfe"

    def __init__(self):
        pass

    def get_local_version(self) -> str:
        return bcsfe.__version__

    def get_pypi_json(self) -> dict[str, Any] | None:
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        # add a User-Agent since pypi started to block the default requests user-agent
        # this probably won't be needed in the future as i assume this block is temporary
        response = core.RequestHandler(
            url, headers={"User-Agent": "BCSFE-Updater"}
        ).get()
        if response is None:
            return None
        try:
            return response.json()
        except core.JSONDecodeError:
            return None

    def get_releases(self) -> list[str] | None:
        pypi_json = self.get_pypi_json()
        if pypi_json is None:
            return None
        releases = pypi_json.get("releases")
        if releases is None:
            return None
        return list(releases.keys())

    def get_latest_version(self, prereleases: bool = False) -> str | None:
        releases = self.get_releases()
        if releases is None:
            return None

        releases.reverse()
        if prereleases:
            return releases[0]
        else:
            for release in releases:
                if "b" not in release:
                    return release
            return releases[0]

    def get_latest_version_info(
        self, prereleases: bool = False
    ) -> dict[str, Any] | None:
        pypi_json = self.get_pypi_json()
        if pypi_json is None:
            return None
        releases = pypi_json.get("releases")
        if releases is None:
            return None
        return releases.get(self.get_latest_version(prereleases))

    def update(self, target_version: str) -> bool:
        binary = sys.orig_argv[0]
        python_aliases = [binary, "py", "python", "python3"]
        for python_alias in python_aliases:
            cmd = f"{python_alias} -m pip install --upgrade {self.package_name}=={target_version}"
            result = core.Path().run(cmd)
            if result.exit_code == 0:
                break
        else:
            pip_aliases = ["pip", "pip3"]
            for pip_alias in pip_aliases:
                cmd = f"{pip_alias} install --upgrade {self.package_name}=={target_version}"
                result = core.Path().run(cmd)
                if result.exit_code == 0:
                    break
            else:
                return False
        return True

    def has_enabled_pre_release(self) -> bool:
        return core.core_data.config.get_bool(core.ConfigKey.UPDATE_TO_BETA)
