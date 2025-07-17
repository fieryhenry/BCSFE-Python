from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import dialog_creator


class Stage:
    def __init__(self, score: int):
        self.score = score

    @staticmethod
    def init() -> Stage:
        return Stage(0)

    @staticmethod
    def read(stream: core.Data) -> Stage:
        score = stream.read_int()
        return Stage(score)

    def write(self, stream: core.Data):
        stream.write_int(self.score)

    def serialize(self) -> int:
        return self.score

    @staticmethod
    def deserialize(data: int) -> Stage:
        return Stage(data)

    def __repr__(self) -> str:
        return f"Stage(score={self.score!r})"

    def __str__(self) -> str:
        return f"Stage(score={self.score!r})"


class Chapter:
    def __init__(self, stages: dict[int, Stage]):
        self.stages = stages

    def get_stage(self, stage_id: int) -> Stage:
        if stage_id not in self.stages:
            self.stages[stage_id] = Stage.init()
        return self.stages[stage_id]

    @staticmethod
    def init() -> Chapter:
        return Chapter({})

    @staticmethod
    def read(stream: core.Data) -> Chapter:
        total = stream.read_int()
        stages: dict[int, Stage] = {}
        for _ in range(total):
            stage_id = stream.read_int()
            stage = Stage.read(stream)
            stages[stage_id] = stage

        return Chapter(stages)

    def write(self, stream: core.Data):
        stream.write_int(len(self.stages))
        for stage_id, stage in self.stages.items():
            stream.write_int(stage_id)
            stage.write(stream)

    def serialize(self) -> dict[int, Any]:
        return {stage_id: stage.serialize() for stage_id, stage in self.stages.items()}

    @staticmethod
    def deserialize(data: dict[int, Any]) -> Chapter:
        return Chapter(
            {stage_id: Stage.deserialize(stage) for stage_id, stage in data.items()}
        )

    def __repr__(self) -> str:
        return f"Chapter(stages={self.stages!r})"

    def __str__(self) -> str:
        return f"Chapter(stages={self.stages!r})"


class Chapters:
    def __init__(self, chapters: dict[int, Chapter]):
        self.chapters = chapters

    def get_stage(self, chapter_id: int, stage_id: int) -> Stage:
        if chapter_id not in self.chapters:
            self.chapters[chapter_id] = Chapter.init()
        return self.chapters[chapter_id].get_stage(stage_id)

    @staticmethod
    def init() -> Chapters:
        return Chapters({})

    @staticmethod
    def read(stream: core.Data) -> Chapters:
        total = stream.read_int()
        chapters: dict[int, Chapter] = {}
        for _ in range(total):
            chapter_id = stream.read_int()
            chapter = Chapter.read(stream)
            chapters[chapter_id] = chapter

        return Chapters(chapters)

    def write(self, stream: core.Data):
        stream.write_int(len(self.chapters))
        for chapter_id, chapter in self.chapters.items():
            stream.write_int(chapter_id)
            chapter.write(stream)

    def serialize(self) -> dict[int, Any]:
        return {
            chapter_id: chapter.serialize()
            for chapter_id, chapter in self.chapters.items()
        }

    @staticmethod
    def deserialize(data: dict[int, Any]) -> Chapters:
        return Chapters(
            {
                chapter_id: Chapter.deserialize(chapter)
                for chapter_id, chapter in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"Chapters(chapters={self.chapters!r})"

    def __str__(self) -> str:
        return f"Chapters(chapters={self.chapters!r})"


class Ranking:
    def __init__(
        self,
        score: int,
        ranking: int,
        has_submitted: bool,
        has_completed: bool,
        has_seen_results: bool,
        start_date: int,
        end_date: int,
        event_number: int,
        should_show_rank_description: bool,
        should_show_start_message: bool,
        submit_error_flag: bool,
        other: str | None,
    ):
        self.score = score
        self.ranking = ranking
        self.has_submitted = has_submitted
        self.has_completed = has_completed
        self.has_seen_results = has_seen_results
        self.start_date = start_date
        self.end_date = end_date
        self.event_number = event_number
        self.should_show_rank_description = should_show_rank_description
        self.should_show_start_message = should_show_start_message
        self.submit_error_flag = submit_error_flag
        self.did_win_rewards = False
        self.other = other

    @staticmethod
    def init() -> Ranking:
        return Ranking(
            0,
            0,
            False,
            False,
            False,
            0,
            0,
            0,
            False,
            False,
            False,
            None,
        )

    @staticmethod
    def read(stream: core.Data, game_version: core.GameVersion) -> Ranking:
        score = stream.read_int()
        ranking = stream.read_int()
        has_submitted = stream.read_bool()
        has_completed = stream.read_bool()
        has_seen_results = stream.read_bool()
        start_date = stream.read_int()
        end_date = stream.read_int()
        event_number = stream.read_int()
        should_show_rank_description = stream.read_bool()
        should_show_start_message = stream.read_bool()
        submit_error_flag = stream.read_bool()

        if game_version >= 140500:
            # game seems to do more that just this, may break in the future
            other = stream.read_string()
        else:
            other = None
        return Ranking(
            score,
            ranking,
            has_submitted,
            has_completed,
            has_seen_results,
            start_date,
            end_date,
            event_number,
            should_show_rank_description,
            should_show_start_message,
            submit_error_flag,
            other,
        )

    def write(self, stream: core.Data, game_version: core.GameVersion):
        stream.write_int(self.score)
        stream.write_int(self.ranking)
        stream.write_bool(self.has_submitted)
        stream.write_bool(self.has_completed)
        stream.write_bool(self.has_seen_results)
        stream.write_int(self.start_date)
        stream.write_int(self.end_date)
        stream.write_int(self.event_number)
        stream.write_bool(self.should_show_rank_description)
        stream.write_bool(self.should_show_start_message)
        stream.write_bool(self.submit_error_flag)
        if game_version >= 140500:
            # game seems to do more that just this, may break in the future
            stream.write_string(self.other or "")

    def read_did_win_rewards(self, stream: core.Data):
        self.did_win_rewards = stream.read_bool()

    def write_did_win_rewards(self, stream: core.Data):
        stream.write_bool(self.did_win_rewards)

    def serialize(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "ranking": self.ranking,
            "has_submitted": self.has_submitted,
            "has_completed": self.has_completed,
            "has_seen_results": self.has_seen_results,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "event_number": self.event_number,
            "should_show_rank_description": self.should_show_rank_description,
            "should_show_start_message": self.should_show_start_message,
            "submit_error_flag": self.submit_error_flag,
            "did_win_rewards": self.did_win_rewards,
            "other": self.other,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Ranking:
        ranking = Ranking(
            data.get("score", 0),
            data.get("ranking", 0),
            data.get("has_submitted", False),
            data.get("has_completed", False),
            data.get("has_seen_results", False),
            data.get("start_date", 0),
            data.get("end_date", 0),
            data.get("event_number", 0),
            data.get("should_show_rank_description", False),
            data.get("should_show_start_message", False),
            data.get("submit_error_flag", False),
            data.get("other", None),
        )
        ranking.did_win_rewards = data.get("did_win_rewards", False)
        return ranking

    def __repr__(self) -> str:
        return (
            f"Ranking(score={self.score!r}, ranking={self.ranking!r}, "
            f"has_submitted={self.has_submitted!r}, has_completed={self.has_completed!r}, "
            f"has_seen_results={self.has_seen_results!r}, start_date={self.start_date!r}, "
            f"end_date={self.end_date!r}, event_number={self.event_number!r}, "
            f"should_show_rank_description={self.should_show_rank_description!r}, "
            f"should_show_start_message={self.should_show_start_message!r}, "
            f"submit_error_flag={self.submit_error_flag!r},"
            f"did_win_rewards={self.did_win_rewards!r}),"
            f"other={self.other!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


class Dojo:
    def __init__(self, chapters: Chapters):
        self.chapters = chapters
        self.item_lock_flags = False
        self.item_locks = [False] * 6
        self.ranking = Ranking.init()

    @staticmethod
    def init() -> Dojo:
        return Dojo(Chapters.init())

    @staticmethod
    def read_chapters(stream: core.Data) -> Dojo:
        chapters = Chapters.read(stream)
        return Dojo(chapters)

    def write_chapters(self, stream: core.Data):
        self.chapters.write(stream)

    def read_item_locks(self, stream: core.Data):
        self.item_lock_flags = stream.read_bool()
        self.item_locks = stream.read_bool_list(6)

    def write_item_locks(self, stream: core.Data):
        stream.write_bool(self.item_lock_flags)
        stream.write_bool_list(self.item_locks, write_length=False, length=6)

    def read_ranking(self, stream: core.Data, game_version: core.GameVersion):
        self.ranking = Ranking.read(stream, game_version)

    def write_ranking(self, stream: core.Data, game_version: core.GameVersion):
        self.ranking.write(stream, game_version)

    def serialize(self) -> dict[str, Any]:
        return {
            "chapters": self.chapters.serialize(),
            "item_locks": self.item_locks,
            "item_lock_flags": self.item_lock_flags,
            "ranking": self.ranking.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Dojo:
        chapters = Chapters.deserialize(data.get("chapters", {}))
        item_locks = data.get("item_locks", [])
        item_lock_flags = data.get("item_lock_flags", False)
        dojo = Dojo(chapters)
        dojo.item_locks = item_locks
        dojo.item_lock_flags = item_lock_flags
        dojo.ranking = Ranking.deserialize(data.get("ranking", {}))
        return dojo

    def __repr__(self) -> str:
        return f"Dojo(chapters={self.chapters!r}, item_locks={self.item_locks!r}, item_lock_flags={self.item_lock_flags!r}, ranking={self.ranking!r})"

    def __str__(self) -> str:
        return self.__repr__()

    def edit_score(self):
        stage = self.chapters.get_stage(0, 0)
        stage.score = dialog_creator.SingleEditor(
            "dojo_score",
            stage.score,
            None,
            localized_item=True,
        ).edit()


def edit_dojo_score(save_file: core.SaveFile):
    save_file.dojo.edit_score()
