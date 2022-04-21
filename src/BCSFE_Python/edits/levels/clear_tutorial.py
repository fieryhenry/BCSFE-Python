def clear_tutorial(save_stats):
    save_stats["tutorial_cleared"]["Value"] = 1
    print("Successfully cleared the tutorial")
    return save_stats