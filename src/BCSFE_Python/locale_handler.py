from . import config_manager, helper
import os


class PropertySet:
    def __init__(self, locale: str, property: str):
        self.locale = locale
        self.path = os.path.join(
            helper.get_local_files_path(), "locales", locale, property + ".properties"
        )
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path))
        self.properties: dict[str, str] = {}
        self.parse()

    def parse(self):
        lines = helper.read_file_string(self.path).splitlines()
        for line in lines:
            if line.startswith("#") or line == "":
                continue
            parts = line.split("=")
            if len(parts) < 2:
                continue
            key = parts[0]
            value = "=".join(parts[1:])
            self.properties[key] = value

    def get_key(self, key: str) -> str:
        return self.properties[key].replace("\\n", "\n")

    @staticmethod
    def from_config(property: str) -> "PropertySet":
        return PropertySet(config_manager.get_config_value("LOCALE"), property)


class LocalManager:
    def __init__(self, locale: str):
        self.locale = locale
        self.path = os.path.join(helper.get_local_files_path(), "locales", locale)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.properties: dict[str, PropertySet] = {}
        self.is_en = locale == "en"
        if not self.is_en:
            self.en_path = os.path.join(helper.get_local_files_path(), "locales", "en")
            if not os.path.exists(self.en_path):
                os.makedirs(self.en_path)
            self.en_properties: dict[str, PropertySet] = {}
        self.parse()

    def parse(self):
        for file in helper.get_files_in_dir(self.path):
            file_name = os.path.basename(file)
            if file_name.endswith(".properties"):
                self.properties[file_name[:-11]] = PropertySet(
                    self.locale, file_name[:-11]
                )
        if not self.is_en:
            for file in helper.get_files_in_dir(self.en_path):
                file_name = os.path.basename(file)
                if file_name.endswith(".properties"):
                    self.en_properties[file_name[:-11]] = PropertySet(
                        "en", file_name[:-11]
                    )

    def get_key(self, property: str, key: str) -> str:
        return self.properties[property].get_key(key)

    def search_key(self, key: str) -> str:
        value = None
        for prop in self.properties.values():
            if key in prop.properties:
                value = prop.get_key(key)
        if not self.is_en:
            for prop in self.en_properties.values():
                if key in prop.properties:
                    value = prop.get_key(key)
        if value is None:
            raise KeyError(f"Key {key} not found")

        while True:
            start = value.find("{{")
            if start == -1:
                break
            end = value.find("}}")
            if end == -1:
                break
            value = value.replace(
                value[start : end + 2], self.search_key(value[start + 2 : end])
            )
        return value

    @staticmethod
    def from_config() -> "LocalManager":
        return LocalManager(config_manager.get_config_value("LOCALE"))

    @staticmethod
    def get_locales() -> list[str]:
        return helper.get_dirs(os.path.join(helper.get_local_files_path(), "locales"))
