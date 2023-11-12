from typing import Any, Optional
from bcsfe import core


class Updater:
    package_name = "bcsfe"

    def __init__(self):
        pass

    def get_local_version(self) -> str:
        return core.Path("version.txt", is_relative=True).read().to_str().strip()

    def get_pypi_json(self) -> Optional[dict[str, Any]]:
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        response = core.RequestHandler(url).get()
        if response is None:
            return None
        return response.json()

    def get_releases(self) -> Optional[list[str]]:
        pypi_json = self.get_pypi_json()
        if pypi_json is None:
            return None
        releases = pypi_json.get("releases")
        if releases is None:
            return None
        return list(releases.keys())

    def get_latest_version(self, prereleases: bool = False) -> Optional[str]:
        releases = self.get_releases()
        if releases is None:
            return None

        releases.reverse()
        if prereleases:
            return releases[0]
        else:
            for release in releases:
                if not "b" in release:
                    return release
            return releases[0]

    def get_latest_version_info(
        self, prereleases: bool = False
    ) -> Optional[dict[str, Any]]:
        pypi_json = self.get_pypi_json()
        if pypi_json is None:
            return None
        releases = pypi_json.get("releases")
        if releases is None:
            return None
        return releases.get(self.get_latest_version(prereleases))

    def update(self, target_version: str) -> bool:
        python_aliases = ["py", "python", "python3"]
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
