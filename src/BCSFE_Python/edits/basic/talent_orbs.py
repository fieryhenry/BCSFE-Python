"""Handler for editing talent orbs"""

from typing import Any

from ... import helper, user_input_handler

def edit_all_orbs(save_stats: dict[str, Any], orb_list: list[str]) -> dict[str, Any]:
    """Handler for editing all talent orbs"""

    val = user_input_handler.colored_input(
        "What do you want to set the value of all talent orbs to?:"
    )
    val = helper.check_int(val)
    if val is None:
        print("Error please enter a number")
        return save_stats

    for orb in orb_list:
        save_stats["talent_orbs"][orb_list.index(orb)] = val

    helper.colored_text(f"Set all talent orbs to &{val}&")
    return save_stats


def edit_talent_orbs(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editing talent orbs"""

    orb_list = get_talent_orbs_types()

    talent_orbs = save_stats["talent_orbs"]
    print("You have:")
    for orb in talent_orbs:
        if talent_orbs[orb] > 0:
            helper.colored_text(f"&{talent_orbs[orb]}& {orb_list[orb]} orbs")

    orbs_str = user_input_handler.colored_input(
        "Enter the name of the orb that you want. You can enter multiple orb names separated by &spaces& to edit multiple at once or you can enter &all& to select all talent orbs to edit (e.g &angel a massive red d strong black b resistant&):"
    ).split(" ")
    if orbs_str[0] == "all":
        return edit_all_orbs(save_stats, orb_list)
    length = len(orbs_str) // 3
    orbs_to_set: list[int] = []

    for i in range(length):
        orb_name = " ".join(orbs_str[i * 3 : i * 3 + 3]).lower()
        orb_name = orb_name.replace("angle", "angel").title()
        try:
            orbs_to_set.append(orb_list.index(orb_name))
        except ValueError:
            helper.colored_text(f"Error orb &{orb_name}& does not exist")

    for orb_id in orbs_to_set:
        name = orb_list[orb_id]
        val = helper.check_int(
            user_input_handler.colored_input(
                f"What do you want to set the value of &{name}& to?:"
            )
        )
        if val is None:
            print("Error please enter a number")
            continue
        talent_orbs[orb_id] = val
    save_stats["talent_orbs"] = talent_orbs

    return save_stats


ATTRIBUTES = [
    "Red",
    "Floating",
    "Black",
    "Metal",
    "Angel",
    "Alien",
    "Zombie",
]
EFFECTS = [
    "Attack",
    "Defense",
    "Strong",
    "Massive",
    "Resistant",
]
GRADES = [
    "D",
    "C",
    "B",
    "A",
    "S",
]


def create_orb_list(
    attributes: list[str], effects: list[str], grades: list[str], incl_metal: bool
) -> list[str]:
    """Create a list of all possible talent orbs"""

    orb_list: list[str] = []
    for attribute in attributes:
        effects_trim = effects

        if attribute == "Metal" and incl_metal:
            effects_trim = [effects[1]]
        if attribute == "Metal" and not incl_metal:
            effects_trim = []

        for effect in effects_trim:
            for grade in grades:
                orb_list.append(f"{attribute} {grade} {effect}")

    return orb_list


def get_talent_orbs_types() -> list[str]:
    """Get a list of all possible talent orbs"""

    orb_list = create_orb_list(ATTRIBUTES, EFFECTS[0:2], GRADES, True)
    orb_list += create_orb_list(ATTRIBUTES, EFFECTS[2:], GRADES, False)
    return orb_list
