from typing import Any
from bcsfe.core import io, server


class Updater:
    package_name = "battle-cats-save-editor"

    def __init__(self):
        pass

    def get_local_version(self) -> str:
        return io.path.Path("version.txt", is_relative=True).read().to_str().strip()

    def get_pypi_json(self) -> dict[str, Any]:
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        try:
            response = server.request.RequestHandler(url).get()
        except server.request.requests.exceptions.ConnectionError:
            return {}
        return response.json()

    def get_releases(self) -> list[str]:
        return list(self.get_pypi_json()["releases"].keys())

    def get_latest_version(self, prereleases: bool = False) -> str:
        releases = self.get_releases()
        if prereleases:
            return releases[0]
        else:
            for release in releases:
                if not "b" in release:
                    return release
            return releases[0]

    def get_latest_version_info(self, prereleases: bool = False) -> dict[str, Any]:
        return self.get_pypi_json()["releases"][self.get_latest_version(prereleases)]

    def check_for_updates(self) -> bool:
        return self.get_local_version() < self.get_latest_version()

    def check_for_prereleases(self) -> bool:
        return self.get_local_version() < self.get_latest_version(prereleases=True)

    def update(self, prereleases: bool = False) -> bool:
        python_aliases = ["py", "python", "python3"]
        for python_alias in python_aliases:
            cmd = f"{python_alias} -m pip install --upgrade {self.package_name}=={self.get_latest_version(prereleases)}"
            try:
                io.path.Path().run(cmd)
                break
            except FileNotFoundError:
                continue
        else:
            pip_aliases = ["pip", "pip3"]
            for pip_alias in pip_aliases:
                cmd = f"{pip_alias} install --upgrade {self.package_name}=={self.get_latest_version(prereleases)}"
                try:
                    io.path.Path().run(cmd)
                    break
                except FileNotFoundError:
                    continue
            else:
                return False
        return True
