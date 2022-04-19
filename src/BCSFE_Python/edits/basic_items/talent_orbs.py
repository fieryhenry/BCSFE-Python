from BCSFE_Python import helper

def create_orb_list(attributes, effects, grades, incl_metal):
    orb_list = []
    for attribute in attributes:
        effects_trim = effects
        if attribute == "Metal" and incl_metal: effects_trim = [effects[1]]
        if attribute == "Metal" and not incl_metal: effects_trim = []
        for effect in effects_trim:
            for grade in grades:
                orb_list.append(f"{attribute} {grade} {effect}")
    return orb_list

def edit_talent_orbs(save_stats):
    attributes = ["Red", "Floating", "Black", "Metal", "Angel", "Alien", "Zombie"]#, "Relic", "Traitless"]
    effects = ["Attack", "Defense", "Strong", "Massive", "Resistant"]
    grades = ["D", "C", "B", "A", "S"]

    orb_list = create_orb_list(attributes, effects[0:2], grades, True)
    orb_list += create_orb_list(attributes, effects[2::], grades, False)

    talent_orbs = save_stats["talent_orbs"]
    print("You have:")
    for orb in talent_orbs:
        if talent_orbs[orb] > 0:
            helper.coloured_text(f"&{talent_orbs[orb]}& {orb_list[orb]} orbs")
    
    orbs_str = helper.coloured_text("Enter the name of the orb that you want. You can enter multiple orb names separated by &spaces& to edit multiple at once (e.g &angel a massive red d strong black b resistant&):", is_input=True).split(' ')
    length = len(orbs_str) // 3
    orbs_to_set = []
    for i in range(length):
        orb_name = " ".join(orbs_str[i*3:i*3+3]).lower()
        orb_name = orb_name.replace("angle", "angel").title()
        try:
            orbs_to_set.append(orb_list.index(orb_name))
        except ValueError:
            helper.coloured_text(f"Error orb &{orb_name}& does not exist")

    for orb_id in orbs_to_set:
        name = orb_list[orb_id]
        val = helper.validate_int(helper.coloured_text(f"What do you want to set the value of &{name}& to?:", is_input=True))
        if val == None:
            print("Error please enter a number")
            continue
        talent_orbs[orb_id] = val
    save_stats["talent_orbs"] = talent_orbs

    return save_stats
