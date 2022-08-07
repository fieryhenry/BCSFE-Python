import os
from BCSFE_Python import parse_save, patcher


def test_parse():
    """Test parse save data"""

    # get all files in the saves dir
    save_files: list[str] = []
    for file in os.listdir(os.path.join(os.path.dirname(__file__), "saves")):
        path = os.path.join(os.path.dirname(__file__), "saves", file)
        if (
            os.path.isfile(path)
            and not file.endswith(".bak")
            and not file.endswith("_backup")
        ):
            save_files.append(path)

    _ = [run_testparse(file) for file in save_files]


def run_testparse(file: str):
    """Run test parse save data"""
    data = open(file, "rb").read()
    gv = parse_save.get_game_version(data)
    if gv < 110000:
        return
    gv_c = patcher.detect_game_version(data)
    parse_save.parse_save(data, gv_c)
    print(f"Parsed {file}")
        