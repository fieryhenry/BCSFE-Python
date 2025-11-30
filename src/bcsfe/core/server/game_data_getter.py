from __future__ import annotations
from io import BytesIO
from typing import Any, Callable

from bcsfe.cli import color

import tarfile

from bcsfe import core


class GameDataGetter:
    def __init__(
        self, cc: core.CountryCode, gv: core.GameVersion, do_print: bool = True
    ):
        self.repo_url = core.core_data.config.get_game_data_repo()
        self.print = do_print
        self.lang = core.core_data.config.get_str(core.ConfigKey.LOCALE)
        self.cc = cc.get_cc_lang()
        self.real_cc = cc
        self.gv = gv
        self.cc = self.cc if not self.cc.is_lang() else self.real_cc
        self.version, exact_match = self.find_gv(self.cc, gv)

        self.all_versions = None
        self.url = None
        self.filepath = None

        if exact_match:
            return

        self.metadata = self.get_metadata()
        if self.metadata is None:
            return
        self.all_versions = self.get_versions(self.metadata)
        self.url = self.metadata.get("base_url")
        if self.all_versions is not None:
            self.version, self.filepath = self.get_version(self.all_versions, self.cc)

    def find_gv(
        self, cc: core.CountryCode, gv: core.GameVersion
    ) -> tuple[str | None, bool]:
        versions = GameDataGetter.get_all_downloaded_versions().get(cc.get_code())
        if versions is None:
            return None, False

        versions_int = [
            core.GameVersion.from_string(version).game_version for version in versions
        ]

        versions_int.sort()

        for version in versions_int:
            if version >= gv.game_version:
                return core.GameVersion(version).to_string(), version == gv.game_version
        return None, False

    def does_save_version_match(self, save_file: core.SaveFile) -> bool:
        if self.version is None:
            return False

        return save_file.game_version == self.version

    def get_version(
        self, versions: dict[str, dict[str, str]], cc: core.CountryCode
    ) -> tuple[str | None, str | None]:
        cc_versions = versions.get(cc.get_code())
        if cc_versions is None:
            return None, None
        if not cc_versions:
            return None, None
        gv_string = self.gv.to_string()
        if gv_string not in cc_versions:
            cc_version_keys = list(cc_versions.keys())
            cc_version_keys.sort()
            for version in cc_version_keys:
                if (
                    core.GameVersion.from_string(version).game_version
                    >= self.gv.game_version
                ):
                    return version, cc_versions[version]
            return cc_version_keys[-1], cc_versions[cc_version_keys[-1]]
        return gv_string, cc_versions[gv_string]

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

    def get_versions(self, metdata: dict[str, Any]) -> dict[str, dict[str, str]] | None:
        return metdata.get("versions")

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
        pack_name = self.get_packname(pack_name)
        path = self.get_version_path()
        if path is None:
            return None
        return path.add(pack_name).generate_dirs().add(file_name)

    def download_version_data(self):
        if self.url is None or self.filepath is None or self.version is None:
            return None
        url = self.url + self.filepath

        if self.print:
            color.ColoredText.localize("downloading_compressed_data", url=url)

        downloaded_data = core.RequestHandler(url).get()
        if downloaded_data is None:
            if self.print:
                color.ColoredText.localize("no_internet")
            return None

        archive = tarfile.open(
            name=self.filepath, fileobj=BytesIO(downloaded_data.content)
        )

        outdir = (
            GameDataGetter.get_game_data_dir().add(self.cc.get_code()).add(self.version)
        ).generate_dirs()

        archive.extractall(outdir.path)

        outdir.add("downloaded").write(core.Data())

        return True

    def get_version_path(self) -> core.Path | None:
        if self.version is None:
            return None
        return (
            GameDataGetter.get_game_data_dir().add(self.cc.get_code()).add(self.version)
        ).generate_dirs()

    def has_downloaded(self) -> bool:
        path = self.get_version_path()
        if path is None:
            return False
        return path.add("downloaded").exists()

    def get_file(self, pack_name: str, file_name: str) -> core.Data | bool:
        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return False

        if path.exists():
            return path.read()
        else:
            if self.has_downloaded():
                return True
            if self.download_version_data() is None:
                return False

            path = self.get_file_path(pack_name, file_name)
            if path is None:
                return False

            if path.exists():
                return path.read()
            return self.has_downloaded()

    def save_file(self, pack_name: str, file_name: str) -> core.Data | bool:
        pack_name = self.get_packname(pack_name)
        data = self.get_file(pack_name, file_name)
        if isinstance(data, bool):
            return data

        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return False
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

        if display_text and not self.has_downloaded():
            color.ColoredText.localize(
                "downloading",
                file_name=file_name,
                pack_name=pack_name,
                country_code=self.cc.get_code(),
                version=version,
            )
        data = self.save_file(pack_name, file_name)
        if isinstance(data, bool):
            if not data and display_text:
                self.print_no_file(pack_name, file_name)
            return None

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
                if not version.add("downloaded").exists():
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
                url=self.url,
            )
