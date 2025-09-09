from __future__ import annotations
from typing import Any, Callable

import bs4
from bcsfe import core
from bcsfe.cli import color


class MapNames:
    def __init__(
        self,
        save_file: core.SaveFile,
        code: str,
        output: bool = True,
        no_r_prefix: bool = False,
        base_index: int | None = None,
    ):
        self.save_file = save_file
        self.out = output
        self.code = code
        self.base_index = base_index
        self.no_r_prefix = no_r_prefix
        self.gdg = core.core_data.get_game_data_getter(self.save_file)
        self.map_names: dict[int, str | None] = {}
        self.stage_names: dict[int, list[str]] = {}
        self.get_map_names()
        self.save_map_names()

    def get_file_path(self) -> core.Path:
        return (
            core.Path("map_names", True)
            .add(self.code)
            .generate_dirs()
            .add(f"{self.gdg.cc.get_code()}.json")
        )

    def read_map_names(self) -> dict[int, str | None]:
        file_path = self.get_file_path()
        if file_path.exists():
            names = core.JsonFile(file_path.read()).to_object()
            for id in names.keys():
                self.map_names[int(id)] = names[id]
            return names
        return {}

    def download_map_name(self, id: int):
        file_name = f"{self.code}{str(id).zfill(3)}.html"
        if self.gdg.cc != core.CountryCodeType.JP:
            url = f"https://ponosgames.com/information/appli/battlecats/stage/{self.gdg.cc.get_code()}/{file_name}"
        else:
            url = (
                f"https://ponosgames.com/information/appli/battlecats/stage/{file_name}"
            )
        data = core.RequestHandler(url).get()
        if data is None:
            return None
        if data.status_code != 200:
            return None
        html = data.content.decode("utf-8")
        bs = bs4.BeautifulSoup(html, "html.parser")
        name = bs.find("h2")
        if name is None:
            return None
        name = name.text.strip()
        if name:
            self.map_names[id] = name
        else:
            self.map_names[id] = None
        return name

    def get_map_names_in_game(
        self, base_index: int, total_stages: int
    ) -> dict[int, str | None] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        map_name_data = gdg.download("resLocal", "Map_Name.csv")
        if map_name_data is None:
            return None

        csv = core.CSV(
            map_name_data, core.Delimeter.from_country_code_res(self.save_file.cc)
        )
        names: dict[int, str | None] = {}
        for row in csv:
            id = row[0].to_int()
            name = row[1].to_str()

            for i in range(total_stages):
                index = i + base_index
                if id == index:
                    names[i] = name
                    break

        return names

    def get_map_names(self) -> dict[int, str | None] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        r_prefix = "" if self.no_r_prefix else "R"
        stage_names = gdg.download(
            "resLocal",
            f"StageName_{r_prefix}{self.code}_{core.core_data.get_lang(self.save_file)}.csv",
        )
        if stage_names is None:
            return None
        csv = core.CSV(
            stage_names,
            core.Delimeter.from_country_code_res(self.save_file.cc),
        )
        for i, row in enumerate(csv):
            stage_names_row = row.to_str_list()
            if not stage_names_row:
                continue
            self.stage_names[i] = stage_names_row

        if self.base_index is None:
            names = self.read_map_names()
            total_downloaded = len(names)
            funcs: list[Callable[..., Any]] = []
            args: list[tuple[Any]] = []
            for i in range(len(csv)):
                if i < total_downloaded:
                    continue
                funcs.append(self.download_map_name)
                args.append((i,))

            if self.out:
                color.ColoredText.localize("downloading_map_names", code=self.code)
            core.thread_run_many(funcs, args)
        else:
            names = self.get_map_names_in_game(self.base_index, len(self.stage_names))
            if names is None:
                return None
            self.map_names = names
        return self.map_names

    def save_map_names(self):
        file_path = self.get_file_path()
        self.map_names = dict(sorted(self.map_names.items(), key=lambda item: item[0]))
        core.JsonFile.from_object(self.map_names).to_file(file_path)
