from __future__ import annotations
from typing import Any
from bcsfe import core


class UncannyChapters:
    def __init__(self, chapters: core.Chapters, unknown: list[int]):
        self.chapters = chapters
        self.unknown = unknown

    @staticmethod
    def init() -> UncannyChapters:
        return UncannyChapters(core.Chapters.init(), [])

    @staticmethod
    def read(data: core.Data) -> UncannyChapters:
        ch = core.Chapters.read(data, read_every_time=False)
        unknown = data.read_int_list(length=len(ch.chapters))
        return UncannyChapters(ch, unknown)

    def write(self, data: core.Data):
        self.chapters.write(data, write_every_time=False)
        data.write_int_list(self.unknown, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "unknown": self.unknown,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> UncannyChapters:
        return UncannyChapters(
            core.Chapters.deserialize(data.get("chapters", {})),
            data.get("unknown", []),
        )

    def __repr__(self):
        return f"Uncanny({self.chapters}, {self.unknown})"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def edit_uncanny(save_file: core.SaveFile):
        uncanny = save_file.uncanny
        uncanny.chapters.edit_chapters(save_file, "NA")
