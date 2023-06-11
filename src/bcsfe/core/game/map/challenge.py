from typing import Any
from bcsfe.core import io
from bcsfe.core.game.map import chapters
from bcsfe.cli import dialog_creator


class Challenge:
    def __init__(self, chapters: chapters.Chapters):
        self.chapters = chapters
        self.scores: list[int] = []
        self.shown_popup: bool = False

    @staticmethod
    def init() -> "Challenge":
        return Challenge(chapters.Chapters.init())

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
        challenge = Challenge(
            chapters.Chapters.deserialize(data.get("chapters", {})),
        )
        challenge.scores = data.get("scores", [])
        challenge.shown_popup = data.get("shown_popup", False)
        return challenge

    def __repr__(self):
        return f"Challenge({self.chapters})"

    def __str__(self):
        return self.__repr__()

    def edit_score(self):
        if not self.scores:
            self.scores = [0]
        self.scores[0] = dialog_creator.SingleEditor(
            "challenge_score", self.scores[0], None, localized_item=True
        ).edit()
