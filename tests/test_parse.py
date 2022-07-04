"""Test the parse and serialize functions"""

import os

from BCSFE_Python import parse_save
from BCSFE_Python import patcher
from BCSFE_Python import serialise_save

SAVES_PATH = "tests/saves"
save_files = [
    f for f in os.listdir(SAVES_PATH) if os.path.isfile(os.path.join(SAVES_PATH, f))
]
for save in save_files:
    path = os.path.join(SAVES_PATH, save).replace("\\", "/")
    with open(path, "rb") as file:
        data = file.read()
    gv = parse_save.get_game_version(data)

    if gv < 110000:
        continue
    gv_c = patcher.detect_game_version(data)
    print(f"path = {path}\tgv_c = {gv_c}\tgv = {gv}")

    save_stats = parse_save.start_parse(data, gv_c)

    save_data_1 = serialise_save.start_serialize(save_stats)

    save_stats = parse_save.start_parse(save_data_1, gv_c)

    save_data_2 = serialise_save.start_serialize(save_stats)

    if save_data_1 != save_data_2 or save_data_1 != data:
        print("DIFFERENT")
