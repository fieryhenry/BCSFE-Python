"""Handler for editting meow medals"""
from enum import Enum
import json
from typing import Any, Optional

from ... import helper, user_input_handler, game_data_getter


def get_medal_names(is_jp: bool) -> Optional[list[str]]:
    """Get all medal names"""

    file_data = game_data_getter.get_file_latest("resLocal", "medalname.tsv", is_jp)
    if file_data is None:
        helper.error_text("Failed to get medal names")
        return None
    medal_names = file_data.decode("utf-8").splitlines()
    names: list[str] = []
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


def set_medals(medal_stats: dict[str, Any], ids: list[int]) -> dict[str, Any]:
    """Set the medal stats of a set of medals"""

    for medal_id in ids:
        if medal_id == 0:
            continue
        medal_id -= 1
        if medal_id not in medal_stats["medal_data_1"]:
            if medal_id not in medal_stats["medal_data_2"]:
                medal_stats["medal_data_1"].append(medal_id)
            medal_stats["medal_data_2"][medal_id] = 0
    return medal_stats


def remove_medals(medal_stats: dict[str, Any], ids: list[int]) -> dict[str, Any]:
    """Remove the medal stats of a set of medals"""

    for medal_id in ids:
        if medal_id == 0:
            continue
        medal_id -= 1
        if medal_id in medal_stats["medal_data_1"]:
            medal_stats["medal_data_1"].remove(medal_id)
        if medal_id in medal_stats["medal_data_2"]:
            medal_stats["medal_data_2"].pop(medal_id)
    return medal_stats


class BaseMapIds(Enum):
    """Base map IDs"""

    STORY_CHAPTERS = 3000
    OUTBREAKS_EOC = 20000
    OUTBREAKS_ITF = 21000
    OUTBREAKS_COTC = 22000
    FILIBUSTER = 23000
    LEGEND_STAGES = 0
    EVENT_STAGES = 1000
    TOWER_STAGES = 7000
    LEGEND_QUEST = 16000
    IDI_RE = 4026
    AKU_REALM = 4042
    GAUNTLETS = 24000


class ActionTypes(Enum):
    """Action types"""

    EARN_CENT = 0
    GAMATOTO_EXPLORE = 1
    CAT_BASE_WEAPONS = 2
    USER_RANK = 3
    RECRUIT_GAMATOTO_ASSISTANT = 4


class Medal:
    """Medal"""

    def __init__(self, medal_id: int, grade: int, line: int):
        self.medal_id = medal_id
        self.grade = grade
        self.line = line


class StageMedal(Medal):
    """Stage medal"""

    def __init__(
        self,
        medal_id: int,
        grade: int,
        line: int,
        maps: Optional[list[int]],
        condition: Optional[dict[str, Any]] = None,
        star: Optional[int] = None,
    ):
        super().__init__(medal_id, grade, line)
        self.maps = maps
        self.condition = condition
        self.star = star


class TreasureMedal(StageMedal):
    """Treasure medal"""

    def __init__(
        self,
        medal_id: int,
        grade: int,
        line: int,
        maps: Optional[list[int]],
        treasure: int,
        condition: Optional[dict[str, Any]] = None,
    ):
        super().__init__(medal_id, grade, line, maps, condition)
        self.treasure = treasure


class ActionMedal(Medal):
    """Action medal"""

    def __init__(self, medal_id: int, grade: int, line: int, action: ActionTypes):
        super().__init__(medal_id, grade, line)
        self.action = action


class CharacterMedal(StageMedal):
    """Character medal"""

    def __init__(
        self,
        medal_id: int,
        grade: int,
        line: int,
        maps: Optional[list[int]],
        chara: int,
        condition: Optional[dict[str, Any]] = None,
    ):
        super().__init__(medal_id, grade, line, maps, condition)
        self.chara = chara


class Medals:
    """Medals"""

    def __init__(
        self,
        treasures: list[TreasureMedal],
        characters: list[CharacterMedal],
        actions: list[ActionMedal],
        stages: list[StageMedal],
    ):
        self.treasures = treasures
        self.characters = characters
        self.actions = actions
        self.stages = stages


def get_medal_data(is_jp: bool) -> Optional[Medals]:
    """Get the medal data"""

    file_data = game_data_getter.get_file_latest("DataLocal", "medallist.json", is_jp)
    if file_data is None:
        helper.error_text("Failed to get medal data")
        return None
    medal_data = json.loads(file_data.decode("utf-8"))["iconID"]

    treasures: list[TreasureMedal] = []
    characters: list[CharacterMedal] = []
    actions: list[ActionMedal] = []
    stages: list[StageMedal] = []

    for i, medal in enumerate(medal_data):
        if "condition" not in medal:
            medal["condition"] = None
        if "treasure" in medal:
            treasures.append(
                TreasureMedal(
                    i,
                    medal["grade"],
                    medal["line"],
                    medal["map"],
                    medal["treasure"],
                    medal["condition"],
                )
            )
        elif "chara" in medal:
            characters.append(
                CharacterMedal(
                    i,
                    medal["grade"],
                    medal["line"],
                    None,
                    medal["chara"],
                    medal["condition"],
                )
            )
        elif "action" in medal:
            actions.append(
                ActionMedal(
                    i,
                    medal["grade"],
                    medal["line"],
                    ActionTypes(medal["action"]),
                )
            )
        else:
            if "star" not in medal:
                medal["star"] = None
            if "map" not in medal:
                medal["map"] = None
            stages.append(
                StageMedal(
                    i,
                    medal["grade"],
                    medal["line"],
                    medal["map"],
                    medal["condition"],
                    medal["star"],
                )
            )

    return Medals(treasures, characters, actions, stages)


def medals(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting meow medals"""

    medal_stats = save_stats["medals"]
    remove = (
        user_input_handler.colored_input(
            "Do you want to add or remove medals? (&a&/&r&):"
        )
        == "r"
    )

    names = get_medal_names(helper.check_data_is_jp(save_stats))
    if names is None:
        return save_stats
    helper.colored_list(names)

    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter medal ids (You can enter all to get &all&, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):"
        ),
        len(names) + 1,
    )
    if remove:
        medal_stats = remove_medals(medal_stats, ids)
    else:
        medal_stats = set_medals(medal_stats, ids)
    save_stats["medals"] = medal_stats
    print(f"Successfully {'gave' if not remove else 'removed'} medals")
    return save_stats
