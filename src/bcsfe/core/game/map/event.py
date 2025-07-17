from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator, edits


class EventStage:
    def __init__(self, clear_amount: int):
        self.clear_amount = clear_amount

    @staticmethod
    def init() -> EventStage:
        return EventStage(0)

    @staticmethod
    def read(data: core.Data, is_int: bool) -> EventStage:
        if is_int:
            clear_amount = data.read_int()
        else:
            clear_amount = data.read_short()
        return EventStage(clear_amount)

    def write(self, data: core.Data, is_int: bool):
        if is_int:
            data.write_int(self.clear_amount)
        else:
            data.write_short(self.clear_amount)

    def serialize(self) -> int:
        return self.clear_amount

    @staticmethod
    def deserialize(data: int) -> EventStage:
        return EventStage(
            clear_amount=data,
        )

    def __repr__(self) -> str:
        return f"<EventStage clear_amount={self.clear_amount}>"

    def __str__(self) -> str:
        return self.__repr__()

    def clear_stage(self, clear_amount: int = 1):
        self.clear_amount = clear_amount

    def unclear_stage(self):
        self.clear_amount = 0


class EventSubChapter:
    def __init__(self, selected_stage: int, total_stages: int = 0):
        self.selected_stage = selected_stage
        self.clear_progress = 0
        self.stages = [EventStage.init() for _ in range(total_stages)]
        self.chapter_unlock_state = 0
        self.total_stages = 0

    def clear_stage(
        self,
        index: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ) -> bool:
        if overwrite_clear_progress:
            self.clear_progress = index + 1
        else:
            self.clear_progress = max(self.clear_progress, index + 1)
        self.stages[index].clear_stage(clear_amount)
        self.chapter_unlock_state = 3
        if index == self.total_stages - 1:
            return True
        return False

    def unclear_stage(self, index: int) -> bool:
        self.clear_progress = min(self.clear_progress, index)
        self.stages[index].unclear_stage()

        return True

    def clear_map(self, increment: bool = True) -> bool:
        self.clear_progress = len(self.stages)
        self.chapter_unlock_state = 3
        for stage in self.stages:
            if increment:
                clear_amount = stage.clear_amount + 1
            else:
                clear_amount = stage.clear_amount or 1
            stage.clear_stage(clear_amount)
        return True

    @staticmethod
    def init(total_stages: int) -> EventSubChapter:
        return EventSubChapter(0, total_stages)

    @staticmethod
    def read_selected_stage(data: core.Data, is_int: bool) -> EventSubChapter:
        if is_int:
            selected_stage = data.read_int()
        else:
            selected_stage = data.read_byte()
        return EventSubChapter(selected_stage)

    def write_selected_stage(self, data: core.Data, is_int: bool):
        if is_int:
            data.write_int(self.selected_stage)
        else:
            data.write_byte(self.selected_stage)

    def read_clear_progress(self, data: core.Data, is_int: bool):
        if is_int:
            self.clear_progress = data.read_int()
        else:
            self.clear_progress = data.read_byte()

    def write_clear_progress(self, data: core.Data, is_int: bool):
        if is_int:
            data.write_int(self.clear_progress)
        else:
            data.write_byte(self.clear_progress)

    def read_stages(self, data: core.Data, total_stages: int, is_int: bool):
        self.stages = [EventStage.read(data, is_int) for _ in range(total_stages)]

    def write_stages(self, data: core.Data, is_int: bool):
        for stage in self.stages:
            stage.write(data, is_int)

    def read_chapter_unlock_state(self, data: core.Data, is_int: bool):
        if is_int:
            self.chapter_unlock_state = data.read_int()
        else:
            self.chapter_unlock_state = data.read_byte()

    def write_chapter_unlock_state(self, data: core.Data, is_int: bool):
        if is_int:
            data.write_int(self.chapter_unlock_state)
        else:
            data.write_byte(self.chapter_unlock_state)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "clear_progress": self.clear_progress,
            "stages": [stage.serialize() for stage in self.stages],
            "chapter_unlock_state": self.chapter_unlock_state,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EventSubChapter:
        sub_chapter = EventSubChapter(
            selected_stage=data.get("selected_stage", 0),
        )
        sub_chapter.clear_progress = data.get("clear_progress", 0)
        sub_chapter.stages = [
            EventStage.deserialize(stage) for stage in data.get("stages", [])
        ]
        sub_chapter.chapter_unlock_state = data.get("chapter_unlock_state", 0)
        return sub_chapter

    def __repr__(self) -> str:
        return f"<EventSubChapter selected_stage={self.selected_stage}, clear_progress={self.clear_progress}, stages={self.stages}, chapter_unlock_state={self.chapter_unlock_state}>"

    def __str__(self) -> str:
        return self.__repr__()


class EventSubChapterStars:
    def __init__(self, chapters: list[EventSubChapter]):
        self.chapters = chapters
        self.legend_restriction = 0

    def clear_stage(
        self,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ) -> bool:
        finished = self.chapters[star].clear_stage(
            stage, clear_amount, overwrite_clear_progress
        )
        if finished:
            if star + 1 < len(self.chapters):
                self.chapters[star + 1].chapter_unlock_state = 1
        return finished

    def unclear_stage(self, star: int, stage: int):
        finished = self.chapters[star].unclear_stage(stage)
        if finished and star + 1 < len(self.chapters):
            for chapter in self.chapters[star + 1 :]:
                chapter.chapter_unlock_state = 0
        return finished

    def clear_map(self, star: int, increment: bool = True) -> bool:
        finished = self.chapters[star].clear_map(increment)
        if finished:
            if star + 1 < len(self.chapters):
                self.chapters[star + 1].chapter_unlock_state = 1
        return finished

    def clear_chapter(self, increment: bool = True) -> bool:
        for chapter in self.chapters:
            chapter.clear_map(increment)
        return True

    @staticmethod
    def init(total_stars: int) -> EventSubChapterStars:
        return EventSubChapterStars(
            [EventSubChapter.init(0) for _ in range(total_stars)]
        )

    @staticmethod
    def read_selected_stage(
        data: core.Data, total_stars: int, is_int: bool
    ) -> EventSubChapterStars:
        chapters = [
            EventSubChapter.read_selected_stage(data, is_int)
            for _ in range(total_stars)
        ]
        return EventSubChapterStars(chapters)

    def write_selected_stage(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

    def read_clear_progress(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_clear_progress(data, is_int)

    def write_clear_progress(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

    def read_stages(self, data: core.Data, total_stages: int, is_int: bool):
        for _ in range(total_stages):
            for chapter in self.chapters:
                chapter.stages.append(EventStage.read(data, is_int))
                # chapter.read_stages(data, total_stages, is_int)

    def write_stages(self, data: core.Data, is_int: bool):
        for i in range(len(self.chapters[0].stages)):
            for chapter in self.chapters:
                chapter.stages[i].write(data, is_int)
                # chapter.write_stages(data, is_int)

    def read_chapter_unlock_state(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data, is_int)

    def write_chapter_unlock_state(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(self, data: core.Data):
        self.legend_restriction = data.read_int()

    def write_legend_restrictions(self, data: core.Data):
        data.write_int(self.legend_restriction)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": [chapter.serialize() for chapter in self.chapters],
            "legend_restriction": self.legend_restriction,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EventSubChapterStars:
        chapters = [
            EventSubChapter.deserialize(chapter) for chapter in data.get("chapters", [])
        ]
        chapter = EventSubChapterStars(chapters)
        chapter.legend_restriction = data.get("legend_restriction", 0)
        return chapter

    def __repr__(self) -> str:
        return f"<EventSubChapterStars chapters={self.chapters}, legend_restriction={self.legend_restriction}>"

    def __str__(self) -> str:
        return self.__repr__()


class EventChapterGroup:
    def __init__(self, chapters: list[EventSubChapterStars]):
        self.chapters = chapters

    def clear_stage(
        self,
        map: int,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ):
        finished = self.chapters[map].clear_stage(
            star, stage, clear_amount, overwrite_clear_progress
        )
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

    def unclear_stage(self, map: int, star: int, stage: int):
        finished = self.chapters[map].unclear_stage(star, stage)
        if finished and map + 1 < len(self.chapters) and star == 0:
            for chapter in self.chapters[map + 1].chapters:
                chapter.chapter_unlock_state = 0

    def clear_map(self, map: int, star: int, increment: bool = True):
        finished = self.chapters[map].clear_map(star, increment)
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

    def clear_chapter(self, map: int, increment: bool = True):
        finished = self.chapters[map].clear_chapter(increment)
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

    def clear_group(self, increment: bool = True):
        for chapter in self.chapters:
            chapter.clear_chapter(increment)

    @staticmethod
    def init(total_subchapters: int, total_stars: int) -> EventChapterGroup:
        return EventChapterGroup(
            [EventSubChapterStars.init(total_stars) for _ in range(total_subchapters)]
        )

    @staticmethod
    def read_selected_stage(
        data: core.Data, total_subchapters: int, total_stars: int, is_int: bool
    ) -> EventChapterGroup:
        chapters = [
            EventSubChapterStars.read_selected_stage(data, total_stars, is_int)
            for _ in range(total_subchapters)
        ]
        return EventChapterGroup(chapters)

    def write_selected_stage(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

    def read_clear_progress(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_clear_progress(data, is_int)

    def write_clear_progress(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

    def read_stages(self, data: core.Data, total_stages: int, is_int: bool):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages, is_int)

    def write_stages(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_stages(data, is_int)

    def read_chapter_unlock_state(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data, is_int)

    def write_chapter_unlock_state(self, data: core.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(self, data: core.Data):
        for chapter in self.chapters:
            chapter.read_legend_restrictions(data)

    def write_legend_restrictions(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_legend_restrictions(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> EventChapterGroup:
        chapters = [EventSubChapterStars.deserialize(chapter) for chapter in data]
        return EventChapterGroup(chapters)

    def __repr__(self) -> str:
        return f"<EventChapterGroup chapters={self.chapters}>"

    def __str__(self) -> str:
        return self.__repr__()


class EventChapters:
    def __init__(self, chapters: list[EventChapterGroup]):
        self.chapters = chapters
        self.completed_one_level_in_chapter: dict[int, int] = {}
        self.displayed_cleared_limit_text: dict[int, bool] = {}
        self.event_start_dates: dict[int, int] = {}
        self.stages_reward_claimed: list[int] = []

    def clear_stage(
        self,
        type: int,
        map: int,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ):
        self.chapters[type].clear_stage(
            map,
            star,
            stage,
            clear_amount,
            overwrite_clear_progress,
        )

    def unclear_stage(self, type: int, map: int, star: int, stage: int):
        self.chapters[type].unclear_stage(map, star, stage)

    def clear_map(self, type: int, map: int, star: int, increment: bool = True):
        self.chapters[type].clear_map(map, star, increment)

    def clear_chapter(self, type: int, map: int, increment: bool = True):
        self.chapters[type].clear_chapter(map, increment)

    def clear_group(self, type: int, increment: bool = True):
        self.chapters[type].clear_group(increment)

    @staticmethod
    def init(gv: core.GameVersion) -> EventChapters:
        if gv < 20:
            return EventChapters([])
        if gv <= 32:
            total_map_types = 3
            total_subchapters = 150
            stars_per_subchapter = 3
        elif gv <= 34:
            total_map_types = 4
            total_subchapters = 150
            stars_per_subchapter = 3
        else:
            total_map_types = 0
            total_subchapters = 0
            stars_per_subchapter = 0

        return EventChapters(
            [
                EventChapterGroup.init(total_subchapters, stars_per_subchapter)
                for _ in range(total_map_types)
            ]
        )

    @staticmethod
    def read(data: core.Data, gv: core.GameVersion) -> EventChapters:
        if gv < 20:
            return EventChapters([])
        stages_per_subchapter = 0
        if 80099 < gv:
            total_map_types = data.read_byte()
            total_subchapters = data.read_short()
            stars_per_subchapter = data.read_byte()
            stages_per_subchapter = data.read_byte()
            is_int = False
        elif gv <= 32:
            total_map_types = 3
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        elif gv <= 34:
            total_map_types = 4
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        else:
            total_map_types = data.read_int()
            total_subchapters = data.read_int()
            stars_per_subchapter = data.read_int()
            is_int = True
        chapters = [
            EventChapterGroup.read_selected_stage(
                data, total_subchapters, stars_per_subchapter, is_int
            )
            for _ in range(total_map_types)
        ]
        if 80099 < gv:
            is_int = False
        elif gv <= 32:
            total_map_types = 3
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        elif gv <= 34:
            total_map_types = 4
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        else:
            total_map_types = data.read_int()
            total_subchapters = data.read_int()
            stars_per_subchapter = data.read_int()
            is_int = True

        for chapter in chapters:
            chapter.read_clear_progress(data, is_int)

        if 80099 < gv:
            is_int = False
        elif gv <= 32:
            total_map_types = 3
            total_subchapters = 150
            stars_per_subchapter = 3
            stages_per_subchapter = 12
            is_int = True
        elif gv <= 34:
            total_map_types = 4
            total_subchapters = 150
            stars_per_subchapter = 3
            stages_per_subchapter = 12
            is_int = True
        else:
            total_map_types = data.read_int()
            total_subchapters = data.read_int()
            stages_per_subchapter = data.read_int()
            stars_per_subchapter = data.read_int()
            is_int = True

        for chapter in chapters:
            chapter.read_stages(data, stages_per_subchapter, is_int)

        if 80099 < gv:
            is_int = False
        elif gv <= 32:
            total_map_types = 3
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        elif gv <= 34:
            total_map_types = 4
            total_subchapters = 150
            stars_per_subchapter = 3
            is_int = True
        else:
            total_map_types = data.read_int()
            total_subchapters = data.read_int()
            stars_per_subchapter = data.read_int()
            is_int = True

        for chapter in chapters:
            chapter.read_chapter_unlock_state(data, is_int)

        return EventChapters(chapters)

    def get_lengths(self) -> tuple[int, int, int, int]:
        total_map_types = len(self.chapters)
        try:
            total_subchapters = len(self.chapters[0].chapters)
        except IndexError:
            total_subchapters = 0

        try:
            stars_per_subchapter = len(self.chapters[0].chapters[0].chapters)
        except IndexError:
            stars_per_subchapter = 0

        try:
            stages_per_subchapter = len(self.chapters[0].chapters[0].chapters[0].stages)
        except IndexError:
            stages_per_subchapter = 0
        return (
            total_map_types,
            total_subchapters,
            stars_per_subchapter,
            stages_per_subchapter,
        )

    def write(self, data: core.Data, gv: core.GameVersion):
        (
            total_map_types,
            total_subchapters,
            stars_per_subchapter,
            stages_per_subchapter,
        ) = self.get_lengths()
        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                data.write_byte(total_map_types)
                data.write_short(total_subchapters)
                data.write_byte(stars_per_subchapter)
                data.write_byte(stages_per_subchapter)
                is_int = False
            else:
                data.write_int(total_map_types)
                data.write_int(total_subchapters)
                data.write_int(stars_per_subchapter)
                is_int = True

        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(total_map_types)
                data.write_int(total_subchapters)
                data.write_int(stars_per_subchapter)
                is_int = True

        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(total_map_types)
                data.write_int(total_subchapters)
                data.write_int(stages_per_subchapter)
                data.write_int(stars_per_subchapter)
                is_int = True

        for chapter in self.chapters:
            chapter.write_stages(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(total_map_types)
                data.write_int(total_subchapters)
                data.write_int(stars_per_subchapter)
                is_int = True

        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(self, data: core.Data, gv: core.GameVersion):
        if gv < 20:
            return
        if gv < 33:
            total_map_types = 3  # type: ignore
            total_subchapters = 150  # type: ignore
        elif gv < 41:
            total_map_types = 4  # type: ignore
            total_subchapters = 150  # type: ignore
        else:
            total_map_types = data.read_int()  # type: ignore
            total_subchapters = data.read_int()  # type: ignore

        for chapter in self.chapters:
            chapter.read_legend_restrictions(data)

    def write_legend_restrictions(self, data: core.Data, gv: core.GameVersion):
        if gv < 20:
            return
        if gv >= 41:
            data.write_int(len(self.chapters))
            try:
                data.write_int(len(self.chapters[0].chapters))
            except IndexError:
                data.write_int(0)

        for chapter in self.chapters:
            chapter.write_legend_restrictions(data)

    def read_dicts(self, data: core.Data):
        self.completed_one_level_in_chapter = data.read_int_int_dict()
        self.displayed_cleared_limit_text = data.read_int_bool_dict()
        self.event_start_dates = data.read_int_int_dict()
        self.stages_reward_claimed = data.read_int_list()

    def write_dicts(self, data: core.Data):
        data.write_int_int_dict(self.completed_one_level_in_chapter)
        data.write_int_bool_dict(self.displayed_cleared_limit_text)
        data.write_int_int_dict(self.event_start_dates)
        data.write_int_list(self.stages_reward_claimed)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": [chapter.serialize() for chapter in self.chapters],
            "completed_one_level_in_chapter": self.completed_one_level_in_chapter,
            "displayed_cleared_limit_text": self.displayed_cleared_limit_text,
            "event_start_dates": self.event_start_dates,
            "stages_reward_claimed": self.stages_reward_claimed,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> EventChapters:
        chapters = [
            EventChapterGroup.deserialize(chapter)
            for chapter in data.get("chapters", [])
        ]
        ch = EventChapters(chapters)
        ch.completed_one_level_in_chapter = data.get(
            "completed_one_level_in_chapter", {}
        )
        ch.displayed_cleared_limit_text = data.get("displayed_cleared_limit_text", {})
        ch.event_start_dates = data.get("event_start_dates", {})
        ch.stages_reward_claimed = data.get("stages_reward_claimed", [])
        return ch

    def __repr__(self) -> str:
        return f"EventChapters({self.chapters}, {self.completed_one_level_in_chapter}, {self.displayed_cleared_limit_text}, {self.event_start_dates}, {self.stages_reward_claimed})"

    def __str__(self) -> str:
        return self.__repr__()

    def get_total_stars(self, type: int, map: int) -> int:
        return len(self.chapters[type].chapters[map].chapters)

    def get_total_stages(self, type: int, map: int, star: int) -> int:
        return len(self.chapters[type].chapters[map].chapters[star].stages)

    @staticmethod
    def ask_stars(
        max_stars: int, prompt: str = "custom_star_count_per_chapter"
    ) -> int | None:
        stars = dialog_creator.IntInput(min=0, max=max_stars).get_basic_input_locale(
            prompt, {"max": max_stars}
        )
        if stars is None:
            return None
        return stars

    @staticmethod
    def ask_stages(map_names: core.MapNames, chapter_id: int) -> list[int] | None:
        stage_names = map_names.stage_names.get(chapter_id)
        if stage_names is None:
            return None
        new_stage_names: list[str] = []
        for stage in stage_names:
            if stage == "＠":
                continue
            new_stage_names.append(stage)
        stage_names = new_stage_names

        dialog_creator.ListOutput(
            stage_names, ints=[], dialog="select_stage", localize_elements=False
        ).display_locale()

        choices = dialog_creator.RangeInput(len(stage_names), 1).get_input_locale(
            "stages_select", {}
        )
        if choices is None:
            return None
        return [c - 1 for c in choices]

    @staticmethod
    def ask_stages_stage_names(stage_names: list[str]) -> list[int] | None:
        new_stage_names: list[str] = []
        for stage in stage_names:
            if stage == "＠":
                continue
            new_stage_names.append(stage)
        stage_names = new_stage_names
        choice = dialog_creator.ChoiceInput.from_reduced(
            stage_names, dialog="select_stage_progress", single_choice=True
        ).single_choice()
        if choice is None:
            return None
        return list(range(choice))

    @staticmethod
    def ask_clear_amount() -> int | None:
        return dialog_creator.IntInput(
            max=core.core_data.max_value_manager.get("stage_clear_count")
        ).get_basic_input_locale("clear_amount_enter", {})

    @staticmethod
    def edit_sol_chapters(save_file: core.SaveFile):
        EventChapters.edit_chapters(save_file, 0, "N")

    @staticmethod
    def edit_event_chapters(save_file: core.SaveFile):
        EventChapters.edit_chapters(save_file, 1, "S")

    @staticmethod
    def edit_collab_chapters(save_file: core.SaveFile):
        EventChapters.edit_chapters(save_file, 2, "C")

    @staticmethod
    def select_map_names(names_dict: dict[int, str | None]) -> list[int] | None:
        map_ids: list[int] = []
        names_list: list[str] = []
        names_dict = dict(sorted(names_dict.items()))
        ids = list(names_dict.keys())
        for id, map_name in names_dict.items():
            if map_name is None:
                map_name = core.core_data.local_manager.get_key(
                    "unknown_map_name", id=id
                )
            else:
                map_name = core.core_data.local_manager.get_key(
                    "map_name", name=map_name, id=id
                )
            names_list.append(map_name)

        while True:
            dialog_creator.ListOutput(
                names_list, [], "select_map", localize_elements=False
            ).display_locale()
            if names_list:
                example_name = names_list[0]
            else:
                example_name = ""
            usr_input = (
                color.ColoredInput()
                .localize("select_map_dialog", example=example_name, escape=False)
                .lower()
                .strip()
            )
            if usr_input == "q":
                return None
            usr_ids = dialog_creator.RangeInput(max=len(names_list), min=1).parse(
                usr_input
            )
            if not usr_ids:
                found_names: list[tuple[int, str]] = []
                for i, name in enumerate(names_list):
                    if usr_input.replace(" ", "_") in name.lower().strip().replace(
                        " ", "_"
                    ):
                        true_id = ids[i]
                        found_names.append((i, name))

                if len(found_names) == 0:
                    color.ColoredText.localize("no_map_found", name=usr_input)
                elif len(found_names) == 1:
                    id = found_names[0][0]
                    true_id = ids[id]
                    if true_id not in map_ids:
                        map_ids.append(true_id)
                else:
                    selected_ids, _ = dialog_creator.ChoiceInput.from_reduced(
                        [name for _, name in found_names],
                        dialog="select_map_from_names",
                    ).multiple_choice(False)
                    if selected_ids is None:
                        continue
                    for i in selected_ids:
                        id = found_names[i][0]
                        true_id = ids[id]
                        if true_id not in map_ids:
                            map_ids.append(true_id)
            else:
                for id in usr_ids:
                    id -= 1
                    true_id = ids[id]
                    if true_id not in map_ids:
                        map_ids.append(true_id)

            color.ColoredText.localize("current_maps", maps=map_ids)

            for id in map_ids:
                name = names_dict[id]
                EventChapters.print_current_chapter(name, id)

            finished = dialog_creator.YesNoInput().get_input_once(
                "finished_selecting_maps"
            )
            if finished is None:
                return None
            if finished:
                break
        return map_ids

    @staticmethod
    def print_current_chapter(name: str | None, id: int):
        if name is None:
            name = core.core_data.local_manager.get_key("unknown_map_name", id=id)
        color.ColoredText.localize("current_sol_chapter", name=name, id=id)

    @staticmethod
    def edit_chapters(save_file: core.SaveFile, type: int, letter_code: str):
        edits.map.edit_chapters(save_file, save_file.event_stages, letter_code, type)

    def unclear_rest(
        self,
        stages: list[int],
        stars: int,
        id: int,
        type: int,
    ):
        if not stages:
            return
        for star in range(stars, self.get_total_stars(type, id)):
            for stage in range(max(stages), self.get_total_stages(type, id, star)):
                self.chapters[type].chapters[id].chapters[star].stages[
                    stage
                ].clear_amount = 0
                self.chapters[type].chapters[id].chapters[star].clear_progress = 0

    def set_total_stages(self, map: int, type: int, total_stages: int):
        for chapter in self.chapters[type].chapters[map].chapters:
            chapter.total_stages = total_stages
