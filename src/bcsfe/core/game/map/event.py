from typing import Any
from bcsfe.core import game_version, io


class EventStage:
    def __init__(self, clear_amount: int):
        self.clear_amount = clear_amount

    @staticmethod
    def read(data: io.data.Data, is_int: bool) -> "EventStage":
        if is_int:
            clear_amount = data.read_int()
        else:
            clear_amount = data.read_short()
        return EventStage(clear_amount)

    def write(self, data: io.data.Data, is_int: bool):
        if is_int:
            data.write_int(self.clear_amount)
        else:
            data.write_short(self.clear_amount)

    def serialize(self) -> int:
        return self.clear_amount

    @staticmethod
    def deserialize(data: int) -> "EventStage":
        return EventStage(
            clear_amount=data,
        )

    def __repr__(self) -> str:
        return f"<EventStage clear_amount={self.clear_amount}>"

    def __str__(self) -> str:
        return self.__repr__()


class EventSubChapter:
    def __init__(self, selected_stage: int):
        self.selected_stage = selected_stage

    @staticmethod
    def read_selected_stage(data: io.data.Data, is_int: bool) -> "EventSubChapter":
        if is_int:
            selected_stage = data.read_int()
        else:
            selected_stage = data.read_byte()
        return EventSubChapter(selected_stage)

    def write_selected_stage(self, data: io.data.Data, is_int: bool):
        if is_int:
            data.write_int(self.selected_stage)
        else:
            data.write_byte(self.selected_stage)

    def read_clear_progress(self, data: io.data.Data, is_int: bool):
        if is_int:
            self.clear_progress = data.read_int()
        else:
            self.clear_progress = data.read_byte()

    def write_clear_progress(self, data: io.data.Data, is_int: bool):
        if is_int:
            data.write_int(self.clear_progress)
        else:
            data.write_byte(self.clear_progress)

    def read_stages(self, data: io.data.Data, total_stages: int, is_int: bool):
        self.stages = [EventStage.read(data, is_int) for _ in range(total_stages)]

    def write_stages(self, data: io.data.Data, is_int: bool):
        for stage in self.stages:
            stage.write(data, is_int)

    def read_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
        if is_int:
            self.chapter_unlock_state = data.read_int()
        else:
            self.chapter_unlock_state = data.read_byte()

    def write_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
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
    def deserialize(data: dict[str, Any]) -> "EventSubChapter":
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

    @staticmethod
    def read_selected_stage(
        data: io.data.Data, total_stars: int, is_int: bool
    ) -> "EventSubChapterStars":
        chapters = [
            EventSubChapter.read_selected_stage(data, is_int)
            for _ in range(total_stars)
        ]
        return EventSubChapterStars(chapters)

    def write_selected_stage(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

    def read_clear_progress(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_clear_progress(data, is_int)

    def write_clear_progress(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

    def read_stages(self, data: io.data.Data, total_stages: int, is_int: bool):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages, is_int)

    def write_stages(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_stages(data, is_int)

    def read_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data, is_int)

    def write_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(self, data: io.data.Data):
        self.legend_restriction = data.read_int()

    def write_legend_restrictions(self, data: io.data.Data):
        data.write_int(self.legend_restriction)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": [chapter.serialize() for chapter in self.chapters],
            "legend_restriction": self.legend_restriction,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "EventSubChapterStars":
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

    @staticmethod
    def read_selected_stage(
        data: io.data.Data, total_subchapters: int, total_stars: int, is_int: bool
    ) -> "EventChapterGroup":
        chapters = [
            EventSubChapterStars.read_selected_stage(data, total_stars, is_int)
            for _ in range(total_subchapters)
        ]
        return EventChapterGroup(chapters)

    def write_selected_stage(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

    def read_clear_progress(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_clear_progress(data, is_int)

    def write_clear_progress(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

    def read_stages(self, data: io.data.Data, total_stages: int, is_int: bool):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages, is_int)

    def write_stages(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_stages(data, is_int)

    def read_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data, is_int)

    def write_chapter_unlock_state(self, data: io.data.Data, is_int: bool):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.read_legend_restrictions(data)

    def write_legend_restrictions(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_legend_restrictions(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "EventChapterGroup":
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

    @staticmethod
    def read(data: io.data.Data, gv: "game_version.GameVersion") -> "EventChapters":
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

    def write(self, data: io.data.Data, gv: "game_version.GameVersion"):
        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                data.write_byte(len(self.chapters))
                data.write_short(len(self.chapters[0].chapters))
                data.write_byte(len(self.chapters[0].chapters[0].chapters))
                data.write_byte(len(self.chapters[0].chapters[0].chapters[0].stages))
                is_int = False
            else:
                data.write_int(len(self.chapters))
                data.write_int(len(self.chapters[0].chapters))
                data.write_int(len(self.chapters[0].chapters[0].chapters))
                is_int = True

        for chapter in self.chapters:
            chapter.write_selected_stage(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(len(self.chapters))
                data.write_int(len(self.chapters[0].chapters))
                data.write_int(len(self.chapters[0].chapters[0].chapters))
                is_int = True

        for chapter in self.chapters:
            chapter.write_clear_progress(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(len(self.chapters))
                data.write_int(len(self.chapters[0].chapters))
                data.write_int(len(self.chapters[0].chapters[0].chapters[0].stages))
                data.write_int(len(self.chapters[0].chapters[0].chapters))
                is_int = True

        for chapter in self.chapters:
            chapter.write_stages(data, is_int)

        if gv <= 34:
            is_int = True
        else:
            if 80099 < gv:
                is_int = False
            else:
                data.write_int(len(self.chapters))
                data.write_int(len(self.chapters[0].chapters))
                data.write_int(len(self.chapters[0].chapters[0].chapters))
                is_int = True

        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data, is_int)

    def read_legend_restrictions(
        self, data: io.data.Data, gv: "game_version.GameVersion"
    ):
        if gv < 20:
            return
        if gv < 33:
            total_map_types = 3
            total_subchapters = 150
        elif gv < 41:
            total_map_types = 4
            total_subchapters = 150
        else:
            total_map_types = data.read_int()
            total_subchapters = data.read_int()

        for chapter in self.chapters:
            chapter.read_legend_restrictions(data)

    def write_legend_restrictions(
        self, data: io.data.Data, gv: "game_version.GameVersion"
    ):
        if gv < 20:
            return
        if gv >= 41:
            data.write_int(len(self.chapters))
            data.write_int(len(self.chapters[0].chapters))

        for chapter in self.chapters:
            chapter.write_legend_restrictions(data)

    def read_dicts(self, data: io.data.Data):
        self.completed_one_level_in_chapter = data.read_int_int_dict()
        self.displayed_cleared_limit_text = data.read_int_bool_dict()
        self.event_start_dates = data.read_int_int_dict()
        self.stages_reward_claimed = data.read_int_list()

    def write_dicts(self, data: io.data.Data):
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
    def deserialize(data: dict[str, Any]) -> "EventChapters":
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
