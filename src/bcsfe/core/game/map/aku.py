from typing import Any
from bcsfe import core


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times

    @staticmethod
    def init() -> "Stage":
        return Stage(0)

    @staticmethod
    def read(data: "core.Data") -> "Stage":
        clear_times = data.read_short()
        return Stage(clear_times)

    def write(self, data: "core.Data"):
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
    def __init__(self, clear_progress: int, total_stages: int = 0):
        self.clear_progress = clear_progress
        self.stages: list[Stage] = [Stage.init() for _ in range(total_stages)]

    @staticmethod
    def init(total_stages: int) -> "Chapter":
        return Chapter(0, total_stages)

    @staticmethod
    def read_clear_progress(data: "core.Data"):
        clear_progress = data.read_byte()
        return Chapter(clear_progress)

    def write_clear_progress(self, data: "core.Data"):
        data.write_byte(self.clear_progress)

    def read_stages(self, data: "core.Data", total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]

    def write_stages(self, data: "core.Data"):
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
    def init(total_stages: int, total_stars: int) -> "ChaptersStars":
        return ChaptersStars([Chapter.init(total_stages) for _ in range(total_stars)])

    @staticmethod
    def read_clear_progress(data: "core.Data", total_stars: int):
        chapters = [Chapter.read_clear_progress(data) for _ in range(total_stars)]
        return ChaptersStars(chapters)

    def write_clear_progress(self, data: "core.Data"):
        for chapter in self.chapters:
            chapter.write_clear_progress(data)

    def read_stages(self, data: "core.Data", total_stages: int):
        for chapter in self.chapters:
            chapter.read_stages(data, total_stages)

    def write_stages(self, data: "core.Data"):
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


class AkuChapters:
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    @staticmethod
    def init() -> "AkuChapters":
        return AkuChapters([])

    @staticmethod
    def read(data: "core.Data") -> "AkuChapters":
        total_chapters = data.read_short()
        total_stages = data.read_byte()
        total_stars = data.read_byte()

        chapters = [
            ChaptersStars.read_clear_progress(data, total_stars)
            for _ in range(total_chapters)
        ]

        for chapter in chapters:
            chapter.read_stages(data, total_stages)

        return AkuChapters(chapters)

    def write(self, data: "core.Data"):
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
            chapter.write_clear_progress(data)

        for chapter in self.chapters:
            chapter.write_stages(data)

    def serialize(self) -> list[list[dict[str, Any]]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[list[dict[str, Any]]]) -> "AkuChapters":
        chapters = [ChaptersStars.deserialize(chapter) for chapter in data]
        return AkuChapters(chapters)

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()
