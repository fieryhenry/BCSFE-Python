from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import edits


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times

    @staticmethod
    def init() -> Stage:
        return Stage(0)

    @staticmethod
    def read(data: core.Data) -> Stage:
        clear_times = data.read_int()
        return Stage(clear_times)

    def write(self, data: core.Data):
        data.write_int(self.clear_times)

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

    def clear_stage(self, clear_amount: int = 1, ensure_cleared_only: bool = False):
        if ensure_cleared_only:
            self.clear_times = self.clear_times or clear_amount
        else:
            self.clear_times = clear_amount

    def unclear_stage(self):
        self.clear_times = 0


class Chapter:
    def __init__(self, selected_stage: int, total_stages: int = 0):
        self.selected_stage = selected_stage
        self.clear_progress = 0
        self.stages: list[Stage] = [Stage.init() for _ in range(total_stages)]
        self.chapter_unlock_state = 0

        self.total_stages = 0

    def clear_stage(
        self,
        index: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
        ensure_cleared_only: bool = False,
    ) -> bool:
        if overwrite_clear_progress:
            self.clear_progress = index + 1
        else:
            self.clear_progress = max(self.clear_progress, index + 1)
        self.chapter_unlock_state = 3
        self.stages[index].clear_stage(clear_amount, ensure_cleared_only)
        if index == self.total_stages - 1:
            return True
        return False

    def unclear_stage(self, index: int):
        self.clear_progress = min(self.clear_progress, index)
        self.stages[index].unclear_stage()
        return True

    @staticmethod
    def init(total_stages: int) -> Chapter:
        return Chapter(0, total_stages)

    @staticmethod
    def read_selected_stage(data: core.Data) -> Chapter:
        selected_stage = data.read_int()
        return Chapter(selected_stage)

    def write_selected_stage(self, data: core.Data):
        data.write_int(self.selected_stage)

    def read_clear_progress(self, data: core.Data):
        self.clear_progress = data.read_int()

    def write_clear_progress(self, data: core.Data):
        data.write_int(self.clear_progress)

    def read_stages(self, data: core.Data, total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]

    def write_stages(self, data: core.Data):
        for stage in self.stages:
            stage.write(data)

    def read_chapter_unlock_state(self, data: core.Data):
        self.chapter_unlock_state = data.read_int()

    def write_chapter_unlock_state(self, data: core.Data):
        data.write_int(self.chapter_unlock_state)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "clear_progress": self.clear_progress,
            "stages": [stage.serialize() for stage in self.stages],
            "chapter_unlock_state": self.chapter_unlock_state,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Chapter:
        chapter = Chapter(data.get("selected_stage", 0))
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

    def clear_stage(
        self,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
        ensure_cleared_only: bool = False,
    ) -> bool:
        finished = self.chapters[star].clear_stage(
            stage, clear_amount, overwrite_clear_progress, ensure_cleared_only
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

    @staticmethod
    def init(total_stages: int, total_stars: int) -> ChaptersStars:
        chapters = [Chapter.init(total_stages) for _ in range(total_stars)]
        return ChaptersStars(chapters)

    @staticmethod
    def read_selected_stage(data: core.Data, total_stars: int) -> ChaptersStars:
        chapters = [Chapter.read_selected_stage(data) for _ in range(total_stars)]
        return ChaptersStars(chapters)

    def write_selected_stage(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_selected_stage(data)

    def read_clear_progress(self, data: core.Data):
        for chapter in self.chapters:
            chapter.read_clear_progress(data)

    def write_clear_progress(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_clear_progress(data)

    def read_stages(self, data: core.Data, total_stages: int):
        for _ in range(total_stages):
            for chapter in self.chapters:
                chapter.stages.append(Stage.read(data))

    def write_stages(self, data: core.Data):
        for i in range(len(self.chapters[0].stages)):
            for chapter in self.chapters:
                chapter.stages[i].write(data)

    def read_chapter_unlock_state(self, data: core.Data):
        for chapter in self.chapters:
            chapter.read_chapter_unlock_state(data)

    def write_chapter_unlock_state(self, data: core.Data):
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data)

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


class Chapters:
    def __init__(self, chapters: list[ChaptersStars]):
        self.chapters = chapters

    def get_total_stars(self, map: int) -> int:
        return len(self.chapters[map].chapters)

    def get_total_stages(self, map: int, star: int) -> int:
        return len(self.chapters[map].chapters[star].stages)

    def clear_stage(
        self,
        map: int,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
        ensure_cleared_only: bool = False,
    ) -> bool:
        finished = self.chapters[map].clear_stage(
            star, stage, clear_amount, overwrite_clear_progress, ensure_cleared_only
        )
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

        return finished

    def unclear_stage(self, map: int, star: int, stage: int) -> bool:
        finished = self.chapters[map].unclear_stage(star, stage)
        if finished and map + 1 < len(self.chapters) and star == 0:
            for chapter in self.chapters[map + 1].chapters:
                chapter.chapter_unlock_state = 0

        return finished

    @staticmethod
    def init() -> Chapters:
        return Chapters([])

    @staticmethod
    def read(data: core.Data, read_every_time: bool = True) -> Chapters:
        total_stages = 0
        total_chapters = 0
        total_stars = 0
        if read_every_time:
            total_chapters = data.read_int()
            total_stars = data.read_int()
        else:
            total_chapters = data.read_int()
            total_stages = data.read_int()
            total_stars = data.read_int()

        chapters = [
            ChaptersStars.read_selected_stage(data, total_stars)
            for _ in range(total_chapters)
        ]

        if read_every_time:
            total_chapters = data.read_int()
            total_stars = data.read_int()

        for chapter in chapters:
            chapter.read_clear_progress(data)

        if read_every_time:
            total_chapters = data.read_int()
            total_stages = data.read_int()
            total_stars = data.read_int()

        for chapter in chapters:
            chapter.read_stages(data, total_stages)

        if read_every_time:
            total_chapters = data.read_int()
            total_stars = data.read_int()

        for chapter in chapters:
            chapter.read_chapter_unlock_state(data)

        return Chapters(chapters)

    def get_lengths(self) -> tuple[int, int, int]:
        total_chapters = len(self.chapters)
        try:
            total_stages = len(self.chapters[0].chapters[0].stages)
        except IndexError:
            total_stages = 0

        try:
            total_stars = len(self.chapters[0].chapters)
        except IndexError:
            total_stars = 0
        return (total_chapters, total_stages, total_stars)

    def write(self, data: core.Data, write_every_time: bool = True):
        total_chapters, total_stages, total_stars = self.get_lengths()
        if write_every_time:
            data.write_int(total_chapters)
            data.write_int(total_stars)
        else:
            data.write_int(total_chapters)
            data.write_int(total_stages)
            data.write_int(total_stars)
        for chapter in self.chapters:
            chapter.write_selected_stage(data)

        if write_every_time:
            data.write_int(total_chapters)
            data.write_int(total_stars)
        for chapter in self.chapters:
            chapter.write_clear_progress(data)

        if write_every_time:
            data.write_int(total_chapters)
            data.write_int(total_stages)
            data.write_int(total_stars)
        for chapter in self.chapters:
            chapter.write_stages(data)

        if write_every_time:
            data.write_int(total_chapters)
            data.write_int(total_stars)
        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data)

    def serialize(self) -> list[list[dict[str, Any]]]:
        return [chapter.serialize() for chapter in self.chapters]

    @staticmethod
    def deserialize(data: list[list[dict[str, Any]]]) -> Chapters:
        chapters = [ChaptersStars.deserialize(chapter) for chapter in data]
        tower_chapters = Chapters(chapters)
        return tower_chapters

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return self.__repr__()

    def unclear_rest(self, stages: list[int], stars: int, id: int):
        if not stages:
            return
        for star in range(stars, self.get_total_stars(id)):
            for stage in range(max(stages), self.get_total_stages(id, star)):
                self.chapters[id].chapters[star].stages[stage].clear_times = 0
                self.chapters[id].chapters[star].clear_progress = 0

    def edit_chapters(
        self, save_file: core.SaveFile, letter_code: str, base_index: int
    ) -> dict[int, bool] | None:
        return edits.map.edit_chapters(
            save_file, self, letter_code, base_index=base_index
        )

    def set_total_stages(self, map: int, total_stages: int):
        for chapter in self.chapters[map].chapters:
            chapter.total_stages = total_stages
