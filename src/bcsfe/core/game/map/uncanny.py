from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


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
        uncanny.chapters.edit_chapters(save_file, "NA", 13000)

    @staticmethod
    def catamin_clear_count_individual(save_file: core.SaveFile, map_ids: list[int]):
        clear_amount = dialog_creator.int_input_key(
            "enter_clear_amount_catamin", dialog_creator.MaxValue.i32()
        )
        if clear_amount is None:
            return None
        for map_id in map_ids:
            save_file.event_stages.chapter_completion_count[14_000 + map_id] = (
                clear_amount
            )

    @staticmethod
    def catamin_clear_count_many(
        save_file: core.SaveFile, map_ids: list[int], names: core.MapNames
    ):
        for map_id in map_ids:
            name = names.map_names.get(map_id) or core.localize("unknown_map")
            clear_amount = dialog_creator.int_input_key(
                "enter_clear_amount_catamin_map",
                dialog_creator.MaxValue.i32(),
                name=name,
                id=map_id,
            )
            if clear_amount is None:
                return None
            save_file.event_stages.chapter_completion_count[14_000 + map_id] = (
                clear_amount
            )

    @staticmethod
    def change_clear_amount_catamin(save_file: core.SaveFile):
        names = core.MapNames(save_file, "B", base_index=14000)
        map_ids = core.EventChapters.select_map_names(names.map_names)
        if map_ids is None:
            return None
        if len(map_ids) >= 2:
            dialog_creator.single_select_key(
                dialog_creator.Actions[None]
                .new()
                .add_new_key(
                    "individual",
                    lambda _: UncannyChapters.catamin_clear_count_individual(
                        save_file, map_ids
                    ),
                )
                .add_new_key(
                    "all_at_once",
                    lambda _: UncannyChapters.catamin_clear_count_many(
                        save_file, map_ids, names
                    ),
                ),
                "catamin_clear_amounts_q",
            )
        else:
            UncannyChapters.catamin_clear_count_individual(save_file, map_ids)
        color.color_print_key("catamin_stage_success")

    @staticmethod
    def clear_unclear_catamin_stage(save_file: core.SaveFile):
        completed_chapters = save_file.catamin_stages.chapters.edit_chapters(
            save_file, "B", 14000
        )
        if completed_chapters is None:
            return None

    @staticmethod
    def edit_catamin_stages(save_file: core.SaveFile):
        dialog_creator.single_select_key(
            dialog_creator.Actions[None]
            .new()
            .add_new_key(
                "change_clear_amount_catamin",
                lambda _: UncannyChapters.change_clear_amount_catamin(save_file),
            )
            .add_new_key(
                "clear_unclear_stage_catamin",
                lambda _: UncannyChapters.clear_unclear_catamin_stage(save_file),
            ),
            "catamin_stage_clear_q",
        )
