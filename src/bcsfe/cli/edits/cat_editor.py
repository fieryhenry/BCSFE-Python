from __future__ import annotations
import enum
from typing import Any, Callable

from bcsfe import core
from bcsfe.cli import color, dialog_creator


class SelectMode(enum.Enum):
    AND = 0
    OR = 1
    REPLACE = 2


class CatEditor:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file

    def get_current_cats(self):
        return self.save_file.cats.get_unlocked_cats()

    def get_non_unlocked_cats(self):
        return self.save_file.cats.get_non_unlocked_cats()

    def get_non_gacha_cats(self):
        return self.save_file.cats.get_non_gacha_cats(self.save_file)

    def filter_cats(self, cats: list[core.Cat]) -> list[core.Cat]:
        unlocked_cats = self.get_current_cats()
        return [cat for cat in cats if cat in unlocked_cats]

    def get_cats_rarity(self, rarity: int) -> list[core.Cat]:
        return self.save_file.cats.get_cats_rarity(self.save_file, rarity)

    def get_cats_name(self, name: str) -> list[core.Cat]:
        return self.save_file.cats.get_cats_name(self.save_file, name)

    def get_cats_obtainable(self) -> list[core.Cat] | None:
        return self.save_file.cats.get_cats_obtainable(self.save_file)

    def get_cats_unobtainable(self) -> list[core.Cat] | None:
        return self.save_file.cats.get_cats_non_obtainable(self.save_file)

    def get_cats_gatya_banner(self, gatya_id: int) -> list[core.Cat] | None:
        return self.save_file.cats.get_cats_gatya_banner(self.save_file, gatya_id)

    def print_selected_cats(self, current_cats: list[core.Cat]):
        if len(current_cats) > 50:
            color.ColoredText.localize("total_selected_cats", total=len(current_cats))
        else:
            for cat in current_cats:
                names = cat.get_names_cls(self.save_file)
                if not names:
                    names = [str(cat.id)]
                color.ColoredText.localize("selected_cat", id=cat.id, name=names[0])

    def select(
        self, current_cats: list[core.Cat] | None = None, finish_option: bool = True
    ) -> tuple[list[core.Cat], bool]:
        if current_cats is None:
            current_cats = []
        options: dict[str, Callable[[], Any]] = {
            "select_cats_all": self.save_file.cats.get_all_cats,
            "select_cats_current": self.get_current_cats,
            "select_cats_obtainable": self.get_cats_obtainable,
            "select_cats_id": self.select_id,
            "select_cats_name": self.select_name,
            "select_cats_rarity": self.select_rarity,
            "select_cats_gatya_banner": self.select_gatya_banner,
            "select_cats_not_unlocked": self.get_non_unlocked_cats,
            "select_cats_not_obtainable": self.get_cats_unobtainable,
            "select_cats_non_gatya": self.get_non_gacha_cats,
            "select_cats_game_version": self.select_cats_game_version,
        }
        if finish_option:
            options["finish"] = lambda: None
        option_id = dialog_creator.ChoiceInput(
            list(options), list(options), [], {}, "select_cats", True
        ).single_choice()
        if option_id is None:
            return current_cats, False
        option_id -= 1

        if option_id == len(options) - 1 and finish_option:
            return current_cats, True

        func = options[list(options)[option_id]]
        new_cats = func()

        if new_cats is None:
            return current_cats, False

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

        if mode == SelectMode.AND:
            return list(set(current_cats) & set(new_cats)), False
        if mode == SelectMode.OR:
            return list(set(current_cats) | set(new_cats)), False
        if mode == SelectMode.REPLACE:
            return new_cats, False
        return new_cats, False

    def select_id(self) -> list[core.Cat] | None:
        cat_ids = dialog_creator.RangeInput(
            len(self.save_file.cats.cats) - 1
        ).get_input_locale("enter_cat_ids", {})
        if cat_ids is None:
            return None
        return self.save_file.cats.get_cats_by_ids(cat_ids)

    def select_cats_game_version(self) -> list[core.Cat] | None:
        unitbuy = core.UnitBuy(self.save_file)
        if unitbuy.unit_buy is None:
            return None

        versions_set: set[int] = set()
        for cat in unitbuy.unit_buy:
            if cat.game_version == -1:
                continue
            versions_set.add(cat.game_version)

        if not versions_set:
            return None

        versions = list(versions_set)
        versions.sort()

        color.ColoredText.localize("possible_gvs")

        cur_major_v = -1
        for version in versions:
            gv = core.GameVersion(version)
            major_v = gv.get_parts()[0]
            if major_v != cur_major_v:
                if cur_major_v != -1:
                    print()
                cur_major_v = major_v
            else:
                color.ColoredText(", ", end="")
            color.ColoredText(f"<@t>{gv.format()}</>", end="")

        print()

        usr_input = dialog_creator.StringInput().get_input_locale("select_gv")
        if usr_input is None:
            return None
        chunks = usr_input.split(" ")

        versions_selected: list[int] = []
        for chunk in chunks:
            parts = chunk.split("-")
            if len(parts) == 2:
                min = parts[0]
                max = parts[1]

                v1 = core.GameVersion.from_string(min)
                v2 = core.GameVersion.from_string(max)

                for v in range(v1.game_version, v2.game_version + 1):
                    versions_selected.append(v)
            else:
                v = core.GameVersion.from_string(chunk)
                versions_selected.append(v.game_version)

        valid_versions: set[int] = set()
        for version in versions_selected:
            if version in versions_set:
                valid_versions.add(version)

        if not valid_versions:
            color.ColoredText.localize("no_valid_gvs_entered")

        cats: list[core.Cat] = []
        for cat in self.save_file.cats.cats:
            row = unitbuy.get_unit_buy(cat.id)
            if row is None:
                continue
            if row.game_version in valid_versions:
                cats.append(cat)

        return cats

    def select_rarity(self) -> list[core.Cat] | None:
        rarity_names = self.save_file.cats.get_rarity_names(self.save_file)
        rarity_ids, _ = dialog_creator.ChoiceInput(
            rarity_names, rarity_names, [], {}, "select_rarity"
        ).multiple_choice()
        if rarity_ids is None:
            return None
        cats: list[core.Cat] = []
        for rarity_id in rarity_ids:
            rarity_cats = self.get_cats_rarity(rarity_id)
            cats = list(set(cats + rarity_cats))
        return cats

    def select_name(self) -> list[core.Cat] | None:
        usr_name = dialog_creator.StringInput().get_input_locale("enter_name", {})
        if usr_name is None:
            return []
        cats = self.get_cats_name(usr_name)
        if not cats:
            color.ColoredText.localize("no_cats_found_name", name=usr_name)
            return None
        cat_names: list[str] = []
        cat_list: list[core.Cat] = []
        for cat in cats:
            names = cat.get_names_cls(self.save_file)
            if not names:
                names = [str(cat.id)]
            for name in names:
                if usr_name.lower() in name.lower():
                    cat_names.append(name)
                    cat_list.append(cat)
                    break
        if len(cat_names) == 1:
            color.ColoredText(f"<@t>{cat_names[0]}</>")
        cat_option_ids, _ = dialog_creator.ChoiceInput(
            cat_names, cat_names, [], {}, "select_name"
        ).multiple_choice()
        if cat_option_ids is None:
            return None
        cats_selected: list[core.Cat] = []
        for cat_option_id in cat_option_ids:
            cats_selected.append(cat_list[cat_option_id])
        return cats_selected

    def select_obtainable(self) -> list[core.Cat] | None:
        return self.get_cats_obtainable()

    def select_gatya_banner_name(self) -> list[int] | None:

        filter_down = dialog_creator.YesNoInput().get_input_once("filter_down_q_gatya")
        if filter_down is None:
            return None

        all_names = core.GatyaInfos(self.save_file).get_all_names()
        ids = list(all_names.keys())
        ids.sort()
        names: list[str] = []
        for id in ids:
            names.append(all_names[id])
        new_names: list[str] = []
        new_ids: list[int] = []

        unknown_name = core.core_data.local_manager.get_key("unknown_banner")

        if filter_down:
            ids.reverse()
            for id in ids:
                name = all_names[id]
                if name in new_names or name == unknown_name:
                    continue
                new_names.append(name)
                new_ids.append(id)
            new_ids.reverse()
            new_names.reverse()
        else:
            new_names = names
            new_ids = ids

        ids = new_ids

        formatted_names: list[str] = []

        for name in new_names:
            formatted_name = core.core_data.local_manager.get_key(
                "banner_txt", name=name
            )
            formatted_names.append(formatted_name)
        gatya_option_ids, _ = dialog_creator.ChoiceInput.from_reduced(
            formatted_names,
            ints=ids,
            dialog="select_gatya_banner",
            start_index=0,
        ).multiple_choice(False)
        if gatya_option_ids is None:
            return None
        gatya_ids: list[int] = []
        for gatya_option_id in gatya_option_ids:
            gatya_ids.append(ids[gatya_option_id])

        return gatya_ids

    def select_gatya_banner(self) -> list[core.Cat] | None:
        gset = self.save_file.gatya.read_gatya_data_set(self.save_file).gatya_data_set
        if gset is None:
            return None

        by_id = dialog_creator.ChoiceInput.from_reduced(
            ["by_id", "by_name"], dialog="gatya_by_id_q"
        ).single_choice()
        if by_id is None:
            return None

        if by_id == 1:
            gatya_ids = dialog_creator.RangeInput(len(gset) - 1).get_input_locale(
                "select_gatya_banner", {}
            )
        else:
            gatya_ids = self.select_gatya_banner_name()
        if gatya_ids is None:
            return None
        cats: list[core.Cat] = []
        for gatya_id in gatya_ids:
            gatya_cats = self.get_cats_gatya_banner(gatya_id)
            if gatya_cats is None:
                continue
            cats = list(set(cats + gatya_cats))
        return cats

    def unlock_cats(self, cats: list[core.Cat]):
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.unlock(self.save_file)
        color.ColoredText.localize("unlock_success")

    def remove_cats(self, cats: list[core.Cat]):
        reset = core.core_data.config.get_bool(core.ConfigKey.RESET_CAT_DATA)
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.remove(reset=reset, save_file=self.save_file)
        color.ColoredText.localize("remove_success")

    def get_save_cats(self, cats: list[core.Cat]):
        ct_cats: list[core.Cat] = []
        for cat in cats:
            ct = self.save_file.cats.get_cat_by_id(cat.id)
            if ct is None:
                continue
            ct_cats.append(ct)
        return ct_cats

    def true_form_cats(self, cats: list[core.Cat], force: bool = False):
        cats = self.get_save_cats(cats)
        set_current_forms = core.core_data.config.get_bool(
            core.ConfigKey.SET_CAT_CURRENT_FORMS
        )
        self.save_file.cats.true_form_cats(
            self.save_file, cats, force, set_current_forms
        )
        color.ColoredText.localize("true_form_success")

    def fourth_form_cats(self, cats: list[core.Cat], force: bool = False):
        cats = self.get_save_cats(cats)
        set_current_forms = core.core_data.config.get_bool(
            core.ConfigKey.SET_CAT_CURRENT_FORMS
        )
        self.save_file.cats.fourth_form_cats(
            self.save_file, cats, force, set_current_forms
        )
        color.ColoredText.localize("fourth_form_success")

    def remove_true_form_cats(self, cats: list[core.Cat]):
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.remove_true_form()
        color.ColoredText.localize("remove_true_form_success")

    def remove_fourth_form_cats(self, cats: list[core.Cat]):
        cats = self.get_save_cats(cats)
        for cat in cats:
            cat.remove_fourth_form()
        color.ColoredText.localize("remove_fourth_form_success")

    def upgrade_cats(self, cats: list[core.Cat]):
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
        success = False
        if option_id == 0:
            for cat in cats:
                names = cat.get_names_cls(self.save_file)
                if not names:
                    names = [str(cat.id)]
                color.ColoredText.localize(
                    "selected_cat_upgrades",
                    name=names[0],
                    id=cat.id,
                    base_level=cat.upgrade.base + 1,
                    plus_level=cat.upgrade.plus,
                )
                power_up = core.PowerUpHelper(cat, self.save_file)
                upgrade, should_exit = core.Upgrade.get_user_upgrade(
                    power_up.get_max_possible_base() - 1,
                    power_up.get_max_possible_plus(),
                )
                if should_exit:
                    return
                if upgrade is not None:
                    power_up.reset_upgrade()
                    power_up.upgrade_by(upgrade.base)
                    cat.set_upgrade(self.save_file, upgrade, True)
                    color.ColoredText.localize(
                        "selected_cat_upgraded",
                        name=names[0],
                        id=cat.id,
                        base_level=cat.upgrade.base + 1,
                        plus_level=cat.upgrade.plus,
                    )
                    success = True
        else:
            power_up = core.PowerUpHelper(cats[0], self.save_file)
            upgrade, should_exit = core.Upgrade.get_user_upgrade(
                power_up.get_max_max_base_upgrade_level() - 1,
                power_up.get_max_max_plus_upgrade_level(),
            )
            if upgrade is None or should_exit:
                return
            success = True
            for cat in cats:
                power_up = core.PowerUpHelper(cat, self.save_file)
                power_up.reset_upgrade()
                power_up.upgrade_by(upgrade.base)
                cat.set_upgrade(self.save_file, upgrade, True)
        if success:
            color.ColoredText.localize("upgrade_success")

    def remove_talents_cats(self, cats: list[core.Cat]):
        for cat in cats:
            if cat.talents is None:
                continue
            for talent in cat.talents:
                talent.level = 0
        color.ColoredText.localize("talents_remove_success")

    def unlock_cat_guide(self, cats: list[core.Cat]):
        for cat in cats:
            if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
                cat.unlock(self.save_file)
            cat.catguide_collected = True
        color.ColoredText.localize("unlock_cat_guide_success")

    def remove_cat_guide(self, cats: list[core.Cat]):
        for cat in cats:
            cat.catguide_collected = False
        color.ColoredText.localize("remove_cat_guide_success")

    def upgrade_talents_cats(self, cats: list[core.Cat]):
        cats = self.get_save_cats(cats)
        if not cats:
            return
        gdg = core.core_data.get_game_data_getter(self.save_file)
        is_good_version = gdg.does_save_version_match(self.save_file)
        if not is_good_version:
            data_version = gdg.version
            if data_version is None:
                color.ColoredText.localize("no_data_version")
                return
            color.ColoredText.localize(
                "talents_version_warning",
                save_version=self.save_file.game_version.to_string(),
                data_version=data_version,
            )
            should_stay = dialog_creator.YesNoInput().get_input_once("continue_q")
            if not should_stay:
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
        if talent_data is None:
            return
        if option_id == 0:
            for cat in cats:
                if cat.talents is None:
                    continue
                names = cat.get_names_cls(self.save_file)
                if not names:
                    names = [str(cat.id)]
                color.ColoredText.localize(
                    "selected_cat",
                    name=names[0],
                    id=cat.id,
                )
                data = talent_data.get_cat_talents(cat)
                if data is None:
                    color.ColoredText.localize("no_talent_data", id=cat.id)
                    continue
                if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
                    cat.unlock(self.save_file)
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
                data = talent_data.get_cat_talents(cat)
                if data is None:
                    continue
                if core.core_data.config.get_bool(core.ConfigKey.UNLOCK_CAT_ON_EDIT):
                    cat.unlock(self.save_file)
                talent_names, max_levels, current_levels, ids = data
                for i, id in enumerate(ids):
                    talent = cat.get_talent_from_id(id)
                    if talent is None:
                        continue
                    talent.level = max_levels[i]
        color.ColoredText.localize("talents_success")

    @staticmethod
    def edit_cats(save_file: core.SaveFile):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        while True:
            should_exit, current_cats = cat_editor.run_edit_cats(current_cats)
            if should_exit:
                break

    @staticmethod
    def unlock_remove_cats_run(
        save_file: core.SaveFile,
        current_cats: list[core.Cat] | None = None,
        cat_editor: CatEditor | None = None,
    ):
        if cat_editor is None or current_cats is None:
            cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        choice = dialog_creator.ChoiceInput(
            ["unlock_cats", "remove_cats"],
            ["unlock_cats", "remove_cats"],
            [],
            {},
            "unlock_remove_q",
            True,
            remove_alias=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            cat_editor.unlock_cats(current_cats)
        elif choice == 1:
            cat_editor.remove_cats(current_cats)
        CatEditor.set_rank_up_sale(save_file)

    @staticmethod
    def true_form_remove_form_cats_run(
        save_file: core.SaveFile,
        current_cats: list[core.Cat] | None = None,
        cat_editor: CatEditor | None = None,
    ):
        if cat_editor is None or current_cats is None:
            cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        choice = dialog_creator.ChoiceInput.from_reduced(
            ["true_form_cats", "remove_true_form_cats"],
            dialog="true_form_remove_form_q",
            single_choice=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            cat_editor.true_form_cats(current_cats)
        elif choice == 1:
            cat_editor.remove_true_form_cats(current_cats)

    @staticmethod
    def fourth_form_remove_form_cats_run(
        save_file: core.SaveFile,
        current_cats: list[core.Cat] | None = None,
        cat_editor: CatEditor | None = None,
    ):
        if cat_editor is None or current_cats is None:
            cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        choice = dialog_creator.ChoiceInput.from_reduced(
            ["fourth_form_cats", "remove_fourth_form_cats"],
            dialog="fourth_form_remove_form_q",
            single_choice=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            cat_editor.fourth_form_cats(current_cats)
        elif choice == 1:
            cat_editor.remove_fourth_form_cats(current_cats)

    @staticmethod
    def force_true_form_cats_run(save_file: core.SaveFile):
        color.ColoredText.localize("force_true_form_cats_warning")
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.true_form_cats(current_cats, force=True)

    @staticmethod
    def force_fourth_form_cats_run(save_file: core.SaveFile):
        color.ColoredText.localize("force_fourth_form_cats_warning")
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.fourth_form_cats(current_cats, force=True)

    @staticmethod
    def upgrade_cats_run(save_file: core.SaveFile):
        cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        cat_editor.upgrade_cats(current_cats)
        CatEditor.set_rank_up_sale(save_file)

    @staticmethod
    def upgrade_talents_remove_talents_cats_run(
        save_file: core.SaveFile,
        current_cats: list[core.Cat] | None = None,
        cat_editor: CatEditor | None = None,
    ):
        if cat_editor is None or current_cats is None:
            cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        choice = dialog_creator.ChoiceInput(
            ["upgrade_talents_cats", "remove_talents_cats"],
            ["upgrade_talents_cats", "remove_talents_cats"],
            [],
            {},
            "upgrade_talents_remove_talents_q",
            True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            cat_editor.upgrade_talents_cats(current_cats)
        elif choice == 1:
            cat_editor.remove_talents_cats(current_cats)

    @staticmethod
    def unlock_cat_guide_remove_guide_run(
        save_file: core.SaveFile,
        current_cats: list[core.Cat] | None = None,
        cat_editor: CatEditor | None = None,
    ):
        if cat_editor is None or current_cats is None:
            cat_editor, current_cats = CatEditor.from_save_file(save_file)
        if cat_editor is None:
            return
        choice = dialog_creator.ChoiceInput(
            ["unlock_cat_guide", "remove_cat_guide"],
            ["unlock_cat_guide", "remove_cat_guide"],
            [],
            {},
            "unlock_cat_guide_remove_guide_q",
            True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            cat_editor.unlock_cat_guide(current_cats)
        elif choice == 1:
            cat_editor.remove_cat_guide(current_cats)

    @staticmethod
    def from_save_file(
        save_file: core.SaveFile,
    ) -> tuple[CatEditor | None, list[core.Cat]]:
        cat_editor = CatEditor(save_file)
        stop = False
        cats = []
        while not stop:
            current_cats, finished = cat_editor.select(cats)
            cats = current_cats
            cat_editor.print_selected_cats(cats)
            if finished:
                stop = True
                continue
            finished = dialog_creator.YesNoInput().get_input_once(
                "finished_cats_selection"
            )
            if finished is None:
                return None, []
            stop = finished
        return cat_editor, cats

    def run_edit_cats(
        self,
        cats: list[core.Cat],
    ) -> tuple[bool, list[core.Cat]]:
        self.print_selected_cats(cats)
        options: list[str] = [
            "select_cats_again",
            "unlock_remove_cats",
            "upgrade_cats",
            "true_form_remove_form_cats",
            "force_true_form_cats",
            "fourth_form_remove_form_cats",
            "force_fourth_form_cats",
            "upgrade_talents_remove_talents_cats",
            "unlock_remove_cat_guide",
            "finish_edit_cats",
        ]
        option_id = dialog_creator.ChoiceInput(
            options,
            options,
            [],
            {},
            "select_edit_cats_option",
            True,
            remove_alias=True,
        ).single_choice()
        if option_id is None:
            return False, cats
        option_id -= 1
        if option_id == 0:
            cats_, _ = self.select(cats, False)
            cats = cats_
        elif option_id == 1:
            self.unlock_remove_cats_run(self.save_file, cats, self)
        elif option_id == 2:
            self.upgrade_cats(cats)
        elif option_id == 3:
            self.true_form_remove_form_cats_run(self.save_file, cats, self)
        elif option_id == 4:
            color.ColoredText.localize("force_true_form_cats_warning")
            self.true_form_cats(cats, force=True)
        elif option_id == 5:
            self.fourth_form_remove_form_cats_run(self.save_file, cats, self)
        elif option_id == 6:
            color.ColoredText.localize("force_fourth_form_cats_warning")
            self.fourth_form_cats(cats, force=True)
        elif option_id == 7:
            self.upgrade_talents_remove_talents_cats_run(self.save_file, cats, self)
        elif option_id == 8:
            self.unlock_cat_guide_remove_guide_run(self.save_file, cats, self)
        CatEditor.set_rank_up_sale(self.save_file)
        if option_id == 9:
            return True, cats
        return False, cats

    @staticmethod
    def set_rank_up_sale(save_file: core.SaveFile):
        save_file.rank_up_sale_value = 0x7FFFFFFF
