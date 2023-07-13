from typing import Any
from bcsfe import core


class TowerChapters:
    def __init__(self, chapters: "core.Chapters"):
        self.chapters = chapters
        self.item_obtain_states: list[list[bool]] = []

    @staticmethod
    def init() -> "TowerChapters":
        return TowerChapters(core.Chapters.init())

    @staticmethod
    def read(data: "core.Data") -> "TowerChapters":
        ch = core.Chapters.read(data)
        return TowerChapters(ch)

    def write(self, data: "core.Data"):
        self.chapters.write(data)

    def read_item_obtain_states(self, data: "core.Data"):
        total_stars = data.read_int()
        total_stages = data.read_int()
        self.item_obtain_states: list[list[bool]] = []
        for _ in range(total_stars):
            self.item_obtain_states.append(data.read_bool_list(total_stages))

    def write_item_obtain_states(self, data: "core.Data"):
        data.write_int(len(self.item_obtain_states))
        try:
            data.write_int(len(self.item_obtain_states[0]))
        except IndexError:
            data.write_int(0)
        for item_obtain_state in self.item_obtain_states:
            data.write_bool_list(item_obtain_state, write_length=False)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "item_obtain_states": self.item_obtain_states,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "TowerChapters":
        tower = TowerChapters(
            core.Chapters.deserialize(data.get("chapters", {})),
        )
        tower.item_obtain_states = data.get("item_obtain_states", [])
        return tower

    def __repr__(self):
        return f"Tower({self.chapters}, {self.item_obtain_states})"

    def __str__(self):
        return self.__repr__()
