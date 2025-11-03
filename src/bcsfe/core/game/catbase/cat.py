from __future__ import annotations
from typing import Any
from bcsfe import core


class SkillLevel:
    def __init__(
        self,
        id: int,
        levels: list[int],
    ):
        self.id = id
        self.levels = levels

    def get_total_levels(self) -> int:
        return len(self.levels)

    @staticmethod
    def from_row(row: core.Row):
        id = row[0].to_int()
        levels = row[1:].to_int_list()
        return SkillLevel(id, levels)


class SkillLevelData:
    def __init__(self, levels: list[SkillLevel] | None):
        self.levels = levels

    @staticmethod
    def from_game_data(save_file: core.SaveFile) -> SkillLevelData | None:
        gdg = core.core_data.get_game_data_getter(save_file)
        data = gdg.download("DataLocal", "SkillLevel.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        levels: list[SkillLevel] = []
        for line in csv.lines[1:]:
            levels.append(SkillLevel.from_row(line))
        return SkillLevelData(levels)

    def get_skill_level(self, id: int) -> SkillLevel | None:
        if self.levels is None:
            return None
        for level in self.levels:
            if level.id == id:
                return level
        return None


class Skill:
    def __init__(
        self,
        ability_id: int,
        max_lv: int,
        min1: int,
        max1: int,
        min2: int,
        max2: int,
        min3: int,
        max3: int,
        min4: int,
        max4: int,
        text_id: int,
        lvid: int,
        name_id: int,
        limit: int,
    ):
        self.ability_id = ability_id
        self.max_lv = max_lv
        self.min1 = min1
        self.max1 = max1
        self.min2 = min2
        self.max2 = max2
        self.min3 = min3
        self.max3 = max3
        self.min4 = min4
        self.max4 = max4
        self.text_id = text_id
        self.lvid = lvid
        self.name_id = name_id
        self.limit = limit


class CatSkill:
    def __init__(
        self,
        cat_id: int,
        type_id: int,
        skills: list[Skill],
    ):
        self.cat_id = cat_id
        self.type_id = type_id
        self.skills = skills

    @staticmethod
    def from_row(row: core.Row):
        cat_id = row[0].to_int()
        type_id = row[1].to_int()
        skills: list[Skill] = []
        for i in range(2, len(row), 14):
            skill = Skill(
                row[i].to_int(),
                row[i + 1].to_int(),
                row[i + 2].to_int(),
                row[i + 3].to_int(),
                row[i + 4].to_int(),
                row[i + 5].to_int(),
                row[i + 6].to_int(),
                row[i + 7].to_int(),
                row[i + 8].to_int(),
                row[i + 9].to_int(),
                row[i + 10].to_int(),
                row[i + 11].to_int(),
                row[i + 12].to_int(),
                row[i + 13].to_int(),
            )
            skills.append(skill)
        return CatSkill(cat_id, type_id, skills)


class CatSkills:
    def __init__(self, skills: dict[int, CatSkill]):
        self.skills = skills

    @staticmethod
    def from_game_data(save_file: core.SaveFile) -> CatSkills | None:
        gdg = core.core_data.get_game_data_getter(save_file)
        data = gdg.download("DataLocal", "SkillAcquisition.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        skills: dict[int, CatSkill] = {}
        for line in csv.lines[1:]:
            skill = CatSkill.from_row(line)
            skills[skill.cat_id] = skill
        return CatSkills(skills)

    def get_cat_skill(self, cat_id: int) -> CatSkill | None:
        return self.skills.get(cat_id)


class SkillNames:
    def __init__(self, names: dict[int, str]):
        self.names = names

    @staticmethod
    def from_game_data(save_file: core.SaveFile) -> SkillNames | None:
        gdg = core.core_data.get_game_data_getter(save_file)
        data = gdg.download("resLocal", "SkillDescriptions.csv")
        if data is None:
            return None
        csv = core.CSV(
            data, delimiter=core.Delimeter.from_country_code_res(save_file.cc)
        )
        names: dict[int, str] = {}
        for line in csv.lines[1:]:
            names[line[0].to_int()] = line[1].to_str()
        return SkillNames(names)

    def get_skill_name(self, skill_id: int) -> str | None:
        return self.names.get(skill_id)


class TalentData:
    def __init__(
        self,
        skill_names: SkillNames,
        skill_levels: SkillLevelData,
        cats: CatSkills,
    ):
        self.skill_names = skill_names
        self.skill_levels = skill_levels
        self.cats = cats

    @staticmethod
    def from_game_data(save_file: core.SaveFile) -> TalentData | None:
        skill_names = SkillNames.from_game_data(save_file)
        skill_levels = SkillLevelData.from_game_data(save_file)
        cats = CatSkills.from_game_data(save_file)
        if skill_names is None or skill_levels is None or cats is None:
            return None

        return TalentData(skill_names, skill_levels, cats)

    def get_skill_name(self, skill_id: int) -> str | None:
        return self.skill_names.get_skill_name(skill_id)

    def get_skill_level(self, skill_id: int) -> SkillLevel | None:
        return self.skill_levels.get_skill_level(skill_id)

    def get_cat_skill(self, cat_id: int) -> CatSkill | None:
        return self.cats.get_cat_skill(cat_id)

    def get_skill_from_cat(self, cat_id: int, skill_id: int) -> Skill | None:
        cat_skill = self.get_cat_skill(cat_id)
        if cat_skill is None:
            return None
        for skill in cat_skill.skills:
            if skill.ability_id == skill_id:
                return skill
        return None

    def get_talent_from_cat_skill(self, cat: core.Cat, skill_id: int) -> Talent | None:
        talents = cat.talents
        if talents is None:
            return None
        for talent in talents:
            if talent.id == skill_id:
                return talent
        return None

    def get_cat_skill_name(self, cat_id: int, skill_id: int) -> str | None:
        skill = self.get_skill_from_cat(cat_id, skill_id)
        if skill is None:
            return None
        return self.get_skill_name(skill.text_id)

    def get_cat_skill_level(self, cat_id: int, skill_id: int) -> SkillLevel | None:
        skill = self.get_skill_from_cat(cat_id, skill_id)
        if skill is None:
            return None
        return self.get_skill_level(skill.lvid)

    def get_cat_talents(
        self, cat: core.Cat
    ) -> tuple[list[str], list[int], list[int], list[int]] | None:
        talent_data_cat = self.get_cat_skill(cat.id)
        if talent_data_cat is None or cat.talents is None:
            return None
        # save_talent_data = cat.talents
        talent_names: list[str] = []
        max_levels: list[int] = []
        current_levels: list[int] = []
        ids: list[int] = []
        for skill in talent_data_cat.skills:
            name = self.get_skill_name(skill.text_id)
            talent = self.get_talent_from_cat_skill(cat, skill.ability_id)
            if name is None or talent is None:
                continue

            max_level = skill.max_lv
            if max_level == 0:
                max_level = 1

            max_levels.append(max_level)
            talent_names.append(name.split("<br>")[0])
            current_levels.append(talent.level)
            ids.append(skill.ability_id)

        return talent_names, max_levels, current_levels, ids


class Talent:
    def __init__(self, id: int, level: int):
        self.id = id
        self.level = level

    @staticmethod
    def init() -> Talent:
        return Talent(0, 0)

    def reset(self):
        self.level = 0

    @staticmethod
    def read(stream: core.Data):
        return Talent(stream.read_int(), stream.read_int())

    def write(self, stream: core.Data):
        stream.write_int(self.id)
        stream.write_int(self.level)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "level": self.level,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Talent:
        return Talent(
            data["id"],
            data["level"],
        )

    def __repr__(self):
        return f"Talent({self.id}, {self.level})"

    def __str__(self):
        return self.__repr__()


class NyankoPictureBookCatData:
    def __init__(
        self,
        cat_id: int,
        is_displayed_in_catguide: bool,
        limited: bool,
        total_forms: int,
        hint_display_type: int,
        scale_0: int,
        scale_1: int,
        scale_2: int,
        scale_3: int,
    ):
        self.cat_id = cat_id
        self.is_displayed_in_catguide = is_displayed_in_catguide
        self.limited = limited
        self.total_forms = total_forms
        self.hint_display_type = hint_display_type
        self.scale_0 = scale_0
        self.scale_1 = scale_1
        self.scale_2 = scale_2
        self.scale_3 = scale_3


class NyankoPictureBook:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.cats = self.get_cats()

    def get_cats(self) -> list[NyankoPictureBookCatData] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "nyankoPictureBookData.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        cats: list[NyankoPictureBookCatData] = []
        for i, line in enumerate(csv):
            cat = NyankoPictureBookCatData(
                i,
                line[0].to_bool(),
                line[1].to_bool(),
                line[2].to_int(),
                line[3].to_int(),
                line[4].to_int(),
                line[5].to_int(),
                line[6].to_int(),
                line[7].to_int(),
            )
            cats.append(cat)
        return cats

    def get_cat(self, cat_id: int) -> NyankoPictureBookCatData | None:
        if self.cats is None:
            return None
        for cat in self.cats:
            if cat.cat_id == cat_id:
                return cat
        return None

    def get_obtainable_cats(self) -> list[NyankoPictureBookCatData] | None:
        if self.cats is None:
            return None
        return [cat for cat in self.cats if cat.is_displayed_in_catguide]


class EvolveItem:
    """Represents an item used to evolve a unit."""

    def __init__(
        self,
        item_id: int,
        amount: int,
    ):
        """Initializes a new EvolveItem object.

        Args:
            item_id (int): The ID of the item.
            amount (int): The amount of the item.
        """
        self.item_id = item_id
        self.amount = amount

    def __str__(self) -> str:
        """Gets a string representation of the EvolveItem object.

        Returns:
            str: The string representation of the EvolveItem object.
        """
        return f"{self.item_id}:{self.amount}"

    def __repr__(self) -> str:
        """Gets a string representation of the EvolveItem object.

        Returns:
            str: The string representation of the EvolveItem object.
        """
        return str(self)


class EvolveItems:
    """Represents the items used to evolve a unit."""

    def __init__(self, evolve_items: list[EvolveItem]):
        """Initializes a new EvolveItems object.

        Args:
            evolve_items (list[EvolveItem]): The items used to evolve a unit.
        """
        self.evolve_items = evolve_items

    @staticmethod
    def from_unit_buy_list(raw_data: core.Row, start_index: int) -> EvolveItems:
        """Creates a new EvolveItems object from a row from unitbuy.csv.

        Args:
            raw_data (core.Row): The row from unitbuy.csv.

        Returns:
            EvolveItems: The EvolveItems object.
        """
        items: list[EvolveItem] = []
        for i in range(5):
            item_id = raw_data[start_index + i * 2].to_int()
            amount = raw_data[start_index + 1 + i * 2].to_int()
            items.append(EvolveItem(item_id, amount))
        return EvolveItems(items)


class UnitBuyCatData:
    def __init__(self, id: int, raw_data: core.Row):
        self.id = id
        self.assign(raw_data)

    def assign(self, raw_data: core.Row):
        self.stage_unlock = raw_data[0].to_int()
        self.purchase_cost = raw_data[1].to_int()
        self.upgrade_costs = [cost.to_int() for cost in raw_data[2:12]]
        self.unlock_source = raw_data[12].to_int()
        self.rarity = raw_data[13].to_int()
        self.position_order = raw_data[14].to_int()
        self.chapter_unlock = raw_data[15].to_int()
        self.sell_price = raw_data[16].to_int()
        self.gatya_rarity = raw_data[17].to_int()
        self.original_max_levels = raw_data[18].to_int(), raw_data[19].to_int()
        self.force_true_form_level = raw_data[20].to_int()
        self.second_form_unlock_level = raw_data[21].to_int()
        self.unknown_22 = raw_data[22].to_int()
        self.tf_id = raw_data[23].to_int()
        self.ff_id = raw_data[24].to_int()
        self.evolve_level_tf = raw_data[25].to_int()
        self.evolve_level_ff = raw_data[26].to_int()
        self.evolve_cost_tf = raw_data[27].to_int()
        self.evolve_items_tf = EvolveItems.from_unit_buy_list(raw_data, 28)
        self.evolve_cost_ff = raw_data[38].to_int()
        self.evolve_items_ff = EvolveItems.from_unit_buy_list(raw_data, 39)
        self.max_upgrade_level_no_catseye = raw_data[49].to_int()
        self.max_upgrade_level_catseye = raw_data[50].to_int()
        self.max_plus_upgrade_level = raw_data[51].to_int()
        self.unknown_52 = raw_data[52].to_int()
        self.unknown_53 = raw_data[53].to_int()
        self.unknown_54 = raw_data[54].to_int()
        self.unknown_55 = raw_data[55].to_int()
        self.catseye_usage_pattern = raw_data[56].to_int()
        self.game_version = raw_data[57].to_int()
        self.np_sell_price = raw_data[58].to_int()
        self.unknwon_59 = raw_data[59].to_int()
        self.unknown_60 = raw_data[60].to_int()
        self.egg_value = raw_data[61].to_int()
        self.egg_id = raw_data[62].to_int()


class UnitBuy:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.unit_buy = self.read_unit_buy()

    def read_unit_buy(self) -> list[UnitBuyCatData] | None:
        unit_buy: list[UnitBuyCatData] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "unitbuy.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        for i, line in enumerate(csv):
            unit_buy.append(UnitBuyCatData(i, line))
        return unit_buy

    def get_unit_buy(self, id: int) -> UnitBuyCatData | None:
        if self.unit_buy is None:
            return None
        try:
            return self.unit_buy[id]
        except IndexError:
            return None

    def get_cat_rarity(self, id: int) -> int:
        unit_buy = self.get_unit_buy(id)
        if unit_buy is None:
            return -1
        return unit_buy.rarity


class UnitLimitCatData:
    def __init__(self, cat_id: int, values: list[int]):
        self.cat_id = cat_id
        self.values = values


class UnitLimit:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.unit_limit = self.read_unit_limit()

    def read_unit_limit(self) -> list[UnitLimitCatData] | None:
        unit_limit: list[UnitLimitCatData] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "unitlimit.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        for i, line in enumerate(csv):
            unit_limit.append(UnitLimitCatData(i, line.to_int_list()))
        return unit_limit

    def get_unit_limit(self, id: int) -> UnitLimitCatData | None:
        if self.unit_limit is None:
            return None

        try:
            return self.unit_limit[id]
        except IndexError:
            return None


class Cat:
    def __init__(self, id: int, unlocked: int):
        self.id = id
        self.unlocked = unlocked
        self.talents: list[Talent] | None = None
        self.upgrade: core.Upgrade = core.Upgrade.init()
        self.current_form: int = 0
        self.unlocked_forms: int = 0
        self.gatya_seen: int = 0
        self.max_upgrade_level: core.Upgrade = core.Upgrade.init()
        self.catguide_collected: bool = False
        self.fourth_form: int = 0
        self.catseyes_used: int = 0

        self.names: list[str] | None = None

    def get_talent_from_id(self, id: int) -> Talent | None:
        for talent in self.talents or []:
            if talent.id == id:
                return talent
        return None

    def unlock(self, save_file: core.SaveFile):
        self.unlocked = 1
        self.gatya_seen = 1
        core.core_data.get_chara_drop(save_file).unlock_drops_from_cat_id(self.id)
        save_file.unlock_equip_menu()

    def remove(self, reset: bool = False, save_file: core.SaveFile | None = None):
        self.unlocked = 0
        if reset:
            self.reset()
            if save_file is not None:
                save_file.cats.chara_new_flags[self.id] = 0
                core.core_data.get_chara_drop(save_file).remove_drops_from_cat_id(
                    self.id
                )

    def true_form(self, save_file: core.SaveFile, set_current_form: bool = True):
        self.set_form(2, save_file, set_current_form)

    def set_form(
        self, form: int, save_file: core.SaveFile, set_current_form: bool = True
    ):
        if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
            self.unlock(save_file)
        self.unlocked_forms = form + 1
        if set_current_form:
            self.current_form = form

    def set_form_true(
        self,
        save_file: core.SaveFile,
        total_forms: int,
        set_current_form: bool = True,
        fourth_form: bool = False,
    ):
        if total_forms == 4 and self.unlocked_forms == 3 and fourth_form:
            self.unlock_fourth_form(save_file, set_current_form)
        elif total_forms >= 3:
            self.true_form(save_file, set_current_form)
        elif total_forms == 2:
            self.unlocked_forms = 0
            self.current_form = 1
        else:
            self.unlocked_forms = 0
            self.current_form = 0

    def remove_true_form(self):
        self.unlocked_forms = 0
        self.current_form = min(self.current_form, 1)
        self.fourth_form = 0

    def unlock_fourth_form(
        self, save_file: core.SaveFile, set_current_form: bool = True
    ):
        if set_current_form:
            self.current_form = 3
        if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
            self.unlock(save_file)
        self.fourth_form = 2

    def remove_fourth_form(self):
        self.current_form = min(self.current_form, 2)
        self.fourth_form = 0

    def set_upgrade(
        self,
        save_file: core.SaveFile,
        upgrade: core.Upgrade,
        only_plus: bool = False,
    ):
        if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
            self.unlock(save_file)
        base = upgrade.base
        plus = upgrade.plus
        if base != -1 and not only_plus:
            self.upgrade.base = upgrade.get_random_base()
        if plus != -1:
            self.upgrade.plus = upgrade.get_random_plus()

    def upgrade_base(self, save_file: core.SaveFile):
        if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
            self.unlock(save_file)
        self.upgrade.upgrade()

    def reset(self):
        self.unlocked = 0
        self.current_form = 0
        self.unlocked_forms = 0
        self.gatya_seen = 0
        self.catguide_collected = False
        self.fourth_form = 0
        self.catseyes_used = 0
        self.upgrade.reset()
        for talent in self.talents or []:
            talent.reset()

    @staticmethod
    def init(id: int) -> Cat:
        return Cat(id, 0)

    @staticmethod
    def read_unlocked(id: int, stream: core.Data):
        return Cat(id, stream.read_int())

    def write_unlocked(self, stream: core.Data):
        stream.write_int(self.unlocked)

    def read_upgrade(self, stream: core.Data):
        self.upgrade = core.Upgrade.read(stream)

    def write_upgrade(self, stream: core.Data):
        self.upgrade.write(stream)

    def read_current_form(self, stream: core.Data):
        self.current_form = stream.read_int()

    def write_current_form(self, stream: core.Data):
        stream.write_int(self.current_form)

    def read_unlocked_forms(self, stream: core.Data):
        self.unlocked_forms = stream.read_int()

    def write_unlocked_forms(self, stream: core.Data):
        stream.write_int(self.unlocked_forms)

    def read_gatya_seen(self, stream: core.Data):
        self.gatya_seen = stream.read_int()

    def write_gatya_seen(self, stream: core.Data):
        stream.write_int(self.gatya_seen)

    def read_max_upgrade_level(self, stream: core.Data):
        level = core.Upgrade.read(stream)
        self.max_upgrade_level = level

    def write_max_upgrade_level(self, stream: core.Data):
        self.max_upgrade_level.write(stream)

    def read_catguide_collected(self, stream: core.Data):
        self.catguide_collected = stream.read_bool()

    def write_catguide_collected(self, stream: core.Data):
        stream.write_bool(self.catguide_collected)

    def read_fourth_form(self, stream: core.Data):
        self.fourth_form = stream.read_int()

    def write_fourth_form(self, stream: core.Data):
        stream.write_int(self.fourth_form)

    def read_catseyes_used(self, stream: core.Data):
        self.catseyes_used = stream.read_int()

    def write_catseyes_used(self, stream: core.Data):
        stream.write_int(self.catseyes_used)

    def serialize(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "unlocked": self.unlocked,
            "upgrade": self.upgrade.serialize(),
            "current_form": self.current_form,
            "unlocked_forms": self.unlocked_forms,
            "gatya_seen": self.gatya_seen,
            "max_upgrade_level": self.max_upgrade_level.serialize(),
            "catguide_collected": self.catguide_collected,
            "fourth_form": self.fourth_form,
            "catseyes_used": self.catseyes_used,
            "talents": (
                [talent.serialize() for talent in self.talents]
                if self.talents is not None
                else None
            ),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Cat:
        cat = Cat(data["id"], data["unlocked"])
        cat.upgrade = core.Upgrade.deserialize(data["upgrade"])
        cat.current_form = data["current_form"]
        cat.unlocked_forms = data["unlocked_forms"]
        cat.gatya_seen = data["gatya_seen"]
        cat.max_upgrade_level = core.Upgrade.deserialize(data["max_upgrade_level"])
        cat.catguide_collected = data["catguide_collected"]
        cat.fourth_form = data["fourth_form"]
        cat.catseyes_used = data["catseyes_used"]
        cat.talents = (
            [Talent.deserialize(talent) for talent in data["talents"]]
            if data["talents"] is not None
            else None
        )
        return cat

    def __repr__(self) -> str:
        return f"Cat(id={self.id}, unlocked={self.unlocked}, upgrade={self.upgrade}, current_form={self.current_form}, unlocked_forms={self.unlocked_forms}, gatya_seen={self.gatya_seen}, max_upgrade_level={self.max_upgrade_level}, catguide_collected={self.catguide_collected}, fourth_form={self.fourth_form}, catseyes_used={self.catseyes_used}, talents={self.talents})"

    def __str__(self) -> str:
        return self.__repr__()

    def read_talents(self, stream: core.Data):
        self.talents = []
        for _ in range(stream.read_int()):
            self.talents.append(Talent.read(stream))

    def write_talents(self, stream: core.Data):
        if self.talents is None:
            return
        stream.write_int(len(self.talents))
        for talent in self.talents:
            talent.write(stream)

    def get_names_cls(self, save_file: core.SaveFile) -> list[str] | None:
        if self.names is None:
            self.names = Cat.get_names(self.id, save_file)
        return self.names

    @staticmethod
    def get_names(
        id: int,
        save_file: core.SaveFile,
    ) -> list[str] | None:
        file_name = f"Unit_Explanation{id + 1}_{core.core_data.get_lang(save_file)}.csv"
        data = core.core_data.get_game_data_getter(save_file).download(
            "resLocal", file_name
        )
        if data is None:
            return None
        csv = core.CSV(
            data,
            core.Delimeter.from_country_code_res(save_file.cc),
            remove_empty=False,
        )
        names: list[str] = []
        for line in csv.lines:
            names.append(line[0].to_str())

        return names


class StorageItem:
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.item_type = 0

    @staticmethod
    def from_cat(cat_id: int) -> StorageItem:
        item = StorageItem(cat_id)
        item.item_type = 1
        return item

    @staticmethod
    def from_special_skill(special_skill_id: int) -> StorageItem:
        item = StorageItem(special_skill_id)
        item.item_type = 2
        return item

    @staticmethod
    def init() -> StorageItem:
        return StorageItem(0)

    @staticmethod
    def read_item_id(stream: core.Data):
        return StorageItem(stream.read_int())

    def write_item_id(self, stream: core.Data):
        stream.write_int(self.item_id)

    def read_item_type(self, stream: core.Data):
        self.item_type = stream.read_int()

    def write_item_type(self, stream: core.Data):
        stream.write_int(self.item_type)

    def serialize(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> StorageItem:
        item = StorageItem(data.get("item_id", 0))
        item.item_type = data.get("item_type", 0)
        return item

    def __repr__(self) -> str:
        return f"StorageItem(item_id={self.item_id}, item_type={self.item_type})"

    def __str__(self) -> str:
        return f"StorageItem(item_id={self.item_id}, item_type={self.item_type})"


class Cats:
    def __init__(self, cats: list[Cat], total_storage_items: int = 0):
        self.cats = cats
        self.storage_items = [StorageItem.init() for _ in range(total_storage_items)]
        self.favourites: dict[int, bool] = {}
        self.chara_new_flags: dict[int, int] = {}
        self.unit_buy: UnitBuy | None = None
        self.unit_limit: UnitLimit | None = None
        self.nyanko_picture_book: NyankoPictureBook | None = None
        self.talent_data: TalentData | None = None

    def get_all_cats(self) -> list[Cat]:
        return self.cats

    @staticmethod
    def init(gv: core.GameVersion) -> Cats:
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = 0
        cats_l: list[Cat] = []
        for i in range(total_cats):
            cats_l.append(Cat.init(i))

        if gv < 110100:
            total_storage_items = 100
        else:
            total_storage_items = 0
        return Cats(cats_l, total_storage_items)

    @staticmethod
    def get_gv_cats(gv: core.GameVersion) -> int | None:
        if gv == 20:
            total_cats = 203
        elif gv == 21:
            total_cats = 214
        elif gv == 22:
            total_cats = 231
        elif gv == 23:
            total_cats = 241
        elif gv == 24:
            total_cats = 249
        elif gv == 25:
            total_cats = 260
        else:
            total_cats = None
        return total_cats

    def get_unlocked_cats(self) -> list[Cat]:
        return [cat for cat in self.cats if cat.unlocked]

    def get_non_unlocked_cats(self) -> list[Cat]:
        return [cat for cat in self.cats if not cat.unlocked]

    def get_non_gacha_cats(self, save_file: core.SaveFile) -> list[Cat]:
        unitbuy = self.read_unitbuy(save_file)
        cats: list[Cat] = []
        for cat in self.cats:
            unit_buy_data = unitbuy.get_unit_buy(cat.id)
            if unit_buy_data is None:
                continue

            if unit_buy_data.unlock_source != 2:
                cats.append(cat)

        return cats

    def read_unitbuy(self, save_file: core.SaveFile) -> UnitBuy:
        if self.unit_buy is None:
            self.unit_buy = UnitBuy(save_file)
        return self.unit_buy

    def read_unitlimit(self, save_file: core.SaveFile) -> UnitLimit:
        if self.unit_limit is None:
            self.unit_limit = UnitLimit(save_file)
        return self.unit_limit

    def read_nyanko_picture_book(self, save_file: core.SaveFile) -> NyankoPictureBook:
        if self.nyanko_picture_book is None:
            self.nyanko_picture_book = NyankoPictureBook(save_file)
        return self.nyanko_picture_book

    def read_talent_data(self, save_file: core.SaveFile) -> TalentData | None:
        if self.talent_data is None:
            self.talent_data = TalentData.from_game_data(save_file)
        return self.talent_data

    def get_cats_rarity(self, save_file: core.SaveFile, rarity: int) -> list[Cat]:
        unit_buy = self.read_unitbuy(save_file)
        return [cat for cat in self.cats if unit_buy.get_cat_rarity(cat.id) == rarity]

    def get_cats_name(
        self,
        save_file: core.SaveFile,
        search_name: str,
    ) -> list[Cat]:
        cats: list[Cat] = []
        for cat in self.cats:
            names = cat.get_names_cls(save_file)
            if names is None:
                continue
            for name in names:
                if search_name.lower() in name.lower():
                    cats.append(cat)
                    break
        return cats

    def get_cats_obtainable(self, save_file: core.SaveFile) -> list[Cat] | None:
        nyanko_picture_book = self.read_nyanko_picture_book(save_file)
        obtainable_cats = nyanko_picture_book.get_obtainable_cats()
        if obtainable_cats is None:
            return None
        ny_cats = [cat.cat_id for cat in obtainable_cats]
        cats: list[Cat] = []
        for cat in self.cats:
            if cat.id in ny_cats:
                cats.append(cat)
        return cats

    def get_cats_non_obtainable(self, save_file: core.SaveFile) -> list[Cat] | None:
        nyanko_picture_book = self.read_nyanko_picture_book(save_file)
        obtainable_cats = nyanko_picture_book.get_obtainable_cats()
        if obtainable_cats is None:
            return None
        ny_cats = [cat.cat_id for cat in obtainable_cats]
        cats: list[Cat] = []
        for cat in self.cats:
            if cat.id not in ny_cats:
                cats.append(cat)
        return cats

    def get_cats_gatya_banner(
        self, save_file: core.SaveFile, gatya_id: int
    ) -> list[core.Cat] | None:
        cat_ids = save_file.gatya.read_gatya_data_set(save_file).get_cat_ids(gatya_id)
        if cat_ids is None:
            return None
        return self.get_cats_by_ids(cat_ids)

    def true_form_cats(
        self,
        save_file: core.SaveFile,
        cats: list[Cat],
        force: bool = False,
        set_current_forms: bool = True,
    ):
        pic_book = self.read_nyanko_picture_book(save_file)
        for cat in cats:
            pic_book_cat = pic_book.get_cat(cat.id)
            if force:
                cat.true_form(save_file, set_current_form=set_current_forms)
            elif pic_book_cat is not None:
                cat.set_form_true(
                    save_file,
                    pic_book_cat.total_forms,
                    set_current_form=set_current_forms,
                )

    def fourth_form_cats(
        self,
        save_file: core.SaveFile,
        cats: list[Cat],
        force: bool = False,
        set_current_forms: bool = True,
    ):
        pic_book = self.read_nyanko_picture_book(save_file)
        for cat in cats:
            pic_book_cat = pic_book.get_cat(cat.id)
            if force:
                cat.unlock_fourth_form(save_file, set_current_form=set_current_forms)
            elif pic_book_cat is not None:
                cat.set_form_true(
                    save_file,
                    pic_book_cat.total_forms,
                    set_current_form=set_current_forms,
                    fourth_form=True,
                )

    def get_cats_by_ids(self, ids: list[int]) -> list[Cat]:
        cats: list[Cat] = []
        for cat in self.cats:
            if cat.id in ids:
                cats.append(cat)
        return cats

    def get_cat_by_id(self, id: int) -> Cat | None:
        for cat in self.cats:
            if cat.id == id:
                return cat
        return None

    @staticmethod
    def get_rarity_names(save_file: core.SaveFile) -> list[str]:
        localizable = save_file.get_localizable()
        rarity_names: list[str] = []
        rarity_index = 1
        while True:
            rarity_name = localizable.get(f"rarity_name_{rarity_index}")
            if rarity_name is None:
                break
            rarity_names.append(rarity_name)
            rarity_index += 1
        return rarity_names

    @staticmethod
    def read_unlocked(stream: core.Data, gv: core.GameVersion) -> Cats:
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        cats_l: list[Cat] = []
        for i in range(total_cats):
            cats_l.append(Cat.read_unlocked(i, stream))
        return Cats(cats_l)

    def write_unlocked(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_unlocked(stream)

    def read_upgrade(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_upgrade(stream)

    def write_upgrade(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_upgrade(stream)

    def read_current_form(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_current_form(stream)

    def write_current_form(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_current_form(stream)

    def read_unlocked_forms(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_unlocked_forms(stream)

    def write_unlocked_forms(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_unlocked_forms(stream)

    def read_gatya_seen(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_gatya_seen(stream)

    def write_gatya_seen(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_gatya_seen(stream)

    def read_max_upgrade_levels(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            total_cats = stream.read_int()
        for cat in self.cats:
            cat.read_max_upgrade_level(stream)

    def write_max_upgrade_levels(self, stream: core.Data, gv: core.GameVersion):
        total_cats = Cats.get_gv_cats(gv)
        if total_cats is None:
            stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_max_upgrade_level(stream)

    def read_storage(self, stream: core.Data, gv: core.GameVersion):
        if gv < 110100:
            total_storage = 100
        else:
            total_storage = stream.read_short()
        self.storage_items: list[StorageItem] = []
        for _ in range(total_storage):
            self.storage_items.append(StorageItem.read_item_id(stream))
        for item in self.storage_items:
            item.read_item_type(stream)

    def write_storage(self, stream: core.Data, gv: core.GameVersion):
        if gv >= 110100:
            stream.write_short(len(self.storage_items))
        for item in self.storage_items:
            item.write_item_id(stream)
        for item in self.storage_items:
            item.write_item_type(stream)

    def read_catguide_collected(self, stream: core.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_catguide_collected(stream)

    def write_catguide_collected(self, stream: core.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_catguide_collected(stream)

    def read_fourth_forms(self, stream: core.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_fourth_form(stream)

    def read_catseyes_used(self, stream: core.Data):
        total_cats = stream.read_int()
        for i in range(total_cats):
            self.cats[i].read_catseyes_used(stream)

    def write_catseyes_used(self, stream: core.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_catseyes_used(stream)

    def write_fourth_forms(self, stream: core.Data):
        stream.write_int(len(self.cats))
        for cat in self.cats:
            cat.write_fourth_form(stream)

    def read_favorites(self, stream: core.Data):
        self.favourites: dict[int, bool] = {}
        total_cats = stream.read_int()
        for _ in range(total_cats):
            cat_id = stream.read_int()
            self.favourites[cat_id] = stream.read_bool()

    def write_favorites(self, stream: core.Data):
        stream.write_int(len(self.favourites))
        for cat_id, is_favourite in self.favourites.items():
            stream.write_int(cat_id)
            stream.write_bool(is_favourite)

    def read_chara_new_flags(self, stream: core.Data):
        self.chara_new_flags: dict[int, int] = {}
        total_cats = stream.read_int()
        for _ in range(total_cats):
            cat_id = stream.read_int()
            self.chara_new_flags[cat_id] = stream.read_int()

    def write_chara_new_flags(self, stream: core.Data):
        stream.write_int(len(self.chara_new_flags))
        for cat_id, new_flag in self.chara_new_flags.items():
            stream.write_int(cat_id)
            stream.write_int(new_flag)

    def read_talents(self, stream: core.Data):
        total_cats = stream.read_int()
        for _ in range(total_cats):
            cat_id = stream.read_int()
            if cat_id < 0 or cat_id >= len(self.cats):
                continue
            self.cats[cat_id].read_talents(stream)

    def write_talents(self, stream: core.Data):
        total_talents = 0
        for cat in self.cats:
            total_talents += 1 if cat.talents is not None else 0
        stream.write_int(total_talents)
        for cat in self.cats:
            if not cat.talents:
                continue
            stream.write_int(cat.id)
            cat.write_talents(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "cats": [cat.serialize() for cat in self.cats],
            "storage_items": [item.serialize() for item in self.storage_items],
            "favorites": self.favourites,
            "chara_new_flags": self.chara_new_flags,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Cats:
        cats_l = [Cat.deserialize(cat) for cat in data.get("cats", [])]
        cats = Cats(cats_l)
        cats.storage_items = [
            StorageItem.deserialize(item) for item in data.get("storage_items", [])
        ]
        cats.favourites = data.get("favorites", {})
        cats.chara_new_flags = data.get("chara_new_flags", {})
        return cats

    def __repr__(self) -> str:
        return f"Cats(cats={self.cats}, storage_items={self.storage_items}, favourites={self.favourites}, chara_new_flags={self.chara_new_flags})"

    def __str__(self) -> str:
        return self.__repr__()
