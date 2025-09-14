from __future__ import annotations
from typing import Any, Callable

import zipfile

from bcsfe.cli import color

from bcsfe import core


class GameDataGetter:
    def __init__(self, cc: core.CountryCode, gv: core.GameVersion):
        self.repo_url = core.core_data.config.get_game_data_repo()
        self.lang = core.core_data.config.get_str(core.ConfigKey.LOCALE)
        self.cc = cc.get_cc_lang()
        self.real_cc = cc
        self.gv = gv
        self.cc = self.cc if not self.cc.is_lang() else self.real_cc
        self.metadata = self.get_metadata()
        if self.metadata is not None:
            self.all_versions = self.get_versions(self.metadata)
            self.url = self.metadata.get("base_url")
        else:
            self.all_versions = None
            self.url = None

        if self.all_versions is None:
            self.version = None
        else:
            self.version = self.get_version(self.all_versions, self.cc)

    def does_save_version_match(self, save_file: core.SaveFile) -> bool:
        if self.version is None:
            return False

        return save_file.game_version == self.version

    def get_version(
        self, versions: dict[str, list[str]], cc: core.CountryCode
    ) -> str | None:
        cc_versions = versions.get(cc.get_code())
        if cc_versions is None:
            return None
        if not cc_versions:
            return None
        gv_string = self.gv.to_string()
        if gv_string not in cc_versions:
            cc_versions.sort(reverse=True)
            # TODO: do closest version rather than always latest version
            return cc_versions[0]
        return gv_string

    def get_metadata(self) -> dict[str, Any] | None:
        response = core.RequestHandler(self.repo_url).get()
        if response is None:
            return None
        try:
            data = response.json()
        except core.JSONDecodeError as e:
            print(e)
            return None
        return data

    def get_cat_names_fast(
        self, display_text: bool = True
    ) -> dict[str, core.Data] | None:
        version = self.version
        if version is None or self.metadata is None:
            return None

        versions = (
            self.metadata.get("cat_names", {}).get(self.cc.get_code(), {}).get(version)
        )

        if versions is None:
            return None

        if not isinstance(versions, str):
            if self.cc != core.CountryCodeType.EN:
                key = self.cc.get_code()
            elif self.lang in core.CountryCode.get_langs():
                key = self.lang
            else:
                key = self.cc.get_code()

            if key is None:
                return

            url = versions.get(key)

            if url is None:
                return None
        else:
            url = versions

        if display_text:
            color.ColoredText.localize("downloading_cat_names", url=url)

        response = core.RequestHandler(url).get()
        if response is None:
            return None

        if response.status_code != 200:
            return None

        try:
            zip = zipfile.ZipFile(core.Data(response.content).to_bytes_io())
        except zipfile.BadZipFile:
            return None

        files: dict[str, core.Data] = {}

        for file in zip.filelist:
            data = zip.read(file.filename)
            files[file.filename] = core.Data(data)

        return files

    def save_all_cat_names_fast(self, display_text: bool = True):
        files = self.get_cat_names_fast(display_text)
        if files is None:
            return

        for filename, data in files.items():
            self.save_file_data("resLocal", filename, data)

    def get_versions(self, metdata: dict[str, Any]) -> dict[str, list[str]] | None:
        return metdata.get("versions")

    def get_file(self, pack_name: str, file_name: str) -> core.Data | None:
        pack_name = self.get_packname(pack_name)
        version = self.version
        if version is None or self.url is None:
            return None
        url = self.url + f"{self.cc.get_code()}/{version}/{pack_name}/{file_name}"
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
    def get_game_data_dir() -> core.Path:
        return core.Path.get_documents_folder().add("game_data")

    def get_file_path(self, pack_name: str, file_name: str) -> core.Path | None:
        version = self.version

        if version is None:
            return None
        pack_name = self.get_packname(pack_name)
        path = (
            GameDataGetter.get_game_data_dir()
            .add(self.cc.get_code())
            .add(version)
            .add(pack_name)
        )
        path.generate_dirs()
        path = path.add(file_name)
        return path

    def save_file(self, pack_name: str, file_name: str) -> core.Data | None:
        pack_name = self.get_packname(pack_name)
        data = self.get_file(pack_name, file_name)
        if data is None:
            return None

        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return None
        data.to_file(path)
        return data

    def save_file_data(
        self, pack_name: str, file_name: str, data: core.Data
    ) -> core.Data | None:
        pack_name = self.get_packname(pack_name)

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
    ) -> core.Data | None:
        pack_name, file_name = path.split("/")
        pack_name = self.get_packname(pack_name)
        return self.download(pack_name, file_name, retries, display_text)

    def download(
        self,
        pack_name: str,
        file_name: str,
        retries: int = 2,
        display_text: bool = True,
    ) -> core.Data | None:
        retries -= 1
        pack_name = self.get_packname(pack_name)

        if self.is_downloaded(pack_name, file_name):
            path = self.get_file_path(pack_name, file_name)
            if path is None:
                return None
            try:
                return path.read()
            except FileNotFoundError:
                return None

        if retries == 0:
            return None

        version = self.version

        if version is None:
            if display_text:
                self.print_no_file(pack_name, file_name)
            return None

        if display_text:
            color.ColoredText.localize(
                "downloading",
                file_name=file_name,
                pack_name=pack_name,
                country_code=self.cc.get_code(),
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
    ) -> list[tuple[str, core.Data] | None]:
        pack_name = self.get_packname(pack_name)

        callables: list[Callable[..., Any]] = []
        args: list[tuple[str, str, int, bool]] = []
        for file_name in file_names:
            callables.append(self.download)
            args.append((pack_name, file_name, 2, display_text))
        core.thread_run_many(callables, args)
        data_list: list[tuple[str, core.Data] | None] = []
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
    def get_all_downloaded_versions() -> dict[str, list[str]]:
        versions: dict[str, list[str]] = {}
        for cc in core.CountryCode.get_all_str():
            dir = GameDataGetter.get_game_data_dir().add(cc)
            if not dir.exists():
                continue
            for version in GameDataGetter.get_game_data_dir().add(cc).get_dirs():
                if not version.exists():
                    continue
                if cc in versions:
                    versions[cc].append(version.basename())
                else:
                    versions[cc] = [version.basename()]

        return versions

    @staticmethod
    def delete_old_versions(to_keep: int) -> None:
        versions = GameDataGetter.get_all_downloaded_versions()
        for cc, cc_versions in versions.items():
            cc_versions.sort(reverse=True)
            to_keep = min(to_keep, len(cc_versions))
            for version in cc_versions[to_keep:]:
                path = GameDataGetter.get_game_data_dir().add(cc).add(version)
                path.remove()

    def print_no_file(self, packname: str, file_name: str) -> None:
        if self.version is None:
            color.ColoredText.localize("failed_to_get_game_versions")
        else:
            color.ColoredText.localize(
                "failed_to_download_game_data",
                file_name=file_name,
                pack_name=packname,
                country_code=self.cc.get_code(),
                version=self.version,
            )
