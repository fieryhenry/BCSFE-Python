from typing import Any
from bcsfe.core import io
from bcsfe.core.game.map import chapters


class Uncanny:
    def __init__(self, chapters: chapters.Chapters, unknown: list[int]):
        self.chapters = chapters
        self.unknown = unknown

    @staticmethod
    def read(data: io.data.Data) -> "Uncanny":
        ch = chapters.Chapters.read(data, read_every_time=False)
        unknown = data.read_int_list(length=len(ch.chapters))
        return Uncanny(ch, unknown)

    def write(self, data: io.data.Data):
        self.chapters.write(data, write_every_time=False)
        data.write_int_list(self.unknown, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "unknown": self.unknown,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Uncanny":
        return Uncanny(
            chapters.Chapters.deserialize(data["chapters"]),
            data["unknown"],
        )

    def __repr__(self):
        return f"Uncanny({self.chapters}, {self.unknown})"

    def __str__(self):
        return self.__repr__()
