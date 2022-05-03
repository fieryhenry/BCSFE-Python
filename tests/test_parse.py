import sys
import os
local_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/BCSFE_Python")
sys.path.insert(1, local_path)

import patcher
import parse_save
import serialise_save
saves_path = "tests/saves"
save_files = [f for f in os.listdir(saves_path) if os.path.isfile(os.path.join(saves_path, f))]
for save in save_files:
    path = os.path.join(saves_path, save)
    data = open(path, "rb").read()
    gv = parse_save.get_game_version(data)
    if gv < 110000:
        continue
    gv_c = patcher.detect_game_version(data)
    print(path)
    if gv:
        save_stats = parse_save.start_parse(data, gv_c)
        save_data = serialise_save.start_serialize(save_stats)
        save_stats = parse_save.start_parse(save_data, gv_c)

