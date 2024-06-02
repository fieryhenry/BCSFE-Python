from __future__ import annotations
from bcsfe import core


class Stage:
    def __init__(self, clear_amount: int):
        self.clear_amount = clear_amount

    @staticmethod
    def init() -> Stage:
        return Stage(0)

    @staticmethod
    def read(stream: core.Data) -> Stage:
        clear_amount = stream.read_int()
        return Stage(clear_amount)

    def write(self, stream: core.Data):
        stream.write_int(self.clear_amount)

    def serialize(self) -> int:
        return self.clear_amount

    @staticmethod
    def deserialize(data: int) -> Stage:
        return Stage(data)

    def __repr__(self) -> str:
        return f"Stage(clear_amount={self.clear_amount!r})"

    def __str__(self) -> str:
        return f"Stage(clear_amount={self.clear_amount!r})"


class Chapter:
    def __init__(self, stages: list[Stage]):
        self.stages = stages

    @staticmethod
    def init() -> Chapter:
        return Chapter([Stage.init() for _ in range(12)])

    @staticmethod
    def read(stream: core.Data) -> Chapter:
        total = 12
        stages: list[Stage] = []
        for _ in range(total):
            stages.append(Stage.read(stream))
        return Chapter(stages)

    def write(self, stream: core.Data):
        for stage in self.stages:
            stage.write(stream)

    def serialize(self) -> list[int]:
        return [stage.serialize() for stage in self.stages]

    @staticmethod
    def deserialize(data: list[int]) -> Chapter:
        return Chapter([Stage.deserialize(stage) for stage in data])

    def __repr__(self) -> str:
        return f"Chapter(stages={self.stages!r})"

    def __str__(self) -> str:
        return f"Chapter(stages={self.stages!r})"


class ExChapters:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    @staticmethod
    def init() -> ExChapters:
        return ExChapters([])

    @staticmethod
    def read(stream: core.Data) -> ExChapters:
        total = stream.read_int()
        chapters: list[Chapter] = []
        for _ in range(total):
            chapters.append(Chapter.read(stream))

        return ExChapters(chapters)

    def write(self, stream: core.Data):
        stream.write_int(len(self.chapters))
        for chapter in self.chapters:
            chapter.write(stream)

    def serialize(self) -> list[list[int]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[list[int]]) -> ExChapters:
        return ExChapters([Chapter.deserialize(chapter) for chapter in data])

    def __repr__(self) -> str:
        return f"Chapters(chapters={self.chapters!r})"

    def __str__(self) -> str:
        return f"Chapters(chapters={self.chapters!r})"
