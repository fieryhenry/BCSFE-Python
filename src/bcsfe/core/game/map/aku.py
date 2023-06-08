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

    def serialize(self) -> int:
        return self.clear_times

    @staticmethod
    def deserialize(data: int) -> "Stage":
        return Stage(
            data,
        )

    def __repr__(self):
        return f"Stage({self.clear_times})"

    def __str__(self):
        return self.__repr__()


class Chapter:
    def __init__(self, clear_progress: int):
        self.clear_progress = clear_progress

    @staticmethod
    def read_clear_progress(data: io.data.Data):
        clear_progress = data.read_byte()
        return Chapter(clear_progress)

    def write_clear_progress(self, data: io.data.Data):
        data.write_byte(self.clear_progress)

    def read_stages(self, data: io.data.Data, total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]

    def write_stages(self, data: io.data.Data):
        for stage in self.stages:
            stage.write(data)

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_progress": self.clear_progress,
            "stages": [stage.serialize() for stage in self.stages],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapter":
        chapter = Chapter(data.get("clear_progress", 0))
        chapter.stages = [Stage.deserialize(stage) for stage in data.get("stages", [])]
        return chapter

    def __repr__(self):
        return f"Chapter({self.clear_progress}, {self.stages})"

    def __str__(self):
        return self.__repr__()


class ChaptersStars:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    @staticmethod
    def read_clear_progress(data: io.data.Data, total_stars: int):
        chapters = [Chapter.read_clear_progress(data) for _ in range(total_stars)]
        return ChaptersStars(chapters)

    def write_clear_progress(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_clear_progress(data)

    def read_stages(self, data: io.data.Data, total_stages: int):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages)

    def write_stages(self, data: io.data.Data):
        for chapter in self.chapters:
            chapter.write_stages(data)

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
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    @staticmethod
    def read(data: io.data.Data) -> "Chapters":
        total_chapters = data.read_short()
        total_stages = data.read_byte()
        total_stars = data.read_byte()

        chapters = [
            ChaptersStars.read_clear_progress(data, total_stars)
            for _ in range(total_chapters)
        ]

        for chapter in chapters:
            chapter.read_stages(data, total_stages)

        return Chapters(chapters)

    def write(self, data: io.data.Data):
        data.write_short(len(self.chapters))
        data.write_byte(len(self.chapters[0].chapters[0].stages))
        data.write_byte(len(self.chapters[0].chapters))

        for chapter in self.chapters:
            chapter.write_clear_progress(data)

        for chapter in self.chapters:
            chapter.write_stages(data)

    def serialize(self) -> list[list[dict[str, Any]]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[list[dict[str, Any]]]) -> "Chapters":
        chapters = [ChaptersStars.deserialize(chapter) for chapter in data]
        return Chapters(chapters)

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()
