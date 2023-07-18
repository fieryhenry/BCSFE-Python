import enum
from typing import Any
from bcsfe import core


class ConfigKey(enum.Enum):
    UPDATE_TO_BETA = "update_to_beta"
    LOCALE = "locale"
    DISABLE_MAXES = "disable_maxes"
    MAX_SAVE_COUNT = "max_save_count"
    THEME = "theme"
    RESET_CAT_DATA = "reset_cat_data"
    FILTER_CURRENT_CATS = "filter_current_cats"
    SET_CAT_CURRENT_FORMS = "set_cat_current_forms"
    STRICT_UPGRADE = "strict_upgrade"
    SEPARATE_CAT_UPGRADE_OPTIONS = "separate_cat_upgrade_options"
    STRICT_BAN_PREVENTION = "strict_ban_prevention"


class Config:
    def __init__(self):
        config = core.YamlFile(Config.get_config_path())
        if config.yaml is None:
            config.yaml = {}
        self.config: dict[ConfigKey, Any] = {}
        for key, value in config.yaml.items():
            try:
                self.config[ConfigKey(key)] = value
            except ValueError:
                pass
        self.config_object = config
        self.initialize_config()

    @staticmethod
    def get_config_path() -> "core.Path":
        return core.Path.get_documents_folder().add("config.yaml")

    def __getitem__(self, key: ConfigKey) -> Any:
        return self.config[key]

    def __setitem__(self, key: ConfigKey, value: Any) -> None:
        self.config[key] = value

    def __contains__(self, key: ConfigKey) -> bool:
        return key in self.config

    def initialize_config(self):
        initial_values = {
            ConfigKey.UPDATE_TO_BETA: False,
            ConfigKey.LOCALE: "en",
            ConfigKey.DISABLE_MAXES: False,
            ConfigKey.MAX_SAVE_COUNT: 50,
            ConfigKey.THEME: "default",
            ConfigKey.RESET_CAT_DATA: True,
            ConfigKey.FILTER_CURRENT_CATS: True,
            ConfigKey.SET_CAT_CURRENT_FORMS: True,
            ConfigKey.STRICT_UPGRADE: False,
            ConfigKey.SEPARATE_CAT_UPGRADE_OPTIONS: True,
            ConfigKey.STRICT_BAN_PREVENTION: False,
        }
        for key, value in initial_values.items():
            if key not in self.config:
                self.config[key] = value
        self.save()

    def save(self):
        for key, value in self.config.items():
            self.config_object.yaml[key.value] = value
        self.config_object.save()

    def get(self, key: ConfigKey) -> Any:
        return self.config[key]

    def reset(self):
        self.config.clear()
        self.config_object.remove()
        self.initialize_config()

    def set(self, key: ConfigKey, value: Any):
        self.config[key] = value
        self.save()
