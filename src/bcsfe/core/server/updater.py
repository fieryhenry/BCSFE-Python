from typing import Any
from bcsfe import core


class Updater:
    package_name = "battle-cats-save-editor"

    def __init__(self):
        pass

    def get_local_version(self) -> str:
        return core.Path("version.txt", is_relative=True).read().to_str().strip()

    def get_pypi_json(self) -> dict[str, Any]:
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        try:
            response = core.RequestHandler(url).get()
        except core.ConnectionError:
            return {}
        return response.json()

    def get_releases(self) -> list[str]:
        return list(self.get_pypi_json()["releases"].keys())

    def get_latest_version(self, prereleases: bool = False) -> str:
        releases = self.get_releases()
        releases.reverse()
        if prereleases:
            return releases[0]
        else:
            for release in releases:
                if not "b" in release:
                    return release
            return releases[0]

    def get_latest_version_info(self, prereleases: bool = False) -> dict[str, Any]:
        return self.get_pypi_json()["releases"][self.get_latest_version(prereleases)]

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
        return core.config.get(core.ConfigKey.UPDATE_TO_BETA)
