import enum
from typing import Any
import colored  # type: ignore
from bcsfe.core import locale_handler


class ColorHex(enum.Enum):
    GREEN = "#008000"
    RED = "#FF0000"
    DARK_YELLOW = "#D7C32A"
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    CYAN = "#00FFFF"
    DARK_GREY = "#A9A9A9"
    BLUE = "#0000FF"
    YELLOW = "#FFFF00"
    MAGENTA = "#FF00FF"
    DARK_BLUE = "#00008B"
    DARK_CYAN = "#008B8B"
    DARK_MAGENTA = "#8B008B"
    DARK_RED = "#8B0000"
    DARK_GREEN = "#006400"
    LIGHT_GREY = "#D3D3D3"

    @staticmethod
    def from_name(name: str) -> str:
        return ColorHex[name.upper()].value


class ColoredText:
    def __init__(self, string: str, end: str = "\n") -> None:
        string = string.replace("\\n", "\n")
        self.string = string
        self.end = end
        self.display(string)

    def display(self, string: str) -> None:
        text_data = self.parse(string)
        for i, (text, color) in enumerate(text_data):
            if i == len(text_data) - 1:
                text += self.end
            if color == "":
                print(text, end="")
            else:
                try:
                    fg = colored.fg(color)  # type: ignore
                except KeyError:
                    print(text, end="")
                    continue
                print(colored.stylize(text, fg), end="")  # type: ignore

    @staticmethod
    def localize(string: str, perams: tuple[Any, ...]) -> "ColoredText":
        text = locale_handler.LocalManager().get_key(string)
        try:
            text = text % perams
        except TypeError:
            pass
        return ColoredText(text)

    def parse(self, txt: str) -> list[tuple[str, str]]:
        # example: "This is a <red>red</red> text"
        # output: [("This is a ", ""), ("red", "#FF0000"), (" text", "")]
        # example: "This is a <red>red</red> text with <green>green</green> text"
        # output: [("This is a ", ""), ("red", "#FF0000"), (" text with ", ""), ("green", "#00FF00"), (" text", "")]
        # example: "This is a <#FF0000>red</#FF0000> text with <#00FF00>green</#00FF00> text"
        # output: [("This is a ", ""), ("red", "#FF0000"), (" text with ", ""), ("green", "#00FF00"), (" text", "")]
        # example: "<red>This is a <white>white</white> red text</red>"
        # output: [("This is a ", "#FF0000"), ("white", "#FFFFFF"), (" red text", "#FF0000")]

        # allow escaping of < and > with \, so that \\<red\\> is not parsed as a color tag
        if not txt.endswith(">"):
            txt += "</>"
        output: list[tuple[str, str]] = []
        i = 0
        tags: list[str] = []
        inside_tag = False
        in_closing_tag = False
        tag_text = ""
        text = ""
        while i < len(txt):
            char = txt[i]
            if char == "\\":
                i += 1
                char = txt[i]
                text += char
                i += 1
                continue
            if tags:
                tag = tags[-1]
            else:
                tag = ""
            if char == ">" and inside_tag:
                inside_tag = False
                if not in_closing_tag:
                    tags.append(tag_text)
                if in_closing_tag:
                    in_closing_tag = False
                tag_text = ""
            if char == "<" and not inside_tag:
                inside_tag = True
                if text:
                    if not tag.startswith("#"):
                        try:
                            hex_code = ColorHex.from_name(tag)
                        except KeyError:
                            hex_code = tag
                    else:
                        hex_code = tag
                    output.append((text, hex_code))
                    text = ""
                    tag_text = ""
            if char == "/" and inside_tag:
                in_closing_tag = True
                if tags:
                    tags.pop()
            if not inside_tag and char != ">" and char != "<":
                text += char
            if inside_tag and char != "<" and char != ">":
                tag_text += char
            i += 1
        return output


class ColoredInput(ColoredText):
    def __init__(self, end: str = "") -> None:
        super().__init__(end)

    def get(self, display_string: str) -> str:
        self.display(display_string)
        return input()

    def get_int(
        self,
        display_string: str,
        error_message: str = "<red>Please enter a valid number</>",
    ) -> int:
        while True:
            try:
                return int(self.get(display_string))
            except ValueError:
                self.display(error_message)

    def get_bool(
        self,
        display_string: str,
        true_string: str = "y",
        false_string: str = "n",
    ):
        while True:
            result = self.get(display_string).lower()
            if result == true_string:
                return True
            if result == false_string:
                return False
