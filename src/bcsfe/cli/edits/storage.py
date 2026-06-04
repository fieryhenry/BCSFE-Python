from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color, dialog_creator
from bcsfe.cli.edits import cat_editor


def display_storage(save_file: core.SaveFile, storage: list[core.StorageItem]):
    color.color_print_key("current_storage_items")
    index = 0
    for item in storage:
        if item.item_type == 0:
            continue

        index += 1
        color.color_print(f"{index}. ", end="")
        display_item(item, save_file)

    if index == 0:
        color.color_print_key("storage_is_empty")

    available_slots = len(storage) - index

    color.color_print_key("available_storage", slots=available_slots)


def display_item(item: core.StorageItem, save_file: core.SaveFile):
    color.color_print(get_item_str(item, save_file))


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

    color.color_print_key("storage_success")


def add_cats(save_file: core.SaveFile):
    storage = save_file.cats.storage_items
    editor, cats = cat_editor.CatEditor.from_save_file(save_file)
    if editor is None:
        return

    new_cats: list[core.Cat] = []
    for cat in cats:
        names = cat.get_names_cls(save_file)
        if names is None or not names:
            name = core.localize("unknown")
        else:
            name = names[0]
        quantity = dialog_creator.int_input_key(
            "cat_quantity",
            default=1,
            _max=dialog_creator.MaxValue.i32().hide_max(),
            name=name,
            id=cat.id,
        )
        if quantity is None:
            return
        for _ in range(quantity):
            new_cats.append(cat)

    cats = new_cats

    space = get_storage_space(storage)
    if len(cats) > len(storage):
        color.color_print_key(
            "too_many_cats_selected", max=len(storage), current=len(cats)
        )
        return

    needs = len(cats) - space
    if needs > 0:
        color.color_print_key("need_x_more_space", needs=needs)
        return

    color.color_print_key("added_cats")
    for cat in cats:
        item = core.StorageItem.from_cat(cat.id)
        add_item(storage, item)
        display_item(item, save_file)


def add_special_skills(save_file: core.SaveFile):
    storage = save_file.cats.storage_items
    skill_names: list[str] = list(
        map(
            lambda sk: sk[1] or str(sk[0].id),
            core.core_data.get_gatya_item_buy(save_file).get_names_by_category(
                core.GatyaItemCategory.SPECIAL_SKILLS
            )
            or [],
        )
    )

    options = dialog_creator.multi_select_indexes_key(
        skill_names, dialog="select_special_skills"
    )

    if options is None:
        return

    items: list[core.StorageItem] = []

    for id in options:
        item = core.StorageItem.from_special_skill(id)

        quantity = dialog_creator.int_input_key(
            "skill_quantity",
            dialog_creator.MaxValue.i32().hide_max(),
            default=1,
            name=skill_names[id],
        )
        if quantity is None:
            return
        for _ in range(quantity):
            items.append(item)

    space = get_storage_space(storage)
    if len(options) > len(storage):
        color.color_print_key(
            "too_many_skills_selected", max=len(storage), current=len(options)
        )
        return

    needs = len(options) - space
    if needs > 0:
        color.color_print_key("need_x_more_space", needs=needs)
        return

    color.color_print_key("added_special_skills")
    for item in items:
        add_item(storage, item)
        display_item(item, save_file)


def remove_items(save_file: core.SaveFile):
    storage = save_file.cats.storage_items
    options2: list[str] = []
    for item in storage:
        if item.item_type == 0:
            continue
        options2.append(get_item_str(item, save_file))

    choices = dialog_creator.multi_select_indexes_key(options2, "select_item")
    if choices is None:
        return

    color.color_print_key("removed_items")
    index = 0
    for item in storage:
        if item.item_type == 0:
            continue

        if index in choices:
            display_item(item, save_file)
            item.item_type = 0
            item.item_id = 0

        index += 1


def edit_loop(save_file: core.SaveFile) -> bool | None:
    storage = save_file.cats.storage_items

    return dialog_creator.single_select_key(
        dialog_creator.Actions[bool]
        .new()
        .add_new_key(
            "display_storage",
            lambda _: core.consume(display_storage(save_file, storage), False),
        )
        .add_new_key(
            "clear_storage", lambda _: core.consume(clear_storage(storage), False)
        )
        .add_new_key("add_cats", lambda _: core.consume(add_cats(save_file), False))
        .add_new_key(
            "add_special_skills",
            lambda _: core.consume(add_special_skills(save_file), False),
        )
        .add_new_key(
            "remove_items", lambda _: core.consume(remove_items(save_file), False)
        )
        .add_new_key("finish", lambda _: True),
        "select_option",
    )
