from typing import Any, Optional
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class RawOrbInfo:
    def __init__(
        self,
        orb_id: int,
        grade_id: int,
        effect_id: int,
        value: list[int],
        attribute_id: int,
    ):
        """Initialize the RawOrbInfo class

        Args:
            orb_id (int): The id of the orb
            grade_id (int): The id of the grade
            effect_id (int): The id of the effect
            value (list[int]): The value of the effect? idk
            attribute_id (int): The id of the attribute
        """
        self.orb_id = orb_id
        self.grade_id = grade_id
        self.effect_id = effect_id
        self.value = value
        self.attribute_id = attribute_id


def color_from_enemy_type(enemy_type: str) -> str:
    enemy_type = enemy_type.lower().strip()
    if enemy_type == "red":
        return color.ColorHex.RED
    elif enemy_type == "floating":
        return color.ColorHex.GREEN
    elif enemy_type == "black":
        return color.ColorHex.DARK_GREY
    elif enemy_type == "metal":
        return color.ColorHex.LIGHT_GREY
    elif enemy_type == "angel":
        return color.ColorHex.YELLOW
    elif enemy_type == "alien":
        return color.ColorHex.BLUE
    elif enemy_type == "zombie":
        return color.ColorHex.MAGENTA
    elif enemy_type == "relic":
        return color.ColorHex.DARK_GREEN
    elif enemy_type == "traitless":
        return color.ColorHex.WHITE
    elif enemy_type == "witch":
        return color.ColorHex.DARK_MAGENTA
    elif enemy_type == "eva angel":
        return color.ColorHex.ORANGE
    elif enemy_type == "aku":
        return color.ColorHex.CYAN
    return color.ColorHex.BLACK


def color_from_grade(grade: str) -> str:
    grade = grade.lower().strip()
    if grade == "d":
        return color.ColorHex.RED
    elif grade == "c":
        return color.ColorHex.ORANGE
    elif grade == "b":
        return color.ColorHex.YELLOW
    elif grade == "a":
        return color.ColorHex.GREEN
    elif grade == "s":
        return color.ColorHex.BLUE
    return color.ColorHex.BLACK


def color_from_effect(effect_name: str):
    effect_name = effect_name.lower().strip().split(" ")[0]
    if effect_name == "attack":
        return color.ColorHex.RED
    elif effect_name == "defense":
        return color.ColorHex.BLUE
    elif effect_name == "strong":
        return color.ColorHex.GREEN
    elif effect_name == "massive":
        return color.ColorHex.YELLOW
    elif effect_name == "tough":
        return color.ColorHex.BLUE

    return color.ColorHex.BLACK


class OrbInfo:
    def __init__(
        self,
        raw_orb_info: RawOrbInfo,
        grade: str,
        attribute: str,
        effect: str,
    ):
        """Initialize the OrbInfo class

        Args:
            raw_orb_info (RawOrbInfo): The raw orb info
            grade (str): The grade of the orb (e.g. "S")
            attribute (str): The attribute of the orb (e.g. "Red")
            effect (str): The effect of the orb (e.g. "Attack Up %@: %@")
        """
        self.raw_orb_info = raw_orb_info
        self.grade = grade
        self.attribute = attribute
        self.effect = effect

    def __str__(self) -> str:
        """Get the string representation of the OrbInfo

        Returns:
            str: The string representation of the OrbInfo
        """
        attribute_color = color_from_enemy_type(self.attribute)
        grade_color = color_from_grade(self.grade)
        effect_color = color_from_effect(self.effect.split("%@")[0])
        effect_text = self.effect.replace("%@", "{}")
        effect_text = f"<{effect_color}>{effect_text}</>"
        effect = effect_text.format(
            f"<{grade_color}>{self.grade}</>", f"<{attribute_color}>{self.attribute}</>"
        )
        return f"{effect}"

    def to_colortext(self) -> str:
        """Get the string representation of the OrbInfo with color

        Returns:
            str: The string representation of the OrbInfo with color
        """
        return str(self)

    @staticmethod
    def create_unknown(orb_id: int) -> "OrbInfo":
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
    def create(save_file: "core.SaveFile") -> Optional["OrbInfoList"]:
        """Create an OrbInfoList

        Args:
            save_file (core.SaveFile): The save file

        Returns:
            Optional[OrbInfoList]: The OrbInfoList
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
    def parse_json_data(json_data: "core.Data") -> Optional[list[RawOrbInfo]]:
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
            attribute = orb["attribute"]
            orb_info_list.append(RawOrbInfo(id, grade_id, content, value, attribute))
        return orb_info_list

    @staticmethod
    def load_names(
        raw_orb_info: list[RawOrbInfo],
        grade_data: "core.Data",
        attribute_data: "core.Data",
        effect_data: "core.Data",
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
            grade = grade_csv[orb.grade_id][3].to_str()
            attribute = attribute_tsv[orb.attribute_id][0].to_str()
            effect = effect_csv[orb.effect_id][0].to_str()
            orb_info_list.append(OrbInfo(orb, grade, attribute, effect))
        return orb_info_list

    def get_orb_info(self, orb_id: int) -> Optional[OrbInfo]:
        """Get the OrbInfo from the id

        Args:
            orb_id (int): The id of the orb

        Returns:
            Optional[OrbInfo]: The OrbInfo
        """
        try:
            return self.orb_info_list[orb_id]
        except IndexError:
            return None

    def get_orb_from_components(
        self,
        grade: str,
        attribute: str,
        effect: str,
    ) -> Optional[OrbInfo]:
        """Get the OrbInfo from the components

        Args:
            grade (str): The grade of the orb
            attribute (str): The attribute of the orb
            effect (str): The effect of the orb

        Returns:
            Optional[OrbInfo]: The OrbInfo
        """
        for orb in self.orb_info_list:
            if (
                orb.grade == grade
                and orb.attribute == attribute
                and orb.effect == effect
            ):
                return orb
        return None

    def get_orbs_from_component_fuzzy(
        self,
        grade: str,
        attribute: str,
        effect: str,
    ) -> list[OrbInfo]:
        """Get the OrbInfo from the components matching the first word of the effect and lowercased

        Args:
            grade (str): The grade of the orb
            attribute (str): The attribute of the orb
            effect (str): The effect of the orb

        Returns:
            list[OrbInfo]: The list of OrbInfo
        """
        orbs: list[OrbInfo] = []
        for orb in self.orb_info_list:
            if (
                (orb.grade.lower() == grade.lower() or grade == "*")
                and (orb.attribute.lower() == attribute.lower() or attribute == "*")
                and (
                    orb.effect.lower().split(" ")[0] == effect.lower().split(" ")[0]
                    or effect == "*"
                )
            ):
                orbs.append(orb)
        return orbs

    def get_all_grades(self) -> list[str]:
        """Get all the grades

        Returns:
            list[str]: The list of grades
        """
        return list(set([orb.grade for orb in self.orb_info_list]))

    def get_all_attributes(self) -> list[str]:
        """Get all the attributes

        Returns:
            list[str]: The list of attributes
        """
        return list(set([orb.attribute for orb in self.orb_info_list]))

    def get_all_effects(self) -> list[str]:
        """Get all the effects

        Returns:
            list[str]: The list of effects
        """
        return list(set([orb.effect for orb in self.orb_info_list]))


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
    def from_save_file(save_file: "core.SaveFile") -> Optional["SaveOrbs"]:
        """Create a SaveOrbs from the save stats

        Args:
            save_file (core.SaveFile): The save file

        Returns:
            Optional[SaveOrbs]: The SaveOrbs
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
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.grade_id)
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.effect_id)
        orbs.sort(key=lambda orb: orb.orb.raw_orb_info.attribute_id)

    def edit(self):
        """Edit the orbs"""
        self.print()
        all_grades = self.orb_info_list.get_all_grades()
        all_grades = [grade.lower() for grade in all_grades]
        all_grades.sort()
        all_attributes = self.orb_info_list.get_all_attributes()
        all_attributes = [attribute.lower() for attribute in all_attributes]
        all_attributes.sort()
        all_effects = self.orb_info_list.get_all_effects()
        all_effects = [effect.lower().split(" ")[0] for effect in all_effects]
        all_effects.sort()

        all_grades_str = "".join(
            f"<{color_from_grade(grade)}>{grade}</>," for grade in all_grades
        )

        all_attributes_str = "".join(
            f"<{color_from_enemy_type(attribute)}>{attribute}</>,"
            for attribute in all_attributes
        )

        all_effects_str = "".join(
            f"<{color_from_effect(effect)}>{effect}</>," for effect in all_effects
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
            parts = [part for part in parts if part != ""]
            if len(parts) == 0:
                continue
            if parts[0] == "*":
                orb_selection = self.orb_info_list.orb_info_list
                break
            for available_grade in all_grades:
                if available_grade in parts:
                    grade = available_grade
                    break
            for available_attribute in all_attributes:
                if available_attribute in parts:
                    attribute = available_attribute
                    break
            for available_effect in all_effects:
                if available_effect in parts:
                    effect = available_effect
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
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.grade_id)
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.effect_id)
        orb_selection.sort(key=lambda orb: orb.raw_orb_info.attribute_id)

        color.ColoredText.localize("selected_orbs")

        for orb in orb_selection:
            color.ColoredText(orb.to_colortext())

        max_orbs = core.core_data.max_value_manager.get("talent_orbs")

        individual = (
            color.ColoredInput().localize("edit_orbs_individually").lower() == "i"
        )
        if individual:
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                try:
                    orb_count = self.orbs[orb_id].count
                except KeyError:
                    orb_count = 0

                orb_count = color.ColoredInput().localize(
                    "input", name=orb.to_colortext(), value=orb_count, max=max_orbs
                )
                if orb_count == core.core_data.local_manager.get_key("quit_key"):
                    break
                try:
                    orb_count = int(orb_count)
                except ValueError:
                    continue
                orb_count = min(orb_count, max_orbs)

                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        else:
            int_input = dialog_creator.IntInput(max_orbs)
            orb_count = int_input.get_input_locale_while("edit_orbs_all", {})
            if orb_count is None:
                return
            orb_count = int_input.clamp_value(orb_count)
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        self.print()

    def save(self, save_file: "core.SaveFile"):
        """Save the orbs to the save_stats

        Args:
            save_file (core.SaveFile): The save_stats to save the orbs to
        """
        for orb_id, orb in self.orbs.items():
            save_file.talent_orbs.orbs[orb_id] = core.TalentOrb(orb_id, orb.count)

    @staticmethod
    def edit_talent_orbs(save_file: "core.SaveFile"):
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
