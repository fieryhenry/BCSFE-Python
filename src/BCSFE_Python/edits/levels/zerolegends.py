"""Handler for editting zero legends"""
from typing import Any

from . import event_stages
from ... import user_input_handler

def count_chapters(save_stats) -> int:
    data1 = save_stats.get("zero_legends", {})
    count = len(data1)
    return count
    
def count_stages(data) -> int:
    data1 = data.get("stages", {})
    count = len(data1)
    return count
    
def set_zl(stage_data, ids, lengths):
    for stage_id in ids:
        chapter_index = int(stage_id - 1)
        chapter_stages_count = count_stages(stage_data[chapter_index]["stars"][0])
        stage_data[chapter_index]["stars"][0]["stages_cleared"] = chapter_stages_count #stage count
        stage_data[chapter_index]["stars"][0]["unlock_next"] = 3 #idk what this means, but when i cleared stages myself, value was 3.
        for i in range(0, (chapter_stages_count - 1)):
            stage_data[chapter_index]["stars"][0]["stages"][i] = 1 #how many you cleared this stage
            i += 1
    return stage_data

def edit_zl(save_stats: dict[str, Any]) -> dict[str, Any]:
    """Handler for editting zero legends"""
    stage_data = save_stats["zero_legends"]
    lengths = count_chapters(save_stats)
    ids = []
    ids = user_input_handler.get_range(
        user_input_handler.colored_input(
            "Enter stage ids (e.g &1& = Zero Field, &2& = The Edge of Spacetime)(You can enter &all& to get all, a range e.g &1&-&8&, or ids separate by spaces e.g &5 4 7&):"
        ),
        lengths,
    )
    save_stats["zero_legends"] = set_zl(stage_data, ids, lengths)
    print("Successfully set Zero Legend Chapters.")
    return save_stats
