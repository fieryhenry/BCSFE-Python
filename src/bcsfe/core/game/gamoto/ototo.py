from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator, color


@dataclass
class LevelPartRecipeUnlock:
    index: int
    cannon_id: int
    part_id: int
    unknown: int
    unknown2: int
    level: int


class CastleRecipeUnlock:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.level_part_recipe_unlocks = self.get_recipe_unlocks()

    def get_recipe_unlocks(self) -> list[LevelPartRecipeUnlock] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "CastleRecipeUnlock.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        level_part_recipe_unlocks: list[LevelPartRecipeUnlock] = []
        for i, line in enumerate(csv):
            level_part_recipe_unlocks.append(
                LevelPartRecipeUnlock(
                    index=i,
                    cannon_id=line[0].to_int(),
                    part_id=line[1].to_int(),
                    unknown=line[2].to_int(),
                    unknown2=line[3].to_int(),
                    level=line[4].to_int(),
                )
            )

        return level_part_recipe_unlocks

    def get_recipe_unlock(self, index: int) -> LevelPartRecipeUnlock | None:
        if self.level_part_recipe_unlocks is None:
            return None
        for recipe_unlock in self.level_part_recipe_unlocks:
            if recipe_unlock.index == index:
                return recipe_unlock

        return None

    def get_max_level(self, cannon_id: int, part_id: int) -> int | None:
        if self.level_part_recipe_unlocks is None:
            return None
        max_level = 0

        for recipe_unlock in self.level_part_recipe_unlocks:
            if (
                recipe_unlock.cannon_id == cannon_id
                and recipe_unlock.part_id == part_id
            ):
                if recipe_unlock.level > max_level:
                    max_level = recipe_unlock.level

        return max_level

    def get_max_part_level(self, part_id: int) -> int | None:
        if self.level_part_recipe_unlocks is None:
            return None
        max_level = 0
        for recipe_unlock in self.level_part_recipe_unlocks:
            if recipe_unlock.part_id == part_id:
                if recipe_unlock.level > max_level:
                    max_level = recipe_unlock.level

        return max_level


@dataclass
class CannonDescription:
    cannon_id: int
    build_name: str
    foundation_build_description: str
    style_build_description: str
    effect_build_description: str
    cannon_build_description: str
    cannon_name: str
    foundation_name: str
    style_name: str
    effect_description: str
    improve_foundation_description: str
    improve_style_description: str
    improved_foundation_name: str
    improved_style_name: str
    improved_effect1_description: str
    improved_effect2_description: str

    def get_part_names(self) -> list[str]:
        effect_name = self.effect_build_description.split("<br>")[0]
        if not effect_name:
            effect_name = self.build_name
        return [
            effect_name,
            self.improve_foundation_description.split("<br>")[0],
            self.improve_style_description.split("<br>")[0],
        ]

    def get_part_name(self, index: int) -> str:
        return self.get_part_names()[index]

    def get_longest_part_name(self) -> str:
        return max(self.get_part_names(), key=len)

    def get_cannon_name(self) -> str:
        return self.cannon_name


class CannonDescriptions:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.cannon_descriptions = self.get_cannon_descriptions()

    def get_cannon_descriptions(self) -> list[CannonDescription] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", "CastleRecipeDescriptions.csv")
        if data is None:
            return None
        csv = core.CSV(
            data,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
            remove_empty=False,
        )
        cannon_descriptions: list[CannonDescription] = []
        for line in csv:
            cannon_descriptions.append(
                CannonDescription(
                    cannon_id=line[0].to_int(),
                    build_name=line[1].to_str(),
                    foundation_build_description=line[2].to_str(),
                    style_build_description=line[3].to_str(),
                    effect_build_description=line[4].to_str(),
                    cannon_build_description=line[5].to_str(),
                    cannon_name=line[6].to_str(),
                    foundation_name=line[7].to_str(),
                    style_name=line[8].to_str(),
                    effect_description=line[9].to_str(),
                    improve_foundation_description=line[10].to_str(),
                    improve_style_description=line[11].to_str(),
                    improved_foundation_name=line[12].to_str(),
                    improved_style_name=line[13].to_str(),
                    improved_effect1_description=line[14].to_str(),
                    improved_effect2_description=line[15].to_str(),
                )
            )

        return cannon_descriptions

    def get_cannon_description(
        self, cannon_id: int
    ) -> CannonDescription | None:
        if self.cannon_descriptions is None:
            return None
        for cannon_description in self.cannon_descriptions:
            if cannon_description.cannon_id == cannon_id:
                return cannon_description

        return None

    def get_longest_longest_part_name(self) -> str | None:
        if self.cannon_descriptions is None:
            return None
        longest_part_name = ""
        for cannon_description in self.cannon_descriptions:
            l_name = cannon_description.get_longest_part_name()
            if len(l_name) > len(longest_part_name):
                longest_part_name = l_name

        return longest_part_name


class Cannon:
    def __init__(self, development: int, levels: list[int]):
        self.development = development
        self.levels = levels

    @staticmethod
    def init() -> Cannon:
        return Cannon(0, [])

    @staticmethod
    def read(stream: core.Data) -> Cannon:
        total = stream.read_int()
        levels: list[int] = []
        development = stream.read_int()
        for _ in range(total - 1):
            levels.append(stream.read_int())
        return Cannon(development, levels)

    def write(self, stream: core.Data):
        stream.write_int(len(self.levels) + 1)
        stream.write_int(self.development)
        for level in self.levels:
            stream.write_int(level)

    def serialize(self) -> list[int]:
        return [self.development] + self.levels

    @staticmethod
    def deserialize(data: list[int]) -> Cannon:
        return Cannon(data[0], data[1:])

    def __repr__(self):
        return f"Cannon({self.development}, {self.levels})"

    def __str__(self):
        return f"Cannon({self.development}, {self.levels})"


class Cannons:
    def __init__(
        self, cannons: dict[int, Cannon], selected_parts: list[list[int]]
    ):
        self.cannons = cannons
        self.selected_parts = selected_parts

    @staticmethod
    def init(gv: core.GameVersion) -> Cannons:
        cannnons = {}
        if gv < 80200:
            selected_parts = [[0, 0, 0]]
        else:
            if gv > 90699:
                total_selected_parts = 0
            else:
                total_selected_parts = 10

            selected_parts = [[0, 0, 0] for _ in range(total_selected_parts)]
        return Cannons(cannnons, selected_parts)

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> Cannons:
        total = stream.read_int()
        cannons: dict[int, Cannon] = {}
        for _ in range(total):
            cannon_id = stream.read_int()
            cannon = Cannon.read(stream)
            cannons[cannon_id] = cannon
        if gv < 80200:
            selected_parts = [stream.read_int_list(length=3)]
        else:
            if gv > 90699:
                total_selected_parts = stream.read_byte()
            else:
                total_selected_parts = 10

            selected_parts: list[list[int]] = []
            for _ in range(total_selected_parts):
                selected_parts.append(stream.read_byte_list(length=3))

        return Cannons(cannons, selected_parts)

    def write(self, stream: core.Data, gv: core.GameVersion):
        stream.write_int(len(self.cannons))
        for cannon_id, cannon in self.cannons.items():
            stream.write_int(cannon_id)
            cannon.write(stream)
        if gv < 80200:
            stream.write_int_list(
                self.selected_parts[0], write_length=False, length=3
            )
        else:
            if gv > 90699:
                stream.write_byte(len(self.selected_parts))

            for part in self.selected_parts:
                stream.write_byte_list(part, write_length=False, length=3)

    def serialize(self) -> dict[str, Any]:
        return {
            "cannons": {
                cannon_id: cannon.serialize()
                for cannon_id, cannon in self.cannons.items()
            },
            "selected_parts": self.selected_parts,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Cannons:
        return Cannons(
            {
                cannon_id: Cannon.deserialize(cannon)
                for cannon_id, cannon in data.get("cannons", {}).items()
            },
            data.get("selected_parts", []),
        )

    def __repr__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"

    def __str__(self):
        return f"Cannons({self.cannons}, {self.selected_parts})"


class Ototo:
    def __init__(
        self,
        base_materials: core.BaseMaterials,
        game_version: core.GameVersion | None = None,
    ):
        self.base_materials = base_materials
        self.remaining_seconds = 0.0
        self.return_flag = False
        self.improve_id = 0
        self.engineers = 0
        self.cannons = Cannons.init(game_version) if game_version else None

    @staticmethod
    def init(game_version: core.GameVersion) -> Ototo:
        return Ototo(core.BaseMaterials.init(), game_version)

    @staticmethod
    def read(stream: core.Data) -> Ototo:
        bm = core.BaseMaterials.read(stream)
        return Ototo(bm)

    def write(self, stream: core.Data):
        self.base_materials.write(stream)

    def read_2(self, stream: core.Data, gv: core.GameVersion):
        self.remaining_seconds = stream.read_double()
        self.return_flag = stream.read_bool()
        self.improve_id = stream.read_int()
        self.engineers = stream.read_int()
        self.cannons = Cannons.read(stream, gv)

    def write_2(self, stream: core.Data, gv: core.GameVersion):
        stream.write_double(self.remaining_seconds)
        stream.write_bool(self.return_flag)
        stream.write_int(self.improve_id)
        stream.write_int(self.engineers)
        if self.cannons is None:
            Cannons.init(gv).write(stream, gv)
        else:
            self.cannons.write(stream, gv)

    def serialize(self) -> dict[str, Any]:
        return {
            "base_materials": self.base_materials.serialize(),
            "remaining_seconds": self.remaining_seconds,
            "return_flag": self.return_flag,
            "improve_id": self.improve_id,
            "engineers": self.engineers,
            "cannons": self.cannons.serialize() if self.cannons else None,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Ototo:
        ototo = Ototo(
            core.BaseMaterials.deserialize(data.get("base_materials", []))
        )
        ototo.remaining_seconds = data.get("remaining_seconds", 0.0)
        ototo.return_flag = data.get("return_flag", False)
        ototo.improve_id = data.get("improve_id", 0)
        ototo.engineers = data.get("engineers", 0)
        ototo.cannons = Cannons.deserialize(data.get("cannons", {}))
        return ototo

    def __repr__(self):
        return f"Ototo({self.base_materials}, {self.remaining_seconds}, {self.return_flag}, {self.improve_id}, {self.engineers}, {self.cannons})"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def get_max_engineers(save_file: core.SaveFile) -> int:
        file = core.core_data.get_game_data_getter(save_file).download(
            "DataLocal", "CastleCustomLimit.csv"
        )
        if file is None:
            return 5
        csv = core.CSV(file)
        return csv.lines[0][0].to_int()

    def edit_engineers(self, save_file: core.SaveFile):
        name = core.core_data.get_gatya_item_names(save_file).get_name(92)
        if name is None:
            name = "engineers"
            localized_item = True
        else:
            localized_item = False
        self.engineers = dialog_creator.SingleEditor(
            name,
            self.engineers,
            Ototo.get_max_engineers(save_file),
            localized_item=localized_item,
        ).edit()

    def display_current_cannons(
        self, save_file: core.SaveFile
    ) -> list[str] | None:
        descriptions = CannonDescriptions(save_file)
        recipe_unlocks = CastleRecipeUnlock(save_file)

        color.ColoredText.localize("current_cannon_stats")

        if self.cannons is None:
            self.cannons = Cannons.init(save_file.game_version)

        names: list[str] = []
        longest_part_name = descriptions.get_longest_longest_part_name()
        if longest_part_name is None:
            return None
        longest_part_name = len(longest_part_name)

        for cannon_id, cannon in self.cannons.cannons.items():
            description = descriptions.get_cannon_description(cannon_id)
            if description is None:
                continue
            recipe_unlock = recipe_unlocks.get_recipe_unlock(cannon_id)
            if recipe_unlock is None:
                continue
            cannon_name = description.get_cannon_name()
            names.append(cannon_name)
            text = cannon_name
            if cannon_id != 0:
                cannon_name_length = len(cannon_name) - 10
                buffer = " " * (longest_part_name - cannon_name_length)
                text += core.core_data.local_manager.get_key(
                    "development",
                    development=Ototo.get_stage_name(cannon.development),
                    escape=False,
                    buffer=buffer,
                )

            for part_id, level in enumerate(cannon.levels):
                if part_id == 0:
                    level += 1

                text += "\n"
                text += "        "
                buffer = " " * (
                    longest_part_name
                    - len(description.get_part_name(part_id))
                    + 2
                )
                name = description.get_part_name(part_id)
                text += core.core_data.local_manager.get_key(
                    "cannon_part", name=name, level=level, buffer=buffer
                )

            text += "\n"

            color.ColoredText.localize("cannon_stats", parts=text, escape=False)

        return names

    def edit_cannon(self, save_file: core.SaveFile):
        if self.cannons is None:
            self.cannons = Cannons.init(save_file.game_version)

        names = self.display_current_cannons(save_file)
        if names is None:
            return

        cannon_ids, all_at_once = dialog_creator.ChoiceInput.from_reduced(
            names, dialog="select_cannon"
        ).multiple_choice()
        if cannon_ids is None:
            return

        if len(cannon_ids) > 1 and not all_at_once:
            choice = dialog_creator.ChoiceInput.from_reduced(
                ["individual", "edit_all_at_once"],
                dialog="cannon_edit_type",
                single_choice=True,
            ).single_choice()
            if choice is None:
                return
            choice -= 1
            if choice == 0:
                all_at_once = False
            else:
                all_at_once = True

        if len(cannon_ids) > 1 or (len(cannon_ids) == 1 and cannon_ids[0] != 0):
            choice = dialog_creator.ChoiceInput.from_reduced(
                ["development_o", "level_o"],
                dialog="cannon_dev_level_q",
                single_choice=True,
            ).single_choice()
            if choice is None:
                return
            choice -= 1
        else:
            choice = 1
        if choice == 0:
            self.edit_cannon_development(save_file, all_at_once, cannon_ids)
        elif choice == 1:
            self.edit_cannon_level(save_file, all_at_once, cannon_ids)

        color.ColoredText.localize("cannon_success")

        self.display_current_cannons(save_file)

    def select_development(self) -> int | None:
        return dialog_creator.ChoiceInput.from_reduced(
            ["none", "foundation", "style", "effect"],
            dialog="select_development",
            single_choice=True,
        ).single_choice()

    def edit_cannon_development(
        self, save_file: core.SaveFile, all_at_once: bool, cannon_ids: list[int]
    ):
        if self.cannons is None:
            self.cannons = Cannons.init(save_file.game_version)
        if all_at_once:
            development = self.select_development()
            if development is None:
                return
            for cannon_id in cannon_ids:
                if cannon_id == 0:
                    continue
                self.cannons.cannons[cannon_id].development = development - 1
        else:
            for cannon_id in cannon_ids:
                if cannon_id == 0:
                    continue
                cannon_description = CannonDescriptions(
                    save_file
                ).get_cannon_description(cannon_id)
                if cannon_description is None:
                    continue
                current_development = self.cannons.cannons[
                    cannon_id
                ].development

                color.ColoredText.localize(
                    "selected_cannon_stage",
                    name=cannon_description.get_cannon_name(),
                    stage=Ototo.get_stage_name(current_development),
                    escape=False,
                )
                development = self.select_development()
                if development is None:
                    return
                self.cannons.cannons[cannon_id].development = development - 1

    def edit_cannon_level(
        self, save_file: core.SaveFile, all_at_once: bool, cannon_ids: list[int]
    ):
        if self.cannons is None:
            self.cannons = Cannons.init(save_file.game_version)
        cannon_descriptions = CannonDescriptions(save_file)
        cannon_recipe = CastleRecipeUnlock(save_file)
        if all_at_once:
            max_part_level_0 = cannon_recipe.get_max_part_level(0)
            max_part_level_1 = cannon_recipe.get_max_part_level(1)
            max_part_level_2 = cannon_recipe.get_max_part_level(2)
            if (
                max_part_level_0 is None
                or max_part_level_1 is None
                or max_part_level_2 is None
            ):
                return
            levels = dialog_creator.MultiEditor.from_reduced(
                "cannon_level",
                ["effect", "improved_foundation", "improved_style"],
                None,
                max_values=[
                    max_part_level_0,
                    max_part_level_1,
                    max_part_level_2,
                ],
                group_name_localized=True,
                items_localized=True,
            ).edit()
            if not levels:
                return
            for cannon_id in cannon_ids:
                cannon = self.get_cannon(cannon_id)
                if cannon is None:
                    continue
                cannon.development = max(cannon.development, 3)

                for part_id, level in enumerate(levels):
                    if part_id == 0:
                        level -= 1
                    max_level = cannon_recipe.get_max_level(cannon_id, part_id)
                    if max_level is None:
                        continue
                    if part_id >= len(cannon.levels):
                        break
                    cannon.levels[part_id] = min(level, max_level)
        else:
            for cannon_id in cannon_ids:
                cannon = self.get_cannon(cannon_id)
                if cannon is None:
                    continue
                cannon.development = max(cannon.development, 3)

                cannon_desc = cannon_descriptions.get_cannon_description(
                    cannon_id
                )
                if cannon_desc is None:
                    continue
                levels = cannon.levels
                levels[0] += 1
                names = ["effect", "improved_foundation", "improved_style"]
                if cannon_id == 0:
                    names = ["effect"]
                max_part_level_0 = cannon_recipe.get_max_part_level(0)
                max_part_level_1 = cannon_recipe.get_max_part_level(1)
                max_part_level_2 = cannon_recipe.get_max_part_level(2)
                if (
                    max_part_level_0 is None
                    or max_part_level_1 is None
                    or max_part_level_2 is None
                ):
                    return

                levels = dialog_creator.MultiEditor.from_reduced(
                    cannon_desc.get_cannon_name(),
                    names,
                    levels,
                    max_values=[
                        max_part_level_0,
                        max_part_level_1,
                        max_part_level_2,
                    ],
                    items_localized=True,
                ).edit()
                for part_id, level in enumerate(levels):
                    if part_id == 0:
                        level -= 1
                    cannon.levels[part_id] = level

    def get_cannon(self, cannon_id: int) -> Cannon | None:
        if self.cannons is None:
            return None
        return self.cannons.cannons.get(cannon_id, None)

    @staticmethod
    def get_stage_name(development: int) -> str:
        if development == 0:
            return core.core_data.local_manager.get_key("none")
        if development == 1:
            return core.core_data.local_manager.get_key("foundation")
        if development == 2:
            return core.core_data.local_manager.get_key("style")
        if development == 3:
            return core.core_data.local_manager.get_key("effect")
        return core.core_data.local_manager.get_key(
            "unknown_stage", stage=development
        )


def edit_cannon(save_file: core.SaveFile):
    save_file.ototo.edit_cannon(save_file)
