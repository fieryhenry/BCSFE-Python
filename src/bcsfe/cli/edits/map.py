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


def get_total_maps(chapters: ChaptersType) -> int:
    if isinstance(chapters, core.EventChapters):
        return chapters.get_lengths()[1]
    return len(chapters.chapters)


def unclear_stage(
    chapters: ChaptersType,
    map: int,
    star: int,
    stage: int,
    type: int | None = None,
) -> bool:
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        return chapters.unclear_stage(type, map, star, stage)
    else:
        return chapters.unclear_stage(map, star, stage)


def clear_stage(
    chapters: ChaptersType,
    map: int,
    star: int,
    stage: int,
    clear_amount: int = 1,
    overwrite_clear_progress: bool = False,
    type: int | None = None,
    ensure_cleared_only: bool = False,
) -> bool:
    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")

        return chapters.clear_stage(
            type, map, star, stage, clear_amount, overwrite_clear_progress
        )
    else:
        return chapters.clear_stage(
            map,
            star,
            stage,
            clear_amount,
            overwrite_clear_progress,
            ensure_cleared_only=ensure_cleared_only,
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


def get_total_stars(
    map_option: core.MapOption,
    base_index: int,
    chapters: ChaptersType,
    id: int,
    type: int | None = None,
) -> int:

    max_stars = get_max_stars(chapters, id, type)

    map_option_stars = map_option.get_map(base_index + id)
    if map_option_stars is not None:
        return min(max_stars, map_option_stars.crown_count)
    return max_stars


def get_max_max_stars(
    map_option: core.MapOption,
    base_index: int,
    ids: list[int],
    chapters: ChaptersType,
    type: int | None = None,
) -> int:
    m = 0
    for id in ids:
        val = get_total_stars(map_option, base_index, chapters, id, type)
        if val > m:
            m = val

    return m


def get_max_stars(
    chapters: ChaptersType,
    id: int,
    type: int | None = None,
) -> int:

    if isinstance(chapters, core.EventChapters):
        if type is None:
            raise ValueError("Type must be specified for EventChapters!")
        max_stars = chapters.get_total_stars(type, id)
    else:
        max_stars = chapters.get_total_stars(id)

    return max_stars


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


def select_maps(
    save_file: core.SaveFile,
    chapters: ChaptersType,
    letter_code: str,
    base_index: int,
    no_r_prefix: bool = False,
) -> list[int] | None:
    map_names = core.MapNames(
        save_file, letter_code, no_r_prefix=no_r_prefix, base_index=base_index
    )
    names: dict[int, str | None] = {}
    for id, name in map_names.map_names.items():
        if id >= get_total_maps(chapters):
            continue
        names[id] = name

    return core.EventChapters.select_map_names(names)


def select_maps_stars(
    save_file: core.SaveFile,
    map_option: core.MapOption,
    chapters: ChaptersType,
    letter_code: str,
    base_index: int,
    type: int | None = None,
    no_r_prefix: bool = False,
) -> list[tuple[int, int]] | None:
    map_names = core.MapNames(
        save_file, letter_code, no_r_prefix=no_r_prefix, base_index=base_index
    )
    names: dict[int, str | None] = {}
    for id, name in map_names.map_names.items():
        if id >= get_total_maps(chapters):
            continue

        for star in range(get_total_stars(map_option, base_index, chapters, id, type)):
            names[id * 10 + star] = core.localize(
                "map_name_star", name=name, star=star + 1
            )

    ids = core.EventChapters.select_map_names(names)
    if ids is None:
        return None

    new_ids: list[tuple[int, int]] = []

    for id in ids:
        map_id = id // 10
        star_index = id % 10

        new_ids.append((map_id, star_index))

    return new_ids


def edit_chapters2_clear_count(
    save_file: core.SaveFile,
    chapters: ChaptersType,
    letter_code: str,
    base_index: int,
    type: int | None = None,
    no_r_prefix: bool = False,
):

    map_names = core.MapNames(
        save_file, letter_code, no_r_prefix=no_r_prefix, base_index=base_index
    )

    map_option = core.MapOption.from_save(save_file)
    if map_option is None:
        return None

    map_choices = select_maps_stars(
        save_file, map_option, chapters, letter_code, base_index, type, no_r_prefix
    )
    if map_choices is None:
        return None

    clear_all = edit_all_or_handle_ind(len(map_choices))
    if clear_all is None:
        return None

    if clear_all == 0:
        clear_count = core.EventChapters.ask_clear_amount()
        if clear_count is None:
            return None

        for local_map_id, star in map_choices:
            total_stages = get_total_stages(chapters, local_map_id, star, type)
            for stage in range(total_stages):
                clear_stage(chapters, local_map_id, star, stage, clear_count, type=type)
    else:
        for local_map_id, star in map_choices:
            print()
            core.EventChapters.print_current_chapter(
                core.localize(
                    "map_name_star",
                    star=star,
                    name=map_names.map_names.get(local_map_id),
                ),
                local_map_id,
            )
            clear_whole = dialog_creator.ChoiceInput.from_reduced(
                ["edit_whole_chapter", "edit_specific_stages"], dialog="edit_chapter_q"
            ).single_choice()
            if clear_whole is None:
                return None

            clear_whole -= 1

            if clear_whole == 0:
                clear_count = core.EventChapters.ask_clear_amount()
                if clear_count is None:
                    return None

                for stage in range(
                    get_total_stages(chapters, local_map_id, star, type)
                ):
                    clear_stage(
                        chapters, local_map_id, star, stage, clear_count, type=type
                    )
            else:
                stage_ids = core.EventChapters.ask_stages(map_names, local_map_id)

                if stage_ids is None:
                    return None

                all_selected_stages = dialog_creator.ChoiceInput.from_reduced(
                    ["each_stage_individually", "stage_all_at_once"],
                    dialog="set_clear_count_stage_q",
                ).single_choice()
                if all_selected_stages is None:
                    return None

                all_selected_stages -= 1

                stage_names = core.EventChapters.get_stage_names(
                    map_names, local_map_id
                )
                if stage_names is None:
                    stage_names = []
                if all_selected_stages == 0:
                    for stage in stage_ids:
                        print()
                        if stage < len(stage_names):
                            stage_name = stage_names[stage]
                        else:
                            stage_name = None
                        core.EventChapters.print_current_stage(stage_name, stage)
                        clear_count = core.EventChapters.ask_clear_amount()
                        if clear_count is None:
                            return None
                        clear_stage(
                            chapters, local_map_id, star, stage, clear_count, type=type
                        )
                else:
                    clear_count = core.EventChapters.ask_clear_amount()
                    if clear_count is None:
                        return None
                    for stage in stage_ids:
                        clear_stage(
                            chapters, local_map_id, star, stage, clear_count, type=type
                        )


def clear_all_or_handle_ind(map_choices_len: int) -> int | None:
    if map_choices_len <= 1:
        clear_all = 1
    else:
        clear_all = dialog_creator.ChoiceInput.from_reduced(
            ["clear_all", "handle_individually"], dialog="clear_chapters_q"
        ).single_choice()
        if clear_all is None:
            return None

        clear_all -= 1

    return clear_all


def unclear_all_or_handle_ind(map_choices_len: int) -> int | None:
    if map_choices_len <= 1:
        clear_all = 1
    else:
        clear_all = dialog_creator.ChoiceInput.from_reduced(
            ["unclear_all", "handle_individually"], dialog="unclear_chapters_q"
        ).single_choice()
        if clear_all is None:
            return None

        clear_all -= 1

    return clear_all


def edit_all_or_handle_ind(map_choices_len: int) -> int | None:
    if map_choices_len <= 1:
        clear_all = 1
    else:
        clear_all = dialog_creator.ChoiceInput.from_reduced(
            ["edit_map_all", "handle_individually"], dialog="edit_chapters_q_all"
        ).single_choice()
        if clear_all is None:
            return None

        clear_all -= 1

    return clear_all


def edit_chapters2_progress(
    save_file: core.SaveFile,
    chapters: ChaptersType,
    letter_code: str,
    base_index: int,
    type: int | None = None,
    no_r_prefix: bool = False,
    allow_unclear: bool = False,
):
    map_names = core.MapNames(
        save_file, letter_code, no_r_prefix=no_r_prefix, base_index=base_index
    )

    map_choices = select_maps(save_file, chapters, letter_code, base_index, no_r_prefix)
    if map_choices is None:
        return None

    clear_all = clear_all_or_handle_ind(len(map_choices))
    if clear_all is None:
        return None

    map_option = core.MapOption.from_save(save_file)
    if map_option is None:
        return None

    if clear_all == 0:
        max_stars = get_max_max_stars(
            map_option, base_index, map_choices, chapters, type
        )
        if allow_unclear:
            stars = core.EventChapters.ask_stars_unclear(max_stars, "max_stars")
        else:
            stars = core.EventChapters.ask_stars(max_stars, "max_stars")
        if stars is None:
            return None
        for local_map_id in map_choices:
            unclear_rest(
                chapters,
                [0],
                max(0, stars - 1),
                local_map_id,
                type,
            )
            for star in range(stars):
                total_stages = get_total_stages(chapters, local_map_id, star, type)
                for stage in range(total_stages):
                    clear_stage(
                        chapters,
                        local_map_id,
                        star,
                        stage,
                        type=type,
                        ensure_cleared_only=True,
                    )

        return map_choices

    for local_map_id in map_choices:
        name = map_names.map_names.get(local_map_id)
        core.EventChapters.print_current_chapter(name, local_map_id)
        clear_whole = dialog_creator.ChoiceInput.from_reduced(
            ["clear_whole_chapter", "clear_to_specific_stage"], dialog="clear_whole_q"
        ).single_choice()
        if clear_whole is None:
            return None

        clear_whole -= 1

        if clear_whole == 0:
            max_stars = get_total_stars(
                map_option, base_index, chapters, local_map_id, type
            )
            if allow_unclear:
                stars = core.EventChapters.ask_stars_unclear(max_stars)
            else:
                stars = core.EventChapters.ask_stars(max_stars)
            if stars is None:
                return None

            unclear_rest(
                chapters,
                [0],
                max(stars - 1, 0),
                local_map_id,
                type,
            )

            for star in range(stars):
                total_stages = get_total_stages(chapters, local_map_id, star, type)
                for stage in range(total_stages):
                    clear_stage(
                        chapters,
                        local_map_id,
                        star,
                        stage,
                        type=type,
                        ensure_cleared_only=True,
                    )

        else:
            stage_names = map_names.stage_names.get(local_map_id)
            stage_names = [
                stage_name
                for stage_name in stage_names or []
                if stage_name and stage_name != "＠"
            ]
            stage_id = core.EventChapters.ask_stages_stage_names_one(stage_names)
            if stage_id is None:
                return None

            max_stars = get_total_stars(
                map_option, base_index, chapters, local_map_id, type
            )

            if allow_unclear:
                stars = core.EventChapters.ask_stars_unclear(max_stars)
            else:
                stars = core.EventChapters.ask_stars(max_stars)
            if stars is None:
                return None

            unclear_rest(
                chapters, list(range(stage_id)), max(stars - 1, 0), local_map_id, type
            )

            for star in range(stars - 1):
                total_stages = get_total_stages(chapters, local_map_id, star, type)
                for stage in range(total_stages):
                    clear_stage(
                        chapters,
                        local_map_id,
                        star,
                        stage,
                        type=type,
                        ensure_cleared_only=True,
                    )

            for stage in range(stage_id + 1):
                clear_stage(
                    chapters,
                    local_map_id,
                    stars - 1,
                    stage,
                    type=type,
                    ensure_cleared_only=True,
                )


def edit_chapters(
    save_file: core.SaveFile,
    chapters: ChaptersType,
    letter_code: str,
    base_index: int,
    type: int | None = None,
    no_r_prefix: bool = False,
) -> dict[int, bool] | None:
    while True:
        choice = dialog_creator.ChoiceInput.from_reduced(
            [
                "edit_progress_clear",
                "edit_progress_unclear",
                "edit_clear_counts",
                "finish",
            ],
            dialog="edit_chapters_q",
        ).single_choice()
        if choice is None:
            return None
        choice -= 1

        if choice == 0:
            edit_chapters2_progress(
                save_file, chapters, letter_code, base_index, type, no_r_prefix
            )
        elif choice == 1:
            edit_chapters2_progress(
                save_file,
                chapters,
                letter_code,
                base_index,
                type,
                no_r_prefix,
                allow_unclear=True,
            )
        elif choice == 2:
            edit_chapters2_clear_count(
                save_file, chapters, letter_code, base_index, type, no_r_prefix
            )
        else:
            break
        color.ColoredText.localize("map_chapters_edited")
    color.ColoredText.localize("map_chapters_edited")

    return None
