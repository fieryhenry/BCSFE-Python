import helper

def edit_play_time(save_stats):
    play_time = save_stats["play_time"]
    
    hours = play_time["hh"]
    minutes = play_time["mm"]

    helper.coloured_text(f"You currently have a play time of: &{hours}& hours and &{minutes}& minutes")
    hours = helper.validate_int(helper.coloured_text(f"How many hours do you want to set?:", is_input=True))
    minutes = helper.validate_int(helper.coloured_text(f"How many minutes do you want to set?:", is_input=True))
    if hours == None or minutes == None:
        print("Please enter valid numbers")
        return save_stats
    play_time["hh"] = hours
    play_time["mm"] = minutes

    save_stats["play_time"] = play_time

    print("Successfully set play time")
    return save_stats
