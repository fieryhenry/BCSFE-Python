"""Handler for editting meow medals"""

from ... import helper, user_input_handler


def get_medal_names() -> list:
    """Get all medal names"""

    medal_names = helper.read_file_string(
        helper.get_file("game_data/medals/medalname.tsv")
    ).splitlines()
    names = []
    for line in medal_names:
        line_split = line.split("\t")
        name = (
            line_split[0]
            .rstrip("\n")
            .replace("&", "and")
            .replace("â˜…", "")
            .lstrip(" ")
        )
        names.append(name)
    return names


def medals(save_stats: dict) -> dict:
    """Handler for editting meow medals"""

    medal_stats = save_stats["medals"]

    names = get_medal_names()
    helper.colored_list(names)

    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter medal ids (You can enter all to get &all&, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        len(names) + 1,
    )

    for medal_id in ids:
        if medal_id == 0:
            continue
        medal_id -= 1
        if medal_id not in medal_stats["medal_data_1"]:
            if medal_id not in medal_stats["medal_data_2"]:
                medal_stats["medal_data_1"].append(medal_id)
            medal_stats["medal_data_2"][medal_id] = 0
    save_stats["medals"] = medal_stats
    print("Successfully gave medals")
    return save_stats
