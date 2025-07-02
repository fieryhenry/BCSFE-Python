from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times
        self.treasure = 0
        self.itf_timed_score = 0

    @staticmethod
    def init() -> Stage:
        return Stage(0)

    @staticmethod
    def read_clear_times(stream: core.Data) -> Stage:
        return Stage(stream.read_int())

    def read_treasure(self, stream: core.Data):
        self.treasure = stream.read_int()

    def read_itf_timed_score(self, stream: core.Data):
        self.itf_timed_score = stream.read_int()

    def write_clear_times(self, stream: core.Data):
        stream.write_int(self.clear_times)

    def write_treasure(self, stream: core.Data):
        stream.write_int(self.treasure)

    def write_itf_timed_score(self, stream: core.Data):
        stream.write_int(self.itf_timed_score)

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_times": self.clear_times,
            "treasure": self.treasure,
            "itf_timed_score": self.itf_timed_score,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Stage:
        stage = Stage(data.get("clear_times", 0))
        stage.treasure = data.get("treasure", 0)
        stage.itf_timed_score = data.get("itf_timed_score", 0)
        return stage

    def __repr__(self):
        return f"Stage({self.clear_times}, {self.treasure}, {self.itf_timed_score})"

    def __str__(self):
        return self.__repr__()

    def clear_stage(self, clear_amount: int = 1):
        self.clear_times = clear_amount

    def unclear_stage(self):
        self.clear_times = 0

    def is_cleared(self) -> bool:
        return self.clear_times > 0

    def set_treasure(self, treasure: int):
        self.treasure = treasure


class Chapter:
    def __init__(self, selected_stage: int):
        self.selected_stage = selected_stage
        self.progress = 0
        self.stages = [Stage.init() for _ in range(51)]
        self.time_until_treasure_chance = 0
        self.treasure_chance_duration = 0
        self.treasure_chance_value = 0
        self.treasure_chance_stage_id = 0
        self.treasure_festival_type = 0

    def clear_stage(
        self,
        index: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ):
        if overwrite_clear_progress:
            self.progress = index + 1
        else:
            self.progress = max(self.progress, index + 1)
        self.stages[index].clear_stage(clear_amount)

    def set_treasure(self, stage_id: int, treasure: int):
        self.stages[stage_id].set_treasure(treasure)

    def is_stage_clear(self, stage_id: int) -> bool:
        return self.stages[stage_id].is_cleared()

    @staticmethod
    def init() -> Chapter:
        return Chapter(0)

    def get_treasure_stages(self) -> list[Stage]:
        return self.stages[:49]

    def get_valid_treasure_stages(self) -> list[Stage]:
        return self.stages[:48]

    @staticmethod
    def read_selected_stage(stream: core.Data) -> Chapter:
        return Chapter(stream.read_int())

    def read_progress(self, stream: core.Data):
        self.progress = stream.read_int()

    def read_clear_times(self, stream: core.Data):
        total_stages = 51
        self.stages = [Stage.read_clear_times(stream) for _ in range(total_stages)]

    def read_treasure(self, stream: core.Data):
        for stage in self.get_treasure_stages():
            stage.read_treasure(stream)

    def read_time_until_treasure_chance(self, stream: core.Data):
        self.time_until_treasure_chance = stream.read_int()

    def read_treasure_chance_duration(self, stream: core.Data):
        self.treasure_chance_duration = stream.read_int()

    def read_treasure_chance_value(self, stream: core.Data):
        self.treasure_chance_value = stream.read_int()

    def read_treasure_chance_stage_id(self, stream: core.Data):
        self.treasure_chance_stage_id = stream.read_int()

    def read_treasure_festival_type(self, stream: core.Data):
        self.treasure_festival_type = stream.read_int()

    def read_itf_timed_scores(self, stream: core.Data):
        for stage in self.stages:
            stage.read_itf_timed_score(stream)

    def write_selected_stage(self, stream: core.Data):
        stream.write_int(self.selected_stage)

    def write_progress(self, stream: core.Data):
        stream.write_int(self.progress)

    def write_clear_times(self, stream: core.Data):
        for stage in self.stages:
            stage.write_clear_times(stream)

    def write_treasure(self, stream: core.Data):
        for stage in self.get_treasure_stages():
            stage.write_treasure(stream)

    def write_time_until_treasure_chance(self, stream: core.Data):
        stream.write_int(self.time_until_treasure_chance)

    def write_treasure_chance_duration(self, stream: core.Data):
        stream.write_int(self.treasure_chance_duration)

    def write_treasure_chance_value(self, stream: core.Data):
        stream.write_int(self.treasure_chance_value)

    def write_treasure_chance_stage_id(self, stream: core.Data):
        stream.write_int(self.treasure_chance_stage_id)

    def write_treasure_festival_type(self, stream: core.Data):
        stream.write_int(self.treasure_festival_type)

    def write_itf_timed_scores(self, stream: core.Data):
        for stage in self.stages:
            stage.write_itf_timed_score(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "progress": self.progress,
            "stages": [stage.serialize() for stage in self.stages],
            "time_until_treasure_chance": self.time_until_treasure_chance,
            "treasure_chance_duration": self.treasure_chance_duration,
            "treasure_chance_value": self.treasure_chance_value,
            "treasure_chance_stage_id": self.treasure_chance_stage_id,
            "treasure_festival_type": self.treasure_festival_type,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Chapter:
        chapter = Chapter(data.get("selected_stage", 0))
        chapter.progress = data.get("progress", 0)
        chapter.stages = [Stage.deserialize(stage) for stage in data.get("stages", [])]
        chapter.time_until_treasure_chance = data.get("time_until_treasure_chance", 0)
        chapter.treasure_chance_duration = data.get("treasure_chance_duration", 0)
        chapter.treasure_chance_value = data.get("treasure_chance_value", 0)
        chapter.treasure_chance_stage_id = data.get("treasure_chance_stage_id", 0)
        chapter.treasure_festival_type = data.get("treasure_festival_type", 0)
        return chapter

    def __repr__(self):
        return f"Chapter({self.selected_stage}, {self.progress}, {self.stages}, {self.time_until_treasure_chance}, {self.treasure_chance_duration}, {self.treasure_chance_value}, {self.treasure_chance_stage_id}, {self.treasure_festival_type})"

    def __str__(self):
        return f"Chapter({self.selected_stage}, {self.progress}, {self.stages}, {self.time_until_treasure_chance}, {self.treasure_chance_duration}, {self.treasure_chance_value}, {self.treasure_chance_stage_id}, {self.treasure_festival_type})"

    def apply_progress(self, progress: int, clear_times: list[int] | None = None):
        if clear_times is None:
            clear_times = [1] * progress

        self.progress = progress
        for i in range(progress + 1, 48):
            self.stages[i].unclear_stage()

        for i in range(progress):
            self.stages[i].clear_stage(clear_times[i])

    def clear_chapter(self):
        self.apply_progress(48)


class StoryChapters:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    def get_real_chapters(self) -> list[Chapter]:
        new_chapters: list[Chapter] = []
        for i, chapter in enumerate(self.chapters):
            if i == 3:
                continue
            new_chapters.append(chapter)
        return new_chapters

    def clear_stage(
        self,
        map: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
        chapters: list[Chapter] | None = None,
    ):
        if chapters is None:
            chapters = self.chapters
        chapters[map].clear_stage(stage, clear_amount, overwrite_clear_progress)

    def set_treasure(self, chapter: int, stage: int, treasure: int):
        self.chapters[chapter].set_treasure(stage, treasure)

    def is_stage_clear(self, chapter: int, stage: int) -> bool:
        return self.chapters[chapter].is_stage_clear(stage)

    @staticmethod
    def init() -> StoryChapters:
        chapters = [Chapter.init() for _ in range(10)]
        return StoryChapters(chapters)

    @staticmethod
    def read(stream: core.Data) -> StoryChapters:
        total_chapters = 10
        chapters_l = [
            Chapter.read_selected_stage(stream) for _ in range(total_chapters)
        ]
        chapters = StoryChapters(chapters_l)
        for chapter in chapters.chapters:
            chapter.read_progress(stream)
        for chapter in chapters.chapters:
            chapter.read_clear_times(stream)
        for chapter in chapters.chapters:
            chapter.read_treasure(stream)
        return chapters

    def read_treasure_festival(self, stream: core.Data):
        for chapter in self.chapters:
            chapter.read_time_until_treasure_chance(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_duration(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_value(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_stage_id(stream)
        for chapter in self.chapters:
            chapter.read_treasure_festival_type(stream)

    def write(self, stream: core.Data):
        for chapter in self.chapters:
            chapter.write_selected_stage(stream)
        for chapter in self.chapters:
            chapter.write_progress(stream)
        for chapter in self.chapters:
            chapter.write_clear_times(stream)
        for chapter in self.chapters:
            chapter.write_treasure(stream)

    def write_treasure_festival(self, stream: core.Data):
        for chapter in self.chapters:
            chapter.write_time_until_treasure_chance(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_duration(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_value(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_stage_id(stream)
        for chapter in self.chapters:
            chapter.write_treasure_festival_type(stream)

    def read_itf_timed_scores(self, stream: core.Data):
        # 0: eoc 1
        # 1: eoc 2
        # 2: eoc 3
        # 3: _
        # 4: itf 1
        # 5: itf 2
        # 6: itf 3
        # 7: cotc 1
        # 8: cotc 2
        # 9: cotc 3

        for i, chapter in enumerate(self.chapters):
            if i > 3 and i < 7:
                chapter.read_itf_timed_scores(stream)

    def write_itf_timed_scores(self, stream: core.Data):
        for i, chapter in enumerate(self.chapters):
            if i > 3 and i < 7:
                chapter.write_itf_timed_scores(stream)

    def serialize(self) -> list[dict[str, Any]]:
        chapters = [chapter.serialize() for chapter in self.chapters]
        return chapters

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> StoryChapters:
        chapters = StoryChapters([Chapter.deserialize(chapter) for chapter in data])
        return chapters

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return f"Chapters({self.chapters})"

    @staticmethod
    def clear_tutorial(save_file: core.SaveFile):
        save_file.tutorial_state = max(save_file.tutorial_state, 1)
        save_file.koreaSuperiorTreasureState = max(
            save_file.koreaSuperiorTreasureState, 2
        )
        save_file.ui6 = max(save_file.ui6, 1)
        new_length = len(save_file.new_dialogs_2)
        if new_length < 6:
            save_file.new_dialogs_2.extend([0] * (6 - new_length))

        save_file.new_dialogs_2[1] = max(save_file.new_dialogs_2[1], 2)
        save_file.new_dialogs_2[5] = max(save_file.new_dialogs_2[5], 2)
        if save_file.story.chapters[0].stages[0].clear_times == 0:
            save_file.story.clear_stage(0, 0)

    @staticmethod
    def get_chapter_names(
        save_file: core.SaveFile, chapter_ids: list[int] | None = None
    ) -> list[str] | None:
        if chapter_ids is None:
            chapter_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        chapter_names: list[str] = []
        localizable = core.core_data.get_localizable(save_file)
        eoc_name = localizable.get("everyplay_mapname_J")
        itf_name = localizable.get("everyplay_mapname_W")
        cotc_name = localizable.get("everyplay_mapname_P")
        if eoc_name is None or itf_name is None or cotc_name is None:
            return None

        for chapter_id in chapter_ids:
            if chapter_id < 3:
                chapter_names.append(eoc_name.replace("%d", str(chapter_id + 1)))
            elif chapter_id < 6:
                chapter_names.append(itf_name.replace("%d", str(chapter_id - 2)))
            else:
                chapter_names.append(cotc_name.replace("%d", str(chapter_id - 5)))

        return chapter_names

    @staticmethod
    def select_story_chapters(
        save_file: core.SaveFile, chapters: list[int] | None = None
    ) -> list[int] | None:
        chapter_names = StoryChapters.get_chapter_names(save_file, chapters)

        if chapter_names is None:
            return None

        selected_chapters, _ = dialog_creator.ChoiceInput.from_reduced(
            chapter_names, dialog="select_story_chapters"
        ).multiple_choice(localized_options=False)

        return selected_chapters

    @staticmethod
    def get_selected_chapter_progress(max_stages: int = 48) -> int | None:
        progress = dialog_creator.IntInput(
            min=0, max=max_stages
        ).get_input_locale_while("edit_chapter_progress_all", {"max": max_stages})
        if progress is None:
            return None

        return progress

    @staticmethod
    def edit_chapter_progress(
        save_file: core.SaveFile,
        chapter_id: int,
        chapter_name: str,
        clear_amount: int,
        clear_amount_choose: int,
    ) -> bool:
        max_stages = 48
        chapter = save_file.story.get_real_chapters()[chapter_id]
        progress = dialog_creator.IntInput(
            min=0, max=max_stages
        ).get_input_locale_while(
            "edit_chapter_progress",
            {"max": max_stages, "chapter_name": chapter_name},
        )
        if progress is None:
            return False
        clear_amounts = [1] * progress
        if clear_amount_choose == 0:
            clear_amount2 = core.EventChapters.ask_clear_amount()
            if clear_amount2 is None:
                return False
            clear_amounts = [clear_amount2] * progress
        elif clear_amount_choose == 1:
            clear_amounts = [clear_amount] * progress
        elif clear_amount_choose == 2:
            for i in range(progress):
                StoryChapters.print_current_stage(save_file, chapter_id, i)
                clear_amount2 = core.EventChapters.ask_clear_amount()
                if clear_amount2 is None:
                    return False
                clear_amounts[i] = clear_amount2

        chapter.apply_progress(progress, clear_amounts)
        return progress != 0

    @staticmethod
    def convert_stage_id(index: int) -> int:
        if index == 46:
            return 46
        if index == 47:
            return 47
        index = 45 - index
        return index

    @staticmethod
    def ask_clear_count() -> int | None:
        clear_count = dialog_creator.IntInput(
            min=0, max=core.core_data.max_value_manager.get("stage_clear_count")
        ).get_input_locale_while("edit_stage_clear_count", {})

        return clear_count

    @staticmethod
    def ask_if_individual_clear_counts() -> bool | None:
        options = ["individual_clear_counts", "all_clear_counts"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="individual_clear_counts_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return None
        choice -= 1
        return choice == 0

    @staticmethod
    def edit_stage_clear_count(
        save_file: core.SaveFile, chapter_id: int, stage_id: int
    ):
        chapter = save_file.story.get_real_chapters()[chapter_id]
        stage = chapter.stages[stage_id]
        clear_count = StoryChapters.ask_clear_count()
        if clear_count is None:
            return
        stage.clear_times = clear_count

    def clear_previous_chapters(self, chapter_id: int):
        chapters = self.get_real_chapters()
        """
        0: eoc 1
        1: eoc 2 - requires eoc 1
        2: eoc 3 - requires eoc 1 + eoc 2
        3: itf 1 - requires eoc 1
        4: itf 2 - requires eoc 1 + itf 1
        5: itf 3 - requires eoc 1 + itf 1 + itf 2
        6: cotc 1 - requires eoc 1 + itf 1
        7: cotc 2 - requires eoc 1 + itf 1 + cotc 1
        8: cotc 3 - requires eoc 1 + itf 1 + cotc 1 + cotc 2

        """
        if chapter_id == 1:  # eoc 2
            chapters[0].clear_chapter()
        elif chapter_id == 2:  # eoc 3
            chapters[0].clear_chapter()
            chapters[1].clear_chapter()
        elif chapter_id == 3:  # itf 1
            chapters[0].clear_chapter()
        elif chapter_id == 4:  # itf 2
            chapters[0].clear_chapter()
            chapters[3].clear_chapter()
        elif chapter_id == 5:  # itf 3
            chapters[0].clear_chapter()
            chapters[3].clear_chapter()
            chapters[4].clear_chapter()
        elif chapter_id == 6:  # cotc 1
            chapters[0].clear_chapter()
            chapters[3].clear_chapter()
        elif chapter_id == 7:  # cotc 2
            chapters[0].clear_chapter()
            chapters[3].clear_chapter()
            chapters[6].clear_chapter()
        elif chapter_id == 8:  # cotc 3
            chapters[0].clear_chapter()
            chapters[3].clear_chapter()
            chapters[6].clear_chapter()
            chapters[7].clear_chapter()

    @staticmethod
    def print_current_chapter(save_file: core.SaveFile, chapter_id: int):
        chapter_names = StoryChapters.get_chapter_names(save_file)
        if chapter_names is None:
            return
        chapter_name = chapter_names[chapter_id]
        color.ColoredText.localize("current_chapter", chapter_name=chapter_name)

    @staticmethod
    def print_current_treasure_group(
        save_file: core.SaveFile, chapter_id: int, treasure_group_id: int
    ):
        chapter_type = StoryChapters.get_chapter_type_from_index(chapter_id)

        treasure_group_names = TreasureGroupNames(
            save_file, chapter_type
        ).treasure_group_names
        if treasure_group_names is None:
            return
        treasure_group_name = treasure_group_names[treasure_group_id]
        color.ColoredText.localize(
            "current_treasure_group", treasure_group_name=treasure_group_name
        )

    @staticmethod
    def clear_story(save_file: core.SaveFile):
        story = save_file.story
        story.edit_chapters(
            save_file,
        )

    def edit_chapters(self, save_file: core.SaveFile):
        chapters = self.get_real_chapters()
        names = StoryChapters.get_chapter_names(save_file)
        if names is None:
            return

        map_choices = StoryChapters.select_story_chapters(save_file)
        if not map_choices:
            return

        clear_type_choice = dialog_creator.ChoiceInput.from_reduced(
            ["clear_whole_chapters", "clear_specific_stages"],
            dialog="select_clear_type",
            single_choice=True,
        ).single_choice()
        if clear_type_choice is None:
            return
        clear_type_choice -= 1

        modify_clear_amounts = dialog_creator.YesNoInput().get_input_once(
            "modify_clear_amounts"
        )
        if modify_clear_amounts is None:
            return
        clear_amount = 1
        clear_amount_type = -1
        if modify_clear_amounts:
            if len(map_choices) == 1:
                clear_amount_type = 0
            else:
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

        for id in map_choices:
            stage_names = StageNames(
                save_file, chapter=str(self.get_chapter_type_from_index(id))
            )
            stage_names = stage_names.stage_names
            if stage_names is None:
                return

            new_stage_names: list[str] = []
            for i in range(48):
                index_stage_id = StoryChapters.convert_stage_id(i)
                new_stage_names.append(stage_names[index_stage_id])
            stage_names = new_stage_names
            map_name = names[id]
            color.ColoredText.localize("current_sol_chapter", name=map_name, id=id)
            if clear_type_choice:
                stages = core.EventChapters.ask_stages_stage_names(stage_names)
                if stages is None:
                    return
            else:
                stages = list(range(48))

            if clear_amount_type == 0:
                clear_amount = core.EventChapters.ask_clear_amount()
                if clear_amount is None:
                    return

            could_unclear_stages = False

            if chapters[id].progress > max(stages) + 1:
                could_unclear_stages = True

            for stage in range(max(stages) + 1, 48):
                if chapters[id].stages[stage].clear_times:
                    could_unclear_stages = True

            if could_unclear_stages:
                unclear_other_stages = dialog_creator.YesNoInput().get_input_once(
                    "unclear_other_stages"
                )
                if unclear_other_stages is None:
                    return
            else:
                unclear_other_stages = False

            if unclear_other_stages:
                chapters[id].progress = 0
                for stage in range(max(stages), 48):
                    chapters[id].stages[stage].clear_times = 0

            for stage in stages:
                if clear_amount_type == 2:
                    stage_name = stage_names[stage]
                    color.ColoredText.localize(
                        "current_sol_stage", name=stage_name, id=stage
                    )
                if clear_amount_type == 2:
                    clear_amount = core.EventChapters.ask_clear_amount()
                    if clear_amount is None:
                        return
                self.clear_stage(
                    id,
                    stage,
                    overwrite_clear_progress=True,
                    clear_amount=clear_amount,
                    chapters=chapters,
                )

        color.ColoredText.localize("map_chapters_edited")

    @staticmethod
    def ask_treasure_level(save_file: core.SaveFile) -> int | None:
        treasure_text = core.core_data.get_treasure_text(save_file).treasure_text
        if treasure_text is None:
            return None
        if len(treasure_text) < 3:
            return None
        options = [
            "no_treasure",
            treasure_text[0],
            treasure_text[1],
            treasure_text[2],
            "custom_treasure_level",
        ]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="treasure_level_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return None
        choice -= 1

        max_treasure_level = core.core_data.max_value_manager.get("treasure_level")

        if choice == 4:
            treasure_level = dialog_creator.IntInput(
                min=0, max=max_treasure_level
            ).get_input_locale_while("custom_treasure_level_dialog", {})
            if treasure_level is None:
                return None
            return treasure_level

        return choice

    @staticmethod
    def get_per_chapter(chapters: list[int]) -> int | None:
        if len(chapters) == 1:
            return 0

        options = ["per_chapter", "all_selected_chapters"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="treasure_dialog_per_chapter", single_choice=True
        ).single_choice()
        if choice is None:
            return None
        choice -= 1
        return choice

    @staticmethod
    def edit_treasures_whole_chapters(save_file: core.SaveFile, chapters: list[int]):
        choice = StoryChapters.get_per_chapter(chapters)
        if choice is None:
            return

        if choice == 0:
            for chapter_id in chapters:
                StoryChapters.print_current_chapter(save_file, chapter_id)
                chapter = save_file.story.get_real_chapters()[chapter_id]
                treasure_level = StoryChapters.ask_treasure_level(save_file)
                if treasure_level is None:
                    return
                for stage in chapter.get_valid_treasure_stages():
                    stage.set_treasure(treasure_level)
        else:
            treasure_level = StoryChapters.ask_treasure_level(save_file)
            if treasure_level is None:
                return
            for chapter_id in chapters:
                chapter = save_file.story.get_real_chapters()[chapter_id]
                for stage in chapter.get_valid_treasure_stages():
                    stage.set_treasure(treasure_level)

    @staticmethod
    def get_chapter_type_from_index(index: int) -> int:
        if index < 3:
            return 0
        if index < 6:
            return 1
        return 2

    @staticmethod
    def select_stages(save_file: core.SaveFile, chapter_id: int) -> list[int] | None:
        options = ["select_stage_by_id", "select_stage_by_name"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="select_stage_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return None
        choice -= 1

        if choice == 0:
            stage_ids = dialog_creator.RangeInput(48, 1).get_input_locale(
                "select_stage_id", {}
            )
            if stage_ids is None:
                return None
            stage_ids = [stage_id - 1 for stage_id in stage_ids]
            return stage_ids

        chapter_type = StoryChapters.get_chapter_type_from_index(chapter_id)
        stage_names = StageNames(save_file, str(chapter_type)).stage_names
        if not stage_names:
            return None
        new_stage_names: list[str] = []
        for i in range(48):
            index_stage_id = StoryChapters.convert_stage_id(i)
            new_stage_names.append(stage_names[index_stage_id])
        selected_stages, _ = dialog_creator.ChoiceInput.from_reduced(
            new_stage_names, dialog="select_stages_name"
        ).multiple_choice(localized_options=False)

        if not selected_stages:
            return None

        return selected_stages

    @staticmethod
    def edit_treasures_individual_stages(save_file: core.SaveFile, chapters: list[int]):
        choice = StoryChapters.get_per_chapter(chapters)
        if choice is None:
            return
        if choice == 0:
            for chapter_id in chapters:
                StoryChapters.print_current_chapter(save_file, chapter_id)
                chapter = save_file.story.get_real_chapters()[chapter_id]
                stage_ids = StoryChapters.select_stages(save_file, chapter_id)
                if stage_ids is None:
                    return
                treasure_level = StoryChapters.ask_treasure_level(save_file)
                if treasure_level is None:
                    return
                for stage_id in stage_ids:
                    real_stage_id = StoryChapters.convert_stage_id(stage_id)
                    chapter.set_treasure(real_stage_id, treasure_level)
        else:
            stage_ids = StoryChapters.select_stages(save_file, 0)
            if stage_ids is None:
                return
            treasure_level = StoryChapters.ask_treasure_level(save_file)
            if treasure_level is None:
                return
            for chapter_id in chapters:
                chapter = save_file.story.get_real_chapters()[chapter_id]
                for stage_id in stage_ids:
                    real_stage_id = StoryChapters.convert_stage_id(stage_id)
                    chapter.set_treasure(real_stage_id, treasure_level)

    @staticmethod
    def edit_treasures_groups(save_file: core.SaveFile, chapters: list[int]):
        for chapter_id in chapters:
            StoryChapters.print_current_chapter(save_file, chapter_id)
            chapter = save_file.story.get_real_chapters()[chapter_id]
            chapter_type = StoryChapters.get_chapter_type_from_index(chapter_id)
            treasure_group_data = TreasureGroupData(
                save_file, chapter_type
            ).treasure_group_data
            treasure_group_names = TreasureGroupNames(
                save_file, chapter_type
            ).treasure_group_names
            if not treasure_group_data or not treasure_group_names:
                return
            treasure_group_names_new: list[str] = []
            for i in range(len(treasure_group_data)):
                treasure_group_names_new.append(treasure_group_names[i])

            selected_treasure_groups, _ = dialog_creator.ChoiceInput.from_reduced(
                treasure_group_names_new, dialog="select_treasure_groups"
            ).multiple_choice(localized_options=False)

            if not selected_treasure_groups:
                return

            options = ["group_individual", "group_all_at_once"]
            choice = dialog_creator.ChoiceInput.from_reduced(
                options, dialog="select_treasure_groups_individual"
            ).single_choice()
            if choice is None:
                return
            choice -= 1

            if choice == 0:
                for treasure_group_id in selected_treasure_groups:
                    StoryChapters.print_current_treasure_group(
                        save_file, chapter_id, treasure_group_id
                    )
                    treasure_level = StoryChapters.ask_treasure_level(save_file)
                    if treasure_level is None:
                        return
                    treasure_group = treasure_group_data[treasure_group_id]
                    for stage_id in treasure_group:
                        chapter.set_treasure(stage_id, treasure_level)

            else:
                treasure_level = StoryChapters.ask_treasure_level(save_file)
                if treasure_level is None:
                    return

                for treasure_group_id in selected_treasure_groups:
                    treasure_group = treasure_group_data[treasure_group_id]
                    for stage_id in treasure_group:
                        chapter.set_treasure(stage_id, treasure_level)

    @staticmethod
    def edit_treasures(save_file: core.SaveFile):
        selected_chapters = StoryChapters.select_story_chapters(save_file)
        if not selected_chapters:
            return
        options = ["whole_chapters", "individual_stages", "treasure_groups"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="treasure_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return
        choice -= 1

        if choice == 0:
            StoryChapters.edit_treasures_whole_chapters(save_file, selected_chapters)
        elif choice == 1:
            StoryChapters.edit_treasures_individual_stages(save_file, selected_chapters)
        elif choice == 2:
            StoryChapters.edit_treasures_groups(save_file, selected_chapters)

        color.ColoredText.localize("treasures_edited")

    @staticmethod
    def edit_itf_timed_scores(save_file: core.SaveFile):
        selected_chapters = StoryChapters.select_story_chapters(
            save_file, chapters=[3, 4, 5]
        )
        if not selected_chapters:
            return
        options = ["whole_chapters", "individual_stages"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="itf_timed_scores_dialog", single_choice=True
        ).single_choice()
        if choice is None:
            return
        choice -= 1

        selected_chapters = [chapter_id + 3 for chapter_id in selected_chapters]

        if choice == 0:
            StoryChapters.edit_itf_timed_scores_whole_chapters(
                save_file, selected_chapters
            )
        elif choice == 1:
            StoryChapters.edit_itf_timed_scores_individual_stages(
                save_file, selected_chapters
            )

        color.ColoredText.localize("itf_timed_scores_edited")

    @staticmethod
    def edit_itf_timed_scores_whole_chapters(
        save_file: core.SaveFile, chapters: list[int]
    ):
        choice = StoryChapters.get_per_chapter(chapters)
        if choice is None:
            return

        if choice == 0:
            for chapter_id in chapters:
                print(chapter_id)
                StoryChapters.print_current_chapter(save_file, chapter_id)
                chapter = save_file.story.get_real_chapters()[chapter_id]
                score = dialog_creator.IntInput(
                    min=0,
                    max=core.core_data.max_value_manager.get("itf_timed_score"),
                ).get_input_locale_while("itf_timed_score_dialog", {})
                if score is None:
                    return
                for stage in chapter.get_valid_treasure_stages():
                    stage.itf_timed_score = score
        else:
            score = dialog_creator.IntInput(
                min=0,
                max=core.core_data.max_value_manager.get("itf_timed_score"),
            ).get_input_locale_while("itf_timed_score_dialog", {})
            if score is None:
                return
            for chapter_id in chapters:
                chapter = save_file.story.get_real_chapters()[chapter_id]
                for stage in chapter.get_valid_treasure_stages():
                    stage.itf_timed_score = score

    @staticmethod
    def print_current_stage(save_file: core.SaveFile, chapter_id: int, stage_id: int):
        chapter_names = StoryChapters.get_chapter_names(save_file)
        if chapter_names is None:
            return
        chapter_name = chapter_names[chapter_id]
        chapter_type = StoryChapters.get_chapter_type_from_index(chapter_id)
        stage_names = StageNames(save_file, str(chapter_type)).stage_names
        if stage_names is None:
            return
        stage_id = StoryChapters.convert_stage_id(stage_id)
        stage_name = stage_names[stage_id]
        color.ColoredText.localize(
            "current_stage", chapter_name=chapter_name, stage_name=stage_name
        )

    @staticmethod
    def edit_itf_timed_scores_individual_stages(
        save_file: core.SaveFile, chapters: list[int]
    ):
        choice = StoryChapters.get_per_chapter(chapters)
        if choice is None:
            return
        options = ["individual_stages", "all_selected_stages"]
        choice2 = dialog_creator.ChoiceInput.from_reduced(
            options,
            dialog="itf_timed_scores_individual_dialog",
            single_choice=True,
        ).single_choice()
        if choice2 is None:
            return
        choice2 -= 1

        if choice == 0:
            for chapter_id in chapters:
                StoryChapters.print_current_chapter(save_file, chapter_id)
                chapter = save_file.story.get_real_chapters()[chapter_id]
                stage_ids = StoryChapters.select_stages(save_file, chapter_id)
                if stage_ids is None:
                    return
                if choice2 == 0:
                    for stage_id in stage_ids:
                        StoryChapters.print_current_stage(
                            save_file, chapter_id, stage_id
                        )

                        score = dialog_creator.IntInput(
                            min=0,
                            max=core.core_data.max_value_manager.get("itf_timed_score"),
                        ).get_input_locale_while("itf_timed_score_dialog", {})
                        if score is None:
                            return
                        chapter.stages[stage_id].itf_timed_score = score
                elif choice2 == 1:
                    score = dialog_creator.IntInput(
                        min=0,
                        max=core.core_data.max_value_manager.get("itf_timed_score"),
                    ).get_input_locale_while("itf_timed_score_dialog", {})
                    if score is None:
                        return
                    for stage_id in stage_ids:
                        chapter.stages[stage_id].itf_timed_score = score
        else:
            stage_ids = StoryChapters.select_stages(save_file, 3)
            if stage_ids is None:
                return
            if choice2 == 0:
                for stage_id in stage_ids:
                    StoryChapters.print_current_stage(save_file, 3, stage_id)
                    score = dialog_creator.IntInput(
                        min=0,
                        max=core.core_data.max_value_manager.get("itf_timed_score"),
                    ).get_input_locale_while("itf_timed_score_dialog", {})
                    if score is None:
                        return
                    for chapter_id in chapters:
                        chapter = save_file.story.get_real_chapters()[chapter_id]
                        chapter.stages[stage_id].itf_timed_score = score
            elif choice2 == 1:
                score = dialog_creator.IntInput(
                    min=0,
                    max=core.core_data.max_value_manager.get("itf_timed_score"),
                ).get_input_locale_while("itf_timed_score_dialog", {})
                if score is None:
                    return
                for chapter_id in chapters:
                    chapter = save_file.story.get_real_chapters()[chapter_id]
                    for stage_id in stage_ids:
                        chapter.stages[stage_id].itf_timed_score = score


class StageNames:
    def __init__(self, save_file: core.SaveFile, chapter: str, max_stages: int = 48):
        self.save_file = save_file
        self.chapter = chapter
        self.max_stages = max_stages
        self.stage_names = self.get_stage_names()

    def get_file_name(self) -> str:
        if self.chapter.isdigit():
            return (
                f"StageName{self.chapter}_{core.core_data.get_lang(self.save_file)}.csv"
            )
        return f"StageName_{self.chapter}_{core.core_data.get_lang(self.save_file)}.csv"

    def get_stage_names(self) -> list[str] | None:
        file_name = self.get_file_name()
        gdg = core.core_data.get_game_data_getter(self.save_file)
        file = gdg.download("resLocal", file_name)
        if file is None:
            return None
        csv = core.CSV(
            file,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
        )
        stage_names: list[str] = []
        if self.chapter.isdigit():
            for row in csv:
                stage_names.append(row[0].to_str())
        else:
            for row in csv:
                for value in row:
                    stage_names.append(value.to_str())
        return stage_names[: self.max_stages]

    def get_stage_name(self, stage_id: int) -> str | None:
        if self.stage_names is None:
            return None
        return self.stage_names[stage_id]


class TreasureText:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.treasure_text = self.get_treasure_text()

    def get_tt_file_name(self) -> str:
        return f"Treasure2_{core.core_data.get_lang(self.save_file)}.csv"

    def get_treasure_text(self) -> list[str] | None:
        file_name = self.get_tt_file_name()
        gdg = core.core_data.get_game_data_getter(self.save_file)
        file = gdg.download("resLocal", file_name)
        if file is None:
            return None
        csv = core.CSV(
            file,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
        )
        treasure_text: list[str] = []
        for row in csv:
            treasure_text.append(row[0].to_str())
        return treasure_text


class TreasureGroupData:
    def __init__(self, save_file: core.SaveFile, chapter_type: int):
        self.save_file = save_file
        self.chapter_type = chapter_type
        self.treasure_group_data = self.get_treasure_group_data()

    def get_tgd_file_name(self) -> str:
        if self.chapter_type == 0:
            return "treasureData0.csv"
        if self.chapter_type == 1:
            return "treasureData1.csv"
        if self.chapter_type == 2:
            return "treasureData2_0.csv"
        return ""

    def get_treasure_group_data(self) -> list[list[int]] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        file = gdg.download("DataLocal", self.get_tgd_file_name())
        if file is None:
            return None
        csv = core.CSV(file)
        treasure_group_data: list[list[int]] = []
        for row in csv.lines[11:22]:
            treasure_group_data.append(
                [value.to_int() for value in row if value.to_int() != -1]
            )

        return treasure_group_data


class TreasureGroupNames:
    def __init__(self, save_file: core.SaveFile, chapter_type: int):
        self.save_file = save_file
        self.chapter_type = chapter_type
        self.treasure_group_names = self.get_treasure_group_names()

    def get_tgn_file_name(self) -> str:
        lang = core.core_data.get_lang(self.save_file)
        if self.chapter_type == 0:
            return f"Treasure3_0_{lang}.csv"
        if self.chapter_type == 1:
            return f"Treasure3_1_{lang}.csv"
        if self.chapter_type == 2:
            return f"Treasure3_2_0_{lang}.csv"
        return ""

    def get_treasure_group_names(self) -> list[str] | None:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        file = gdg.download("resLocal", self.get_tgn_file_name())
        if file is None:
            return None
        csv = core.CSV(
            file,
            delimiter=core.Delimeter.from_country_code_res(self.save_file.cc),
        )
        treasure_group_names: list[str] = []
        for row in csv:
            treasure_group_names.append(row[0].to_str())
        return treasure_group_names
