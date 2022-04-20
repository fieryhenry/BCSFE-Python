from BCSFE_Python import helper as helper_module

def get_gamatoto_helpers():
    f = open(helper_module.get_files_path("game_data/gamatoto/GamatotoExpedition_Members_name_en.csv"), "r").readlines()
    helpers = {}
    for line in f:
        line_data = line.split("|")
        if len(line_data) < 5: break

        id = line_data[0]
        rarity = int(line_data[1])
        type_str = line_data[4]
        helpers[id] = {"Rarity_id" : rarity, "Rarity_name" : type_str}
    return helpers

def generate_helpers(user_input, helper_data):
    final_helpers = []
    values = list(helper_data.values())
    for i in range(len(user_input)):
        for j in range(len(values)):
            if values[j]["Rarity_id"] == i:
                final_helpers += (list(range(j+1, j+1+user_input[i])))
                break
    return final_helpers

def edit_helpers(save_stats):
    helpers = save_stats["helpers"]
    
    helper_data = get_gamatoto_helpers()
    current_helpers = {}
    helper_count = {"Intern" : 0, "Lackey" : 0, "Underling" : 0, "Assistant" : 0, "Legend" : 0}
    for helper in helpers:
        if helper == 0xffffffff: break
        current_helpers[helper] = helper_data[str(helper)]
        helper_count[current_helpers[helper]["Rarity_name"]] += 1

    helpers_counts_input = helper_module.edit_items_list(list(helper_count.keys()), list(helper_count.values()), "Gamatoto Helpers", 10, "amount")

    final_helpers = generate_helpers(helpers_counts_input, helper_data)
    extra_ls = [0xffffffff] * (len(helpers) - len(final_helpers))
    final_helpers += extra_ls
    
    helpers = final_helpers
    save_stats["helpers"] = helpers
    return save_stats