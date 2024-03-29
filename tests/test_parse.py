from bcsfe import core


def run():
    saves_path = core.Path(__file__).parent().add("saves")

    for file in saves_path.get_files():
        print(f"Testing {file.basename()}")
        data1 = file.read()

        save_1 = core.SaveFile(data1)
        data_2 = save_1.to_data()

        assert data1 == data_2

        json_data_1 = save_1.to_dict()

        save_3 = core.SaveFile.from_dict(json_data_1)
        json_data_2 = save_3.to_dict()

        assert json_data_1 == json_data_2

        data_3 = save_3.to_data()

        assert data1 == data_3

        print(f"Tested {file.basename()} {save_1.game_version}")
