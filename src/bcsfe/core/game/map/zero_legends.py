from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import edits, color


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

    def clear_stage(self, clear_amount: int = 1):
        self.clear_times = clear_amount

    def unclear_stage(self):
        self.clear_times = 0


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

    @staticmethod
    def init() -> Chapter:
        return Chapter(0, 0, 0, [])

    @staticmethod
    def read(data: core.Data) -> Chapter:
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

    def write(self, data: core.Data):
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
    def deserialize(data: dict[str, Any]) -> Chapter:
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

    def unclear_stage(self, star: int, stage: int) -> bool:
        finished = self.chapters[star].unclear_stage(stage)
        if finished and star + 1 < len(self.chapters):
            for chapter in self.chapters[star + 1 :]:
                chapter.chapter_unlock_state = 0
        return finished

    @staticmethod
    def init() -> ChaptersStars:
        return ChaptersStars(0, [])

    @staticmethod
    def read(data: core.Data) -> ChaptersStars:
        unknown = data.read_byte()
        total_stars = data.read_byte()
        chapters = [Chapter.read(data) for _ in range(total_stars)]
        return ChaptersStars(
            unknown,
            chapters,
        )

    def write(self, data: core.Data):
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
    def deserialize(data: dict[str, Any]) -> ChaptersStars:
        return ChaptersStars(
            data.get("unknown", 0),
            [
                Chapter.deserialize(chapter)
                for chapter in data.get("chapters", [])
            ],
        )

    def __repr__(self):
        return f"ChaptersStars({self.unknown}, {self.chapters})"

    def __str__(self):
        return self.__repr__()


class ZeroLegendsChapters:
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    def clear_stage(
        self,
        map: int,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ):
        self.create(map)
        finished = self.chapters[map].clear_stage(
            star, stage, clear_amount, overwrite_clear_progress
        )
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

    def unclear_stage(self, map: int, star: int, stage: int):
        self.create(map)
        finished = self.chapters[map].unclear_stage(star, stage)
        if finished and map + 1 < len(self.chapters) and star == 0:
            for chapter in self.chapters[map + 1].chapters:
                chapter.chapter_unlock_state = 0

    @staticmethod
    def init() -> ZeroLegendsChapters:
        return ZeroLegendsChapters([])

    @staticmethod
    def read(data: core.Data) -> ZeroLegendsChapters:
        total_chapters = data.read_short()
        chapters = [ChaptersStars.read(data) for _ in range(total_chapters)]
        return ZeroLegendsChapters(
            chapters,
        )

    def write(self, data: core.Data):
        data.write_short(len(self.chapters))
        for chapter in self.chapters:
            chapter.write(data)

    def serialize(self) -> list[dict[str, Any]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> ZeroLegendsChapters:
        return ZeroLegendsChapters(
            [ChaptersStars.deserialize(chapter) for chapter in data],
        )

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()

    def get_total_stars(self, chapter_id: int) -> int:
        return len(self.chapters[chapter_id].chapters)

    def get_total_stages(self, chapter_id: int, star: int) -> int:
        return len(self.chapters[chapter_id].chapters[star].stages)

    def create(self, chapter_id: int):
        diff = chapter_id - len(self.chapters)

        if diff >= 0:
            for _ in range(diff + 1):
                stages = [Stage(0)] * self.get_total_stages(0, 0)
                chapters = [Chapter(0, 0, 0, stages)] * self.get_total_stars(0)
                chapters_stars = ChaptersStars(0, chapters)
                self.chapters.append(chapters_stars)

    @staticmethod
    def edit_zero_legends(save_file: core.SaveFile):
        zero_legends_chapters = save_file.zero_legends
        zero_legends_chapters.edit_chapters(save_file, "ND")

    def edit_chapters(self, save_file: core.SaveFile, letter_code: str):
        color.ColoredText.localize("zero_legends_warning")
        edits.map.edit_chapters(save_file, self, letter_code)

    def unclear_rest(self, stages: list[int], stars: int, id: int):
        if not stages:
            return
        for star in range(stars, self.get_total_stars(id)):
            for stage in range(max(stages), self.get_total_stages(id, star)):
                self.chapters[id].chapters[star].stages[stage].clear_times = 0
                self.chapters[id].chapters[star].clear_progress = 0

    def set_total_stages(self, map: int, total_stages: int):
        self.create(map)
        for chapter in self.chapters[map].chapters:
            chapter.total_stages = total_stages
