from __future__ import annotations

from bcsfe import core


class MapNames:
    def __init__(
        self,
        save_file: core.SaveFile,
        code: str,
        base_index: int,
        output: bool = True,
        no_r_prefix: bool = False,
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
            name = row[1].to_str().strip()

            for i in range(total_stages):
                index = i + base_index
                if id == index:
                    if name:
                        names[i] = name
                    else:
                        names[i] = None
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

        names = self.get_map_names_in_game(self.base_index, len(self.stage_names))
        if names is None:
            return None
        self.map_names = names
        return self.map_names

    @staticmethod
    def get_code_from_id(id: int) -> str | None:
        base_id = id // 1000

        ids = {
            0: "RN",
            1: "RS",
            2: "RC",
            4: "EX",
            6: "RT",
            7: "RV",
            11: "RR",
            12: "RM",
            13: "RNA",
            14: "RB",
            16: "RD",
            20: "Z",
            21: "Z",
            22: "Z",
            24: "RA",
            25: "RH",
            27: "RCA",
            30: "DM",
            31: "RQ",
            32: "L",
            34: "RND",
        }

        return ids.get(base_id)

    @staticmethod
    def from_id(id: int, save_file: core.SaveFile) -> MapNames | None:
        code = MapNames.get_code_from_id(id)
        if code is None:
            return None
        return MapNames(save_file, code, id, no_r_prefix=True)
