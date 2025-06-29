from __future__ import annotations
from bcsfe import core

from typing import Any

from bcsfe.cli import dialog_creator, color


class SpecialSkill:
    def __init__(self, upg: core.Upgrade):
        self.upgrade = upg
        self.seen = 0
        self.max_upgrade_level = core.Upgrade(0, 0)

    @staticmethod
    def init() -> SpecialSkill:
        return SpecialSkill(core.Upgrade(0, 0))

    @staticmethod
    def read_upgrade(stream: core.Data) -> SpecialSkill:
        up = core.Upgrade.read(stream)
        return SpecialSkill(up)

    def write_upgrade(self, stream: core.Data):
        self.upgrade.write(stream)

    def read_seen(self, stream: core.Data):
        self.seen = stream.read_int()

    def write_seen(self, stream: core.Data):
        stream.write_int(self.seen)

    def read_max_upgrade_level(self, stream: core.Data):
        level = core.Upgrade.read(stream)
        self.max_upgrade_level = level

    def write_max_upgrade_level(self, stream: core.Data):
        self.max_upgrade_level.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "upgrade": self.upgrade.serialize(),
            "seen": self.seen,
            "max_upgrade_level": self.max_upgrade_level.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> SpecialSkill:
        skill = SpecialSkill(core.Upgrade.deserialize(data.get("upgrade", {})))
        skill.seen = data.get("seen", 0)
        skill.max_upgrade_level = core.Upgrade.deserialize(
            data.get("max_upgrade_level", {})
        )
        return skill

    def __repr__(self) -> str:
        return f"Skill(upgrade={self.upgrade}, seen={self.seen}, max_upgrade_level={self.max_upgrade_level})"

    def __str__(self) -> str:
        return self.__repr__()

    def set_upgrade(
        self,
        upgrade: core.Upgrade,
        only_plus: bool = False,
        max_base: int | None = None,
        max_plus: int | None = None,
    ):
        if max_base is not None:
            upgrade.base = min(upgrade.base, max_base)
        if max_plus is not None:
            upgrade.plus = min(upgrade.plus, max_plus)

        base = upgrade.base
        plus = upgrade.plus

        if base != -1 and not only_plus:
            self.upgrade.base = upgrade.get_random_base(max_base)
        if plus != -1:
            self.upgrade.plus = upgrade.get_random_plus(max_plus)


class SpecialSkills:
    def __init__(self, skills: list[SpecialSkill]):
        self.skills = skills

    def get_upgrade(self, valid_skill_id: int) -> SpecialSkill:
        if valid_skill_id >= 1:
            valid_skill_id += 1

        return self.skills[valid_skill_id]

    def set_upgrade(
        self,
        valid_skill_id: int,
        upgrade: core.Upgrade,
        max_base: int | None = None,
        max_plus: int | None = None,
    ):
        u = upgrade.copy()
        valid_skills = self.get_valid_skills()
        valid_skills[valid_skill_id].set_upgrade(
            u, max_base=max_base, max_plus=max_plus
        )

        if (
            valid_skill_id == 0
        ):  # if it is a cat cannon power upgrade, mirror the upgrade to the hidden cat cannon power special skill
            self.skills[1].set_upgrade(u, max_base=max_base, max_plus=max_plus)

    @staticmethod
    def init() -> SpecialSkills:
        skills = [SpecialSkill.init() for _ in range(11)]
        return SpecialSkills(skills)

    def get_valid_skills(self) -> list[SpecialSkill]:
        new_skills: list[SpecialSkill] = []
        for i, skill in enumerate(self.skills):
            if i == 1:
                continue
            new_skills.append(skill)

        return new_skills

    @staticmethod
    def read_upgrades(stream: core.Data) -> SpecialSkills:
        total_skills = 11

        skills: list[SpecialSkill] = []
        for _ in range(total_skills):
            skills.append(SpecialSkill.read_upgrade(stream))

        return SpecialSkills(skills)

    def write_upgrades(self, stream: core.Data):
        for skill in self.skills:
            skill.write_upgrade(stream)

    def read_gatya_seen(self, stream: core.Data):
        for skill in self.get_valid_skills():
            skill.read_seen(stream)

    def write_gatya_seen(self, stream: core.Data):
        for skill in self.get_valid_skills():
            skill.write_seen(stream)

    def read_max_upgrade_levels(self, stream: core.Data):
        for skill in self.skills:
            skill.read_max_upgrade_level(stream)

    def write_max_upgrade_levels(self, stream: core.Data):
        for skill in self.skills:
            skill.write_max_upgrade_level(stream)

    def serialize(self) -> list[dict[str, Any]]:
        return [skill.serialize() for skill in self.skills]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> SpecialSkills:
        skills = SpecialSkills([])
        for skill in data:
            skills.skills.append(SpecialSkill.deserialize(skill))

        return skills

    def __repr__(self) -> str:
        return f"Skills(skills={self.skills})"

    def __str__(self) -> str:
        return f"Skills(skills={self.skills})"

    def edit(self, save_file: core.SaveFile):
        names_o = core.core_data.get_gatya_item_names(save_file)
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(2)
        if items is None:
            return
        names: list[str] = []
        for item in items:
            name = names_o.get_name(item.id)
            if name is None:
                return
            names.append(name)
        ids, _ = dialog_creator.ChoiceInput.from_reduced(
            names, [], {}, "special_skills_dialog"
        ).multiple_choice()
        if not ids:
            return
        skills = self.get_valid_skills()
        if len(ids) == 1:
            option_id = 0
        else:
            options: list[str] = [
                "upgrade_individual_skill",
                "upgrade_all_skills",
            ]
            option_id = dialog_creator.ChoiceInput(
                options, options, [], {}, "upgrade_skills_select_mod", True
            ).single_choice()
            if option_id is None:
                return
            option_id -= 1

        ability_data = core.core_data.get_ability_data(save_file)
        if ability_data.ability_data is None:
            return
        success = False
        if option_id == 0:
            for id in ids:
                color.ColoredText.localize(
                    "selected_skill_upgrades",
                    name=names[id],
                    base_level=skills[id].upgrade.base + 1,
                    plus_level=skills[id].upgrade.plus,
                )
                ability = ability_data.get_ability_data_item(id)
                if ability is None:
                    continue
                upgrade, should_exit = core.Upgrade.get_user_upgrade(
                    ability.max_base_level - 1, ability.max_plus_level
                )
                if should_exit:
                    return
                if upgrade is not None:
                    self.set_upgrade(id, upgrade)
                    color.ColoredText.localize(
                        "selected_skill_upgraded",
                        name=names[id],
                        base_level=skills[id].upgrade.base + 1,
                        plus_level=skills[id].upgrade.plus,
                    )
                    success = True

        elif option_id == 1:
            max_base_level = max(
                [
                    ability.max_base_level
                    for ability in ability_data.ability_data
                ]
            )
            max_plus_level = max(
                [
                    ability.max_plus_level
                    for ability in ability_data.ability_data
                ]
            )
            upgrade, should_exit = core.Upgrade.get_user_upgrade(
                max_base_level - 1, max_plus_level
            )
            if should_exit or upgrade is None:
                return
            for id in ids:
                max_base_level = ability_data.ability_data[id].max_base_level
                max_plus_level = ability_data.ability_data[id].max_plus_level

                self.set_upgrade(
                    id,
                    upgrade.copy(),
                    max_base=max_base_level - 1,
                    max_plus=max_plus_level,
                )

                color.ColoredText.localize(
                    "selected_skill_upgraded",
                    name=names[id],
                    base_level=skills[id].upgrade.base + 1,
                    plus_level=skills[id].upgrade.plus,
                )
            success = True

        if success:
            color.ColoredText.localize("skills_edited")

    def get_from_id(
        self, id: int, only_valid: bool = True
    ) -> SpecialSkill | None:
        if only_valid:
            skills = self.get_valid_skills()
        else:
            skills = self.skills
        if id >= len(skills) or id < 0:
            return None
        return skills[id]


class AbilityDataItem:
    def __init__(
        self,
        index: int,
        sell_price: int,
        gatya_rarity: int,
        max_base_level: int,
        max_plus_level: int,
        chapter_1_to_2_max_level: int,
    ):
        self.index = index
        self.sell_price = sell_price
        self.gatya_rarity = gatya_rarity
        self.max_base_level = max_base_level
        self.max_plus_level = max_plus_level
        self.chapter_1_to_2_max_level = chapter_1_to_2_max_level


class AbilityData:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.ability_data = self.get_ability_data()

    def get_ability_data(self) -> list[AbilityDataItem] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "AbilityData.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        ability_data: list[AbilityDataItem] = []
        for i, row in enumerate(csv):
            ability_data.append(
                AbilityDataItem(
                    i,
                    row[0].to_int(),
                    row[1].to_int(),
                    row[2].to_int(),
                    row[3].to_int(),
                    row[4].to_int(),
                )
            )
        return ability_data

    def get_ability_data_item(self, item_id: int) -> AbilityDataItem | None:
        if self.ability_data is None:
            return None
        return self.ability_data[item_id]
