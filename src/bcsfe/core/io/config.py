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

    def get_full_input_localized(
        self, key: ConfigKey, current_value: str, default_value: str
    ) -> str:
        return core.local_manager.get_key(
            "config_full",
            key_desc=core.local_manager.get_key(
                Config.get_desc_key(key),
                current_value=current_value,
                default_value=default_value,
                escape=False,
            ),
            escape=False,
        )

    def edit_bool(self, key: ConfigKey):
        value = self.get_bool(key)
        color.ColoredText(
            self.get_full_input_localized(
                key,
                self.get_bool_text(value),
                self.get_bool_text(self.get_default(key)),
            ),
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
        print()
        color.ColoredText.localize(
            "config_success",
        )

    @staticmethod
    def get_desc_key(key: ConfigKey) -> str:
        return key.value + "_desc"

    def edit_int(self, key: ConfigKey):
        text = self.get_full_input_localized(
            key, str(self.get_int(key)), str(self.get_default(key))
        )
        color.ColoredText.localize(text)
        value = dialog_creator.SingleEditor(
            key.value, self.get_int(key), signed=False, localized_item=True
        ).edit()
        self.set(key, value)

        color.ColoredText.localize(
            "config_success",
        )

    def edit_locale(self):
        text = self.get_full_input_localized(
            ConfigKey.LOCALE,
            self.get_str(ConfigKey.LOCALE),
            self.get_default(ConfigKey.LOCALE),
        )
        color.ColoredText.localize(text)
        all_locales = core.LocalManager.get_all_locales()
        options = all_locales.copy() + ["add_locale", "remove_locale"]
        value = dialog_creator.ChoiceInput.from_reduced(
            options,
            dialog="locale_dialog",
            single_choice=True,
        ).single_choice()
        if value is None:
            return
        value -= 1
        if value == len(all_locales) + 1:  # remove_locale
            options: list[str] = []
            for locale in all_locales:
                if locale.startswith("ext-"):
                    options.append(locale)

            if not options:
                color.ColoredText.localize(
                    "no_external_locales",
                )
                return

            options.append("cancel")

            choices, _ = dialog_creator.ChoiceInput.from_reduced(
                options, dialog="locale_remove_dialog"
            ).multiple_choice()
            if choices is None:
                return
            for choice in choices:
                if choice == len(options) - 1:
                    return
                core.LocalManager.remove_locale(options[choice])
                color.ColoredText.localize(
                    "locale_removed",
                    locale_name=options[choice],
                )
            return
        elif value == len(all_locales):  # add_locale
            if not core.GitHandler.is_git_installed():
                color.ColoredText.localize(
                    "git_not_installed",
                )
                return
            git_repo = color.ColoredInput().localize("enter_locale_git_repo").strip()
            external_locale = core.ExternalLocale.from_git_repo(git_repo)
            if external_locale is None:
                color.ColoredText.localize(
                    "invalid_git_repo",
                )
                return
            locale_name = external_locale.get_full_name()
            if locale_name in all_locales:
                if not dialog_creator.YesNoInput().get_input_once(
                    "locale_already_exists",
                    {"locale_name": locale_name},
                ):
                    color.ColoredText.localize(
                        "locale_cancelled",
                    )
                    return

            external_locale.save()

            value = locale_name
            color.ColoredText.localize(
                "locale_added",
            )
        else:
            value = all_locales[value]
        self.set(ConfigKey.LOCALE, value)
        color.ColoredText.localize(
            "locale_changed",
            locale_name=value,
        )
        color.ColoredText.localize(
            "config_success",
        )

    @staticmethod
    def edit_config(_: Any = None):
        config = core.config
        features = list(ConfigKey)

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
        feature = features[choice]
        print()
        if isinstance(config.get(feature), bool):
            core.config.edit_bool(feature)
        elif isinstance(config.get(feature), int):
            core.config.edit_int(feature)
        elif feature == ConfigKey.LOCALE:
            core.config.edit_locale()

        print()
