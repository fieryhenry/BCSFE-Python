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
    def __init__(
        self,
        selected_stage: int,
        clear_progress: int,
        unlock_state: int,
        stages: list[Stage],
    ):
        self.selected_stage = selected_stage
        self.clear_progress = clear_progress
        self.unlock_state = unlock_state
        self.stages = stages

    @staticmethod
    def init() -> "Chapter":
        return Chapter(0, 0, 0, [])

    @staticmethod
    def read(data: "core.Data") -> "Chapter":
        selected_stage = data.read_byte()
        clear_progress = data.read_byte()
        unlock_state = data.read_byte()
        total_stages = data.read_short()
        stages = [Stage.read(data) for _ in range(total_stages)]
        return Chapter(
            selected_stage,
            clear_progress,
            unlock_state,
            stages,
        )

    def write(self, data: "core.Data"):
        data.write_byte(self.selected_stage)
        data.write_byte(self.clear_progress)
        data.write_byte(self.unlock_state)
        data.write_short(len(self.stages))
        for stage in self.stages:
            stage.write(data)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "clear_progress": self.clear_progress,
            "unlock_state": self.unlock_state,
            "stages": [stage.serialize() for stage in self.stages],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapter":
        return Chapter(
            data.get("selected_stage", 0),
            data.get("clear_progress", 0),
            data.get("unlock_state", 0),
            [Stage.deserialize(stage) for stage in data.get("stages", [])],
        )

    def __repr__(self):
        return f"Chapter({self.selected_stage}, {self.clear_progress}, {self.unlock_state}, {self.stages})"

    def __str__(self):
        return self.__repr__()


class ChaptersStars:
    def __init__(self, unknown: int, chapters: list[Chapter]):
        self.unknown = unknown
        self.chapters = chapters

    @staticmethod
    def init() -> "ChaptersStars":
        return ChaptersStars(0, [])

    @staticmethod
    def read(data: "core.Data") -> "ChaptersStars":
        unknown = data.read_byte()
        total_stars = data.read_byte()
        chapters = [Chapter.read(data) for _ in range(total_stars)]
        return ChaptersStars(
            unknown,
            chapters,
        )

    def write(self, data: "core.Data"):
        data.write_byte(self.unknown)
        data.write_byte(len(self.chapters))
        for chapter in self.chapters:
            chapter.write(data)

    def serialize(self) -> dict[str, Any]:
        return {
            "unknown": self.unknown,
            "chapters": [chapter.serialize() for chapter in self.chapters],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "ChaptersStars":
        return ChaptersStars(
            data.get("unknown", 0),
            [Chapter.deserialize(chapter) for chapter in data.get("chapters", [])],
        )

    def __repr__(self):
        return f"ChaptersStars({self.unknown}, {self.chapters})"

    def __str__(self):
        return self.__repr__()


class ZeroLegendsChapters:
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    @staticmethod
    def init() -> "ZeroLegendsChapters":
        return ZeroLegendsChapters([])

    @staticmethod
    def read(data: "core.Data") -> "ZeroLegendsChapters":
        total_chapters = data.read_short()
        chapters = [ChaptersStars.read(data) for _ in range(total_chapters)]
        return ZeroLegendsChapters(
            chapters,
        )

    def write(self, data: "core.Data"):
        data.write_short(len(self.chapters))
        for chapter in self.chapters:
            chapter.write(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "ZeroLegendsChapters":
        return ZeroLegendsChapters(
            [ChaptersStars.deserialize(chapter) for chapter in data],
        )

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()
