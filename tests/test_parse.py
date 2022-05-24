import os
import sys

local_path = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), "src/BCSFE_Python")
sys.path.insert(1, local_path)

import parse_save
import patcher
import serialise_save

saves_path = "tests/saves"
save_files = [f for f in os.listdir(
    saves_path) if os.path.isfile(os.path.join(saves_path, f))]
for save in save_files:
    path = os.path.join(saves_path, save)
    data = open(path, "rb").read()
    gv = parse_save.get_game_version(data)
    if gv < 110000:
        continue
    gv_c = patcher.detect_game_version(data)
    print(f"{path=}\t{gv_c=}\t{gv=}")
    if gv:
        save_stats = parse_save.start_parse(data, gv_c)

        save_data_1 = serialise_save.start_serialize(save_stats)

        save_stats = parse_save.start_parse(save_data_1, gv_c)

        save_data_2 = serialise_save.start_serialize(save_stats)

        if not (save_data_1 == save_data_2 and save_data_1 == data):
            print("DIFFERENT")
