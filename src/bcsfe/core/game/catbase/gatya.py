from __future__ import annotations
import enum
from typing import Any, Callable
from bcsfe import core
from bcsfe.cli import dialog_creator, color


class Gatya:
    def __init__(self, rare_seed: int, normal_seed: int):
        self.rare_seed = rare_seed
        self.normal_seed = normal_seed
        self.event_seed = 0
        self.stepup_stage_3_cooldown = 0
        self.previous_normal_roll = 0
        self.previous_normal_roll_type = 0
        self.previous_rare_roll = 0
        self.previous_rare_roll_type = 0
        self.unknown1 = False
        self.roll_single = False
        self.roll_multi = False
        self.trade_progress = 0
        self.step_up_stages: dict[int, int] = {}
        self.stepup_durations: dict[int, float] = {}

        self.gatya_data_set: GatyaDataSet | None = None

    @staticmethod
    def init() -> Gatya:
        return Gatya(0, 0)

    @staticmethod
    def read_rare_normal_seed(data: core.Data, gv: core.GameVersion) -> Gatya:
        if gv < 33:
            return Gatya(data.read_ulong(), data.read_ulong())
        return Gatya(data.read_uint(), data.read_uint())

    def read_event_seed(self, data: core.Data, gv: core.GameVersion):
        if gv < 33:
            self.event_seed = data.read_ulong()
        else:
            self.event_seed = data.read_uint()

    def write_rare_normal_seed(self, data: core.Data):
        data.write_uint(self.rare_seed)
        data.write_uint(self.normal_seed)

    def write_event_seed(self, data: core.Data):
        data.write_uint(self.event_seed)

    def read2(self, data: core.Data):
        self.stepup_stage_3_cooldown = data.read_int()
        self.previous_normal_roll = data.read_int()
        self.previous_normal_roll_type = data.read_int()
        self.previous_rare_roll = data.read_int()
        self.previous_rare_roll_type = data.read_int()
        self.unknown1 = data.read_bool()
        self.roll_single = data.read_bool()
        self.roll_multi = data.read_bool()

    def write2(self, data: core.Data):
        data.write_int(self.stepup_stage_3_cooldown)
        data.write_int(self.previous_normal_roll)
        data.write_int(self.previous_normal_roll_type)
        data.write_int(self.previous_rare_roll)
        data.write_int(self.previous_rare_roll_type)
        data.write_bool(self.unknown1)
        data.write_bool(self.roll_single)
        data.write_bool(self.roll_multi)

    def read_trade_progress(self, data: core.Data):
        self.trade_progress = data.read_int()

    def write_trade_progress(self, data: core.Data):
        data.write_int(self.trade_progress)

    def read_stepup(self, data: core.Data):
        self.step_up_stages: dict[int, int] = {}
        total = data.read_int()
        for _ in range(total):
            key = data.read_int()
            self.step_up_stages[key] = data.read_int()

        self.stepup_durations: dict[int, float] = {}
        total = data.read_int()
        for _ in range(total):
            key = data.read_int()
            self.stepup_durations[key] = data.read_double()

    def write_stepup(self, data: core.Data):
        data.write_int(len(self.step_up_stages))
        for id, stage in self.step_up_stages.items():
            data.write_int(id)
            data.write_int(stage)

        data.write_int(len(self.stepup_durations))
        for id, duration in self.stepup_durations.items():
            data.write_int(id)
            data.write_double(duration)

    def serialize(self) -> dict[str, Any]:
        return {
            "rare_seed": self.rare_seed,
            "normal_seed": self.normal_seed,
            "stepup_stage_3_cooldown": self.stepup_stage_3_cooldown,
            "previous_normal_roll": self.previous_normal_roll,
            "previous_normal_roll_type": self.previous_normal_roll_type,
            "previous_rare_roll": self.previous_rare_roll,
            "previous_rare_roll_type": self.previous_rare_roll_type,
            "unknown1": self.unknown1,
            "roll_single": self.roll_single,
            "roll_multi": self.roll_multi,
            "trade_progress": self.trade_progress,
            "event_seed": self.event_seed,
            "step_up_stages": self.step_up_stages,
            "stepup_durations": self.stepup_durations,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Gatya:
        gatya = Gatya(data.get("rare_seed", 0), data.get("normal_seed", 0))
        gatya.stepup_stage_3_cooldown = data.get("stepup_stage_3_cooldown", 0)
        gatya.previous_normal_roll = data.get("previous_normal_roll", 0)
        gatya.previous_normal_roll_type = data.get("previous_normal_roll_type", 0)
        gatya.previous_rare_roll = data.get("previous_rare_roll", 0)
        gatya.previous_rare_roll_type = data.get("previous_rare_roll_type", 0)
        gatya.unknown1 = data.get("unknown1", False)
        gatya.roll_single = data.get("roll_single", False)
        gatya.roll_multi = data.get("roll_multi", False)
        gatya.trade_progress = data.get("trade_progress", 0)
        gatya.event_seed = data.get("event_seed", 0)
        gatya.step_up_stages = data.get("step_up_stages", {})
        gatya.stepup_durations = data.get("stepup_durations", {})
        return gatya

    def __repr__(self) -> str:
        return f"Gatya({self.serialize()})"

    def __str__(self) -> str:
        return f"Gatya({self.serialize()})"

    def edit_rare_gatya_seed(self):
        self.rare_seed = dialog_creator.SingleEditor(
            "rare_gatya_seed",
            self.rare_seed,
            None,
            localized_item=True,
            signed=False,
        ).edit()

    def edit_normal_gatya_seed(self):
        self.normal_seed = dialog_creator.SingleEditor(
            "normal_gatya_seed",
            self.normal_seed,
            None,
            localized_item=True,
            signed=False,
        ).edit()

    def edit_event_gatya_seed(self):
        self.event_seed = dialog_creator.SingleEditor(
            "event_gatya_seed",
            self.event_seed,
            None,
            localized_item=True,
            signed=False,
        ).edit()

    def read_gatya_data_set(self, save_file: core.SaveFile) -> GatyaDataSet:
        if self.gatya_data_set is not None:
            return self.gatya_data_set
        self.gatya_data_set = GatyaDataSet(save_file)
        return self.gatya_data_set


class GatyaDataSet:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.gatya_data_set = self.load_gatya_data_set("R", 1)

    def load_gatya_data_set(self, rarity: str, id: int) -> list[list[int]] | None:
        file_name = f"GatyaDataSet{rarity.upper()[0]}{id}.csv"
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", file_name)
        if data is None:
            return None
        csv = core.CSV(data)
        dt: list[list[int]] = []
        for line in csv:
            cat_ids: list[int] = []
            for cat_id in line:
                cat_id = cat_id.to_int()
                if cat_id != -1:
                    cat_ids.append(cat_id)
            dt.append(cat_ids)
        return dt

    def get_cat_ids(self, gatya_id: int) -> list[int] | None:
        if self.gatya_data_set is None:
            return None
        try:
            return self.gatya_data_set[gatya_id]
        except IndexError:
            return None


class GatyaInfo:
    def __init__(self, gatya_id: int, cc: core.CountryCode, type_str: str = "R"):
        self.gatya_id = gatya_id
        self.cc = cc
        self.gatya_data_set: GatyaDataSet | None = None
        self.type = type_str
        self.data: core.Data | None = None

    def get_id_str(self) -> str:
        return f"{self.gatya_id:03}"

    def get_cc_str(self) -> str:
        if self.cc == core.CountryCode("jp"):
            return ""
        return self.cc.get_patching_code() + "/"

    def get_url(self) -> str:
        return f"https://ponosgames.com/information/appli/battlecats/gacha/rare/{self.get_cc_str()}{self.type}{self.get_id_str()}.html"

    def download_data(self) -> core.Data | None:
        url = self.get_url()

        response = core.RequestHandler(url).get()
        if response is None:
            return
        data = core.Data(response.content)

        self.save_data(data)
        return data

    def get_file_path(self) -> core.Path:
        return (
            core.Path.get_documents_folder()
            .add("other_game_data")
            .add(self.cc.get_code())
            .add("gatya_info")
            .generate_dirs()
            .add(f"{self.type}{self.get_id_str()}.html")
        )

    def save_data(self, data: core.Data):
        try:
            data.to_file(self.get_file_path())
        except Exception as e:
            color.ColoredText.localize("save_gatya_error", error=e)
        self.data = data

    def load_data_from_file(self) -> core.Data | None:
        if not self.get_file_path().exists():
            return None
        return core.Data.from_file(self.get_file_path())

    def get_data(self) -> core.Data | None:
        if self.data is not None:
            return self.data
        data = self.load_data_from_file()
        if data is None:
            data = self.download_data()
        return data

    def get_name(self) -> str | None:
        data = self.get_data()
        if data is None:
            return None
        # find <h2>...</h2>
        data = data.get_bytes()
        h2 = data.find(b"<h2>")
        if h2 == -1:
            return None
        h2_end = data.find(b"</h2>", h2)
        if h2_end == -1:
            return None
        text = data[h2 + 4 : h2_end].decode("utf-8")
        # remove <span...</span>
        span = text.find("<span")
        if span == -1:
            return text
        span_end = text.find("</span>", span)
        if span_end == -1:
            return text
        return text[:span] + text[span_end + 7 :]


class GatyaInfos:
    def __init__(self, save_file: core.SaveFile, type_str: str = "R", set_id: int = 1):
        self.save_file = save_file
        self.type = type_str
        self.set_id = set_id
        self.gatya_data_set = GatyaDataSet(save_file).load_gatya_data_set(
            type_str, set_id
        )
        self.infos: list[GatyaInfo] = []
        self.got_all = False

    def get_all(
        self,
        threaded: bool = True,
        print_progress: bool = True,
        max_threads: int = 16,
    ):
        if self.gatya_data_set is None:
            return
        all_ids = len(self.gatya_data_set)
        if threaded:
            funcs: list[Callable[..., Any]] = []
            args: list[list[Any]] = []
            for id in range(all_ids):
                funcs.append(self.get)
                args.append([id, print_progress])
            core.thread_run_many(funcs, args, max_threads=max_threads)

        else:
            for id in range(all_ids):
                self.infos.append(self.get(id, print_progress=print_progress))

        self.got_all = True

    def get(self, gatya_id: int, print_progress: bool):
        if print_progress:
            color.ColoredText.localize(
                "gatya_info_progress",
                current=len(self.infos or []) + 1,
                total=len(self.gatya_data_set or []),
            )
        info = GatyaInfo(gatya_id, self.save_file.cc, self.type)
        info.get_data()
        self.infos.append(info)
        return info

    def get_info(self, gatya_id: int) -> GatyaInfo | None:
        if self.infos:
            return self.infos[gatya_id]
        return None

    def get_all_names(self) -> dict[int, str]:
        if not self.got_all:
            self.get_all(True, max_threads=64)
        names: dict[int, str] = {}
        for info in self.infos:
            names[
                info.gatya_id
            ] = info.get_name() or core.core_data.local_manager.get_key(
                "unknown_banner"
            )

        return names


class GatyaDataOptionSet:
    def __init__(
        self,
        id: int,
        banner_on: bool,
        ticket_item_id: int,
        anim_id: int,
        button_cut_id: int,
        series_id: int,
        menu_cut_id: int,
        char_id: int | None,
        wait_maanim: bool | None,
    ):
        self.id = id
        self.banner_on = banner_on
        self.ticket_item_id = ticket_item_id
        self.anim_id = anim_id
        self.button_cut_id = button_cut_id
        self.series_id = series_id
        self.menu_cut_id = menu_cut_id
        self.char_id = char_id
        self.wait_maanim = wait_maanim

    @staticmethod
    def from_csv_row(row: core.Row) -> GatyaDataOptionSet:
        return GatyaDataOptionSet(
            row.next_int(),
            row.next_bool(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int(),
            row.next_int_opt(),
            row.next_bool_opt(),
        )


class GatyaEventType(enum.Enum):
    NORMAL = "N"
    RARE = "R"
    EVENT = "E"


class GatyaDataOption:
    def __init__(self, sets: list[GatyaDataOptionSet]):
        self.sets = sets

    def get(self, set_id: int) -> GatyaDataOptionSet | None:
        for gset in self.sets:
            if gset.id == set_id:
                return gset

        return None

    @staticmethod
    def from_csv(csv: core.CSV) -> GatyaDataOption:
        sets: list[GatyaDataOptionSet] = []
        csv.read_line()  # skip headers
        for row in csv:
            sets.append(GatyaDataOptionSet.from_csv_row(row))

        return GatyaDataOption(sets)

    @staticmethod
    def from_data(data: core.Data) -> GatyaDataOption:
        return GatyaDataOption.from_csv(core.CSV(data, "\t"))

    @staticmethod
    def get_filename(event_type: GatyaEventType) -> str:
        return f"GatyaData_Option_Set{event_type.value}.tsv"

    @staticmethod
    def read(
        save_file: core.SaveFile, e_type: GatyaEventType
    ) -> GatyaDataOption | None:
        gdg = core.core_data.get_game_data_getter(save_file)

        data = gdg.download("DataLocal", GatyaDataOption.get_filename(e_type))
        if data is None:
            return None

        return GatyaDataOption.from_data(data)
