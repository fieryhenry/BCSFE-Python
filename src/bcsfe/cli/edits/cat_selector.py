from typing import Optional
from bcsfe.core import io, game
from bcsfe.cli import color, dialog_creator
import enum


class SelectMode(enum.Enum):
    AND = 0
    OR = 1
    REPLACE = 2


class CatSelector:
    def __init__(self, save_file: "io.save.SaveFile"):
        self.save_file = save_file

    def get_current_cats(self):
        return self.save_file.cats.get_unlocked_cats()

    def filter_cats(
        self, cats: list[game.catbase.cat.Cat]
    ) -> list[game.catbase.cat.Cat]:
        unlocked_cats = self.get_current_cats()
        return [cat for cat in cats if cat in unlocked_cats]

    def get_cats_rarity(self, rarity: int) -> list[game.catbase.cat.Cat]:
        return self.save_file.cats.get_cats_rarity(self.save_file, rarity)

    def get_cats_name(self, name: str) -> list[game.catbase.cat.Cat]:
        return self.save_file.cats.get_cats_name(self.save_file, name)

    def get_cats_obtainable(self) -> list[game.catbase.cat.Cat]:
        return self.save_file.cats.get_cats_obtainable(self.save_file)

    def get_cats_gatya_banner(self, gatya_id: int) -> list[game.catbase.cat.Cat]:
        cat_ids = self.save_file.gatya.read_gatya_data_set(self.save_file).get_cat_ids(
            gatya_id
        )
        return self.save_file.cats.get_cats_by_ids(cat_ids)

    def select(
        self,
        current_cats: Optional[list[game.catbase.cat.Cat]] = None,
        filter: bool = True,
    ) -> list[game.catbase.cat.Cat]:
        if current_cats is None:
            current_cats = []
        if len(current_cats) > 50 or not current_cats:
            color.ColoredText.localize("total_selected_cats", total=len(current_cats))
        else:
            self.save_file.cats.bulk_download_names(self.save_file)
            localizable = self.save_file.get_localizable()
            for cat in current_cats:
                names = cat.get_names_cls(self.save_file, localizable)
                if not names:
                    names = [str(cat.id)]
                color.ColoredText.localize("selected_cat", id=cat.id, name=names[0])

        options: list[str] = [
            "select_cats_rarity",
            "select_cats_name",
            "select_cats_obtainable",
            "select_cats_gatya_banner",
            "select_cats_all",
        ]
        option_id = dialog_creator.ChoiceInput(
            options, options, [], {}, "select_cats", True
        ).single_choice()
        if option_id is None:
            return current_cats
        option_id -= 1
        if option_id == 4:
            if filter:
                cats = self.get_current_cats()
            else:
                cats = self.save_file.cats.cats
            return cats

        if current_cats:
            mode_id = dialog_creator.IntInput().get_basic_input_locale("and_mode_q", {})
            if mode_id is None:
                mode = SelectMode.OR
            elif mode_id == 1:
                mode = SelectMode.AND
            elif mode_id == 2:
                mode = SelectMode.OR
            else:
                mode = SelectMode.OR
        else:
            mode = SelectMode.OR
        if option_id == 0:
            new_cats = self.select_rarity()
        elif option_id == 1:
            new_cats = self.select_name()
        elif option_id == 2:
            new_cats = self.select_obtainable()
        elif option_id == 3:
            new_cats = self.select_gatya_banner()
        else:
            new_cats = []

        if mode == SelectMode.AND:
            return [cat for cat in new_cats if cat in current_cats]
        if mode == SelectMode.OR:
            return list(set(current_cats + new_cats))
        return new_cats

    def select_rarity(self) -> list[game.catbase.cat.Cat]:
        rarity_names = self.save_file.cats.get_rarity_names(self.save_file)
        rarity_ids, _ = dialog_creator.ChoiceInput(
            rarity_names, rarity_names, [], {}, "select_rarity"
        ).multiple_choice()
        cats: list[game.catbase.cat.Cat] = []
        for rarity_id in rarity_ids:
            rarity_cats = self.get_cats_rarity(rarity_id)
            cats = list(set(cats + rarity_cats))
        return cats

    def select_name(self) -> list[game.catbase.cat.Cat]:
        usr_name = dialog_creator.StringInput().get_input_locale("enter_name", {})
        if usr_name is None:
            return []
        cats = self.get_cats_name(usr_name)
        localizable = self.save_file.get_localizable()
        cat_names: list[str] = []
        cat_list: list[game.catbase.cat.Cat] = []
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
        cats_selected: list[game.catbase.cat.Cat] = []
        for cat_option_id in cat_option_ids:
            cats_selected.append(cat_list[cat_option_id])
        return cats_selected

    def select_obtainable(self) -> list[game.catbase.cat.Cat]:
        cats = self.get_cats_obtainable()
        return cats

    def select_gatya_banner(self) -> list[game.catbase.cat.Cat]:
        gatya_ids = color.ColoredInput().get("select_gatya_banner").split(" ")
        gatya_ids = [int(gatya_id) for gatya_id in gatya_ids if gatya_id.isdigit()]
        cats: list[game.catbase.cat.Cat] = []
        for gatya_id in gatya_ids:
            gatya_cats = self.get_cats_gatya_banner(gatya_id)
            cats = list(set(cats + gatya_cats))
        return cats

    @staticmethod
    def edit_cats(save_file: "io.save.SaveFile"):
        cat_selector = CatSelector(save_file)
        cats = cat_selector.select()
        raise NotImplementedError()
