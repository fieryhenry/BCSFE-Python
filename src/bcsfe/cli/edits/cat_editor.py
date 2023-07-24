import enum
from typing import Optional

from bcsfe import core
from bcsfe.cli import color, dialog_creator


class SelectMode(enum.Enum):
    AND = 0
    OR = 1
    REPLACE = 2


class CatEditor:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file

    def get_current_cats(self):
        return self.save_file.cats.get_unlocked_cats()

    def check_and_filter(self, cats: list["core.Cat"]) -> list["core.Cat"]:
        if core.config.get_bool(core.ConfigKey.FILTER_CURRENT_CATS):
            return self.filter_cats(cats)
        return cats

    def filter_cats(self, cats: list["core.Cat"]) -> list["core.Cat"]:
        unlocked_cats = self.get_current_cats()
        return [cat for cat in cats if cat in unlocked_cats]

    def get_cats_rarity(self, rarity: int) -> list["core.Cat"]:
        return self.save_file.cats.get_cats_rarity(self.save_file, rarity)

    def get_cats_name(self, name: str) -> list["core.Cat"]:
        return self.save_file.cats.get_cats_name(self.save_file, name)

    def get_cats_obtainable(self) -> list["core.Cat"]:
        return self.save_file.cats.get_cats_obtainable(self.save_file)

    def get_cats_gatya_banner(self, gatya_id: int) -> list["core.Cat"]:
        cat_ids = self.save_file.gatya.read_gatya_data_set(self.save_file).get_cat_ids(
            gatya_id
        )
        return self.save_file.cats.get_cats_by_ids(cat_ids)

    def print_selected_cats(self, current_cats: list["core.Cat"]):
        if not current_cats:
            return
        if len(current_cats) > 50:
            color.ColoredText.localize("total_selected_cats", total=len(current_cats))
        else:
            self.save_file.cats.bulk_download_names(self.save_file)
            localizable = self.save_file.get_localizable()
            for cat in current_cats:
                names = cat.get_names_cls(self.save_file, localizable)
                if not names:
                    names = [str(cat.id)]
                color.ColoredText.localize("selected_cat", id=cat.id, name=names[0])

    def select(
        self,
        current_cats: Optional[list["core.Cat"]] = None,
    ) -> Optional[list["core.Cat"]]:
        if current_cats is None:
            current_cats = []
        self.print_selected_cats(current_cats)

        options: list[str] = [
            "select_cats_all",
            "select_cats_current",
            "select_cats_obtainable",
            "select_cats_id",
            "select_cats_name",
            "select_cats_rarity",
            "select_cats_gatya_banner",
        ]
        option_id = dialog_creator.ChoiceInput(
            options, options, [], {}, "select_cats", True
        ).single_choice()
        if option_id is None:
            return current_cats
        option_id -= 1
        if option_id == 0:
            cats = self.save_file.cats.cats
            return cats

        if option_id == 1:
            new_cats = self.get_current_cats()
        if option_id == 2:
            new_cats = self.select_obtainable()
        elif option_id == 3:
            new_cats = self.select_id()
        elif option_id == 4:
            new_cats = self.select_name()
        elif option_id == 5:
            new_cats = self.select_rarity()
        elif option_id == 6:
            new_cats = self.select_gatya_banner()
        else:
            new_cats = []

        if new_cats is None:
            return None

        if current_cats:
            mode_id = dialog_creator.IntInput().get_basic_input_locale("and_mode_q", {})
            if mode_id is None:
                mode = SelectMode.OR
            elif mode_id == 1:
                mode = SelectMode.AND
            elif mode_id == 2:
                mode = SelectMode.OR
            elif mode_id == 3:
                mode = SelectMode.REPLACE
            else:
                mode = SelectMode.OR
        else:
            mode = SelectMode.OR

        new_cats = self.check_and_filter(new_cats)

        if mode == SelectMode.AND:
            return [cat for cat in new_cats if cat in current_cats]
        if mode == SelectMode.OR:
            return list(set(current_cats + new_cats))
        if mode == SelectMode.REPLACE:
            return new_cats
        return new_cats

    def select_id(self) -> Optional[list["core.Cat"]]:
        cat_ids = dialog_creator.RangeInput(
            len(self.save_file.cats.cats) - 1
        ).get_input_locale("enter_cat_ids", {})
        if cat_ids is None:
            return None
        return self.save_file.cats.get_cats_by_ids(cat_ids)

    def select_rarity(self) -> Optional[list["core.Cat"]]:
        rarity_names = self.save_file.cats.get_rarity_names(self.save_file)
        rarity_ids, _ = dialog_creator.ChoiceInput(
            rarity_names, rarity_names, [], {}, "select_rarity"
        ).multiple_choice()
        if rarity_ids is None:
            return None
        cats: list["core.Cat"] = []
        for rarity_id in rarity_ids:
            rarity_cats = self.get_cats_rarity(rarity_id)
            cats = list(set(cats + rarity_cats))
        return cats

    def select_name(self) -> Optional[list["core.Cat"]]:
        usr_name = dialog_creator.StringInput().get_input_locale("enter_name", {})
        if usr_name is None:
            return []
        cats = self.get_cats_name(usr_name)
        localizable = self.save_file.get_localizable()
        cat_names: list[str] = []
        cat_list: list["core.Cat"] = []
        for cat in cats:
            names = cat.get_names_cls(self.save_file, localizable)
            if not names:
                names = [str(cat.id)]
            for name in names:
                if usr_name.lower() in name.lower():
                    cat_names.append(name)
                    cat_list.append(cat)
                    break
        cat_option_ids, _ = dialog_creator.ChoiceInput(
            cat_names, cat_names, [], {}, "select_name"
        ).multiple_choice()
        if cat_option_ids is None:
            return None
        cats_selected: list["core.Cat"] = []
        for cat_option_id in cat_option_ids:
            cats_selected.append(cat_list[cat_option_id])
        return cats_selected

    def select_obtainable(self) -> list["core.Cat"]:
        cats = self.get_cats_obtainable()
        return cats

    def select_gatya_banner(self) -> Optional[list["core.Cat"]]:
        gatya_ids = dialog_creator.RangeInput(
            len(self.save_file.gatya.read_gatya_data_set(self.save_file).gatya_data_set)
            - 1
        ).get_input_locale("select_gatya_banner", {})
        if gatya_ids is None:
            return None
        cats: list["core.Cat"] = []
        for gatya_id in gatya_ids:
            gatya_cats = self.get_cats_gatya_banner(gatya_id)
            cats = list(set(cats + gatya_cats))
        return cats

    def unlock_cats(self, cats: list["core.Cat"]):
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.unlock(self.save_file)
        color.ColoredText.localize("unlock_success")

    def remove_cats(self, cats: list["core.Cat"]):
        reset = core.config.get_bool(core.ConfigKey.RESET_CAT_DATA)
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.remove(reset=reset)
        color.ColoredText.localize("remove_success")

    def get_save_cats(self, cats: list["core.Cat"]):
        ct_cats: list["core.Cat"] = []
        for cat in cats:
            ct = self.save_file.cats.get_cat_by_id(cat.id)
            if ct is None:
                continue
            ct_cats.append(ct)
        return ct_cats

    def true_form_cats(self, cats: list["core.Cat"], force: bool = False):
        cats = self.get_save_cats(cats)
        pic_book = self.save_file.cats.read_nyanko_picture_book(self.save_file)
        set_current_forms = core.config.get_bool(core.ConfigKey.SET_CAT_CURRENT_FORMS)
        for cat in cats:
            pic_book_cat = pic_book.get_cat(cat.id)
            if force:
                cat.true_form(self.save_file, set_current_form=set_current_forms)
            elif pic_book_cat is not None:
                cat.set_form_true(
                    self.save_file,
                    pic_book_cat.total_forms,
                    set_current_form=set_current_forms,
                )
        color.ColoredText.localize("true_form_success")

    def remove_true_form_cats(self, cats: list["core.Cat"]):
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.remove_true_form()
        color.ColoredText.localize("remove_true_form_success")

    def upgrade_cats(self, cats: list["core.Cat"]):
        cats = self.get_save_cats(cats)
        if not cats:
            return
        if len(cats) == 1:
            option_id = 0
        else:
            options: list[str] = [
                "upgrade_individual",
                "upgrade_all",
            ]
            option_id = dialog_creator.ChoiceInput(
                options, options, [], {}, "upgrade_cats_select_mod", True
            ).single_choice()
            if option_id is None:
                return
            option_id -= 1
        if option_id == 0:
            localizable = self.save_file.get_localizable()
            for cat in cats:
                color.ColoredText.localize(
                    "selected_cat_upgrades",
                    name=cat.get_names_cls(self.save_file, localizable)[0],
                    id=cat.id,
                    base_level=cat.upgrade.base + 1,
                    plus_level=cat.upgrade.plus,
                )
                power_up = core.PowerUpHelper(cat, self.save_file)
                upgrade, should_exit = core.Upgrade.get_user_upgrade(
                    power_up.get_max_possible_base(), power_up.get_max_possible_plus()
                )
                if should_exit:
                    return
                if upgrade is not None:
                    power_up.reset_upgrade()
                    power_up.upgrade_by(upgrade.base)
                    cat.set_plus_upgrade(self.save_file, upgrade.plus)
        else:
            power_up = core.PowerUpHelper(cats[0], self.save_file)
            upgrade, should_exit = core.Upgrade.get_user_upgrade(
                power_up.get_max_max_base_upgrade_level(),
                power_up.get_max_max_plus_upgrade_level(),
            )
            if upgrade is None or should_exit:
                return
            for cat in cats:
                power_up = core.PowerUpHelper(cat, self.save_file)
                power_up.reset_upgrade()
                power_up.upgrade_by(upgrade.base)
                cat.set_plus_upgrade(self.save_file, upgrade.plus)
        color.ColoredText.localize("upgrade_success")

    def get_cat_talents(
        self, talent_data: "core.TalentData", cat: "core.Cat"
    ) -> Optional[tuple[list[str], list[int], list[int], list[int]]]:
        talent_data_cat = talent_data.get_cat_skill(cat.id)
        if talent_data_cat is None or cat.talents is None:
            return None
        save_talent_data = cat.talents
        talent_names: list[str] = []
        max_levels: list[int] = []
        current_levels: list[int] = []
        ids: list[int] = []
        for talent in save_talent_data:
            talent_data_t = talent_data.get_skill_from_cat(cat.id, talent.id)
            name = talent_data.get_cat_skill_name(cat.id, talent.id)
            if name is None:
                continue
            if talent_data_t is None:
                continue

            max_level = talent_data_t.max_lv
            if max_level == 0:
                max_level = 1

            max_levels.append(max_level)
            talent_names.append(name.split("<br>")[0])
            current_levels.append(talent.level)
            ids.append(talent.id)

        return talent_names, max_levels, current_levels, ids

    def remove_talents_cats(self, cats: list["core.Cat"]):
        for cat in cats:
            if cat.talents is None:
                continue
            for talent in cat.talents:
                talent.level = 0
        color.ColoredText.localize("talents_remove_success")

    def unlock_cat_guide(self, cats: list["core.Cat"]):
        for cat in cats:
            cat.catguide_collected = True
        color.ColoredText.localize("unlock_cat_guide_success")

    def remove_cat_guide(self, cats: list["core.Cat"]):
        for cat in cats:
            cat.catguide_collected = False
        color.ColoredText.localize("remove_cat_guide_success")

    def upgrade_talents_cats(self, cats: list["core.Cat"]):
        cats = self.get_save_cats(cats)
        if not cats:
            return
        if len(cats) == 1:
            option_id = 0
        else:
            options: list[str] = [
                "talents_individual",
                "talents_all",
            ]
            option_id = dialog_creator.ChoiceInput(
                options, options, [], {}, "upgrade_talents_select_mod", True
            ).single_choice()
            if option_id is None:
                return
            option_id -= 1

        talent_data = self.save_file.cats.read_talent_data(self.save_file)
        if option_id == 0:
            localizable = self.save_file.get_localizable()
            for cat in cats:
                if cat.talents is None:
                    continue
                color.ColoredText.localize(
                    "selected_cat",
                    name=cat.get_names_cls(self.save_file, localizable)[0],
                    id=cat.id,
                )
                data = self.get_cat_talents(talent_data, cat)
                if data is None:
                    color.ColoredText.localize("no_talent_data", id=cat.id)
                    continue
                talent_names, max_levels, current_levels, ids = data
                values = dialog_creator.MultiEditor.from_reduced(
                    "talents",
                    talent_names,
                    current_levels,
                    max_levels,
                    group_name_localized=True,
                ).edit()
                current_levels = values
                for i, id in enumerate(ids):
                    talent = cat.get_talent_from_id(id)
                    if talent is None:
                        continue
                    talent.level = current_levels[i]
        else:
            for cat in cats:
                if cat.talents is None:
                    continue
                data = self.get_cat_talents(talent_data, cat)
                if data is None:
                    continue
                talent_names, max_levels, current_levels, ids = data
                for i, id in enumerate(ids):
                    talent = cat.get_talent_from_id(id)
                    if talent is None:
                        continue
                    talent.level = max_levels[i]
        color.ColoredText.localize("talents_success")

    @staticmethod
    def edit_cats(save_file: "core.SaveFile"):
        cat_editor = CatEditor(save_file)
        current_cats = cat_editor.select()
        if current_cats is None:
            return
        while True:
            should_exit, current_cats = CatEditor.run_edit_cats(save_file, current_cats)
            if should_exit:
                break

    @staticmethod
    def unlock_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.unlock_cats(current_cats)
        CatEditor.set_rank_up_sale(save_file)

    @staticmethod
    def remove_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.remove_cats(current_cats)

    @staticmethod
    def true_form_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.true_form_cats(current_cats)

    @staticmethod
    def force_true_form_cats_run(save_file: "core.SaveFile"):
        color.ColoredText.localize("force_true_form_cats_warning")
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.true_form_cats(current_cats, force=True)

    @staticmethod
    def remove_true_form_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.remove_true_form_cats(current_cats)

    @staticmethod
    def upgrade_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.upgrade_cats(current_cats)
        CatEditor.set_rank_up_sale(save_file)

    @staticmethod
    def upgrade_talents_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.upgrade_talents_cats(current_cats)

    @staticmethod
    def remove_talents_cats_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.remove_talents_cats(current_cats)

    @staticmethod
    def unlock_cat_guide_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.unlock_cat_guide(current_cats)

    @staticmethod
    def remove_cat_guide_run(save_file: "core.SaveFile"):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.remove_cat_guide(current_cats)

    @staticmethod
    def from_save_file(
        save_file: "core.SaveFile",
    ) -> tuple[Optional["CatEditor"], list["core.Cat"]]:
        cat_editor = CatEditor(save_file)
        current_cats = cat_editor.select()
        if current_cats is None:
            return None, []
        return cat_editor, current_cats

    @staticmethod
    def run_edit_cats(
        save_file: "core.SaveFile",
        cats: list["core.Cat"],
    ) -> tuple[bool, list["core.Cat"]]:
        cat_editor = CatEditor(save_file)
        cat_editor.print_selected_cats(cats)
        options: list[str] = [
            "select_cats_again",
            "unlock_cats",
            "remove_cats",
            "upgrade_cats",
            "true_form_cats",
            "force_true_form_cats",
            "remove_true_form_cats",
            "upgrade_talents_cats",
            "remove_talents_cats",
            "unlock_cat_guide",
            "remove_cat_guide",
            "finish_edit_cats",
        ]
        option_id = dialog_creator.ChoiceInput(
            options, options, [], {}, "select_edit_cats_option", True
        ).single_choice()
        if option_id is None:
            return False, cats
        option_id -= 1
        if option_id == 0:
            cats_ = cat_editor.select(cats)
            if cats_ is None:
                return False, cats
            cats = cats_
        elif option_id == 1:
            cat_editor.unlock_cats(cats)
        elif option_id == 2:
            cat_editor.remove_cats(cats)
        elif option_id == 3:
            cat_editor.upgrade_cats(cats)
        elif option_id == 4:
            cat_editor.true_form_cats(cats)
        elif option_id == 5:
            color.ColoredText.localize("force_true_form_cats_warning")
            cat_editor.true_form_cats(cats, force=True)
        elif option_id == 6:
            cat_editor.remove_true_form_cats(cats)
        elif option_id == 7:
            cat_editor.upgrade_talents_cats(cats)
        elif option_id == 8:
            cat_editor.remove_talents_cats(cats)
        elif option_id == 9:
            cat_editor.unlock_cat_guide(cats)
        elif option_id == 10:
            cat_editor.remove_cat_guide(cats)
        CatEditor.set_rank_up_sale(save_file)
        if option_id == 11:
            return True, cats
        return False, cats

    @staticmethod
    def set_rank_up_sale(save_file: "core.SaveFile"):
        save_file.rank_up_sale_value = 0x7FFFFFFF
