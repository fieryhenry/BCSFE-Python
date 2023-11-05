from typing import Any, Callable, Optional
from bcsfe.cli import color

from bcsfe import core


class GameDataGetter:
    def __init__(self, cc: "core.CountryCode"):
        self.url = core.core_data.config.get_str(core.ConfigKey.GAME_DATA_REPO)
        self.lang = core.core_data.config.get_str(core.ConfigKey.LOCALE)
        self.cc = cc.get_cc_lang()
        self.real_cc = cc
        self.cc = self.cc if not self.cc.is_lang() else self.real_cc
        self.all_versions = self.get_versions()
        if self.all_versions is None:
            self.latest_version = None
        else:
            self.latest_version = self.get_latest_version(self.all_versions, self.cc)

    def get_latest_version(
        self, versions: list[str], cc: "core.CountryCode"
    ) -> Optional[str]:
        length = len(versions)
        if cc == core.CountryCodeType.EN and length >= 1:
            return versions[0]
        if cc == core.CountryCodeType.JP and length >= 2:
            return versions[1]
        if cc == core.CountryCodeType.KR and length >= 3:
            return versions[2]
        if cc == core.CountryCodeType.TW and length >= 4:
            return versions[3]
        return None

    def get_versions(self) -> Optional[list[str]]:
        response = core.RequestHandler(self.url + "latest.txt").get()
        if response is None:
            return None
        versions = response.text.split("\n")
        return versions

    def get_file(self, pack_name: str, file_name: str) -> Optional["core.Data"]:
        pack_name = self.get_packname(pack_name)
        version = self.latest_version
        if version is None:
            return None
        url = self.url + f"{version}/{pack_name}/{file_name}"
        response = core.RequestHandler(url).get()
        if response is None:
            return None
        if response.status_code != 200:
            return None
        return core.Data(response.content)

    def get_packname(self, packname: str) -> str:
        if packname != "resLocal":
            return packname
        if self.cc != core.CountryCodeType.EN:
            return packname
        langs = core.CountryCode.get_langs()
        if self.lang in langs:
            return f"{packname}_{self.lang}"
        return packname

    @staticmethod
    def get_game_data_dir() -> "core.Path":
        return core.Path("game_data", is_relative=True)

    def get_file_path(self, pack_name: str, file_name: str) -> Optional["core.Path"]:
        version = self.latest_version

        if version is None:
            return None
        pack_name = self.get_packname(pack_name)
        path = GameDataGetter.get_game_data_dir().add(version).add(pack_name)
        path.generate_dirs()
        path = path.add(file_name)
        return path

    def save_file(self, pack_name: str, file_name: str) -> Optional["core.Data"]:
        pack_name = self.get_packname(pack_name)
        data = self.get_file(pack_name, file_name)
        if data is None:
            return None

        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return None
        data.to_file(path)
        return data

    def is_downloaded(self, pack_name: str, file_name: str) -> bool:
        pack_name = self.get_packname(pack_name)
        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return False
        return path.exists()

    def download_from_path(
        self, path: str, retries: int = 2, display_text: bool = True
    ) -> Optional["core.Data"]:
        pack_name, file_name = path.split("/")
        pack_name = self.get_packname(pack_name)
        return self.download(pack_name, file_name, retries, display_text)

    def download(
        self,
        pack_name: str,
        file_name: str,
        retries: int = 2,
        display_text: bool = True,
    ) -> Optional["core.Data"]:
        retries -= 1
        pack_name = self.get_packname(pack_name)

        if self.is_downloaded(pack_name, file_name):
            path = self.get_file_path(pack_name, file_name)
            if path is None:
                return None
            return path.read()

        if retries == 0:
            return None

        version = self.latest_version

        if version is None:
            if display_text:
                self.print_no_file(pack_name, file_name)
            return None

        if display_text:
            color.ColoredText.localize(
                "downloading",
                file_name=file_name,
                pack_name=pack_name,
                version=version,
            )
        data = self.save_file(pack_name, file_name)
        if data is None:
            data = self.download(pack_name, file_name, retries, display_text)
        if data is None:
            if display_text:
                self.print_no_file(pack_name, file_name)
            return None
        return data

    def download_all(
        self,
        pack_name: str,
        file_names: list[str],
        display_text: bool = True,
    ) -> list[Optional[tuple[str, "core.Data"]]]:
        pack_name = self.get_packname(pack_name)

        callables: list[Callable[..., Any]] = []
        args: list[tuple[str, str, int, bool]] = []
        for file_name in file_names:
            callables.append(self.download)
            args.append((pack_name, file_name, 2, display_text))
        core.thread_run_many(callables, args)
        data_list: list[Optional[tuple[str, core.Data]]] = []
        for file_name in file_names:
            path = self.get_file_path(pack_name, file_name)
            if path is None:
                data_list.append(None)
            elif not path.exists():
                data_list.append(None)
            else:
                data_list.append((file_name, path.read()))
        return data_list

    @staticmethod
    def get_all_downloaded_versions() -> list[str]:
        versions: list[str] = []
        for version in GameDataGetter.get_game_data_dir().get_dirs():
            if version.exists():
                versions.append(version.basename())
        return versions

    @staticmethod
    def delete_old_versions() -> None:
        versions = GameDataGetter.get_all_downloaded_versions()
        ccs: list[str] = []
        for version in versions:
            cc = version[-2:]
            if cc not in ccs:
                ccs.append(cc)

        for cc in ccs:
            versions_cc = list(filter(lambda x: x[-2:] == cc, versions))
            if len(versions_cc) <= 1:
                continue
            versions_cc.sort(reverse=True)
            for version in versions_cc[1:]:
                path = GameDataGetter.get_game_data_dir().add(version)
                path.remove()

    def print_no_file(self, packname: str, file_name: str) -> None:
        color.ColoredText.localize(
            "failed_to_download_game_data",
            file_name=file_name,
            pack_name=packname,
            version=self.latest_version,
        )
