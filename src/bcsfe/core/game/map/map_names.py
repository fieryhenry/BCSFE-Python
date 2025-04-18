from __future__ import annotations
from typing import Any, Callable

import bs4
from bcsfe import core
from bcsfe.cli import color


class MapNames:
    def __init__(
        self, save_file: core.SaveFile, code: str, output: bool = True
    ):
        self.save_file = save_file
        self.out = output
        self.code = code
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
            url = f"https://ponosgames.com/information/appli/battlecats/stage/{file_name}"
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

    def get_map_names(self) -> dict[int, str | None] | None:
        names = self.read_map_names()
        gdg = core.core_data.get_game_data_getter(self.save_file)
        stage_names = gdg.download(
            "resLocal",
            f"StageName_R{self.code}_{core.core_data.get_lang(self.save_file)}.csv",
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
        return self.map_names

    def save_map_names(self):
        file_path = self.get_file_path()
        self.map_names = dict(
            sorted(self.map_names.items(), key=lambda item: item[0])
        )
        core.JsonFile.from_object(self.map_names).to_file(file_path)
