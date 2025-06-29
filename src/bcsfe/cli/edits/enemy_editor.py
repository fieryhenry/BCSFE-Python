from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator
from bcsfe.cli.edits.cat_editor import SelectMode
from bcsfe.core.game.battle.enemy import EnemyNames


class EnemyEditor:
    def __init__(self, save_file: core.SaveFile) -> None:
        self.save_file = save_file

    def unlock_enemy_guide(self, enemies: list[core.Enemy]):
        for enemy in enemies:
            enemy.unlock_enemy_guide(self.save_file)

        color.ColoredText.localize("unlock_enemy_guide_success")

    def remove_enemy_guide(self, enemies: list[core.Enemy]):
        for enemy in enemies:
            enemy.reset_enemy_guide(self.save_file)

        color.ColoredText.localize("remove_enemy_guide_success")

    def print_selected_enemies(self, enemies: list[core.Enemy]):
        if not enemies:
            return
        if len(enemies) > 50:
            color.ColoredText.localize("total_selected_enemies", total=len(enemies))
        else:
            for enemy in enemies:
                color.ColoredText.localize(
                    "selected_enemy",
                    id=enemy.id,
                    name=enemy.get_name(self.save_file),
                )

    def select(self, current_enemies: list[core.Enemy] | None):
        if current_enemies is None:
            current_enemies = []
        self.print_selected_enemies(current_enemies)

        options: dict[str, Any] = {
            "select_enemies_valid": self.get_all_valid_enemies,
            "select_enemies_all": self.get_all_enemies,
            "select_enemies_id": self.select_id,
            "select_enemies_name": self.select_name,
            "select_enemies_invalid": self.get_all_invalid_enemies,
        }
        option_id = dialog_creator.ChoiceInput.from_reduced(
            list(options), dialog="select_enemies", single_choice=True
        ).single_choice()
        if option_id is None:
            return current_enemies
        option_id -= 1

        func = options[list(options)[option_id]]
        new_enemies = func()
        if new_enemies is None:
            return None

        if current_enemies:
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
            return [enemy for enemy in new_enemies if enemy in current_enemies]
        if mode == SelectMode.OR:
            return list(set(current_enemies + new_enemies))
        if mode == SelectMode.REPLACE:
            return new_enemies
        return new_enemies

    def get_all_enemies(self) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for i in range(len(self.save_file.enemy_guide)):
            enemies.append(core.Enemy(i))
        return enemies

    def get_all_valid_enemies(self) -> list[core.Enemy] | None:
        valid_ids = core.EnemyDictionary(self.save_file).get_valid_enemies()
        if valid_ids is None:
            return None

        return [core.Enemy(id) for id in valid_ids]

    def get_all_invalid_enemies(self) -> list[core.Enemy] | None:
        invalid_ids = core.EnemyDictionary(self.save_file).get_invalid_enemies(
            len(self.save_file.enemy_guide)
        )
        if invalid_ids is None:
            return None

        return [core.Enemy(id) for id in invalid_ids]

    def select_id(self) -> list[core.Enemy] | None:
        enemy_ids = dialog_creator.RangeInput(
            len(self.save_file.enemy_guide) - 1
        ).get_input_locale("enter_enemy_ids", {})
        if enemy_ids is None:
            return None
        enemy_ids = [enemy_id - 2 for enemy_id in enemy_ids]
        return self.get_enemies_by_id(enemy_ids)

    def get_enemies_by_id(self, ids: list[int]) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for enemy in self.get_all_enemies():
            if enemy.id in ids:
                enemies.append(enemy)
        return enemies

    def select_name(self) -> list[core.Enemy] | None:
        usr_name = dialog_creator.StringInput().get_input_locale("enter_enemy_name", {})
        if usr_name is None:
            return None
        enemies = self.get_enemies_by_name(usr_name)
        if not enemies:
            color.ColoredText.localize("enemy_not_found_name", name=usr_name)
            return None

        enemy_names = [enemy.get_name(self.save_file) for enemy in enemies]
        new_enemy_names: list[str] = []
        for enemy_name in enemy_names:
            if enemy_name is None:
                return None

            new_enemy_names.append(enemy_name)

        enemy_option_ids, _ = dialog_creator.ChoiceInput.from_reduced(
            new_enemy_names, dialog="select_enemies", single_choice=False
        ).multiple_choice()
        if enemy_option_ids is None:
            return None
        enemies_selected: list[core.Enemy] = []
        for enemy_option_id in enemy_option_ids:
            enemies_selected.append(enemies[enemy_option_id])
        return enemies_selected

    def get_enemies_by_name(self, name: str) -> list[core.Enemy]:
        enemies: list[core.Enemy] = []
        for enemy in self.get_all_enemies():
            enemy_name = enemy.get_name(self.save_file)
            if enemy_name is None:
                continue
            if name.lower() in enemy_name.lower():
                enemies.append(enemy)
        return enemies

    @staticmethod
    def from_save_file(
        save_file: core.SaveFile,
    ) -> tuple[EnemyEditor | None, list[core.Enemy]]:
        enemy_editor = EnemyEditor(save_file)
        current_enemies = enemy_editor.select([])
        if current_enemies is None:
            return None, []
        return enemy_editor, current_enemies

    @staticmethod
    def edit_enemy_guide(
        save_file: core.SaveFile,
        current_enemies: list[core.Enemy] | None = None,
        enemy_editor: EnemyEditor | None = None,
    ):
        if enemy_editor is None or current_enemies is None:
            enemy_editor, current_enemies = EnemyEditor.from_save_file(save_file)
        if enemy_editor is None or not current_enemies:
            return

        choice = dialog_creator.ChoiceInput.from_reduced(
            ["unlock_enemy_guide", "remove_enemy_guide"],
            dialog="edit_enemy_guide",
            single_choice=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            enemy_editor.unlock_enemy_guide(current_enemies)
        elif choice == 1:
            enemy_editor.remove_enemy_guide(current_enemies)
