from typing import Any
from bcsfe.core import io
from bcsfe.core.game.map import chapters


class Challenge:
    def __init__(self, chapters: chapters.Chapters):
        self.chapters = chapters

    @staticmethod
    def read(data: io.data.Data) -> "Challenge":
        ch = chapters.Chapters.read(data)
        return Challenge(ch)

    def write(self, data: io.data.Data):
        self.chapters.write(data)

    def read_scores(self, data: io.data.Data):
        total_scores = data.read_int()
        self.scores = [data.read_int() for _ in range(total_scores)]

    def write_scores(self, data: io.data.Data):
        data.write_int(len(self.scores))
        for score in self.scores:
            data.write_int(score)

    def read_popup(self, data: io.data.Data):
        self.shown_popup = data.read_bool()

    def write_popup(self, data: io.data.Data):
        data.write_bool(self.shown_popup)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "scores": self.scores,
            "shown_popup": self.shown_popup,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Challenge":
        return Challenge(
            chapters.Chapters.deserialize(data["chapters"]),
        )

    def __repr__(self):
        return f"Challenge({self.chapters})"

    def __str__(self):
        return self.__repr__()
