import datetime
from BCSFE_Python import helper

def edit_play_time(save_stats):
    play_time = save_stats["play_time"]
    
    time_data = play_time.split(":")
    hours = int(time_data[0])
    minutes = int(time_data[1])
    seconds = int(time_data[2])

    helper.coloured_text(f"You currently have a play time of: &{hours}& hours and &{minutes}& minutes")
    hours = helper.validate_int(helper.coloured_text(f"How many hours do you want to set?:", is_input=True))
    minutes = helper.validate_int(helper.coloured_text(f"How many minutes do you want to set?:", is_input=True))
    if hours == None or minutes == None:
        print("Please enter valid numbers")
        return save_stats

    delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

    mm, ss = divmod(delta.total_seconds(), 60)
    hh, mm= divmod(mm, 60)

    save_stats["play_time"] = f"{round(hh)}:{str(round(mm)).zfill(2)}:{round(ss)}"

    print("Successfully set play time")
    return save_stats
