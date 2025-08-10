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

    def unclear_stage(self, index: int):
        self.clear_progress = min(self.clear_progress, index)
        self.stages[index].unclear_stage()
        return True

    @staticmethod
    def init(total_stages: int) -> Chapter:
        return Chapter(0, total_stages)

    @staticmethod
    def read_selected_stage(data: core.Data) -> Chapter:
        selected_stage = data.read_byte()
        return Chapter(selected_stage)

    def write_selected_stage(self, data: core.Data):
        data.write_byte(self.selected_stage)

    def read_clear_progress(self, data: core.Data):
        self.clear_progress = data.read_byte()

    def write_clear_progress(self, data: core.Data):
        data.write_byte(self.clear_progress)

    def read_stages(self, data: core.Data, total_stages: int):
        self.stages = [Stage.read(data) for _ in range(total_stages)]

    def write_stages(self, data: core.Data):
        for stage in self.stages:
            stage.write(data)

    def read_chapter_unlock_state(self, data: core.Data):
        self.chapter_unlock_state = data.read_byte()

    def write_chapter_unlock_state(self, data: core.Data):
        data.write_byte(self.chapter_unlock_state)

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
        chapter.stages = [
            Stage.deserialize(stage) for stage in data.get("stages", [])
        ]
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
    ) -> bool:
        finished = self.chapters[star].clear_stage(
            stage, clear_amount, overwrite_clear_progress
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
        chapters = [
            Chapter.read_selected_stage(data) for _ in range(total_stars)
        ]
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


class GauntletChapters:
    def __init__(self, chapters: list[ChaptersStars], unknown: list[int]):
        self.chapters = chapters
        self.unknown = unknown

    def clear_stage(
        self,
        map: int,
        star: int,
        stage: int,
        clear_amount: int = 1,
        overwrite_clear_progress: bool = False,
    ):
        finished = self.chapters[map].clear_stage(
            star, stage, clear_amount, overwrite_clear_progress
        )
        if finished and map + 1 < len(self.chapters):
            self.chapters[map + 1].chapters[0].chapter_unlock_state = 1

    def unclear_stage(self, map: int, star: int, stage: int):
        finished = self.chapters[map].unclear_stage(star, stage)
        if finished and map + 1 < len(self.chapters) and star == 0:
            for chapter in self.chapters[map + 1].chapters:
                chapter.chapter_unlock_state = 0

    @staticmethod
    def init() -> GauntletChapters:
        return GauntletChapters([], [])

    @staticmethod
    def read(data: core.Data) -> GauntletChapters:
        total_chapters = data.read_short()
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

        return GauntletChapters(chapters, unknown)

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
            chapter.write_selected_stage(data)

        for chapter in self.chapters:
            chapter.write_clear_progress(data)

        for chapter in self.chapters:
            chapter.write_stages(data)

        for chapter in self.chapters:
            chapter.write_chapter_unlock_state(data)

        for unknown in self.unknown:
            data.write_byte(unknown)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": [chapter.serialize() for chapter in self.chapters],
            "unknown": self.unknown,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> GauntletChapters:
        chapters = [
            ChaptersStars.deserialize(chapter)
            for chapter in data.get("chapters", [])
        ]
        return GauntletChapters(chapters, data.get("unknown", []))

    def __repr__(self):
        return f"Chapters({self.chapters}, {self.unknown})"

    def __str__(self):
        return self.__repr__()

    def get_total_stars(self, map: int) -> int:
        try:
            return len(self.chapters[map].chapters)
        except IndexError:
            return 0

    def get_total_stages(self, map: int, star: int) -> int:
        try:
            return len(self.chapters[map].chapters[star].stages)
        except IndexError:
            return 0

    @staticmethod
    def edit_gauntlets(save_file: core.SaveFile):
        gauntlets = save_file.gauntlets
        gauntlets.edit_chapters(save_file, "A")

    @staticmethod
    def edit_collab_gauntlets(save_file: core.SaveFile):
        gauntlets = save_file.collab_gauntlets
        gauntlets.edit_chapters(save_file, "CA")

    @staticmethod
    def edit_behemoth_culling(save_file: core.SaveFile):
        gauntlets = save_file.behemoth_culling
        gauntlets.edit_chapters(save_file, "Q")

    def edit_chapters(self, save_file: core.SaveFile, letter_code: str):
        edits.map.edit_chapters(save_file, self, letter_code)

    def unclear_rest(self, stages: list[int], stars: int, id: int):
        if not stages:
            return
        for star in range(stars, self.get_total_stars(id)):
            for stage in range(max(stages), self.get_total_stages(id, star)):
                self.chapters[id].chapters[star].stages[stage].clear_times = 0
                self.chapters[id].chapters[star].clear_progress = 0

    def set_total_stages(self, map: int, total_stages: int):
        for chapter in self.chapters[map].chapters:
            chapter.total_stages = total_stages
