from BCSFE_Python import helper
from BCSFE_Python.edits.levels import event_stages

def edit_uncanny(save_stats):
    stage_data = save_stats["uncanny"]
    lengths = stage_data["Lengths"]

    ids = []
    ids = helper.get_range_input(helper.coloured_text("Enter stage ids (e.g &1& = a new legend, &2& = here be dragons)(You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):", is_input=True), lengths["total"])
    save_stats["uncanny"] = event_stages.stage_handler(stage_data, ids, -1)
    return save_stats