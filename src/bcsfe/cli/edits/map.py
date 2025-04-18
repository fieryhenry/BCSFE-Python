from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color, dialog_creator
from typing import Union

ChaptersType = Union[
    "core.EventChapters",
    "core.GauntletChapters",
    "core.LegendQuestChapters",
    "core.ZeroLegendsChapters",
    "core.Chapters",
]


def unclear_stage(
    chapters: ChaptersType,
    map: int,
    star: int,
    stage: int,
    type: int | None = None,
):
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        chapters.unclear_stage(type, map, star, stage)
    else:
        chapters.unclear_stage(map, star, stage)


def clear_stage(
    chapters: ChaptersType,
    map: int,
    star: int,
    stage: int,
    clear_amount: int = 1,
    overwrite_clear_progress: bool = False,
    type: int | None = None,
):
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        chapters.clear_stage(
            type, map, star, stage, clear_amount, overwrite_clear_progress
        )
    else:
        chapters.clear_stage(
            map, star, stage, clear_amount, overwrite_clear_progress
        )


def unclear_rest(
    chapters: ChaptersType,
    stages: list[int],
    stars: int,
    id: int,
    type: int | None = None,
):
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        chapters.unclear_rest(stages, stars, id, type)
    else:
        chapters.unclear_rest(stages, stars, id)


def get_total_stars(chapters: ChaptersType, id: int, type: int | None = None):
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        total_stars = chapters.get_total_stars(type, id)
    else:
        total_stars = chapters.get_total_stars(id)

    return total_stars


def get_total_stages(
    chapters: ChaptersType, id: int, star: int, type: int | None = None
):
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        total_stars = chapters.get_total_stages(type, id, star)
    else:
        total_stars = chapters.get_total_stages(id, star)

    return total_stars


def edit_chapters(
    save_file: core.SaveFile,
    chapters: ChaptersType,
    letter_code: str,
    type: int | None = None,
):
    map_names = core.MapNames(save_file, letter_code)
    names = map_names.map_names

    choice = dialog_creator.ChoiceInput.from_reduced(
        ["clear_stages", "unclear_stages"],
        dialog="clear_unclear_q",
        single_choice=True,
    ).single_choice()
    if choice is None:
        return

    choice -= 1

    clear = choice == 0

    choice -= 1

    if clear:
        clear_txt = "clear"
        star_prompt = "custom_star_count_per_chapter"
    else:
        clear_txt = "unclear"
        star_prompt = "custom_star_count_per_chapter_unclear"

    map_choices = core.EventChapters.select_map_names(names)
    if not map_choices:
        return
    clear_type_choice = dialog_creator.ChoiceInput.from_reduced(
        [f"{clear_txt}_whole_chapters", f"{clear_txt}_specific_stages"],
        dialog=f"select_{clear_txt}_type",
        single_choice=True,
    ).single_choice()
    if clear_type_choice is None:
        return
    clear_type_choice -= 1

    if len(map_choices) > 1:
        stars_type_choice = dialog_creator.YesNoInput().get_input_once(
            "custom_star_count_per_chapter_yn"
        )
    else:
        stars_type_choice = False

    if stars_type_choice is None:
        return

    if clear:
        modify_clear_amounts = dialog_creator.YesNoInput().get_input_once(
            "modify_clear_amounts"
        )
    else:
        modify_clear_amounts = False

    if modify_clear_amounts is None:
        return

    clear_amount = 1
    clear_amount_type = -1
    if modify_clear_amounts:
        options = ["clear_amount_chapter", "clear_amount_all"]
        if clear_type_choice == 1:
            options.append("clear_amount_stages")
        clear_amount_type = dialog_creator.ChoiceInput.from_reduced(
            options, dialog="select_clear_amount_type", single_choice=True
        ).single_choice()
        if clear_amount_type is None:
            return
        clear_amount_type -= 1
        if clear_amount_type == 1:
            clear_amount = core.EventChapters.ask_clear_amount()
            if clear_amount is None:
                return

    if not stars_type_choice:
        stars = core.EventChapters.ask_stars(
            get_total_stars(chapters, 0, type),
            prompt=star_prompt,
        )
        if stars is None:
            return
    else:
        stars = 0

    for id in map_choices:
        map_name = names[id]
        stage_names = map_names.stage_names.get(id)
        stage_names = [
            stage_name
            for stage_name in stage_names or []
            if stage_name and stage_name != "＠"
        ]
        total_stages = len(stage_names)
        if isinstance(chapters, core.EventChapters):
            if type is None:
                raise ValueError("Type must be specified for EventChapters!")
            chapters.set_total_stages(id, type, total_stages)
        else:
            chapters.set_total_stages(id, total_stages)

        color.ColoredText.localize("current_sol_chapter", name=map_name, id=id)
        if stars_type_choice:
            stars = core.EventChapters.ask_stars(
                get_total_stars(chapters, id, type), prompt=star_prompt
            )
            if stars is None:
                return
        if clear_type_choice:
            stages = core.EventChapters.ask_stages(map_names, id)
            if stages is None:
                return
        else:
            stages = list(range(get_total_stages(chapters, id, 0, type)))

        if clear_amount_type == 0:
            clear_amount = core.EventChapters.ask_clear_amount()
            if clear_amount is None:
                return

        if not clear:
            start = stars - 1
            end = get_total_stars(chapters, id, type)
        else:
            start = 0
            end = stars
            unclear_rest(chapters, stages, stars, id, type)

        for star in range(start, end):
            if clear_amount_type == 2:
                color.ColoredText.localize("current_sol_star", star=star + 1)
            for stage in stages:
                if clear_amount_type == 2:
                    stage_name = stage_names[stage]
                    color.ColoredText.localize(
                        "current_sol_stage", name=stage_name, id=stage
                    )

                if clear_amount_type == 2:
                    clear_amount = core.EventChapters.ask_clear_amount()
                if clear_amount is None:
                    return
                if clear:
                    clear_stage(
                        chapters,
                        id,
                        star,
                        stage,
                        overwrite_clear_progress=True,
                        clear_amount=clear_amount,
                        type=type,
                    )
                else:
                    unclear_stage(chapters, id, star, stage, type)

    color.ColoredText.localize("map_chapters_edited")
