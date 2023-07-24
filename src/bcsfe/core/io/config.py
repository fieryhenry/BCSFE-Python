import enum
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class ConfigKey(enum.Enum):
    UPDATE_TO_BETA = "update_to_beta"
    LOCALE = "locale"
    DISABLE_MAXES = "disable_maxes"
    MAX_BACKUPS = "max_backups"
    THEME = "theme"
    RESET_CAT_DATA = "reset_cat_data"
    FILTER_CURRENT_CATS = "filter_current_cats"
    SET_CAT_CURRENT_FORMS = "set_cat_current_forms"
    STRICT_UPGRADE = "strict_upgrade"
    SEPARATE_CAT_EDIT_OPTIONS = "separate_cat_edit_options"
    STRICT_BAN_PREVENTION = "strict_ban_prevention"
    MAX_REQUEST_TIMEOUT = "max_request_timeout"
    GAME_DATA_REPO = "game_data_repo"
    FORCE_LANG_GAME_DATA = "force_lang_game_data"
    CLEAR_TUTORIAL_ON_LOAD = "clear_tutorial_on_load"
    REMOVE_BAN_MESSAGE_ON_LOAD = "remove_ban_message_on_load"


class Config:
    def __init__(self):
        config = core.YamlFile(Config.get_config_path())
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

    @staticmethod
    def get_defaults() -> dict[ConfigKey, Any]:
        initial_values = {
            ConfigKey.UPDATE_TO_BETA: False,
            ConfigKey.LOCALE: "en",
            ConfigKey.DISABLE_MAXES: False,
            ConfigKey.MAX_BACKUPS: 50,
            ConfigKey.THEME: "default",
            ConfigKey.RESET_CAT_DATA: True,
            ConfigKey.FILTER_CURRENT_CATS: True,
            ConfigKey.SET_CAT_CURRENT_FORMS: True,
            ConfigKey.STRICT_UPGRADE: False,
            ConfigKey.SEPARATE_CAT_EDIT_OPTIONS: True,
            ConfigKey.STRICT_BAN_PREVENTION: False,
            ConfigKey.MAX_REQUEST_TIMEOUT: 20,
            ConfigKey.GAME_DATA_REPO: "https://raw.githubusercontent.com/fieryhenry/BCData/master/",
            ConfigKey.FORCE_LANG_GAME_DATA: False,
            ConfigKey.CLEAR_TUTORIAL_ON_LOAD: True,
            ConfigKey.REMOVE_BAN_MESSAGE_ON_LOAD: True,
        }
        return initial_values

    def get_default(self, key: ConfigKey) -> Any:
        value = Config.get_defaults()[key]
        return value

    def set_default(self, key: ConfigKey):
        value = self.get_default(key)
        self.config[key] = value
        self.save()
        return value

    def initialize_config(self):
        initial_values = Config.get_defaults()

        for key, value in initial_values.items():
            if key not in self.config:
                self.config[key] = value
        self.save()

    def save(self):
        for key, value in self.config.items():
            self.config_object.yaml[key.value] = value
        self.config_object.save()

    def get(self, key: ConfigKey) -> Any:
        value = self.config[key]
        if value is None:
            return self.set_default(key)
        return value

    def get_str(self, key: ConfigKey) -> str:
        value = self.get(key)
        if not isinstance(value, str):
            return self.set_default(key)
        return value

    def get_bool(self, key: ConfigKey) -> bool:
        value = self.get(key)
        if not isinstance(value, bool):
            return self.set_default(key)
        return value

    def get_int(self, key: ConfigKey) -> int:
        value = self.get(key)
        if not isinstance(value, int):
            return self.set_default(key)
        return value

    def reset(self):
        self.config.clear()
        self.config_object.remove()
        self.initialize_config()

    def set(self, key: ConfigKey, value: Any):
        self.config[key] = value
        self.save()

    def get_bool_text(self, value: bool) -> str:
        if value:
            return core.local_manager.get_key("enabled")
        return core.local_manager.get_key("disabled")

    def edit_bool(self, key: ConfigKey):
        value = self.get_bool(key)
        color.ColoredText.localize(
            key.value + "_desc",
            current_value=self.get_bool_text(value),
            default_value=self.get_bool_text(self.get_default(key)),
            escape=False,
        )
        choice = dialog_creator.ChoiceInput(
            ["enable", "disable"],
            ["enable", "disable"],
            [],
            {},
            "enable_disable_dialog",
            True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        if choice == 0:
            value = True
        elif choice == 1:
            value = False
        self.set(key, value)
        color.ColoredText.localize(
            "config_success",
        )

    @staticmethod
    def edit_config(_: Any):
        features = [
            ConfigKey.UPDATE_TO_BETA,
            ConfigKey.DISABLE_MAXES,
            ConfigKey.RESET_CAT_DATA,
            ConfigKey.FILTER_CURRENT_CATS,
            ConfigKey.SET_CAT_CURRENT_FORMS,
            ConfigKey.STRICT_UPGRADE,
            ConfigKey.SEPARATE_CAT_EDIT_OPTIONS,
            ConfigKey.STRICT_BAN_PREVENTION,
            ConfigKey.FORCE_LANG_GAME_DATA,
            ConfigKey.CLEAR_TUTORIAL_ON_LOAD,
            ConfigKey.REMOVE_BAN_MESSAGE_ON_LOAD,
        ]

        choice = dialog_creator.ChoiceInput(
            [key.value for key in features],
            [key.value for key in features],
            [],
            {},
            "config_dialog",
            True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        core.config.edit_bool(features[choice])
