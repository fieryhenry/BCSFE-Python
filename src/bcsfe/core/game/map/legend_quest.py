from typing import Any
from bcsfe.core import io


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times

    @staticmethod
    def read(data: io.data.Data) -> "Stage":
        clear_times = data.read_short()
        return Stage(clear_times)

    def write(self, data: io.data.Data):
        data.write_short(self.clear_times)

    def read_tries(self, data: io.data.Data):
        self.tries = data.read_short()

    def write_tries(self, data: io.data.Data):
        data.write_short(self.tries)

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_times": self.clear_times,
            "tries": self.tries,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Stage":
        stage = Stage(
            data.get("clear_times", 0),
        )
        stage.tries = data.get("tries", 0)
        return stage

    def __repr__(self):
        return f"Stage({self.clear_times}, {self.tries})"

    def __str__(self):
        return self.__repr__()


class Chapter:
    def __init__(self, selected_stage: int):
        self.selected_stage = selected_stage

    @staticmethod
    def read_selected_stage(data: io.data.Data) -> "Chapter":
        selected_stage = data.read_byte()
        return Chapter(selected_stage)

    def write_selected_stage(self, data: io.data.Data):
        data.write_byte(self.selected_stage)

    def read_clear_progress(self, data: io.data.Data):
        self.clear_progress = data.read_byte()

    def write_clear_progress(self, data: io.data.Data):
        data.write_byte(self.clear_progress)

    def read_stages(self, data: io.data.Data, total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]
        for stage in self.stages:
            stage.read_tries(data)

    def write_stages(self, data: io.data.Data):
        for stage in self.stages:
            stage.write(data)

        for stage in self.stages:
            stage.write_tries(data)

    def read_chapter_unlock_state(self, data: io.data.Data):
        self.chapter_unlock_state = data.read_byte()

    def write_chapter_unlock_state(self, data: io.data.Data):
        data.write_byte(self.chapter_unlock_state)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "clear_progress": self.clear_progress,
            "stages": [stage.serialize() for stage in self.stages],
            "chapter_unlock_state": self.chapter_unlock_state,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapter":
        chapter = Chapter(
            data.get("selected_stage", 0),
        )
        chapter.clear_progress = data.get("clear_progress", 0)
        chapter.stages = [Stage.deserialize(stage) for stage in data.get("stages", [])]
        chapter.chapter_unlock_state = data.get("chapter_unlock_state", 0)
        return chapter

    def __repr__(self):
        return f"Chapter({self.selected_stage}, {self.clear_progress}, {self.stages}, {self.chapter_unlock_state})"

    def __str__(self):
        return self.__repr__()


class ChaptersStars:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    @staticmethod
    def read_selected_stage(data: io.data.Data, total_stars: int) -> "ChaptersStars":
        chapters = [Chapter.read_selected_stage(data) for _ in range(total_stars)]
        return ChaptersStars(chapters)

    def write_selected_stage(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_selected_stage(data)

    def read_clear_progress(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.read_clear_progress(data)

    def write_clear_progress(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_clear_progress(data)

    def read_stages(self, data: io.data.Data, total_stages: int):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages)

    def write_stages(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_stages(data)

    def read_chapter_unlock_state(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data)

    def write_chapter_unlock_state(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "ChaptersStars":
        chapters = [Chapter.deserialize(chapter) for chapter in data]
        return ChaptersStars(chapters)

    def __repr__(self):
        return f"ChaptersStars({self.chapters})"

    def __str__(self):
        return self.__repr__()


class Chapters:
    def __init__(
        self, chapters: list[ChaptersStars], unknown: list[int], ids: list[int]
    ):
        self.chapters = chapters
        self.unknown = unknown
        self.ids = ids

    @staticmethod
    def read(data: io.data.Data) -> "Chapters":
        total_chapters = data.read_byte()
        total_stages = data.read_byte()
        total_stars = data.read_byte()

        chapters = [
            ChaptersStars.read_selected_stage(data, total_stars)
            for _ in range(total_chapters)
        ]

        for chapter in chapters:
            chapter.read_clear_progress(data)

        for chapter in chapters:
            chapter.read_stages(data, total_stages)

        for chapter in chapters:
            chapter.read_chapter_unlock_state(data)

        unknown = [data.read_byte() for _ in range(total_chapters)]
        ids = [data.read_int() for _ in range(total_stages)]

        return Chapters(chapters, unknown, ids)

    def write(self, data: io.data.Data):
        data.write_byte(len(self.chapters))
        data.write_byte(len(self.chapters[0].chapters[0].stages))
        data.write_byte(len(self.chapters[0].chapters))

        for chapter in self.chapters:
            chapter.write_selected_stage(data)

        for chapter in self.chapters:
            chapter.write_clear_progress(data)

        for chapter in self.chapters:
            chapter.write_stages(data)

        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data)

        for unknown in self.unknown:
            data.write_byte(unknown)

        for id in self.ids:
            data.write_int(id)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": [chapter.serialize() for chapter in self.chapters],
            "unknown": self.unknown,
            "ids": self.ids,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapters":
        chapters = [
            ChaptersStars.deserialize(chapter) for chapter in data.get("chapters", [])
        ]
        unknown = data.get("unknown", [])
        ids = data.get("ids", [])
        return Chapters(chapters, unknown, ids)

    def __repr__(self):
        return f"Chapters({self.chapters}, {self.unknown}, {self.ids})"

    def __str__(self):
        return self.__repr__()
