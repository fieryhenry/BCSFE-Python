from typing import Any, Optional
from bcsfe import core, cli, scripting
import yaml


class Parser:
    def __init__(self, path: "core.Path"):
        self.data = yaml.safe_load(path.read().to_bytes())

        self.load_wrapper()

    def load_wrapper(self) -> None:
        try:
            self.load()
        except Exception as e:
            cli.color.ColoredText.localize("s!_scripting_error", error=e)
            if not isinstance(e, scripting.ParsingError):
                raise e

    def load(self) -> None:
        self.schema_version = self.data.get("schema-version")
        if self.schema_version is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key("s!_missing_schema")
            )
        if self.schema_version != 0:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key(
                    "s!_unknown_schema", schema=self.schema_version, valid_schemas=[0]
                )
            )

        self.package = self.data.get("package")
        if self.package is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key("s!_missing_package")
            )
        if self.package != "bcsfe":
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key(
                    "s!_unknown_package", package=self.package, valid_packages=["bcsfe"]
                )
            )

        for action in self.data.get("actions", []):
            name = list(action.keys())[0]
            action_contents = action[name]
            if action_contents is None:
                raise scripting.ParsingError(
                    core.core_data.local_manager.get_key(
                        "s!_missing_action_contents", name=name
                    )
                )
            if name == "print":
                print_text(action_contents)
            elif name == "load-save":
                scripting.context.save = scripting.LoadSaveParser(
                    action_contents
                ).load()
            elif name == "edits":
                scripting.EditsParser(action_contents).edit()
            elif name == "save-save":
                scripting.SaveSaveParser(action_contents).save()


def call_function(name: str) -> Optional[str]:
    if name == "get_xp":
        return str(scripting.context.get_save().xp)
    if name == "get_catfood":
        return str(scripting.context.get_save().catfood)
    if name == "get_iq":
        return str(scripting.context.get_save().inquiry_code)
    return None


def parse_text(text: str) -> str:
    # find all instances of {attribute}
    # replace with attribute value
    # return new text

    if text.startswith("\\!"):
        return text[2:]

    new_text = ""
    in_attribute = False
    attribute = ""
    for char in text:
        if char == "{":
            in_attribute = True
        elif char == "}":
            in_attribute = False
            attribute_value = call_function(attribute.replace("()", ""))
            if attribute_value is None:
                raise scripting.ParsingError(f"Unknown attribute: {attribute}")
            new_text += str(attribute_value)
            attribute = ""
        elif in_attribute:
            attribute += char
        else:
            new_text += char
    return new_text


def print_text(text: str) -> None:
    print(parse_text(text))


def input_text(text: str) -> str:
    return input(text)


def input_int(text: str) -> int:
    while True:
        value = input_text(text)
        try:
            return int(value)
        except ValueError:
            print("Invalid input")


def input_bool(text: str) -> bool:
    while True:
        value = input_text(text)
        if value.lower() in ["y", "yes", "t", "true"]:
            return True
        if value.lower() in ["n", "no", "f", "false"]:
            return False
        print("Invalid input")


def handle_string_field(data: dict[str, Any], key_name: str) -> Optional[str]:
    value = data.get(key_name, None)
    if value is None:
        return None
    if value == "!input":
        return input_text(f"Enter {key_name}: ")
    return value


def handle_int_field(data: dict[str, Any], key_name: str) -> Optional[int]:
    value = data.get(key_name, None)
    if value is None:
        return None
    if value == "!input":
        return input_int(f"Enter {key_name}: ")
    return value


def handle_bool_field(data: dict[str, Any], key_name: str) -> Optional[bool]:
    value = data.get(key_name, None)
    if value is None:
        return None
    if value == "!input":
        return input_bool(f"Enter {key_name}: ")
    return value
