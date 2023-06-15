import enum
from typing import Any
from bcsfe.core.io import path, yaml


class Key(enum.Enum):
    UPDATE = "update"
    UPDATE_TO_BETA = "update_to_beta"
    LOCALE = "locale"
    DISABLE_MAXES = "disable_maxes"
    MAX_SAVE_COUNT = "max_save_count"


class Config:
    def __init__(self):
        config = yaml.YamlFile(Config.get_config_path())
        if config.yaml is None:
            config.yaml = {}
        self.config: dict[Key, Any] = {}
        for key, value in config.yaml.items():
            try:
                self.config[Key(key)] = value
            except ValueError:
                pass
        self.config_object = config
        self.initialize_config()

    @staticmethod
    def get_config_path() -> path.Path:
        return path.Path.get_appdata_folder().add("config.yaml")

    def __getitem__(self, key: Key) -> Any:
        return self.config[key]

    def __setitem__(self, key: Key, value: Any) -> None:
        self.config[key] = value

    def __contains__(self, key: Key) -> bool:
        return key in self.config

    def initialize_config(self):
        initial_values = {
            Key.UPDATE: True,
            Key.UPDATE_TO_BETA: False,
            Key.LOCALE: "en",
            Key.DISABLE_MAXES: False,
            Key.MAX_SAVE_COUNT: 50,
        }
        for key, value in initial_values.items():
            if key not in self.config:
                self.config[key] = value
        self.save()

    def save(self):
        for key, value in self.config.items():
            self.config_object.yaml[key.value] = value
        self.config_object.save()

    def get(self, key: Key) -> Any:
        return self.config[key]

    def reset(self):
        self.config.clear()
        self.config_object.remove()
        self.initialize_config()

    def set(self, key: Key, value: Any):
        self.config[key] = value
        self.save()
