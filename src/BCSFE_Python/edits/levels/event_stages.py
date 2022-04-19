from BCSFE_Python import helper

def stage_handler(stage_data, ids, offset, unlock_next=True):
    lengths = stage_data["Lengths"]

    individual = "1"
    if len(ids) > 1:
        individual = helper.coloured_text("Do you want to set the stars/crowns for each stage individually(&1&), or all at once(&2&):", is_input=True)
    first = True
    stars = None
    for id in ids:
        if individual == "2" and first:
            stars = helper.validate_int(helper.coloured_text(f"Enter the number of stars/cowns (max &{lengths['stars']}&):", is_input=True))
            if stars == None:
                print("Please enter a valid number")
                continue
            stars = helper.clamp(stars, 0, lengths['stars'])
            first = False
        elif individual == "1":
            stars = helper.validate_int(helper.coloured_text(f"Enter the number of stars/cowns for stage &{id}& (max &{lengths['stars']}&):", is_input=True))
            if stars == None:
                print("Please enter a valid number")
                continue
            stars = helper.clamp(stars, 0, lengths['stars'])

        id += offset

        stage_data_edit = stage_data
        stage_data_edit["Value"]["clear_progress"][id] = ([lengths["stages"]] * stars) + ([0] * (lengths["stars"] - stars))
        if unlock_next:
            stage_data_edit["Value"]["unlock_next"][id] = ([lengths["stars"]-1] * stars) + ([0] * (lengths["stars"] - stars))
        stage_data_edit["Value"]["clear_amount"][id] = ([[1]*lengths["stages"]] * stars) + ([[0]*lengths["stages"]] * (lengths["stars"] - stars))

    print("Successfully set stages")
    
    return stage_data_edit

def stories_of_legend(save_stats):
    stage_data = save_stats["event_stages"]

    ids = helper.get_range_input(helper.coloured_text("Enter stage ids (e.g &1& = legend begins, &2& = passion land)(You can enter &all& to get all, a range e.g &1&-&49&, or ids separate by spaces e.g &5 4 7&):", is_input=True), 49)
    offset = -1
    save_stats["event_stages"] = stage_handler(stage_data, ids, offset)
    return save_stats
def event_stages(save_stats):
    stage_data = save_stats["event_stages"]
    lengths = stage_data["Lengths"]

    ids = helper.get_range_input(helper.coloured_text("Enter stage ids (Look up &Event Release Order battle cats& to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), lengths["total"] - 400)
    offset = 400
    save_stats["event_stages"] = stage_handler(stage_data, ids, offset)
    return save_stats