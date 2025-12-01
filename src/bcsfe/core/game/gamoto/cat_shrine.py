from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class CatShrine:
    def __init__(
        self,
        unknown: bool,
        stamp_1: float,
        stamp_2: float,
        shrine_gone: bool,
        flags: list[int],
        xp_offering: int,
    ):
        self.unknown = unknown
        self.stamp_1 = stamp_1
        self.stamp_2 = stamp_2
        self.shrine_gone = shrine_gone
        self.flags = flags
        self.xp_offering = xp_offering
        self.dialogs = 0

    @staticmethod
    def init() -> CatShrine:
        return CatShrine(False, 0.0, 0.0, False, [], 0)

    @staticmethod
    def read(stream: core.Data) -> CatShrine:
        unknown = stream.read_bool()
        stamp_1 = stream.read_double()
        stamp_2 = stream.read_double()
        shrine_gone = stream.read_bool()
        flags = stream.read_byte_list(length=stream.read_byte())
        xp_offering = stream.read_long()
        return CatShrine(unknown, stamp_1, stamp_2, shrine_gone, flags, xp_offering)

    def write(self, stream: core.Data):
        stream.write_bool(self.unknown)
        stream.write_double(self.stamp_1)
        stream.write_double(self.stamp_2)
        stream.write_bool(self.shrine_gone)
        stream.write_byte(len(self.flags))
        stream.write_byte_list(self.flags, write_length=False)
        stream.write_long(self.xp_offering)

    def read_dialogs(self, stream: core.Data):
        self.dialogs = stream.read_int()

    def write_dialogs(self, stream: core.Data):
        stream.write_int(self.dialogs)

    def serialize(self) -> dict[str, Any]:
        return {
            "unknown": self.unknown,
            "stamp_1": self.stamp_1,
            "stamp_2": self.stamp_2,
            "shrine_gone": self.shrine_gone,
            "flags": self.flags,
            "xp_offering": self.xp_offering,
            "dialogs": self.dialogs,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> CatShrine:
        shrine = CatShrine(
            data.get("unknown", False),
            data.get("stamp_1", 0.0),
            data.get("stamp_2", 0.0),
            data.get("shrine_gone", False),
            data.get("flags", []),
            data.get("xp_offering", 0),
        )
        shrine.dialogs = data.get("dialogs", 0)
        return shrine

    def __repr__(self):
        return (
            f"CatShrine("
            f"unknown={self.unknown}, "
            f"stamp_1={self.stamp_1}, "
            f"stamp_2={self.stamp_2}, "
            f"shrine_gone={self.shrine_gone}, "
            f"flags={self.flags}, "
            f"xp_offering={self.xp_offering}, "
            f"dialogs={self.dialogs}"
            f")"
        )

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def edit_catshrine(save_file: core.SaveFile):
        shrine = save_file.cat_shrine
        options = [
            "shrine_level",
            "shrine_xp",
            "make_catshrine_appear",
            "make_catshrine_disappear",
        ]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="cat_shrine_choice_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return
        choice -= 1

        if choice == 2:
            shrine.shrine_gone = False
            color.ColoredText.localize("cat_shrine_edited")
            return
        elif choice == 3:
            shrine.shrine_gone = True
            color.ColoredText.localize("cat_shrine_edited")
            return

        data = core.core_data.get_cat_shrine_levels(save_file)

        xp = shrine.xp_offering
        level = data.get_level_from_xp(xp)

        color.ColoredText.localize("current_shrine_xp_level", level=level, xp=xp)

        if choice == 0:
            max_level = data.get_max_level()
            if max_level is None:
                return
            level = dialog_creator.IntInput(
                min=1, max=max_level
            ).get_input_locale_while("shrine_level_dialog", {"max_level": max_level})
            if level is None:
                return
            shrine.xp_offering = data.get_xp_from_level(level)
        elif choice == 1:
            max_xp = data.get_max_xp()
            if max_xp is None:
                return
            xp = dialog_creator.IntInput(min=0, max=max_xp).get_input_locale_while(
                "shrine_xp_dialog", {"max_xp": max_xp}
            )
            if xp is None:
                return
            shrine.xp_offering = xp

        xp = shrine.xp_offering
        if xp is None:
            return
        level = data.get_level_from_xp(xp)
        if level is None:
            return

        shrine.dialogs = level - 1
        shrine.shrine_gone = False
        shrine.stamp_1 = 0.0
        shrine.stamp_2 = 0.0

        color.ColoredText.localize("current_shrine_xp_level", level=level, xp=xp)

        color.ColoredText.localize("cat_shrine_edited")


class CatShrineLevels:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.boundaries = self.get_boundaries()

    def get_boundaries(self) -> list[int] | None:
        file_name = "jinja_level.csv"
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", file_name)
        if data is None:
            return None
        csv = core.CSV(
            data,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
        )
        boundaries: list[int] = []
        counter = 0
        for row in csv:
            xp = row[0].to_int()
            counter += xp
            boundaries.append(counter)

        return boundaries

    def get_level_from_xp(self, xp: int) -> int | None:
        if self.boundaries is None:
            return None
        for i, boundary in enumerate(self.boundaries):
            if xp < boundary:
                return i + 1
        return len(self.boundaries)

    def get_xp_from_level(self, level: int) -> int | None:
        if self.boundaries is None:
            return None
        if level < 1:
            return 0
        if level > len(self.boundaries):
            return self.get_max_xp()
        return self.boundaries[level - 2]

    def get_max_level(self) -> int | None:
        if self.boundaries is None:
            return None
        return len(self.boundaries)

    def get_max_xp(self) -> int | None:
        if self.boundaries is None:
            return None
        return max(self.boundaries)
