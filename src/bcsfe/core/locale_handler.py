from typing import Optional
from bcsfe.core import io


class PropertySet:
    """Represents a set of properties in a property file."""

    def __init__(self, locale: str, property: str):
        """Initializes a new instance of the PropertySet class.

        Args:
            locale (str): Language code of the locale.
            property (str): Name of the property file.
        """
        self.locale = locale
        self.path = (
            io.path.Path("locales", True).add(locale).add(property + ".properties")
        )
        self.properties: dict[str, str] = {}
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
            if line.startswith("#") or not line:
                i += 1
                continue
            if line.startswith(">") and in_multi_line:
                multi_line_text += line[1:] + "\n"
            if (in_multi_line and not line.startswith(">")) or (
                in_multi_line and i == len(lines) - 1
            ):
                in_multi_line = False
                if multi_line_key in self.properties:
                    raise KeyError(
                        f"Key {multi_line_key} already exists in property file"
                    )
                self.properties[multi_line_key] = multi_line_text[:-1]
                multi_line_text = ""
                multi_line_key = ""

            parts = line.split("=")
            if line.strip().endswith("="):
                in_multi_line = True
                multi_line_key = parts[0]

            if not in_multi_line:
                key = parts[0]
                value = "=".join(parts[1:])
                if key in self.properties:
                    raise KeyError(f"Key {key} already exists in property file")
                self.properties[key] = value

            i += 1

    def get_key(self, key: str) -> str:
        """Gets a key from the property file.

        Args:
            key (str): Key to get.

        Returns:
            str: Value of the key.
        """
        return self.properties.get(key, key).replace("\\n", "\n")

    @staticmethod
    def from_config(property: str) -> "PropertySet":
        """Gets a PropertySet from the language code in the config.

        Args:
            property (str): Name of the property file.

        Returns:
            PropertySet: PropertySet for the property file.
        """
        return PropertySet(io.config.Config().get(io.config.Key.LOCALE), property)


class LocalManager:
    """Manages properties for a locale"""

    def __init__(self, locale: Optional[str] = None):
        """Initializes a new instance of the LocalManager class.

        Args:
            locale (str): Language code of the locale.
        """
        if locale is None:
            lc = io.config.Config().get(io.config.Key.LOCALE)
        else:
            lc = locale

        self.locale = lc
        self.path = io.path.Path("locales", True).add(lc)
        self.properties: dict[str, PropertySet] = {}
        self.all_properties: dict[str, str] = {}
        self.en_properties: dict[str, str] = {}
        self.en_properties_path = io.path.Path("locales", True).add("en")
        self.parse()
        if self.locale == "en":
            self.en_properties = self.all_properties

    def parse(self):
        """Parses all property files in the locale folder."""
        for file in self.path.get_files():
            file_name = file.basename()
            if file_name.endswith(".properties"):
                property_set = PropertySet(self.locale, file_name[:-11])
                self.all_properties.update(property_set.properties)
                self.properties[file_name[:-11]] = property_set
        if self.locale != "en":
            for file in self.en_properties_path.get_files():
                file_name = file.basename()
                if file_name.endswith(".properties"):
                    property_set = PropertySet("en", file_name[:-11])
                    self.en_properties.update(property_set.properties)

    def get_key(self, key: str) -> str:
        """Gets a key from the property file.

        Args:
            key (str): Key to get.

        Returns:
            str: Value of the key.
        """
        value = self.all_properties.get(key)
        if value is None:
            return self.en_properties.get(key, key).replace("\\n", "\n")
        return value.replace("\\n", "\n")

    @staticmethod
    def from_config() -> "LocalManager":
        """Gets a LocalManager from the language code in the config.

        Returns:
            LocalManager: LocalManager for the locale.
        """
        return LocalManager(io.config.Config().get(io.config.Key.LOCALE))

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
