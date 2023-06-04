from typing import Any
from bcsfe.core import game_version, io


class Outbreak:
    def __init__(self, cleared: bool):
        self.cleared = cleared

    @staticmethod
    def read(stream: io.data.Data) -> "Outbreak":
        cleared = stream.read_bool()
        return Outbreak(cleared)

    def write(self, stream: io.data.Data):
        stream.write_bool(self.cleared)

    def serialize(self) -> bool:
        return self.cleared

    @staticmethod
    def deserialize(data: bool) -> "Outbreak":
        return Outbreak(data)

    def __repr__(self) -> str:
        return f"Outbreak(cleared={self.cleared!r})"

    def __str__(self) -> str:
        return f"Outbreak(cleared={self.cleared!r})"


class Chapter:
    def __init__(self, outbreaks: dict[int, Outbreak]):
        self.outbreaks = outbreaks

    @staticmethod
    def read(stream: io.data.Data) -> "Chapter":
        total = stream.read_int()
        outbreaks: dict[int, Outbreak] = {}
        for _ in range(total):
            outbreak_id = stream.read_int()
            outbreak = Outbreak.read(stream)
            outbreaks[outbreak_id] = outbreak

        return Chapter(outbreaks)

    def write(self, stream: io.data.Data):
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
    def deserialize(data: dict[int, Any]) -> "Chapter":
        return Chapter(
            {
                outbreak_id: Outbreak.deserialize(outbreak_data)
                for outbreak_id, outbreak_data in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"Chapter(outbreaks={self.outbreaks!r})"

    def __str__(self) -> str:
        return f"Chapter(outbreaks={self.outbreaks!r})"


class Outbreaks:
    def __init__(self, chapters: dict[int, Chapter]):
        self.chapters = chapters

    @staticmethod
    def read_chapters(stream: io.data.Data) -> "Outbreaks":
        total = stream.read_int()
        chapters: dict[int, Chapter] = {}
        for _ in range(total):
            chapter_id = stream.read_int()
            chapter = Chapter.read(stream)
            chapters[chapter_id] = chapter

        return Outbreaks(chapters)

    def write_chapters(self, stream: io.data.Data):
        stream.write_int(len(self.chapters))
        for chapter_id, chapter in self.chapters.items():
            stream.write_int(chapter_id)
            chapter.write(stream)

    def read_2(self, stream: io.data.Data):
        self.zombie_event_remaining_time = stream.read_double()

    def write_2(self, stream: io.data.Data):
        stream.write_double(self.zombie_event_remaining_time)

    def read_current_outbreaks(
        self, stream: io.data.Data, gv: game_version.GameVersion
    ):
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
            chapter = Chapter.read(stream)
            current_outbreaks[chapter_id] = chapter

        self.current_outbreaks = current_outbreaks

    def write_current_outbreaks(
        self, stream: io.data.Data, gv: game_version.GameVersion
    ):
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
    def deserialize(data: dict[str, Any]) -> "Outbreaks":
        outbreaks = Outbreaks(
            {
                chapter_id: Chapter.deserialize(chapter_data)
                for chapter_id, chapter_data in data["chapters"].items()
            }
        )
        outbreaks.zombie_event_remaining_time = data["zombie_event_remaining_time"]
        outbreaks.current_outbreaks = {
            chapter_id: Chapter.deserialize(chapter_data)
            for chapter_id, chapter_data in data["current_outbreaks"].items()
        }

        return outbreaks

    def __repr__(self) -> str:
        return f"Outbreaks(chapters={self.chapters!r}, zombie_event_remaining_time={self.zombie_event_remaining_time!r}, current_outbreaks={self.current_outbreaks!r})"

    def __str__(self) -> str:
        return self.__repr__()
