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
    def edit_catamin_stages(save_file: core.SaveFile):
        choice = dialog_creator.ChoiceInput.from_reduced(
            ["change_clear_amount_catamin", "clear_unclear_stage_catamin"],
            dialog="catamin_stage_clear_q",
        ).single_choice()
        if choice is None:
            return None

        if choice == 1:
            names = core.MapNames(save_file, "B", base_index=14000)
            map_ids = core.EventChapters.select_map_names(names.map_names)
            if map_ids is None:
                return None
            if len(map_ids) >= 2:
                choice2 = dialog_creator.ChoiceInput.from_reduced(
                    ["individual", "all_at_once"], dialog="catamin_clear_amounts_q"
                ).single_choice()
                if choice2 is None:
                    return None
            else:
                choice2 = 1

            if choice2 == 2:
                clear_amount = dialog_creator.IntInput().get_input(
                    "enter_clear_amount_catamin", {}
                )[0]
                if clear_amount is None:
                    return None
                for map_id in map_ids:
                    save_file.event_stages.chapter_completion_count[14_000 + map_id] = (
                        clear_amount
                    )
            elif choice == 1:
                for map_id in map_ids:
                    name = names.map_names.get(map_id) or core.localize("unknown_map")
                    clear_amount = dialog_creator.IntInput().get_input(
                        "enter_clear_amount_catamin_map", {"name": name, "id": map_id}
                    )[0]
                    if clear_amount is None:
                        return None
                    save_file.event_stages.chapter_completion_count[14_000 + map_id] = (
                        clear_amount
                    )

            color.ColoredText.localize("catamin_stage_success")

        elif choice == 2:
            completed_chapters = save_file.catamin_stages.chapters.edit_chapters(
                save_file, "B", 14000
            )
            if completed_chapters is None:
                return None

            # TODO: maybe in the future ask if the user wants to modify the chapter clear amounts
