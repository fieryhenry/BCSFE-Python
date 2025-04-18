from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class TalentOrb:
    def __init__(self, id: int, value: int):
        self.id = id
        self.value = value

    @staticmethod
    def init() -> TalentOrb:
        return TalentOrb(
            0,
            0,
        )

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> TalentOrb:
        id = stream.read_short()
        if gv < 110400:
            value = stream.read_byte()
        else:
            value = stream.read_short()
        return TalentOrb(id, value)

    def write(self, stream: core.Data, gv: core.GameVersion):
        stream.write_short(self.id)
        if gv < 110400:
            stream.write_byte(self.value)
        else:
            stream.write_short(self.value)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "value": self.value,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> TalentOrb:
        return TalentOrb(data.get("id", 0), data.get("value", 0))

    def __repr__(self):
        return f"Orb({self.id}, {self.value})"

    def __str__(self):
        return self.__repr__()


class TalentOrbs:
    def __init__(self, orbs: dict[int, TalentOrb]):
        self.orbs = orbs

    @staticmethod
    def init() -> TalentOrbs:
        return TalentOrbs({})

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> TalentOrbs:
        length = stream.read_short()
        orbs: dict[int, TalentOrb] = {}
        for _ in range(length):
            orb = TalentOrb.read(stream, gv)
            orbs[orb.id] = orb
        return TalentOrbs(orbs)

    def write(self, stream: core.Data, gv: core.GameVersion):
        stream.write_short(len(self.orbs))
        for orb in self.orbs.values():
            orb.write(stream, gv)

    def serialize(self) -> list[dict[str, Any]]:
        return [orb.serialize() for orb in self.orbs.values()]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> TalentOrbs:
        return TalentOrbs(
            {orb.get("id", 0): TalentOrb.deserialize(orb) for orb in data}
        )

    def __repr__(self):
        return f"TalentOrbs({self.orbs})"

    def __str__(self):
        return self.__repr__()

    def set_orb(self, id: int, value: int):
        self.orbs[id] = TalentOrb(id, value)


class RawOrbInfo:
    def __init__(
        self,
        orb_id: int,
        rank_id: int,
        effect_id: int,
        value: list[int],
        target_id: int | None,
    ):
        self.orb_id = orb_id
        self.rank_id = rank_id
        self.effect_id = effect_id
        self.value = value
        self.target_id = target_id


class OrbInfo:
    def __init__(
        self,
        raw_orb_info: RawOrbInfo,
        rank: str,
        target: str | None,
        effect: str,
    ):
        self.raw_orb_info = raw_orb_info
        self.rank = rank
        self.target = target
        self.effect = effect

    def __str__(self) -> str:
        """Get the string representation of the OrbInfo

        Returns:
            str: The string representation of the OrbInfo
        """
        target_color = color_from_enemy_type(self.raw_orb_info.target_id)
        rank_color = color_from_grade(self.raw_orb_info.rank_id)
        effect_color = color_from_effect(self.raw_orb_info.effect_id)
        effect_text = self.effect.replace("%@", "{}")
        effect_text = f"<{effect_color}>{effect_text}</>"
        target = self.target
        effect = effect_text.format(
            f"<{rank_color}>{self.rank}</>",
            f"<{target_color}>{target}</>" if target else "",
        )
        return f"{effect}"

    def to_colortext(self) -> str:
        """Get the string representation of the OrbInfo with color

        Returns:
            str: The string representation of the OrbInfo with color
        """
        return str(self)

    @staticmethod
    def create_unknown(orb_id: int) -> OrbInfo:
        """Create an unknown OrbInfo

        Args:
            orb_id (int): The id of the orb

        Returns:
            OrbInfo: The unknown OrbInfo
        """
        return OrbInfo(
            RawOrbInfo(orb_id, 0, 0, [], 0),
            "???",
            "",
            "%@:%@",
        )


class OrbInfoList:
    equipment_data_file_name = "DataLocal/equipmentlist.json"
    grade_list_file_name = "DataLocal/equipmentgrade.csv"
    attribute_list_file_name = "resLocal/attribute_explonation.tsv"
    effect_list_file_name = "resLocal/equipment_explonation.tsv"

    def __init__(self, orb_info_list: list[OrbInfo]):
        """Initialize the OrbInfoList class

        Args:
            orb_info_list (list[OrbInfo]): The list of OrbInfo
        """
        self.orb_info_list = orb_info_list

    @staticmethod
    def create(save_file: core.SaveFile) -> OrbInfoList | None:
        """Create an OrbInfoList

        Args:
            save_file (core.SaveFile): The save file

        Returns:
            OrbInfoList | None: The OrbInfoList
        """
        gdg = core.core_data.get_game_data_getter(save_file)
        json_data_file = gdg.download_from_path(OrbInfoList.equipment_data_file_name)
        grade_list_file = gdg.download_from_path(OrbInfoList.grade_list_file_name)
        attribute_list_file = gdg.download_from_path(
            OrbInfoList.attribute_list_file_name
        )
        equipment_list_file = gdg.download_from_path(OrbInfoList.effect_list_file_name)
        if (
            json_data_file is None
            or grade_list_file is None
            or attribute_list_file is None
            or equipment_list_file is None
        ):
            return None
        raw_orbs = OrbInfoList.parse_json_data(json_data_file)
        if raw_orbs is None:
            return None
        orbs = OrbInfoList.load_names(
            raw_orbs, grade_list_file, attribute_list_file, equipment_list_file
        )
        return OrbInfoList(orbs)

    @staticmethod
    def parse_json_data(json_data: core.Data) -> list[RawOrbInfo] | None:
        """Parse the json data of the equipment

        Args:
            json_data (core.Data): The json data

        Returns:
            list[RawOrbInfo]: The list of RawOrbInfo
        """
        try:
            data: dict[str, Any] = core.JsonFile.from_data(json_data).to_object()
        except core.JSONDecodeError:
            return None
        orb_info_list: list[RawOrbInfo] = []
        for id, orb in enumerate(data["ID"]):
            grade_id = orb["gradeID"]
            content = orb["content"]
            value = orb["value"]
            attribute = orb.get("attribute")
            orb_info_list.append(RawOrbInfo(id, grade_id, content, value, attribute))
        return orb_info_list

    @staticmethod
    def load_names(
        raw_orb_info: list[RawOrbInfo],
        grade_data: core.Data,
        attribute_data: core.Data,
        effect_data: core.Data,
    ) -> list[OrbInfo]:
        """Load the names of the equipment

        Args:
            raw_orb_info (list[RawOrbInfo]): The list of RawOrbInfo
            grade_data (core.Data): Raw data of the grade list
            attribute_data (core.Data): Raw data of the attribute list
            effect_data (core.Data): Raw data of the effect list

        Returns:
            list[OrbInfo]: The list of OrbInfo
        """
        grade_csv = core.CSV(grade_data)
        attribute_tsv = core.CSV(attribute_data, "\t")
        effect_csv = core.CSV(effect_data, "\t")
        orb_info_list: list[OrbInfo] = []
        for orb in raw_orb_info:
            grade = grade_csv[orb.rank_id][3].to_str()
            effect = effect_csv[orb.effect_id][0].to_str()

            if orb.target_id is not None:
                attribute = attribute_tsv[orb.target_id][0].to_str()
            else:
                attribute = None

            orb_info_list.append(OrbInfo(orb, grade, attribute, effect))
        return orb_info_list

    def get_orb_info(self, orb_id: int) -> OrbInfo | None:
        """Get the OrbInfo from the id

        Args:
            orb_id (int): The id of the orb

        Returns:
            OrbInfo | None: The OrbInfo
        """
        try:
            return self.orb_info_list[orb_id]
        except IndexError:
            return None

    def get_orb_from_components(
        self,
        grade: str,
        attribute: str | None,
        effect: str,
    ) -> OrbInfo | None:
        """Get the OrbInfo from the components

        Args:
            grade (str): The grade of the orb
            attribute (str | None): The attribute of the orb. None if applies to all attributes
            effect (str): The effect of the orb

        Returns:
            OrbInfo | None: The OrbInfo
        """
        for orb in self.orb_info_list:
            if orb.rank == grade and orb.target == attribute and orb.effect == effect:
                return orb
        return None

    def does_match_orb_str(self, str_1: str | None, str_2: str | None) -> bool:
        if str_2 == "*":
            return True

        if str_1 is None:
            return str_2 is None
        if str_2 is None:
            return False

        return str_1.lower() == str_2.lower()

    def get_orbs_from_component_fuzzy(
        self,
        grade: str,
        attribute: str | None,
        effect: str,
    ) -> list[OrbInfo]:
        """Get the OrbInfo from the components matching the first word of the effect and lowercased

        Args:
            grade (str): The grade of the orb
            attribute (str | None): The attribute of the orb. None if all
            effect (str): The effect of the orb

        Returns:
            list[OrbInfo]: The list of OrbInfo
        """
        orbs: list[OrbInfo] = []
        for orb in self.orb_info_list:
            if (
                (orb.rank.lower() == grade.lower() or grade == "*")
                and (self.does_match_orb_str(orb.target, attribute))
                and (orb.effect == effect or effect == "*")
            ):
                orbs.append(orb)
        return orbs

    def get_all_grades(self) -> list[str]:
        """Get all the grades

        Returns:
            list[str]: The list of grades
        """

        data = list(
            set([(orb.rank, orb.raw_orb_info.rank_id) for orb in self.orb_info_list])
        )

        data.sort(key=lambda id: id[1])

        return [orb[0] for orb in data]

    def get_all_attributes(self) -> list[str | None]:
        """Get all the attributes

        Returns:
            list[str]: The list of attributes
        """

        data = list(
            set(
                [
                    (orb.target, orb.raw_orb_info.target_id)
                    for orb in self.orb_info_list
                    if orb.target is not None and orb.raw_orb_info.target_id is not None
                ]
            )
        )

        data.sort(key=lambda id: id[1])

        return [orb[0] for orb in data]

    def get_all_effects(self) -> list[str]:
        """Get all the effects

        Returns:
            list[str]: The list of effects
        """

        data = list(
            set(
                [(orb.effect, orb.raw_orb_info.effect_id) for orb in self.orb_info_list]
            )
        )

        data.sort(key=lambda id: id[1])

        return [orb[0] for orb in data]


class SaveOrb:
    """Represents a saved orb in the save file"""

    def __init__(self, orb: OrbInfo, count: int):
        """Initialize the SaveOrb class

        Args:
            orb (OrbInfo): The OrbInfo
            count (int): The amount of the orb
        """
        self.count = count
        self.orb = orb


def color_from_enemy_type(target_id: int | None) -> str:
    if target_id is None:
        return color.ColorHex.WHITE
    if target_id == 0:
        return color.ColorHex.RED
    elif target_id == 1:
        return color.ColorHex.GREEN
    elif target_id == 2:
        return color.ColorHex.DARK_GREY
    elif target_id == 3:
        return color.ColorHex.LIGHT_GREY
    elif target_id == 4:
        return color.ColorHex.YELLOW
    elif target_id == 5:
        return color.ColorHex.BLUE
    elif target_id == 6:
        return color.ColorHex.MAGENTA
    elif target_id == 7:
        return color.ColorHex.DARK_GREEN
    elif target_id == 8:
        return color.ColorHex.WHITE
    elif target_id == 9:
        return color.ColorHex.DARK_MAGENTA
    elif target_id == 10:
        return color.ColorHex.ORANGE
    elif target_id == 11:
        return color.ColorHex.CYAN
    return color.ColorHex.BLACK


def color_from_grade(grade_id: int) -> str:
    if grade_id == 0:
        return color.ColorHex.RED
    elif grade_id == 1:
        return color.ColorHex.ORANGE
    elif grade_id == 2:
        return color.ColorHex.YELLOW
    elif grade_id == 3:
        return color.ColorHex.GREEN
    elif grade_id == 4:
        return color.ColorHex.BLUE
    return color.ColorHex.BLACK


def color_from_effect(effect_id: int):
    if effect_id == 0:
        return color.ColorHex.RED
    elif effect_id == 1:
        return color.ColorHex.GREEN
    elif effect_id == 2:
        return color.ColorHex.DARK_GREY
    elif effect_id == 3:
        return color.ColorHex.LIGHT_GREY
    elif effect_id == 4:
        return color.ColorHex.YELLOW
    elif effect_id == 5:
        return color.ColorHex.BLUE
    elif effect_id == 6:
        return color.ColorHex.MAGENTA
    elif effect_id == 7:
        return color.ColorHex.DARK_GREEN
    elif effect_id == 8:
        return color.ColorHex.WHITE
    elif effect_id == 9:
        return color.ColorHex.DARK_MAGENTA
    elif effect_id == 10:
        return color.ColorHex.ORANGE

    return color.ColorHex.BLACK


class SaveOrbs:
    def __init__(
        self,
        orbs: dict[int, SaveOrb],
        orb_info_list: OrbInfoList,
    ):
        """Initialize the SaveOrbs class

        Args:
            orbs (dict[int, SaveOrb]): The orbs
            orb_info_list (OrbInfoList): The orb info list
        """
        self.orbs = orbs
        self.orb_info_list = orb_info_list

    @staticmethod
    def from_save_file(save_file: core.SaveFile) -> SaveOrbs | None:
        """Create a SaveOrbs from the save stats

        Args:
            save_file (core.SaveFile): The save file

        Returns:
            SaveOrbs | None: The SaveOrbs
        """
        orb_info_list = OrbInfoList.create(save_file)
        if orb_info_list is None:
            return None
        orbs: dict[int, SaveOrb] = {}
        for orb_id, orb in save_file.talent_orbs.orbs.items():
            try:
                orb_info = orb_info_list.orb_info_list[int(orb_id)]
            except IndexError:
                orb_info = OrbInfo.create_unknown(int(orb_id))
            orbs[int(orb_id)] = SaveOrb(orb_info, orb.value)

        return SaveOrbs(orbs, orb_info_list)

    def print(self):
        """Print the orbs as a formatted list"""
        self.sort_orbs()
        total_orbs = sum([orb.count for orb in self.orbs.values()])
        color.ColoredText.localize("total_current_orbs", total_orbs=total_orbs)
        color.ColoredText.localize(
            "total_current_orb_types", total_types=len(self.orbs)
        )
        color.ColoredText.localize("current_orbs")
        for orb in self.orbs.values():
            color.ColoredText(f"<@q>{orb.count}</> {orb.orb.to_colortext()}")

    def sort_orbs(self):
        """Sort the orbs by attribute, effect, grade and id in that order with attribute being the most important"""
        orbs = list(self.orbs.values())
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.orb_id)
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.rank_id)
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.effect_id)
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.target_id or -1)

    def localize_attribute(self, attribute: str | None) -> str | None:
        if attribute is not None:
            return attribute

    def edit(self):
        """Edit the orbs"""
        # this code sucks quit a lot, but it works and i can't be bothered making it better atm
        self.print()
        all_grades = self.orb_info_list.get_all_grades()
        all_grades = [grade for grade in all_grades]
        all_grades.sort()
        all_attributes = self.orb_info_list.get_all_attributes()
        all_attributes = [
            self.localize_attribute(attribute) or ""
            for attribute in all_attributes
            if attribute
        ]
        all_attributes.sort()
        all_effects = self.orb_info_list.get_all_effects()
        all_effects.sort()
        all_effects_str = [
            effect.lower().replace("%@", "").replace(":", "").strip() + f" ({i})"
            for (i, effect) in enumerate(all_effects)
        ]
        all_effect_ids = [i for i in range(len(all_effects))]

        all_grades_str = "".join(
            f"<{color_from_grade(self.orb_info_list.get_all_grades().index(grade))}>{grade}</>,"
            for grade in all_grades
        )

        all_attributes_str = "".join(
            f"<{color_from_enemy_type(self.orb_info_list.get_all_attributes().index(attribute))}>{attribute}</>,"
            for attribute in all_attributes
        )

        all_effects_str = "".join(
            f"<{color_from_effect(self.orb_info_list.get_all_effects().index(effect))}>{effect_str}</>,"
            for effect_str, effect in zip(all_effects_str, all_effects)
        )

        color.ColoredText.localize(
            "edit_orbs_help",
            escape=False,
            all_grades_str=all_grades_str,
            all_attributes_str=all_attributes_str,
            all_effects_str=all_effects_str,
        )

        orb_input_selection = (
            color.ColoredInput()
            .localize("orb_select")
            .lower()
            .replace("angle", "angel")
            .split(",")
        )
        if orb_input_selection == [core.core_data.local_manager.get_key("quit_key")]:
            return

        orb_selection: list[OrbInfo] = []

        for orb_input in orb_input_selection:
            grade = None
            attribute = None
            effect = None
            orb_input = orb_input.strip()
            parts = orb_input.split(" ")
            parts = [part.lower() for part in parts if part != ""]
            if len(parts) == 0:
                continue
            if parts[0] == "*":
                orb_selection = self.orb_info_list.orb_info_list
                break
            for available_grade in all_grades:
                if available_grade.lower() in parts:
                    grade = available_grade
                    break
            for available_attribute in all_attributes:
                if available_attribute.lower() in parts:
                    attribute = available_attribute
                    break
            for available_effect in all_effect_ids:
                if str(available_effect) in parts:
                    effect = all_effects[available_effect]
                    break
            if grade is None:
                grade = "*"
            if attribute is None:
                attribute = "*"
            if effect is None:
                effect = "*"
            orbs = self.orb_info_list.get_orbs_from_component_fuzzy(
                grade, attribute, effect
            )
            orb_selection.extend(orbs)

        orb_selection = list(set(orb_selection))
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.orb_id)
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.rank_id)
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.effect_id)
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.target_id or -1)

        color.ColoredText.localize("selected_orbs")

        for orb in orb_selection:
            color.ColoredText(orb.to_colortext())

        max_orbs = core.core_data.max_value_manager.get("talent_orbs")

        if len(orb_selection) == 0:
            return
        if len(orb_selection) == 1:
            individual = True
        else:
            individual = dialog_creator.ChoiceInput.from_reduced(
                ["individual", "edit_all_at_once"],
                dialog="edit_orbs_individually",
                single_choice=True,
            ).single_choice()
            if individual is None:
                return
            individual = True if individual == 1 else False
        if individual:
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                try:
                    orb_count = self.orbs[orb_id].count
                except KeyError:
                    orb_count = 0

                orb_count = dialog_creator.SingleEditor(
                    orb.to_colortext(), orb_count, max_orbs
                ).edit(escape_text=False)

                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        else:
            int_input = dialog_creator.IntInput(max_orbs)
            orb_count = int_input.get_input_locale_while(
                "edit_orbs_all", {"max": max_orbs}, escape=False
            )
            if orb_count is None:
                return
            orb_count = int_input.clamp_value(orb_count)
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        self.print()

    def save(self, save_file: core.SaveFile):
        """Save the orbs to the save_stats

        Args:
            save_file (core.SaveFile): The save_stats to save the orbs to
        """
        for orb_id, orb in self.orbs.items():
            save_file.talent_orbs.orbs[orb_id] = core.TalentOrb(orb_id, orb.count)

    @staticmethod
    def edit_talent_orbs(save_file: core.SaveFile):
        """Edit the talent orbs

        Args:
            save_file (core.SaveFile): The save_stats to edit the orbs of

        """
        save_orbs = SaveOrbs.from_save_file(save_file)
        if save_orbs is None:
            color.ColoredText.localize("failed_to_load_orbs")
            return None
        save_orbs.edit()
        save_orbs.save(save_file)
