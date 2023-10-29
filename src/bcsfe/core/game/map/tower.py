from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class TowerChapters:
    def __init__(self, chapters: "core.Chapters"):
        self.chapters = chapters
        self.item_obtain_states: list[list[bool]] = []

    @staticmethod
    def init() -> "TowerChapters":
        return TowerChapters(core.Chapters.init())

    @staticmethod
    def read(data: "core.Data") -> "TowerChapters":
        ch = core.Chapters.read(data)
        return TowerChapters(ch)

    def write(self, data: "core.Data"):
        self.chapters.write(data)

    def read_item_obtain_states(self, data: "core.Data"):
        total_stars = data.read_int()
        total_stages = data.read_int()
        self.item_obtain_states: list[list[bool]] = []
        for _ in range(total_stars):
            self.item_obtain_states.append(data.read_bool_list(total_stages))

    def write_item_obtain_states(self, data: "core.Data"):
        data.write_int(len(self.item_obtain_states))
        try:
            data.write_int(len(self.item_obtain_states[0]))
        except IndexError:
            data.write_int(0)
        for item_obtain_state in self.item_obtain_states:
            data.write_bool_list(item_obtain_state, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "item_obtain_states": self.item_obtain_states,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "TowerChapters":
        tower = TowerChapters(
            core.Chapters.deserialize(data.get("chapters", {})),
        )
        tower.item_obtain_states = data.get("item_obtain_states", [])
        return tower

    def __repr__(self):
        return f"Tower({self.chapters}, {self.item_obtain_states})"

    def __str__(self):
        return self.__repr__()

    def get_total_stars(self, chapter_id: int) -> int:
        return len(self.chapters.chapters[chapter_id].chapters)

    def get_total_stages(self, chapter_id: int, star: int) -> int:
        return len(self.chapters.chapters[chapter_id].chapters[star].stages)

    @staticmethod
    def edit_towers(save_file: "core.SaveFile"):
        towers = save_file.tower
        towers.edit_chapters(save_file, "V")

    def edit_chapters(self, save_file: "core.SaveFile", letter_code: str):
        map_names = core.MapNames(save_file, letter_code)
        names = map_names.map_names

        map_choices = core.EventChapters.select_map_names(names)
        if map_choices is None:
            return

        clear_type_choice = dialog_creator.ChoiceInput.from_reduced(
            ["clear_whole_chapters", "clear_specific_stages"],
            dialog="select_clear_type",
            single_choice=True,
        ).single_choice()
        if clear_type_choice is None:
            return
        clear_type_choice -= 1

        if len(map_choices) > 1:
            stars_type_choice = dialog_creator.YesNoInput().get_input_once(
                "custom_star_count_per_chapter_yn"
            )
        else:
            stars_type_choice = False

        modify_clear_amounts = dialog_creator.YesNoInput().get_input_once(
            "modify_clear_amounts"
        )
        clear_amount = 1
        clear_amount_type = -1
        if modify_clear_amounts:
            options = ["clear_amount_chapter", "clear_amount_all"]
            if clear_type_choice == 1:
                options.append("clear_amount_stages")
            clear_amount_type = dialog_creator.ChoiceInput.from_reduced(
                options, dialog="select_clear_amount_type", single_choice=True
            ).single_choice()
            if clear_amount_type is None:
                return
            clear_amount_type -= 1
            if clear_amount_type == 1:
                clear_amount = core.EventChapters.ask_clear_amount()
                if clear_amount is None:
                    return

        if not stars_type_choice:
            stars = core.EventChapters.ask_stars()
            if stars is None:
                return
        else:
            stars = 0

        for id in map_choices:
            map_name = names[id]
            stage_names = map_names.stage_names.get(id)
            color.ColoredText.localize("current_sol_chapter", name=map_name, id=id)
            if stars_type_choice:
                stars = core.EventChapters.ask_stars()
                if stars is None:
                    return
            if clear_type_choice:
                stages = core.EventChapters.ask_stages(map_names, id)
                if stages is None:
                    return
            else:
                stages = list(range(self.get_total_stages(id, 0)))

            if clear_amount_type == 0:
                clear_amount = core.EventChapters.ask_clear_amount()
                if clear_amount is None:
                    return

            for star in range(self.get_total_stars(id)):
                for stage in range(self.get_total_stages(id, star)):
                    self.chapters.chapters[id].chapters[star].stages[
                        stage
                    ].clear_times = 0
                    self.chapters.chapters[id].chapters[star].clear_progress = 0
            for star in range(stars):
                if clear_amount_type == 2:
                    color.ColoredText.localize("current_sol_star", star=star + 1)
                for stage in stages:
                    if clear_amount_type == 2:
                        if stage_names is None:
                            continue
                        stage_name = stage_names[stage]
                        color.ColoredText.localize(
                            "current_sol_stage", name=stage_name, id=stage
                        )

                    if clear_amount_type == 2:
                        clear_amount = core.EventChapters.ask_clear_amount()
                    self.chapters.clear_stage(
                        id,
                        star,
                        stage,
                        overwrite_clear_progress=True,
                        clear_amount=clear_amount,
                    )

        color.ColoredText.localize("map_chapters_edited")
