from typing import Optional
from bcsfe import core


class Enemy:
    def __init__(self, id: int):
        self.id = id

    def unlock_enemy_guide(self, save_file: "core.SaveFile"):
        save_file.enemy_guide[self.id] = 1

    def reset_enemy_guide(self, save_file: "core.SaveFile"):
        save_file.enemy_guide[self.id] = 0

    def get_name(self, save_file: "core.SaveFile") -> Optional[str]:
        return core.core_data.get_enemy_names(save_file).get_name(self.id)


class EnemyNames:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file
        self.names = self.get_names()

    def get_names(self) -> Optional[list[str]]:
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", "Enemyname.tsv")
        if data is None:
            return None
        csv = core.CSV(
            data,
            "\t",
            remove_empty=False,
        )
        names: list[str] = []
        for row in csv:
            names.append(row[0].to_str())

        return names

    def get_name(self, id: int) -> Optional[str]:
        if self.names is None:
            return None
        try:
            name = self.names[id]
            if not name:
                return core.core_data.local_manager.get_key(
                    "enemy_not_in_name_list", id=id
                )
        except IndexError:
            return core.core_data.local_manager.get_key("enemy_unknown_name", id=id)
        return name
