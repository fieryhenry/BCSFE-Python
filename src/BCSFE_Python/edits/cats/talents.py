import helper

def get_talent_data():
    talent_data_raw = open(helper.get_files_path("game_data/talents/SkillAcquisition.csv"), "r").readlines()
    talent_names = open(helper.get_files_path("game_data/talents/SkillDescriptions.csv"), "r").readlines()

    columns = talent_data_raw[0].split(",")
    talent_data = {}

    for cat_talent_data in talent_data_raw[1:]:
        data = cat_talent_data.split(",")
        cat_data_dict = {}

        if len(columns) < 5: continue

        for i in range(1, len(columns)):
            column = columns[i]

            if column.startswith("textID"):
                filter = "<br>"
                name = talent_names[int(data[i])].split("|")[1]
                if filter in name:
                    index = name.index(filter)
                    name = name[:index]
                cat_data_dict[column] = name
            else:
                cat_data_dict[column] = data[i]
        talent_data[int(data[0])] = cat_data_dict
    return talent_data
         

def find_order(cat_talents, cat_talent_data):
    letters = ["A", "B", "C", "D", "E", "F"]
    letter_order = []

    for i in range(len(cat_talents)):
        if i == 0: continue
        talent_id = cat_talents[i]["id"]
        for letter in letters:
            ability_id = int(cat_talent_data[f"abilityID_{letter}"])
            if ability_id == talent_id:
                letter_order.append(letter)
    return letter_order


def get_cat_talents(cat_talents, cat_talent_data):
    data = {}
    letter_order = find_order(cat_talents, cat_talent_data)
    for i in range(len(cat_talents) - 1):
        cat_data = {}
        cat_data["name"] = cat_talent_data[f"textID_{letter_order[i]}"].strip("\n")
        cat_data["max"] = int(cat_talent_data[f"MAXLv_{letter_order[i]}"])
        if cat_data["max"] == 0: cat_data["max"] = 1
        data[i] = cat_data
    return data


def edit_talents(save_stats):
    length = len(save_stats["cats"])
    talents = save_stats["talents"]
    ids = helper.get_range_input(helper.coloured_text("Enter cat ids (Look up cro battle cats to find ids)(You can enter &all& to get all, a range e.g &1&-&50&, or ids separate by spaces e.g &5 4 7&):", is_input=True), length)
    individual = "1"
    if len(ids) > 1:
        individual = helper.coloured_text("Do you want to set the talents for each cat individually(&1&), or max them all at once(&2&):", is_input=True)
    
    talent_data = get_talent_data()
    cat_talents_levels = []
    for cat_id in ids:
        if cat_id not in talents or cat_id not in talent_data:
            if len(ids) < 20:
                print(f"Error cat {cat_id} does not have any talents")
            continue
        if individual == "2":
            cat_talent_data = talent_data[cat_id]
            cat_talents = talents[cat_id]
            cat_talent_data_formatted = get_cat_talents(cat_talents, cat_talent_data)
            names = []
            maxes = []
            cat_talents_levels = []
            for i in range(len(cat_talent_data_formatted)):
                max_val = cat_talent_data_formatted[i]["max"]
                cat_talents_levels.append(max_val)

        elif individual == "1":
            cat_talent_data = talent_data[cat_id]
            cat_talents = talents[cat_id]
            cat_talent_data_formatted = get_cat_talents(cat_talents, cat_talent_data)
            names = []
            cat_talents_levels = []
            maxes = []
            for i in range(len(cat_talent_data_formatted)):
                names.append(cat_talent_data_formatted[i]['name'])
                cat_talents_levels.append(cat_talents[i+1]["level"])
                maxes.append(cat_talent_data_formatted[i]["max"])

            cat_talents_levels = helper.edit_array_user(names, cat_talents_levels, maxes, "talents", item_name="cat")
            
        for i in range(len(cat_talents_levels)):
            cat_talents[i+1]["level"] = cat_talents_levels[i]
        talents[cat_id] = cat_talents
        save_stats["talents"] = talents
    return save_stats