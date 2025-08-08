from __future__ import annotations
import dataclasses
import tempfile
from typing import Any
from bcsfe import core
from bcsfe.cli import color


class PropertySet:
    """Represents a set of properties in a property file."""

    def __init__(self, locale: str, property: str):
        """Initializes a new instance of the PropertySet class.

        Args:
            locale (str): Language code of the locale.
            property (str): Name of the property file.
        """
        self.locale = locale
        self.property = property
        self.path = LocalManager.get_locale_folder(locale).add(property + ".properties")
        self.properties: dict[str, tuple[str, str]] = {}
        self.parse()

    def parse(self):
        """Parses the property file.

        Raises:
            KeyError: If a key is already defined in the property file.
        """
        lines = self.path.read().to_str().splitlines()
        i = 0
        in_multi_line = False
        multi_line_text = ""
        multi_line_key = ""

        while i < len(lines):
            line = lines[i]
            finish_multiline = False
            if (in_multi_line and not line.startswith(">")) or (
                in_multi_line and i == len(lines) - 1
            ):
                in_multi_line = False
                finish_multiline = True
                if multi_line_key in self.properties:
                    raise KeyError(
                        f"Key {multi_line_key} already exists in property file"
                    )
                if line.startswith(">"):
                    multi_line_text += line[1:]
                else:
                    multi_line_text = multi_line_text[:-1]  # remove extra newline
                self.properties[multi_line_key] = (multi_line_text, self.property)
                multi_line_text = ""
                multi_line_key = ""
            if line.startswith("#") or not line:
                i += 1
                continue
            if line.startswith(">") and in_multi_line:
                multi_line_text += line[1:] + "\n"

            parts = line.split("=")
            if line.strip().endswith("="):
                in_multi_line = True
                multi_line_key = parts[0]

            if not in_multi_line and not finish_multiline:
                key = parts[0]
                value = "=".join(parts[1:])
                if key in self.properties:
                    raise KeyError(f"Key {key} already exists in property file")
                self.properties[key] = (value, self.property)

            i += 1

    def get_key(self, key: str) -> str:
        """Gets a key from the property file.

        Args:
            key (str): Key to get.

        Returns:
            str: Value of the key.
        """
        return (
            self.properties.get(key, key)[0].replace("\\n", "\n").replace("\\t", "\t")
        )

    @staticmethod
    def from_config(property: str) -> PropertySet:
        """Gets a PropertySet from the language code in the config.

        Args:
            property (str): Name of the property file.

        Returns:
            PropertySet: PropertySet for the property file.
        """
        return PropertySet(
            core.core_data.config.get_str(core.ConfigKey.LOCALE), property
        )


class LocalManager:
    """Manages properties for a locale"""

    def __init__(self, locale: str | None = None):
        """Initializes a new instance of the LocalManager class.

        Args:
            locale (str): Language code of the locale.
        """
        if locale is None:
            lc = core.core_data.config.get_str(core.ConfigKey.LOCALE)
        else:
            lc = locale

        self.locale = lc
        self.path = LocalManager.get_locale_folder(lc)
        self.properties: dict[str, PropertySet] = {}
        self.all_properties: dict[str, tuple[str, str]] = {}
        self.en_properties: dict[str, tuple[str, str]] = {}
        self.en_properties_path = LocalManager.get_locale_folder("en")
        self.authors: list[str] = ["fieryhenry"]
        self.name: str = "English"
        self.parse()
        if self.locale == "en":
            self.en_properties = self.all_properties

        if core.core_data.config.get_bool(core.ConfigKey.SHOW_MISSING_LOCALE_KEYS):
            key = self.get_key("missing_locale_keys")
            print(key)
            print()
            missing = self.get_missing_keys()
            for key in missing:
                print(f"{key[2]}\n{key[0]}={key[1]}\n")
            if not missing:
                print(self.get_key("none"))

            print()

            key = self.get_key("extra_locale_keys")
            print(key)
            print()
            extra = self.get_extra_keys()
            for key in extra:
                print(f"{key[2]}\n{key[0]}={key[1]}\n")
            if not extra:
                print(self.get_key("none"))

            print()

    def get_missing_keys(self) -> list[tuple[str, str, str]]:
        missing = set(self.en_properties.keys()) - set(self.all_properties.keys())

        return [
            (
                key,
                self.en_properties[key][0],
                self.en_properties[key][1] + ".properties",
            )
            for key in missing
        ]

    def get_extra_keys(self) -> list[tuple[str, str, str]]:
        extra = set(self.all_properties.keys()) - set(self.en_properties.keys())

        return [
            (
                key,
                self.all_properties[key][0],
                self.all_properties[key][1] + ".properties",
            )
            for key in extra
        ]

    def parse(self):
        """Parses all property files in the locale folder recursively."""
        for file in self.path.glob("**/*.properties", recursive=True):
            file_name = file.strip_path_from(self.path).path
            property_set = PropertySet(self.locale, file_name[:-11])
            self.all_properties.update(property_set.properties)
            self.properties[file_name[:-11]] = property_set

        metadata_path = self.path.add("metadata.json")

        if metadata_path.exists():
            data = core.JsonFile.from_path(metadata_path)
            self.authors = data.get("authors") or ["fieryhenry"]
            self.name = data.get("name") or "English"

        if self.locale != "en":
            for file in self.en_properties_path.glob("**/*.properties", recursive=True):
                file_name = file.strip_path_from(self.en_properties_path).path
                property_set = PropertySet("en", file_name[:-11])
                self.en_properties.update(property_set.properties)

    def get_key(self, key: str, escape: bool = True, **kwargs: Any) -> str:
        """Gets a key from the property file.

        Args:
            key (str): Key to get.

        Returns:
            str: Value of the key.
        """
        try:
            text = self.get_key_recursive(key, kwargs, escape)
        except RecursionError:
            text = key

        for kwarg_key, kwarg_value in kwargs.items():
            value = str(kwarg_value)
            if escape:
                value = LocalManager.escape_string(value)
            text = text.replace("{" + kwarg_key + "}", value)

        if "$(" in text:
            text = self.parse_condition(text, kwargs)

        return text

    def parse_condition(self, text: str, kwargs: dict[str, Any]) -> str:
        counter = 0
        final_text = ""
        in_expression = False
        expression_text = ""
        count_down = 0
        while counter < len(text):
            char = text[counter]
            if counter == len(text) - 1:
                final_text += char
                break
            next_char = text[counter + 1]
            if char == "\\":
                final_text += next_char
                counter += 2
                continue
            if char == "$" and next_char == "(":
                count_down = 0
                in_expression = True
            elif char == "/" and next_char == "$":
                count_down = 2
                in_expression = False
                if len(expression_text) < 3:
                    counter += 1
                    continue
                new_expression_text = expression_text[2:-1]
                expression_text = ""
                parts = new_expression_text.split(":")
                if len(parts) < 2:
                    counter += 1
                    continue
                keyword = parts[0].strip()
                expression = parts[1].strip()
                conditions = expression.split("$,")
                string = ""
                for i, condition in enumerate(conditions):
                    condition = condition.strip()
                    if not condition:
                        continue
                    if i == len(conditions) - 1:
                        string = condition
                        break
                    condition_parts = condition.split("($")
                    if len(condition_parts) < 2:
                        continue
                    logic = condition_parts[0].strip()
                    word = condition_parts[1].strip()
                    if not word:
                        continue
                    word = word[:-1]
                    value = kwargs.get(keyword)
                    if value is None:
                        continue
                    equality = None
                    if logic.startswith("=="):
                        equality = "=="
                    elif logic.startswith("!="):
                        equality = "!="
                    elif logic.startswith(">="):
                        equality = ">="
                    elif logic.startswith("<="):
                        equality = "<="
                    elif logic.startswith(">"):
                        equality = ">"
                    elif logic.startswith("<"):
                        equality = "<"
                    if equality is None:
                        continue
                    logic_parts = logic.split(equality)
                    if len(logic_parts) < 2:
                        continue
                    logic_value = logic_parts[1].strip()

                    if isinstance(value, int):
                        if not logic_value.isdigit():
                            continue
                        logic_value = int(logic_value)

                    if equality == "==":
                        if logic_value == value:
                            string = word
                            break
                    elif equality == "!=":
                        if logic_value != value:
                            string = word
                            break

                    if isinstance(logic_value, int) and not string:
                        if equality == ">":
                            if logic_value > value:
                                string = word
                                break
                        elif equality == ">=":
                            if logic_value >= value:
                                string = word
                                break
                        elif equality == "<":
                            if logic_value < value:
                                string = word
                                break
                        elif equality == "<=":
                            if logic_value <= value:
                                string = word
                                break

                final_text += string

            if in_expression:
                expression_text += char
            else:
                if count_down <= 0:
                    final_text += char
                else:
                    count_down -= 1

            counter += 1

        return final_text

    @staticmethod
    def get_special_chars() -> list[str]:
        return ["<", ">", "/"]

    @staticmethod
    def escape_string(string: str) -> str:
        for char in LocalManager.get_special_chars():
            string = string.replace(char, "\\" + char)
        return string

    def get_key_recursive(
        self,
        key: str,
        kwargs: dict[str, Any],
        escape: bool = True,
    ) -> str:
        value = self.all_properties.get(key)
        if value is None:
            value = self.en_properties.get(key, (key, key))
        value = value[0].replace("\\n", "\n").replace("\\t", "\t")
        # replace {{key}} with the value of the key
        if "{{" not in value:
            return value
        char_index = 0
        while char_index < len(value):
            if value[char_index] == "{" and value[char_index + 1] == "{":
                key_name = ""
                char_index += 2
                while value[char_index] != "}":
                    key_name += value[char_index]
                    char_index += 1

                if key_name != key:
                    value = value.replace(
                        "{{" + key_name + "}}",
                        self.get_key(key_name, escape, **kwargs),
                    )
            char_index += 1

        return value

    @staticmethod
    def get_all_aliases(value: str) -> list[str]:
        """Gets all aliases from a string. Aliases are separated by |.

        Args:
            value (str): String to get aliases from.

        Returns:
            list[str]: List of aliases.
        """
        if "|" not in value:
            return [value]
        i = 0
        aliases: list[str] = []
        while i < len(value):
            char = value[i]
            prev_char = value[i - 1] if i > 0 else ""
            if char == "|" and prev_char != "\\":
                aliases.append(value[:i])
                value = value[i + 1 :]
                i = 0
            i += 1

        aliases.append(value)
        return aliases

    @staticmethod
    def from_config() -> LocalManager:
        """Gets a LocalManager from the language code in the config.

        Returns:
            LocalManager: LocalManager for the locale.
        """
        return LocalManager(core.core_data.config.get_str(core.ConfigKey.LOCALE))

    def check_duplicates(self):
        """Checks for duplicate keys in all property files.

        Raises:
            KeyError: If a key is already defined in the property file.
        """
        keys: set[str] = set()
        for property in self.properties.values():
            for key in property.properties.keys():
                if key in keys:
                    raise KeyError(f"Duplicate key {key}")
                keys.add(key)

    @staticmethod
    def get_all_locales() -> list[str]:
        """Gets all locales in the locales folder.

        Returns:
            list[str]: List of locales.
        """
        locales: list[str] = []
        for folder in LocalManager.get_locales_folder().get_dirs():
            locales.append(folder.basename())
        for folder in LocalManager.get_external_locales_folder().get_dirs():
            locales.append(folder.basename())
        return locales

    @staticmethod
    def get_locales_folder() -> core.Path:
        """Gets the locales folder.

        Returns:
            core.Path: Path to the locales folder.
        """
        return core.Path("locales", True)

    @staticmethod
    def get_external_locales_folder() -> core.Path:
        """Gets the external locales folder.

        Returns:
            core.Path: Path to the external locales folder.
        """
        return core.Path.get_documents_folder().add("external_locales")

    @staticmethod
    def get_locale_folder(locale: str) -> core.Path:
        """Gets the folder for a locale.

        Args:
            locale (str): Language code of the locale.

        Returns:
            core.Path: Path to the locale folder.
        """
        if locale.startswith("ext-"):
            return LocalManager.get_external_locales_folder().add(locale)
        return LocalManager.get_locales_folder().add(locale)

    @staticmethod
    def remove_locale(locale: str):
        """Removes a locale.

        Args:
            locale (str): Language code of the locale.
        """
        if locale not in LocalManager.get_all_locales():
            return
        if locale.startswith("ext-"):
            extern = ExternalLocaleManager.get_external_locale(locale)
            if extern is not None:
                ExternalLocaleManager.delete_locale(extern)
            LocalManager.get_external_locales_folder().add(locale).remove()
        else:
            LocalManager.get_locales_folder().add(locale).remove()

        if core.core_data.config.get_str(core.ConfigKey.LOCALE) == locale:
            core.core_data.config.set(core.ConfigKey.LOCALE, "en")


@dataclasses.dataclass
class ExternalLocale:
    short_name: str
    name: str
    description: str
    author: str
    version: str
    git_repo: str | None = None

    def to_json(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_json(json_data: dict[str, Any]) -> ExternalLocale | None:
        short_name = json_data.get("short_name")
        name = json_data.get("name")
        description = json_data.get("description")
        author = json_data.get("author")
        version = json_data.get("version")
        git_repo = json_data.get("git_repo")
        if (
            short_name is None
            or name is None
            or description is None
            or author is None
            or version is None
        ):
            return None
        return ExternalLocale(
            short_name,
            name,
            description,
            author,
            version,
            git_repo,
        )

    @staticmethod
    def from_git_repo(git_repo: str) -> ExternalLocale | None:
        repo = core.GitHandler().get_repo(git_repo)
        if repo is None:
            return None
        locale_json = repo.get_file(core.Path("locale.json"))
        if locale_json is None:
            return None
        json_data = core.JsonFile.from_data(locale_json).to_object()
        json_data["git_repo"] = git_repo
        return ExternalLocale.from_json(json_data)

    def get_new_version(self) -> bool:
        if self.git_repo is None:
            return False
        repo = core.GitHandler().get_repo(self.git_repo)
        if repo is None:
            return False
        with tempfile.TemporaryDirectory() as tmp:
            temp_dir = core.Path(tmp)
            success = repo.clone_to_temp(temp_dir)
            if not success:
                return False
            external_locale = ExternalLocaleManager.parse_external_locale(temp_dir)
            if external_locale is None:
                return False
            version = external_locale.version

            if version == self.version:
                return False

            self.name = external_locale.name
            self.short_name = external_locale.short_name
            self.description = external_locale.description
            self.author = external_locale.author
            self.version = version

        success = repo.pull()
        if not success:
            return False
        self.save()
        return True

    def save(self):
        ExternalLocaleManager.save_locale(self)

    def get_full_name(self) -> str:
        return f"ext-{self.author}-{self.short_name}"


class ExternalLocaleManager:
    @staticmethod
    def delete_locale(external_locale: ExternalLocale):
        if external_locale.git_repo is None:
            return
        folder = core.GitHandler.get_repo_folder().add(
            external_locale.git_repo.split("/")[-1]
        )
        folder.remove()

    @staticmethod
    def save_locale(
        external_locale: ExternalLocale,
    ):
        """Saves an external locale.

        Args:
            external_locale (ExternalLocale): External locale to save.
        """
        if external_locale.git_repo is None:
            return
        folder = LocalManager.get_external_locales_folder().add(
            external_locale.get_full_name()
        )
        folder.generate_dirs()

        repo = core.GitHandler().get_repo(external_locale.git_repo)
        if repo is None:
            return
        files_dir = repo.get_folder(core.Path("files"))
        if files_dir is None:
            return

        files_dir.copy_tree(folder)

        json_data = external_locale.to_json()
        folder.add("locale.json").write(core.JsonFile.from_object(json_data).to_data())

    @staticmethod
    def parse_external_locale(path: core.Path) -> ExternalLocale | None:
        """Parses an external locale.

        Args:
            path (core.Path): Path to the external locale.

        Returns:
            ExternalLocale: External locale.
        """
        if not path.exists():
            return None
        json_data = core.JsonFile.from_data(path.add("locale.json").read()).to_object()
        return ExternalLocale.from_json(json_data)

    @staticmethod
    def update_external_locale(external_locale: ExternalLocale):
        """Updates an external locale.

        Args:
            external_locale (ExternalLocale): External locale to update.
        """
        if external_locale.git_repo is None:
            return
        color.ColoredText.localize(
            "checking_for_locale_updates",
            locale_name=external_locale.name,
        )
        updated = external_locale.get_new_version()
        if updated:
            color.ColoredText.localize(
                "external_locale_updated",
                locale_name=external_locale.name,
                version=external_locale.version,
            )
        else:
            color.ColoredText.localize(
                "external_locale_no_update",
                locale_name=external_locale.name,
                version=external_locale.version,
            )
        print()

    @staticmethod
    def update_all_external_locales(_: Any = None):
        """Updates all external locales."""
        dirs = LocalManager.get_external_locales_folder().get_dirs()
        if not dirs:
            color.ColoredText.localize(
                "no_external_locales",
            )
            return
        if not core.GitHandler.is_git_installed():
            color.ColoredText.localize(
                "git_not_installed",
            )
            return
        for folder in dirs:
            locale = ExternalLocaleManager.parse_external_locale(folder)
            if locale is None:
                continue
            ExternalLocaleManager.update_external_locale(locale)

    @staticmethod
    def get_external_locale_config() -> ExternalLocale | None:
        """Gets the external locale from the config.

        Returns:
            ExternalLocale: External locale.
        """

        locale = core.core_data.config.get_str(core.ConfigKey.LOCALE)
        if not locale.startswith("ext-"):
            return None
        return ExternalLocaleManager.parse_external_locale(
            LocalManager.get_locale_folder(locale)
        )

    @staticmethod
    def get_external_locale(locale: str) -> ExternalLocale | None:
        """Gets the external locale from the code.

        Returns:
            ExternalLocale: External locale.
        """

        if not locale.startswith("ext-"):
            return None
        return ExternalLocaleManager.parse_external_locale(
            LocalManager.get_locale_folder(locale)
        )
