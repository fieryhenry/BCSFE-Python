"""Handler for editing the aku realm"""


def edit_aku(save_stats: dict) -> dict:
    """Handler for editing the aku realm"""
    aku = save_stats["aku"]
    count = aku["Lengths"]["stages"]
    aku["Value"]["clear_amount"][0][0] = [1] * count
    save_stats["aku"] = aku
    print("Successfully cleared the aku realm")
    return save_stats
