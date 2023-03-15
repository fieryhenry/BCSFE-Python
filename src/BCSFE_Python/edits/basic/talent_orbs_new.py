import json
from typing import Any, Optional
from BCSFE_Python import game_data_getter, csv_handler, helper, user_input_handler


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
        effect_text = self.effect.replace("%@", "{}")
        text = effect_text.format(self.grade, self.attribute).strip()
        return text

    def to_colortext(self) -> str:
        """Get the string representation of the OrbInfo with color

        Returns:
            str: The string representation of the OrbInfo with color
        """
        effect_text = self.effect.replace("%@", "&{}&")
        text = effect_text.format(self.grade, self.attribute).strip()
        return text

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
            "Unknown",
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
    def create(is_jp: bool) -> Optional["OrbInfoList"]:
        """Create an OrbInfoList

        Args:
            is_jp (bool): Whether the game is in Japanese

        Returns:
            Optional[OrbInfoList]: The OrbInfoList
        """
        json_data_file = game_data_getter.get_file_latest_path(
            OrbInfoList.equipment_data_file_name, is_jp
        )
        grade_list_file = game_data_getter.get_file_latest_path(
            OrbInfoList.grade_list_file_name, is_jp
        )
        attribute_list_file = game_data_getter.get_file_latest_path(
            OrbInfoList.attribute_list_file_name, is_jp
        )
        equipment_list_file = game_data_getter.get_file_latest_path(
            OrbInfoList.effect_list_file_name, is_jp
        )
        if (
            json_data_file is None
            or grade_list_file is None
            or attribute_list_file is None
            or equipment_list_file is None
        ):
            return None
        json_data = json_data_file.decode("utf-8")
        grade_list = grade_list_file.decode("utf-8")
        attribute_list = attribute_list_file.decode("utf-8")
        equipment_list = equipment_list_file.decode("utf-8")
        raw_orbs = OrbInfoList.parse_json_data(json_data)
        orbs = OrbInfoList.load_names(
            raw_orbs, grade_list, attribute_list, equipment_list
        )
        return OrbInfoList(orbs)

    @staticmethod
    def parse_json_data(json_data: str) -> list[RawOrbInfo]:
        """Parse the json data of the equipment

        Args:
            json_data (str): The json data

        Returns:
            list[RawOrbInfo]: The list of RawOrbInfo
        """
        data: dict[str, Any] = json.loads(json_data)
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
        grade_data: str,
        attribute_data: str,
        effect_data: str,
    ) -> list[OrbInfo]:
        """Load the names of the equipment

        Args:
            raw_orb_info (list[RawOrbInfo]): The list of RawOrbInfo
            grade_data (str): Raw data of the grade list
            attribute_data (str): Raw data of the attribute list
            effect_data (str): Raw data of the effect list

        Returns:
            list[OrbInfo]: The list of OrbInfo
        """
        grade_csv = csv_handler.parse_csv(grade_data)
        attribute_tsv = csv_handler.parse_csv(attribute_data, "\t")
        effect_csv = csv_handler.parse_csv(effect_data, "\t")
        orb_info_list: list[OrbInfo] = []
        for orb in raw_orb_info:
            grade = grade_csv[orb.grade_id][3]
            attribute = attribute_tsv[orb.attribute_id][0]
            effect = effect_csv[orb.effect_id][0]
            orb_info_list.append(OrbInfo(orb, grade, attribute, effect))
        return orb_info_list

    def get_orb_info(self, orb_id: int) -> Optional[OrbInfo]:
        """Get the OrbInfo from the id

        Args:
            orb_id (int): The id of the orb

        Returns:
            Optional[OrbInfo]: The OrbInfo
        """
        if orb_id >= len(self.orb_info_list):
            return None
        return self.orb_info_list[orb_id]

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
    def from_save_stats(save_stats: dict[str, Any]) -> Optional["SaveOrbs"]:
        """Create a SaveOrbs from the save stats

        Args:
            save_stats (dict[str, Any]): The save stats

        Returns:
            Optional[SaveOrbs]: The SaveOrbs
        """
        is_jp = helper.is_jp(save_stats)
        orb_info_list = OrbInfoList.create(is_jp)
        if orb_info_list is None:
            return None
        orbs: dict[int, SaveOrb] = {}
        for orb_id, amount in save_stats["talent_orbs"].items():
            try:
                orb_info = orb_info_list.orb_info_list[int(orb_id)]
            except IndexError:
                orb_info = OrbInfo.create_unknown(int(orb_id))
            orbs[int(orb_id)] = SaveOrb(orb_info, amount)

        return SaveOrbs(orbs, orb_info_list)

    def print(self):
        """Print the orbs as a formatted list"""
        self.sort_orbs()
        helper.colored_text(
            f"Total current orbs: &{sum([orb.count for orb in self.orbs.values()])}&"
        )
        helper.colored_text(f"Total current types: &{len(self.orbs)}&")
        print("Current Orbs:")
        for orb in self.orbs.values():
            helper.colored_text(f"&{orb.count}& {orb.orb.to_colortext()}")

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

        all_grades_str = "&,& ".join(all_grades)
        all_attributes_str = "&,& ".join(all_attributes)
        all_effects_str = "&,& ".join(all_effects)

        help_text = f"""Help:
Available grades: &{all_grades_str}&
Available attributes: &{all_attributes_str}&
Available effects: &{all_effects_str}&
&Note: Not all grades and effects will be available for all attributes.&
Example inputs:
    &aku& - selects &all aku& orbs
    &red s& - selects &all red &orbs with &s& grade
    &alien d attack& - selects the &alien &orb with &d& grade that increases &attack&.
These can be switched around, so you can also do stuff like:
    &d alien attack&
    &s red&
    &attack d alien&
If you want to select &all& orbs then input:
    &*&
If you want to do &multiple selections& then separate them with a &comma& like this:
    &s black tough&,&d red massive&,&floating&
"""
        helper.colored_text(help_text)

        orb_input_selection = (
            input("Select orbs:").lower().replace("angle", "angel").split(",")
        )
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

        print("Selected orbs:")
        for orb in orb_selection:
            helper.colored_text((orb.to_colortext()))

        individual = (
            input("Edit orb amounts individually? or all at once? (i/a)") == "i"
        )
        if individual:
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                try:
                    orb_count = self.orbs[orb_id].count
                except KeyError:
                    orb_count = 0
                orb_count = user_input_handler.colored_input(
                    f"What do you want to set the amount of {orb.to_colortext()} to? (currently &{orb_count}&) (&q& to exit):"
                )
                if orb_count == "q":
                    break
                orb_count = helper.check_int_max(orb_count)
                if orb_count is None:
                    continue

                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        else:
            orb_count = user_input_handler.get_int(
                "What do you want to set the amount of the selected orbs to?:"
            )
            orb_count = helper.clamp_int(orb_count)
            for orb in orb_selection:
                orb_id = orb.raw_orb_info.orb_id
                self.orbs[orb_id] = SaveOrb(orb, orb_count)

        self.print()

    def save(self, save_stats: dict[str, Any]):
        """Save the orbs to the save_stats

        Args:
            save_stats (dict[str, Any]): The save_stats to save the orbs to
        """
        for orb_id, orb in self.orbs.items():
            save_stats["talent_orbs"][orb_id] = orb.count


def edit_talent_orbs(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Edit the talent orbs

    Args:
        save_stats (dict[str, Any]): The save_stats to edit the orbs in

    Returns:
        dict[str, Any]: The edited save_stats
    """
    save_orbs = SaveOrbs.from_save_stats(save_stats)
    if save_orbs is None:
        print("Failed to load orbs")
        return save_stats
    save_orbs.edit()
    save_orbs.save(save_stats)
    return save_stats
