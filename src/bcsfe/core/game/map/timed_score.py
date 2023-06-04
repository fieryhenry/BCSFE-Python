from typing import Any
from bcsfe.core import game_version, io


class Stage:
    def __init__(self, score: int):
        self.score = score

    @staticmethod
    def read(stream: io.data.Data) -> "Stage":
        return Stage(stream.read_int())

    def write(self, stream: io.data.Data):
        stream.write_int(self.score)

    def serialize(self) -> int:
        return self.score

    @staticmethod
    def deserialize(data: int) -> "Stage":
        return Stage(data)

    def __repr__(self) -> str:
        return f"Stage(score={self.score})"

    def __str__(self) -> str:
        return self.__repr__()


class SubChapter:
    def __init__(self, stages: list[Stage]):
        self.stages = stages

    @staticmethod
    def read(stream: io.data.Data, total_stages: int) -> "SubChapter":
        stages: list[Stage] = []
        for _ in range(total_stages):
            stages.append(Stage.read(stream))
        return SubChapter(stages)

    def write(self, stream: io.data.Data):
        for stage in self.stages:
            stage.write(stream)

    def serialize(self) -> list[int]:
        return [stage.serialize() for stage in self.stages]

    @staticmethod
    def deserialize(data: list[int]) -> "SubChapter":
        return SubChapter([Stage.deserialize(stage) for stage in data])

    def __repr__(self) -> str:
        return f"SubChapter(stages={self.stages})"

    def __str__(self) -> str:
        return self.__repr__()


class SubChapterStars:
    def __init__(self, sub_chapters: list[SubChapter]):
        self.sub_chapters = sub_chapters

    @staticmethod
    def read(
        stream: io.data.Data, total_stages: int, total_stars: int
    ) -> "SubChapterStars":
        sub_chapters: list[SubChapter] = []
        for _ in range(total_stars):
            sub_chapters.append(SubChapter.read(stream, total_stages))
        return SubChapterStars(sub_chapters)

    def write(self, stream: io.data.Data):
        for sub_chapter in self.sub_chapters:
            sub_chapter.write(stream)

    def serialize(self) -> list[list[int]]:
        return [sub_chapter.serialize() for sub_chapter in self.sub_chapters]

    @staticmethod
    def deserialize(data: list[list[int]]) -> "SubChapterStars":
        return SubChapterStars(
            [SubChapter.deserialize(sub_chapter) for sub_chapter in data]
        )

    def __repr__(self) -> str:
        return f"SubChapterStars(sub_chapters={self.sub_chapters})"

    def __str__(self) -> str:
        return self.__repr__()


class Chapters:
    def __init__(self, sub_chapters: list[SubChapterStars]):
        self.sub_chapters = sub_chapters

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "Chapters":
        if gv < 20:
            return Chapters([])
        if gv <= 33:
            total_subchapters = 50
            total_stages = 12
            total_stars = 3
        elif gv <= 34:
            total_subchapters = stream.read_int()
            total_stages = 12
            total_stars = 3
        else:
            total_subchapters = stream.read_int()
            total_stages = stream.read_int()
            total_stars = stream.read_int()
        sub_chapters: list[SubChapterStars] = []
        for _ in range(total_subchapters):
            sub_chapters.append(SubChapterStars.read(stream, total_stages, total_stars))
        return Chapters(sub_chapters)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv < 20:
            return
        if gv <= 33:
            pass
        elif gv <= 34:
            stream.write_int(len(self.sub_chapters))
        else:
            stream.write_int(len(self.sub_chapters))
            stream.write_int(len(self.sub_chapters[0].sub_chapters[0].stages))
            stream.write_int(len(self.sub_chapters[0].sub_chapters))
        for sub_chapter in self.sub_chapters:
            sub_chapter.write(stream)

    def serialize(self) -> list[list[list[int]]]:
        return [sub_chapter.serialize() for sub_chapter in self.sub_chapters]

    @staticmethod
    def deserialize(data: list[list[list[int]]]) -> "Chapters":
        return Chapters(
            [SubChapterStars.deserialize(sub_chapter) for sub_chapter in data]
        )

    def __repr__(self) -> str:
        return f"Chapters(sub_chapters={self.sub_chapters})"

    def __str__(self) -> str:
        return self.__repr__()
