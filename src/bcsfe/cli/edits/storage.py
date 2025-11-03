from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color, dialog_creator
from bcsfe.cli.edits import cat_editor


def display_storage(save_file: core.SaveFile, storage: list[core.StorageItem]):
    color.ColoredText.localize("current_storage_items")
    index = 0
    for item in storage:
        if item.item_type == 0:
            continue

        index += 1
        color.ColoredText(f"{index}. ", end="")
        display_item(item, save_file)

    if index == 0:
        color.ColoredText.localize("storage_is_empty")

    available_slots = len(storage) - index

    color.ColoredText.localize("available_storage", slots=available_slots)


def display_item(item: core.StorageItem, save_file: core.SaveFile):
    color.ColoredText(get_item_str(item, save_file))


def get_item_str(item: core.StorageItem, save_file: core.SaveFile) -> str:
    if item.item_type == 1:
        cat_id = item.item_id
        names = core.Cat.get_names(cat_id, save_file)

        if not names:
            names = [str(cat_id)]

        return core.localize("cat", name=names[0], id=cat_id)
    elif item.item_type == 2:
        skill_id = item.item_id

        skill_names = (
            core.core_data.get_gatya_item_buy(save_file).get_names_by_category(
                core.GatyaItemCategory.SPECIAL_SKILLS
            )
            or []
        )

        if skill_id >= len(skill_names) or skill_id < 0:
            name = str(skill_id)
        else:
            name = skill_names[skill_id][1]

        return core.localize("special_skill", name=name, id=skill_id)
    elif item.item_type == 3:
        item_id = item.item_id

        name = core.core_data.get_gatya_item_names(save_file).get_name(item_id)
        if name is None:
            name = str(item_id)

        return core.localize("item", name=name, id=item_id)
    else:
        return core.localize(
            "unrecognised_storage_item", item_type=item.item_type, id=item.item_id
        )


def clear_storage(storage: list[core.StorageItem]):
    for item in storage:
        item.item_id = 0
        item.item_type = 0


def add_item(storage: list[core.StorageItem], item: core.StorageItem) -> bool:
    for citem in storage:
        if citem.item_type == 0:
            citem.item_type = item.item_type
            citem.item_id = item.item_id
            return True
    return False


def get_storage_space(storage: list[core.StorageItem]) -> int:
    space = 0

    for item in storage:
        if item.item_type == 0:
            space += 1
    return space


def edit_storage(save_file: core.SaveFile):
    display_storage(save_file, save_file.cats.storage_items)
    exit = False
    while not exit:
        exit = edit_loop(save_file)

    color.ColoredText.localize("storage_success")


def edit_loop(save_file: core.SaveFile) -> bool:
    storage = save_file.cats.storage_items

    options = [
        "display_storage",
        "clear_storage",
        "add_cats",
        "add_special_skills",
        "remove_items",
        "finish",
    ]

    choice = dialog_creator.ChoiceInput.from_reduced(
        options, dialog="select_option"
    ).single_choice()
    if choice is None:
        return False

    choice -= 1

    if choice == 0:
        display_storage(save_file, storage)
    if choice == 1:
        clear_storage(storage)
    elif choice == 2:
        editor, cats = cat_editor.CatEditor.from_save_file(save_file)
        if editor is None:
            return False

        space = get_storage_space(storage)
        if len(cats) > len(storage):
            color.ColoredText.localize(
                "too_many_cats_selected", max=len(storage), current=len(cats)
            )
            return False

        needs = len(cats) - space
        if needs > 0:
            color.ColoredText.localize("need_x_more_space", needs=needs)
            return False

        color.ColoredText.localize("added_cats")
        for cat in cats:
            item = core.StorageItem.from_cat(cat.id)
            add_item(storage, item)
            display_item(item, save_file)
    elif choice == 3:

        skill_names: list[str] = list(
            map(
                lambda sk: sk[1] or str(sk[0].id),
                core.core_data.get_gatya_item_buy(save_file).get_names_by_category(
                    core.GatyaItemCategory.SPECIAL_SKILLS
                )
                or [],
            )
        )

        options, _ = dialog_creator.ChoiceInput.from_reduced(
            skill_names, localize_options=False, dialog="select_special_skills"
        ).multiple_choice(False)

        if options is None:
            return False

        space = get_storage_space(storage)
        if len(options) > len(storage):
            color.ColoredText.localize(
                "too_many_skills_selected", max=len(storage), current=len(options)
            )
            return False

        needs = len(options) - space
        if needs > 0:
            color.ColoredText.localize("need_x_more_space", needs=needs)
            return False

        color.ColoredText.localize("added_special_skills")
        for choice in options:
            item = core.StorageItem.from_special_skill(choice)
            add_item(storage, item)
            display_item(item, save_file)

    elif choice == 4:
        options2: list[str] = []
        for item in storage:
            if item.item_type == 0:
                continue
            options2.append(get_item_str(item, save_file))

        choices, _ = dialog_creator.ChoiceInput.from_reduced(
            options2, localize_options=False
        ).multiple_choice(False)
        if choices is None:
            return False

        color.ColoredText.localize("removed_items")
        index = 0
        for item in storage:
            if item.item_type == 0:
                continue

            if index in choices:
                display_item(item, save_file)
                item.item_type = 0
                item.item_id = 0

            index += 1

    elif choice == 5:
        return True

    return False
