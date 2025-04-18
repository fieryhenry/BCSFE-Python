from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times

    @staticmethod
    def init() -> Stage:
        return Stage(0)

    @staticmethod
    def read(data: core.Data) -> Stage:
        clear_times = data.read_short()
        return Stage(clear_times)

    def write(self, data: core.Data):
        data.write_short(self.clear_times)

    def serialize(self) -> int:
        return self.clear_times

    @staticmethod
    def deserialize(data: int) -> Stage:
        return Stage(
            data,
        )

    def __repr__(self):
        return f"Stage({self.clear_times})"

    def __str__(self):
        return self.__repr__()

    def clear_stage(self, clear_count: int = 1):
        self.clear_times = clear_count


class Chapter:
    def __init__(self, current_stage: int, total_stages: int = 0):
        self.current_stage = current_stage
        self.stages: list[Stage] = [Stage.init() for _ in range(total_stages)]

    @staticmethod
    def init(total_stages: int) -> Chapter:
        return Chapter(0, total_stages)

    @staticmethod
    def read_current_stage(data: core.Data):
        current_stage = data.read_byte()
        return Chapter(current_stage)

    def write_current_stage(self, data: core.Data):
        data.write_byte(self.current_stage)

    def read_stages(self, data: core.Data, total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]

    def write_stages(self, data: core.Data):
        for stage in self.stages:
            stage.write(data)

    def serialize(self) -> dict[str, Any]:
        return {
            "current_stage": self.current_stage,
            "stages": [stage.serialize() for stage in self.stages],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Chapter:
        chapter = Chapter(data.get("current_stage", 0))
        chapter.stages = [
            Stage.deserialize(stage) for stage in data.get("stages", [])
        ]
        return chapter

    def __repr__(self):
        return f"Chapter({self.current_stage}, {self.stages})"

    def __str__(self):
        return self.__repr__()


class ChaptersStars:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    @staticmethod
    def init(total_stages: int, total_stars: int) -> ChaptersStars:
        return ChaptersStars(
            [Chapter.init(total_stages) for _ in range(total_stars)]
        )

    @staticmethod
    def read_current_stage(data: core.Data, total_stars: int):
        chapters = [
            Chapter.read_current_stage(data) for _ in range(total_stars)
        ]
        return ChaptersStars(chapters)

    def write_current_stage(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_current_stage(data)

    def read_stages(self, data: core.Data, total_stages: int):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages)

    def write_stages(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_stages(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> ChaptersStars:
        chapters = [Chapter.deserialize(chapter) for chapter in data]
        return ChaptersStars(chapters)

    def __repr__(self):
        return f"ChaptersStars({self.chapters})"

    def __str__(self):
        return self.__repr__()


class AkuChapters:
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    @staticmethod
    def init() -> AkuChapters:
        return AkuChapters([])

    @staticmethod
    def read(data: core.Data) -> AkuChapters:
        total_chapters = data.read_short()
        total_stages = data.read_byte()
        total_stars = data.read_byte()

        chapters = [
            ChaptersStars.read_current_stage(data, total_stars)
            for _ in range(total_chapters)
        ]

        for chapter in chapters:
            chapter.read_stages(data, total_stages)

        return AkuChapters(chapters)

    def write(self, data: core.Data):
        data.write_short(len(self.chapters))
        try:
            data.write_byte(len(self.chapters[0].chapters[0].stages))
        except IndexError:
            data.write_byte(0)
        try:
            data.write_byte(len(self.chapters[0].chapters))
        except IndexError:
            data.write_byte(0)

        for chapter in self.chapters:
            chapter.write_current_stage(data)

        for chapter in self.chapters:
            chapter.write_stages(data)

    def serialize(self) -> list[list[dict[str, Any]]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[list[dict[str, Any]]]) -> AkuChapters:
        chapters = [ChaptersStars.deserialize(chapter) for chapter in data]
        return AkuChapters(chapters)

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def edit_aku_chapters(save_file: core.SaveFile):
        aku = save_file.aku
        chapter = aku.chapters[0].chapters[0]

        clear_progress = core.StoryChapters.get_selected_chapter_progress(
            max_stages=len(chapter.stages)
        )
        if clear_progress is None:
            return

        if clear_progress > 1:
            individual_clear_count = (
                core.StoryChapters.ask_if_individual_clear_counts()
            )
            if individual_clear_count is None:
                return
        else:
            individual_clear_count = True

        if individual_clear_count:
            stage_names = core.StageNames(save_file, "DM", 49).stage_names
            if stage_names is None:
                return
            for i, stage in enumerate(chapter.stages[:clear_progress]):
                stage_name = stage_names[i]
                color.ColoredText.localize(
                    "aku_current_stage", name=stage_name, id=i
                )
                clear_count = core.StoryChapters.ask_clear_count()
                if clear_count is None:
                    return
                stage.clear_stage(clear_count)
        else:
            clear_count = core.StoryChapters.ask_clear_count()
            if clear_count is None:
                return
            for stage in chapter.stages[:clear_progress]:
                stage.clear_stage(clear_count)

        for i in range(clear_progress, len(chapter.stages)):
            chapter.stages[i].clear_stage(clear_count=0)

        color.ColoredText.localize("aku_clear_success")
