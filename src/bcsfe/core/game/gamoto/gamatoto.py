from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


@dataclass
class MemberName:
    member_id: int
    rarity: int
    bonus: int
    name: str
    rarity_name: str
    description: list[str]


class GamatotoMembersName:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.members = self.read_members()

    def read_members(self) -> list[MemberName] | None:
        members: list[MemberName] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download(
            "resLocal",
            f"GamatotoExpedition_Members_name_{core.core_data.get_lang(self.save_file)}.csv",
        )
        if data is None:
            return None
        csv = core.CSV(
            data,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
            remove_empty=False,
        )
        for line in csv.lines[1:]:
            if line[0].to_int() == -1:
                continue
            members.append(
                MemberName(
                    line[0].to_int(),
                    line[1].to_int(),
                    line[2].to_int(),
                    line[3].to_str(),
                    line[4].to_str(),
                    line[5:].to_str_list(),
                )
            )
        return members

    def get_member(self, member_id: int) -> MemberName | None:
        if self.members is None:
            return None
        for member in self.members:
            if member.member_id == member_id:
                return member
        return None

    def get_members_from_ids(self, ids: list[int]) -> list[MemberName | None]:
        return [self.get_member(id) for id in ids]

    def get_all_rarity(self, rarity: int) -> list[MemberName] | None:
        if self.members is None:
            return None

        return [member for member in self.members if member.rarity == rarity]

    def get_members_from_helpers(
        self, helpers: Helpers
    ) -> list[MemberName | None]:
        return self.get_members_from_ids(
            [helper.id for helper in helpers.helpers if helper.is_valid()]
        )

    def get_all_rarity_names(self) -> list[str] | None:
        if self.members is None:
            return None
        names: dict[int, str] = {}
        for member in self.members:
            names[member.rarity] = member.rarity_name
        return [names[i] for i in range(len(names))]


@dataclass
class GamatotoLevel:
    level: int
    xp_needed: int
    discovery_bonus: int
    skin: int


@dataclass
class GamatotoLimit:
    max_level: int
    total_stages: int
    total_helpers: int


class GamatotoLevels:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.levels = self.read_levels()
        self.limit = self.read_max_level()

    def read_levels(self) -> list[GamatotoLevel] | None:
        levels: list[GamatotoLevel] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "GamatotoExpedition.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        for i, line in enumerate(csv):
            levels.append(
                GamatotoLevel(
                    i + 1, line[0].to_int(), line[1].to_int(), line[2].to_int()
                )
            )
        return levels

    def read_max_level(self) -> GamatotoLimit | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "GamatotoExpedition_Limit.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        line = csv[0]
        return GamatotoLimit(
            line[0].to_int(), line[1].to_int(), line[2].to_int()
        )

    def get_level(self, level: int) -> GamatotoLevel | None:
        if self.levels is None:
            return None
        if level < 1:
            return None
        return self.levels[level - 1]

    def get_all_levels(self) -> list[GamatotoLevel] | None:
        return self.levels

    def get_level_from_xp(self, xp: int) -> GamatotoLevel | None:
        if self.levels is None or self.limit is None:
            return None
        for level in self.levels:
            if level.level >= self.limit.max_level:
                break
            if level.xp_needed == -1:
                continue
            if xp < level.xp_needed:
                return level
        if self.limit.max_level >= len(self.levels):
            return self.levels[-1]
        return self.levels[self.limit.max_level - 1]

    def get_xp_from_level(self, level: int) -> int | None:
        if self.levels is None:
            return None
        level -= 1
        if level < 1:
            return 0
        return self.levels[level - 1].xp_needed

    def get_max_level(self) -> int | None:
        if self.limit is None:
            return None
        return self.limit.max_level

    def get_total_stages(self) -> int | None:
        if self.limit is None:
            return None
        return self.limit.total_stages

    def get_total_helpers(self) -> int | None:
        if self.limit is None:
            return None
        return self.limit.total_helpers


class Helper:
    def __init__(self, id: int):
        self.id = id

    @staticmethod
    def init() -> Helper:
        return Helper(-1)

    @staticmethod
    def read(stream: core.Data) -> Helper:
        id = stream.read_int()
        return Helper(id)

    def write(self, stream: core.Data):
        stream.write_int(self.id)

    def serialize(self) -> int:
        return self.id

    @staticmethod
    def deserialize(data: int) -> Helper:
        return Helper(data)

    def __repr__(self) -> str:
        return f"Helper(id={self.id!r})"

    def __str__(self) -> str:
        return f"Helper(id={self.id!r})"

    def is_valid(self) -> bool:
        return self.id != -1


class Helpers:
    def __init__(self, helpers: list[Helper]):
        self.helpers = helpers

    @staticmethod
    def init() -> Helpers:
        return Helpers([])

    @staticmethod
    def read(stream: core.Data) -> Helpers:
        total = stream.read_int()
        helpers: list[Helper] = []
        for _ in range(total):
            helpers.append(Helper.read(stream))
        return Helpers(helpers)

    def write(self, stream: core.Data):
        stream.write_int(len(self.helpers))
        for helper in self.helpers:
            helper.write(stream)

    def serialize(self) -> list[int]:
        return [helper.serialize() for helper in self.helpers]

    @staticmethod
    def deserialize(data: list[int]) -> Helpers:
        return Helpers([Helper.deserialize(helper) for helper in data])

    def __repr__(self) -> str:
        return f"Helpers(helpers={self.helpers!r})"

    def __str__(self) -> str:
        return f"Helpers(helpers={self.helpers!r})"


class Gamatoto:
    def __init__(
        self,
        remaining_seconds: float,
        return_flag: bool,
        xp: int,
        dest_id: int,
        recon_length: int,
        unknown: int,
        notif_value: int,
    ):
        self.remaining_seconds = remaining_seconds
        self.return_flag = return_flag
        self.xp = xp
        self.dest_id = dest_id
        self.recon_length = recon_length
        self.unknown = unknown
        self.notif_value = notif_value
        self.helpers = Helpers.init()
        self.is_ad_present = False
        self.skin = 0
        self.collab_flags: dict[int, bool] = {}
        self.collab_durations: dict[int, float] = {}

    @staticmethod
    def init() -> Gamatoto:
        return Gamatoto(
            0.0,
            False,
            0,
            0,
            0,
            0,
            0,
        )

    @staticmethod
    def read(stream: core.Data) -> Gamatoto:
        remaining_seconds = stream.read_double()
        return_flag = stream.read_bool()
        xp = stream.read_int()
        dest_id = stream.read_int()
        recon_length = stream.read_int()
        unknown = stream.read_int()
        notif_value = stream.read_int()
        return Gamatoto(
            remaining_seconds,
            return_flag,
            xp,
            dest_id,
            recon_length,
            unknown,
            notif_value,
        )

    def write(self, stream: core.Data):
        stream.write_double(self.remaining_seconds)
        stream.write_bool(self.return_flag)
        stream.write_int(self.xp)
        stream.write_int(self.dest_id)
        stream.write_int(self.recon_length)
        stream.write_int(self.unknown)
        stream.write_int(self.notif_value)

    def read_2(self, stream: core.Data):
        self.helpers = Helpers.read(stream)
        self.is_ad_present = stream.read_bool()

    def write_2(self, stream: core.Data):
        self.helpers.write(stream)
        stream.write_bool(self.is_ad_present)

    def read_skin(self, stream: core.Data):
        self.skin = stream.read_int()

    def write_skin(self, stream: core.Data):
        stream.write_int(self.skin)

    def read_collab_data(self, stream: core.Data):
        self.collab_flags: dict[int, bool] = stream.read_int_bool_dict()
        self.collab_durations: dict[int, float] = stream.read_int_double_dict()

    def write_collab_data(self, stream: core.Data):
        stream.write_int_bool_dict(self.collab_flags)
        stream.write_int_double_dict(self.collab_durations)

    def serialize(self) -> dict[str, Any]:
        return {
            "remaining_seconds": self.remaining_seconds,
            "return_flag": self.return_flag,
            "xp": self.xp,
            "dest_id": self.dest_id,
            "recon_length": self.recon_length,
            "unknown": self.unknown,
            "notif_value": self.notif_value,
            "helpers": self.helpers.serialize(),
            "is_ad_present": self.is_ad_present,
            "skin": self.skin,
            "collab_flags": self.collab_flags,
            "collab_durations": self.collab_durations,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Gamatoto:
        gamatoto = Gamatoto(
            data.get("remaining_seconds", 0.0),
            data.get("return_flag", False),
            data.get("xp", 0),
            data.get("dest_id", 0),
            data.get("recon_length", 0),
            data.get("unknown", 0),
            data.get("notif_value", 0),
        )
        gamatoto.helpers = Helpers.deserialize(data.get("helpers", []))
        gamatoto.is_ad_present = data.get("is_ad_present", False)
        gamatoto.skin = data.get("skin", 0)
        gamatoto.collab_flags = data.get("collab_flags", {})
        gamatoto.collab_durations = data.get("collab_durations", {})
        return gamatoto

    def __repr__(self):
        return (
            f"Gamatoto(remaining_seconds={self.remaining_seconds!r}, "
            f"return_flag={self.return_flag!r}, xp={self.xp!r}, "
            f"dest_id={self.dest_id!r}, recon_length={self.recon_length!r}, "
            f"unknown={self.unknown!r}, notif_value={self.notif_value!r}, "
            f"helpers={self.helpers!r}, is_ad_present={self.is_ad_present!r}, "
            f"skin={self.skin!r}, collab_flags={self.collab_flags!r}, "
            f"collab_durations={self.collab_durations!r})"
        )

    def __str__(self):
        return self.__repr__()

    def edit_xp(self, save_file: core.SaveFile):
        gamatoto_levels = core.core_data.get_gamatoto_levels(save_file)
        current_level = gamatoto_levels.get_level_from_xp(self.xp)
        if current_level is None:
            return
        xp = self.xp

        color.ColoredText.localize(
            "gamatoto_level_current", level=current_level.level, xp=xp
        )
        choice = dialog_creator.ChoiceInput(
            ["enter_raw_gamatoto_xp", "enter_gamatoto_level"],
            ["enter_raw_gamatoto_xp", "enter_gamatoto_level"],
            [],
            {},
            "edit_gamatoto_level_q",
            single_choice=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1

        if choice == 0:
            xp = dialog_creator.SingleEditor(
                "gamatoto_xp", self.xp, None, localized_item=True
            ).edit()
            current_level = gamatoto_levels.get_level_from_xp(xp)
        elif choice == 1:
            value = dialog_creator.SingleEditor(
                "gamatoto_level",
                current_level.level,
                gamatoto_levels.get_max_level(),
                localized_item=True,
            ).edit()
            xp = gamatoto_levels.get_xp_from_level(value)
            current_level = gamatoto_levels.get_level(value)

        if xp is None:
            return

        self.xp = xp

        if current_level is None:
            return

        color.ColoredText.localize(
            "gamatoto_level_success", level=current_level.level, xp=xp
        )

    def edit_helpers(self, save_file: core.SaveFile):
        members_name = core.core_data.get_gamatoto_members_name(save_file)

        gamatoto_levels = core.core_data.get_gamatoto_levels(save_file)
        max_helpers = gamatoto_levels.get_total_helpers()

        members = members_name.get_members_from_helpers(self.helpers)
        color.ColoredText.localize("current_gamatoto_helpers")
        for member in members:
            if member is None:
                continue
            color.ColoredText.localize(
                "gamatoto_helper",
                name=member.name,
                rarity_name=member.rarity_name,
            )
        rarity_names = members_name.get_all_rarity_names()
        if rarity_names is None:
            return

        total_rarity_amounts: list[int] = [0] * len(rarity_names)
        for helper in self.helpers.helpers:
            if not helper.is_valid():
                continue
            member = members_name.get_member(helper.id)
            if member is None:
                continue
            total_rarity_amounts[member.rarity] += 1

        rarity_amounts = dialog_creator.MultiEditor.from_reduced(
            "gamatoto_helpers",
            rarity_names,
            total_rarity_amounts,
            max_helpers,
            group_name_localized=True,
            cumulative_max=True,
        ).edit()

        helpers: list[Helper] = []
        for i, rarity_amount in enumerate(rarity_amounts):
            rarity_members = members_name.get_all_rarity(i)
            if rarity_members is None:
                continue
            for _ in range(rarity_amount):
                member = rarity_members.pop(0)
                helpers.append(Helper(member.member_id))
        self.helpers = Helpers(helpers)

        members = members_name.get_members_from_helpers(self.helpers)
        color.ColoredText.localize("new_gamatoto_helpers")
        for member in members:
            if member is None:
                continue
            color.ColoredText.localize(
                "gamatoto_helper",
                name=member.name,
                rarity_name=member.rarity_name,
            )


def edit_xp(save_file: core.SaveFile):
    save_file.gamatoto.edit_xp(save_file)


def edit_helpers(save_file: core.SaveFile):
    save_file.gamatoto.edit_helpers(save_file)
