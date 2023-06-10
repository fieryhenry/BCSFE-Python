from typing import Any
from bcsfe.core import io


class Stage:
    def __init__(self, clear_times: int):
        self.clear_times = clear_times
        self.treasure = 0
        self.itf_timed_score = 0

    @staticmethod
    def init() -> "Stage":
        return Stage(0)

    @staticmethod
    def read_clear_times(stream: io.data.Data) -> "Stage":
        return Stage(stream.read_int())

    def read_treasure(self, stream: io.data.Data):
        self.treasure = stream.read_int()

    def read_itf_timed_score(self, stream: io.data.Data):
        self.itf_timed_score = stream.read_int()

    def write_clear_times(self, stream: io.data.Data):
        stream.write_int(self.clear_times)

    def write_treasure(self, stream: io.data.Data):
        stream.write_int(self.treasure)

    def write_itf_timed_score(self, stream: io.data.Data):
        stream.write_int(self.itf_timed_score)

    def serialize(self) -> dict[str, Any]:
        return {
            "clear_times": self.clear_times,
            "treasure": self.treasure,
            "itf_timed_score": self.itf_timed_score,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Stage":
        stage = Stage(data.get("clear_times", 0))
        stage.treasure = data.get("treasure", 0)
        stage.itf_timed_score = data.get("itf_timed_score", 0)
        return stage

    def __repr__(self):
        return f"Stage({self.clear_times}, {self.treasure}, {self.itf_timed_score})"

    def __str__(self):
        return self.__repr__()


class Chapter:
    def __init__(self, selected_stage: int):
        self.selected_stage = selected_stage
        self.progress = 0
        self.stages = [Stage.init() for _ in range(51)]
        self.time_until_treasure_chance = 0
        self.treasure_chance_duration = 0
        self.treasure_chance_value = 0
        self.treasure_chance_stage_id = 0
        self.treasure_festival_type = 0

    @staticmethod
    def init() -> "Chapter":
        return Chapter(0)

    def get_valid_treasure_stages(self) -> list[Stage]:
        return self.stages[:49]

    @staticmethod
    def read_selected_stage(stream: io.data.Data) -> "Chapter":
        return Chapter(stream.read_int())

    def read_progress(self, stream: io.data.Data):
        self.progress = stream.read_int()

    def read_clear_times(self, stream: io.data.Data):
        total_stages = 51
        self.stages = [Stage.read_clear_times(stream) for _ in range(total_stages)]

    def read_treasure(self, stream: io.data.Data):
        for stage in self.get_valid_treasure_stages():
            stage.read_treasure(stream)

    def read_time_until_treasure_chance(self, stream: io.data.Data):
        self.time_until_treasure_chance = stream.read_int()

    def read_treasure_chance_duration(self, stream: io.data.Data):
        self.treasure_chance_duration = stream.read_int()

    def read_treasure_chance_value(self, stream: io.data.Data):
        self.treasure_chance_value = stream.read_int()

    def read_treasure_chance_stage_id(self, stream: io.data.Data):
        self.treasure_chance_stage_id = stream.read_int()

    def read_treasure_festival_type(self, stream: io.data.Data):
        self.treasure_festival_type = stream.read_int()

    def read_itf_timed_scores(self, stream: io.data.Data):
        for stage in self.stages:
            stage.read_itf_timed_score(stream)

    def write_selected_stage(self, stream: io.data.Data):
        stream.write_int(self.selected_stage)

    def write_progress(self, stream: io.data.Data):
        stream.write_int(self.progress)

    def write_clear_times(self, stream: io.data.Data):
        for stage in self.stages:
            stage.write_clear_times(stream)

    def write_treasure(self, stream: io.data.Data):
        for stage in self.get_valid_treasure_stages():
            stage.write_treasure(stream)

    def write_time_until_treasure_chance(self, stream: io.data.Data):
        stream.write_int(self.time_until_treasure_chance)

    def write_treasure_chance_duration(self, stream: io.data.Data):
        stream.write_int(self.treasure_chance_duration)

    def write_treasure_chance_value(self, stream: io.data.Data):
        stream.write_int(self.treasure_chance_value)

    def write_treasure_chance_stage_id(self, stream: io.data.Data):
        stream.write_int(self.treasure_chance_stage_id)

    def write_treasure_festival_type(self, stream: io.data.Data):
        stream.write_int(self.treasure_festival_type)

    def write_itf_timed_scores(self, stream: io.data.Data):
        for stage in self.stages:
            stage.write_itf_timed_score(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "selected_stage": self.selected_stage,
            "progress": self.progress,
            "stages": [stage.serialize() for stage in self.stages],
            "time_until_treasure_chance": self.time_until_treasure_chance,
            "treasure_chance_duration": self.treasure_chance_duration,
            "treasure_chance_value": self.treasure_chance_value,
            "treasure_chance_stage_id": self.treasure_chance_stage_id,
            "treasure_festival_type": self.treasure_festival_type,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapter":
        chapter = Chapter(data.get("selected_stage", 0))
        chapter.progress = data.get("progress", 0)
        chapter.stages = [Stage.deserialize(stage) for stage in data.get("stages", [])]
        chapter.time_until_treasure_chance = data.get("time_until_treasure_chance", 0)
        chapter.treasure_chance_duration = data.get("treasure_chance_duration", 0)
        chapter.treasure_chance_value = data.get("treasure_chance_value", 0)
        chapter.treasure_chance_stage_id = data.get("treasure_chance_stage_id", 0)
        chapter.treasure_festival_type = data.get("treasure_festival_type", 0)
        return chapter

    def __repr__(self):
        return f"Chapter({self.selected_stage}, {self.progress}, {self.stages}, {self.time_until_treasure_chance}, {self.treasure_chance_duration}, {self.treasure_chance_value}, {self.treasure_chance_stage_id}, {self.treasure_festival_type})"

    def __str__(self):
        return f"Chapter({self.selected_stage}, {self.progress}, {self.stages}, {self.time_until_treasure_chance}, {self.treasure_chance_duration}, {self.treasure_chance_value}, {self.treasure_chance_stage_id}, {self.treasure_festival_type})"


class Chapters:
    def __init__(self, chapters: list[Chapter]):
        self.chapters = chapters

    @staticmethod
    def init() -> "Chapters":
        chapters = [Chapter.init() for _ in range(10)]
        return Chapters(chapters)

    @staticmethod
    def read(stream: io.data.Data) -> "Chapters":
        total_chapters = 10
        chapters_l = [
            Chapter.read_selected_stage(stream) for _ in range(total_chapters)
        ]
        chapters = Chapters(chapters_l)
        for chapter in chapters.chapters:
            chapter.read_progress(stream)
        for chapter in chapters.chapters:
            chapter.read_clear_times(stream)
        for chapter in chapters.chapters:
            chapter.read_treasure(stream)
        return chapters

    def read_treasure_festival(self, stream: io.data.Data):
        for chapter in self.chapters:
            chapter.read_time_until_treasure_chance(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_duration(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_value(stream)
        for chapter in self.chapters:
            chapter.read_treasure_chance_stage_id(stream)
        for chapter in self.chapters:
            chapter.read_treasure_festival_type(stream)

    def write(self, stream: io.data.Data):
        for chapter in self.chapters:
            chapter.write_selected_stage(stream)
        for chapter in self.chapters:
            chapter.write_progress(stream)
        for chapter in self.chapters:
            chapter.write_clear_times(stream)
        for chapter in self.chapters:
            chapter.write_treasure(stream)

    def write_treasure_festival(self, stream: io.data.Data):
        for chapter in self.chapters:
            chapter.write_time_until_treasure_chance(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_duration(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_value(stream)
        for chapter in self.chapters:
            chapter.write_treasure_chance_stage_id(stream)
        for chapter in self.chapters:
            chapter.write_treasure_festival_type(stream)

    def read_itf_timed_scores(self, stream: io.data.Data):
        for i, chapter in enumerate(self.chapters):
            if i > 4 and i < 8:
                chapter.read_itf_timed_scores(stream)

    def write_itf_timed_scores(self, stream: io.data.Data):
        for i, chapter in enumerate(self.chapters):
            if i > 4 and i < 8:
                chapter.write_itf_timed_scores(stream)

    def serialize(self) -> list[dict[str, Any]]:
        chapters = [chapter.serialize() for chapter in self.chapters]
        return chapters

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "Chapters":
        chapters = Chapters([Chapter.deserialize(chapter) for chapter in data])
        return chapters

    def __repr__(self):
        return f"Chapters({self.chapters})"

    def __str__(self):
        return f"Chapters({self.chapters})"
