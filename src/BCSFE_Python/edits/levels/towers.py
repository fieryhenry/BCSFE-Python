from BCSFE_Python import helper
from BCSFE_Python.edits.levels import event_stages

def edit_tower(save_stats):
    stage_data = save_stats["tower"]["progress"]
    stage_data = {"Value" : stage_data, "Lengths" : {"stars" : stage_data["stars"], "stages" : stage_data["stages"]}}

    ids = []
    ids = helper.get_range_input(helper.coloured_text("Enter tower ids (Look up &Event Release Order battle cats& and scroll past the &events& and &gauntlets& to find &tower& ids) (You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):", is_input=True), stage_data["Value"]["total"])
    save_stats["tower"]["progress"] = event_stages.stage_handler(stage_data, ids, 0, False)["Value"]
    save_stats["tower"]["progress"]["total"] = stage_data["Value"]["total"]
    save_stats["tower"]["progress"]["stars"] = stage_data["Lengths"]["stars"]
    save_stats["tower"]["progress"]["stages"] = stage_data["Lengths"]["stages"]
    return save_stats