from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator, color


class Outbreak:
    def __init__(self, cleared: bool):
        self.cleared = cleared

    @staticmethod
    def init() -> Outbreak:
        return Outbreak(False)

    @staticmethod
    def read(stream: core.Data) -> Outbreak:
        cleared = stream.read_bool()
        return Outbreak(cleared)

    def write(self, stream: core.Data):
        stream.write_bool(self.cleared)

    def serialize(self) -> bool:
        return self.cleared

    @staticmethod
    def deserialize(data: bool) -> Outbreak:
        return Outbreak(data)

    def __repr__(self) -> str:
        return f"Outbreak(cleared={self.cleared!r})"

    def __str__(self) -> str:
        return f"Outbreak(cleared={self.cleared!r})"


class Chapter:
    def __init__(self, id: int, outbreaks: dict[int, Outbreak]):
        self.id = id
        self.outbreaks = outbreaks

    def get_true_id(self) -> int:
        if self.id < 3:
            return self.id
        return self.id - 1

    @staticmethod
    def init(id: int) -> Chapter:
        return Chapter(id, {})

    @staticmethod
    def read(stream: core.Data, id: int) -> Chapter:
        total = stream.read_int()
        outbreaks: dict[int, Outbreak] = {}
        for _ in range(total):
            outbreak_id = stream.read_int()
            outbreak = Outbreak.read(stream)
            outbreaks[outbreak_id] = outbreak

        return Chapter(id, outbreaks)

    def write(self, stream: core.Data):
        stream.write_int(len(self.outbreaks))
        for outbreak_id, outbreak in self.outbreaks.items():
            stream.write_int(outbreak_id)
            outbreak.write(stream)

    def serialize(self) -> dict[int, Any]:
        return {
            outbreak_id: outbreak.serialize()
            for outbreak_id, outbreak in self.outbreaks.items()
        }

    @staticmethod
    def deserialize(data: dict[int, Any], id: int) -> Chapter:
        return Chapter(
            id,
            {
                outbreak_id: Outbreak.deserialize(outbreak_data)
                for outbreak_id, outbreak_data in data.items()
            },
        )

    def __repr__(self) -> str:
        return f"Chapter(id={self.id!r}, outbreaks={self.outbreaks!r})"

    def __str__(self) -> str:
        return self.__repr__()


class Outbreaks:
    def __init__(self, chapters: dict[int, Chapter]):
        self.chapters = chapters
        self.zombie_event_remaining_time = 0.0
        self.current_outbreaks: dict[int, Chapter] = {}

    @staticmethod
    def init() -> Outbreaks:
        return Outbreaks({})

    @staticmethod
    def read_chapters(stream: core.Data) -> Outbreaks:
        total = stream.read_int()
        chapters: dict[int, Chapter] = {}
        for _ in range(total):
            chapter_id = stream.read_int()
            chapter = Chapter.read(stream, chapter_id)
            chapters[chapter_id] = chapter

        return Outbreaks(chapters)

    def write_chapters(self, stream: core.Data):
        stream.write_int(len(self.chapters))
        for chapter_id, chapter in self.chapters.items():
            stream.write_int(chapter_id)
            chapter.write(stream)

    def read_2(self, stream: core.Data):
        self.zombie_event_remaining_time = stream.read_double()

    def write_2(self, stream: core.Data):
        stream.write_double(self.zombie_event_remaining_time)

    def read_current_outbreaks(self, stream: core.Data, gv: core.GameVersion):
        if gv <= 43:
            total_chapters = stream.read_int()
            for _ in range(total_chapters):
                stream.read_int()
                total_stage = stream.read_int()
                for _ in range(total_stage):
                    stream.read_int()
                    stream.read_bool()

        total = stream.read_int()
        current_outbreaks: dict[int, Chapter] = {}
        for _ in range(total):
            chapter_id = stream.read_int()
            chapter = Chapter.read(stream, chapter_id)
            current_outbreaks[chapter_id] = chapter

        self.current_outbreaks = current_outbreaks

    def write_current_outbreaks(self, stream: core.Data, gv: core.GameVersion):
        if gv <= 43:
            stream.write_int(0)
        stream.write_int(len(self.current_outbreaks))
        for chapter_id, chapter in self.current_outbreaks.items():
            stream.write_int(chapter_id)
            chapter.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": {
                chapter_id: chapter.serialize()
                for chapter_id, chapter in self.chapters.items()
            },
            "zombie_event_remaining_time": self.zombie_event_remaining_time,
            "current_outbreaks": {
                chapter_id: chapter.serialize()
                for chapter_id, chapter in self.current_outbreaks.items()
            },
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Outbreaks:
        outbreaks = Outbreaks(
            {
                chapter_id: Chapter.deserialize(chapter_data, chapter_id)
                for chapter_id, chapter_data in data.get("chapters", {}).items()
            }
        )
        outbreaks.zombie_event_remaining_time = data.get(
            "zombie_event_remaining_time", 0.0
        )
        outbreaks.current_outbreaks = {
            chapter_id: Chapter.deserialize(chapter_data, chapter_id)
            for chapter_id, chapter_data in data.get("current_outbreaks", {}).items()
        }

        return outbreaks

    def __repr__(self) -> str:
        return f"Outbreaks(chapters={self.chapters!r}, zombie_event_remaining_time={self.zombie_event_remaining_time!r}, current_outbreaks={self.current_outbreaks!r})"

    def __str__(self) -> str:
        return self.__repr__()

    def get_chapter_from_true_id(self, true_id: int) -> Chapter | None:
        if true_id < 3:
            return self.chapters.get(true_id)
        return self.chapters.get(true_id + 1)

    def get_current_chapter_from_true_id(self, true_id: int) -> Chapter | None:
        if true_id < 3:
            return self.current_outbreaks.get(true_id)
        return self.current_outbreaks.get(true_id + 1)

    def get_valid_chapters(self) -> list[Chapter]:
        new_chapters: list[Chapter] = []
        for chapter_id, chapter in self.chapters.items():
            if chapter_id < 9 and len(chapter.outbreaks) > 3:
                new_chapters.append(chapter)

        return new_chapters

    def clear_outbreak(self, chapter_id: int, stage_id: int, clear: bool):
        chapter = self.get_chapter_from_true_id(chapter_id)
        if chapter is not None:
            stage = chapter.outbreaks.get(stage_id)
            if stage is not None:
                stage.cleared = clear
        if clear:
            chapter = self.get_current_chapter_from_true_id(chapter_id)
            if chapter is not None:
                stage = chapter.outbreaks.get(stage_id)
                if stage is not None:
                    stage.cleared = False

    @staticmethod
    def edit_outbreaks(save_file: core.SaveFile):
        outbreaks = save_file.outbreaks
        chapters = outbreaks.get_valid_chapters()
        if not chapters:
            color.ColoredText.localize("no_valid_outbreaks")
            return

        options = ["clear", "unclear"]
        choice = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="clear_unclear_outbreaks", single_choice=True
        ).single_choice()
        if choice is None:
            return
        choice -= 1

        clear = choice == 0

        selected_ids = core.StoryChapters.select_story_chapters(
            save_file, [chapter.get_true_id() for chapter in chapters]
        )
        if not selected_ids:
            return

        choice = core.StoryChapters.get_per_chapter(selected_ids)
        if choice is None:
            return
        if choice == 0:
            for chapter_id in selected_ids:
                stages = core.StoryChapters.select_stages(save_file, chapter_id)
                if not stages:
                    continue
                for stage in stages:
                    outbreaks.clear_outbreak(chapter_id, stage, clear)
        else:
            stages = core.StoryChapters.select_stages(save_file, 0)
            if not stages:
                return
            for stage in stages:
                for chapter_id in selected_ids:
                    outbreaks.clear_outbreak(chapter_id, stage, clear)

        if clear:
            color.ColoredText.localize("clear_outbreaks_success")
        else:
            color.ColoredText.localize("unclear_outbreaks_success")
