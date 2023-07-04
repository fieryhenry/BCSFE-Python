from typing import Any, Callable, Optional
from bcsfe.core import io, country_code
from bcsfe.cli import color

from bcsfe.core.server import request


class GameDataGetter:
    url = "https://raw.githubusercontent.com/fieryhenry/BCData/master/"

    def __init__(self, save_file: io.save.SaveFile):
        self.cc = save_file.cc
        if save_file.latest_game_data_version is None:
            save_file.latest_game_data_version = self.get_latest_version()
        if save_file.latest_game_data_version is None:
            raise Exception("Could not find latest version")
        self.latest_version = save_file.latest_game_data_version

    def get_latest_version(self) -> Optional[str]:
        versions = (
            request.RequestHandler(self.url + "latest.txt").get().text.split("\n")
        )
        length = len(versions)
        if self.cc == country_code.CountryCodeType.EN and length >= 1:
            return versions[0]
        elif self.cc == country_code.CountryCodeType.JP and length >= 2:
            return versions[1]
        elif self.cc == country_code.CountryCodeType.KR and length >= 3:
            return versions[2]
        elif self.cc == country_code.CountryCodeType.TW and length >= 4:
            return versions[3]
        else:
            return None

    def get_file(self, pack_name: str, file_name: str) -> Optional[io.data.Data]:
        url = self.url + f"{self.latest_version}/{pack_name}/{file_name}"
        response = request.RequestHandler(url).get()
        if response.status_code != 200:
            return None
        return io.data.Data(response.content)

    def get_file_path(self, pack_name: str, file_name: str) -> io.path.Path:
        path = (
            io.path.Path("game_data", is_relative=True)
            .add(self.latest_version)
            .add(pack_name)
        )
        path.generate_dirs()
        path = path.add(file_name)
        return path

    def save_file(self, pack_name: str, file_name: str) -> Optional[io.data.Data]:
        data = self.get_file(pack_name, file_name)
        if data is None:
            return None

        path = self.get_file_path(pack_name, file_name)
        data.to_file(path)
        return data

    def is_downloaded(self, pack_name: str, file_name: str) -> bool:
        path = self.get_file_path(pack_name, file_name)
        return path.exists()

    def download_from_path(
        self, path: str, retries: int = 2, display_text: bool = True
    ) -> Optional[io.data.Data]:
        pack_name, file_name = path.split("/")
        return self.download(pack_name, file_name, retries, display_text)

    def download(
        self,
        pack_name: str,
        file_name: str,
        retries: int = 2,
        display_text: bool = True,
    ) -> Optional[io.data.Data]:
        retries -= 1

        if self.is_downloaded(pack_name, file_name):
            path = self.get_file_path(pack_name, file_name)
            return path.read()
        else:
            if retries == 0:
                return None

            if display_text:
                color.ColoredText.localize(
                    "downloading",
                    file_name=file_name,
                    pack_name=pack_name,
                    version=self.latest_version,
                )
            data = self.save_file(pack_name, file_name)
            if data is None:
                return self.download(pack_name, file_name, retries, display_text)
            else:
                return data

    def download_all(
        self, pack_name: str, file_names: list[str], display_text: bool = True
    ) -> list[Optional[tuple[str, io.data.Data]]]:
        callables: list[Callable[..., Any]] = []
        args: list[tuple[str, str, int, bool]] = []
        for file_name in file_names:
            callables.append(self.download)
            args.append((pack_name, file_name, 2, display_text))
        io.thread_helper.run_many(callables, args)
        data_list: list[Optional[tuple[str, io.data.Data]]] = []
        for file_name in file_names:
            path = self.get_file_path(pack_name, file_name)
            if not path.exists():
                data_list.append(None)
            else:
                data_list.append((file_name, path.read()))
        return data_list
