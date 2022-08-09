from typing import Any

from ... import item, csv_handler, game_data_getter, helper


def get_fruit_names(is_jp: bool) -> list[str]:
    """Get the catfruit fruit names"""

    item_names = csv_handler.parse_csv(
        game_data_getter.get_file_latest("resLocal", "GatyaitemName.csv", is_jp).decode(
            "utf-8"
        ),
        delimeter=helper.get_text_splitter(is_jp),
    )
    fruit_ids = helper.parse_int_list_list(
        csv_handler.parse_csv(
            game_data_getter.get_file_latest("DataLocal", "Matatabi.tsv", is_jp).decode(
                "utf-8"
            ),
            delimeter="\t",
        )
    )[1:]
    fruit_names: list[str] = []
    for fruit in fruit_ids:
        fruit_names.append(item_names[fruit[0]][0])
    return fruit_names


def edit_catfruit(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing catruit"""

    max_cf = 128
    if save_stats["game_version"]["Value"] >= 110400:
        max_cf = None

    catfruit = item.create_item_group(
        names=get_fruit_names(helper.is_jp(save_stats)),
        values=save_stats["cat_fruit"],
        maxes=max_cf,
        edit_name="value",
        group_name="Catfruit",
    )
    catfruit.edit()
    save_stats["cat_fruit"] = catfruit.values
    return save_stats
