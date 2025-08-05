from __future__ import annotations
import enum
from typing import Any
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class ConfigKey(enum.Enum):
    UPDATE_TO_BETA = "update_to_beta"
    SHOW_UPDATE_MESSAGE = "show_update_message"
    LOCALE = "locale"
    SHOW_MISSING_LOCALE_KEYS = "show_missing_locale_keys"
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
    UNLOCK_CAT_ON_EDIT = "unlock_cat_on_edit"
    USE_FILE_DIALOG = "use_file_dialog"
    ADB_PATH = "adb_path"
    IGNORE_PARSE_ERROR = "ignore_parse_error"
    USE_WAYDROID = "use_waydroid"


class Config:
    def __init__(self, path: core.Path | None, print_yaml_err: bool = True):
        if path is None:
            path = Config.get_config_path()
        config = core.YamlFile(path, print_yaml_err)
        self.config: dict[ConfigKey, Any] = {}
        for key, value in config.yaml.items():
            try:
                self.config[ConfigKey(key)] = value
            except ValueError:
                pass
        self.config_object = config
        self.initialize_config()

    @staticmethod
    def get_config_path() -> core.Path:
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
            ConfigKey.SHOW_UPDATE_MESSAGE: True,
            ConfigKey.LOCALE: "en",
            ConfigKey.SHOW_MISSING_LOCALE_KEYS: False,
            ConfigKey.DISABLE_MAXES: False,
            ConfigKey.MAX_BACKUPS: 50,
            ConfigKey.THEME: "default",
            ConfigKey.RESET_CAT_DATA: True,
            ConfigKey.SET_CAT_CURRENT_FORMS: True,
            ConfigKey.STRICT_UPGRADE: False,
            ConfigKey.SEPARATE_CAT_EDIT_OPTIONS: True,
            ConfigKey.STRICT_BAN_PREVENTION: False,
            ConfigKey.MAX_REQUEST_TIMEOUT: 30,
            ConfigKey.GAME_DATA_REPO: "https://raw.githubusercontent.com/fieryhenry/BCData/master/",
            ConfigKey.FORCE_LANG_GAME_DATA: False,
            ConfigKey.CLEAR_TUTORIAL_ON_LOAD: True,
            ConfigKey.REMOVE_BAN_MESSAGE_ON_LOAD: True,
            ConfigKey.UNLOCK_CAT_ON_EDIT: True,
            ConfigKey.USE_FILE_DIALOG: True,
            ConfigKey.ADB_PATH: "adb",
            ConfigKey.IGNORE_PARSE_ERROR: False,
            ConfigKey.USE_WAYDROID: False,
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
            return core.core_data.local_manager.get_key("enabled")
        return core.core_data.local_manager.get_key("disabled")

    def get_full_input_localized(
        self, key: ConfigKey, current_value: str, default_value: str
    ) -> str:
        return core.core_data.local_manager.get_key(
            "config_full",
            key_desc=core.core_data.local_manager.get_key(
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

    def edit_game_data_repo(self):
        text = self.get_full_input_localized(
            ConfigKey.GAME_DATA_REPO,
            self.get_str(ConfigKey.GAME_DATA_REPO),
            self.get_default(ConfigKey.GAME_DATA_REPO),
        )
        color.ColoredText.localize(text)
        value = dialog_creator.StringInput().get_input_locale(
            "game_data_repo_dialog", {}
        )
        if value is None:
            return
        self.set(ConfigKey.GAME_DATA_REPO, value)
        color.ColoredText.localize(
            "config_success",
        )

    def edit_str(self, key: ConfigKey):
        text = self.get_full_input_localized(
            key,
            self.get_str(key),
            self.get_default(key),
        )

        color.ColoredText.localize(text)

        str_val = core.core_data.local_manager.get_key(key.value)

        value = dialog_creator.StringInput().get_input_locale(
            "string_config_dialog", {"val": str_val}
        )
        if value is None:
            return

        self.set(key, value)
        color.ColoredText.localize("config_success")

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

    def edit_theme(self):
        themes = core.ThemeHandler.get_all_themes()
        current_theme = self.get_str(ConfigKey.THEME)
        if current_theme not in themes:
            current_theme = "default"
        text = self.get_full_input_localized(
            ConfigKey.THEME,
            current_theme,
            self.get_default(ConfigKey.THEME),
        )
        color.ColoredText.localize(text)
        options = themes.copy() + ["add_theme", "remove_theme"]
        value = dialog_creator.ChoiceInput.from_reduced(
            options,
            dialog="theme_dialog",
            single_choice=True,
        ).single_choice()
        if value is None:
            return
        value -= 1
        if value == len(themes) + 1:  # remove_theme
            options: list[str] = []
            for theme in themes:
                if theme.startswith("ext-"):
                    options.append(theme)

            if not options:
                color.ColoredText.localize(
                    "no_external_themes",
                )
                return

            options.append("cancel")

            choices, _ = dialog_creator.ChoiceInput.from_reduced(
                options, dialog="theme_remove_dialog"
            ).multiple_choice()
            if choices is None:
                return
            for choice in choices:
                if choice == len(options) - 1:
                    return
                core.ThemeHandler.remove_theme(options[choice])
                color.ColoredText.localize(
                    "theme_removed",
                    theme_name=options[choice],
                )
            return
        elif value == len(themes):  # add_theme
            if not core.GitHandler.is_git_installed():
                color.ColoredText.localize(
                    "git_not_installed",
                )
                return
            git_repo = color.ColoredInput().localize("enter_theme_git_repo").strip()
            external_theme = core.ExternalTheme.from_git_repo(git_repo)
            if external_theme is None:
                color.ColoredText.localize(
                    "invalid_git_repo",
                )
                return
            theme_name = external_theme.get_full_name()
            if theme_name in themes:
                if not dialog_creator.YesNoInput().get_input_once(
                    "theme_already_exists",
                    {"theme_name": theme_name},
                ):
                    color.ColoredText.localize(
                        "theme_cancelled",
                    )
                    return

            external_theme.save()

            value = theme_name
            color.ColoredText.localize(
                "theme_added",
            )
        else:
            value = themes[value]
        self.set(ConfigKey.THEME, value)
        color.ColoredText.localize(
            "theme_changed",
            theme_name=value,
        )

    @staticmethod
    def edit_config(_: Any = None):
        config = core.core_data.config
        features = list(ConfigKey)

        choice = dialog_creator.ChoiceInput.from_reduced(
            [key.value for key in features],
            dialog="config_dialog",
            single_choice=True,
        ).single_choice()
        if choice is None:
            return
        choice -= 1
        feature = features[choice]
        print()
        if isinstance(config.get(feature), bool):
            core.core_data.config.edit_bool(feature)
        elif isinstance(config.get(feature), int):
            core.core_data.config.edit_int(feature)
        elif feature == ConfigKey.LOCALE:
            core.core_data.config.edit_locale()
        elif feature == ConfigKey.THEME:
            core.core_data.config.edit_theme()
        elif feature == ConfigKey.GAME_DATA_REPO:
            core.core_data.config.edit_game_data_repo()
        elif isinstance(config.get(feature), str):
            core.core_data.config.edit_str(feature)
        print()
