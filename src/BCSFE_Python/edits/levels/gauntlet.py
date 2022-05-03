import helper
from edits.levels import event_stages

def edit_gauntlet(save_stats):
    stage_data = save_stats["gauntlets"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = helper.get_range_input(helper.coloured_text("Enter gauntlet ids (Look up &Event Release Order battle cats& and scroll past the &events& to find &gauntlet& ids) (You can enter &all& to get all, a range e.g 1-49, or ids separate by spaces e.g &5 4 7&):", is_input=True), lengths["total"])
    save_stats["gauntlets"] = event_stages.stage_handler(stage_data, ids, 0)
    return save_stats