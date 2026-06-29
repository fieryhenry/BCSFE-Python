from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe.cli import color_hex
import enum
import os

if os.name == "nt":
    os.system("color")


class ColorHex(enum.Enum):
    GREEN = "#008000"
    G = GREEN
    RED = "#FF0000"
    R = RED
    DARK_YELLOW = "#D7C32A"
    DY = DARK_YELLOW
    BLACK = "#000000"
    BL = BLACK
    WHITE = "#FFFFFF"
    W = WHITE
    CYAN = "#00FFFF"
    C = CYAN
    DARK_GREY = "#A9A9A9"
    DG = DARK_GREY
    BLUE = "#0000FF"
    B = BLUE
    YELLOW = "#FFFF00"
    Y = YELLOW
    MAGENTA = "#FF00FF"
    M = MAGENTA
    DARK_BLUE = "#00008B"
    DB = DARK_BLUE
    DARK_CYAN = "#008B8B"
    DC = DARK_CYAN
    DARK_MAGENTA = "#8B008B"
    DM = DARK_MAGENTA
    DARK_RED = "#8B0000"
    DR = DARK_RED
    DARK_GREEN = "#006400"
    DGN = DARK_GREEN
    LIGHT_GREY = "#D3D3D3"
    LG = LIGHT_GREY
    ORANGE = "#FFA500"
    O = ORANGE

    @staticmethod
    def from_name(name: str) -> str:
        if not name:
            return ""
        try:
            return getattr(ColorHex, name.upper()).value
        except AttributeError:
            return ""


def __parse_color(color_name: str) -> str:
    if not color_name:
        return ""
    first_char = color_name[0]
    if first_char == "#":
        return color_name
    if first_char != "@":
        return ColorHex.from_name(color_name)

    if len(color_name) < 2:
        return ""
    second_char = color_name[1]
    if len(color_name) >= 3:
        third_char = color_name[2]
    else:
        third_char = ""
    theme_handler = core.core_data.theme_manager
    if second_char == "p":
        return theme_handler.get_primary_color()
    if second_char == "s" and third_char != "u":
        return theme_handler.get_secondary_color()
    if second_char == "t":
        return theme_handler.get_tertiary_color()
    if second_char == "q":
        return theme_handler.get_quaternary_color()
    if second_char == "e":
        return theme_handler.get_error_color()
    if second_char == "w":
        return theme_handler.get_warning_color()
    if second_char == "s" and third_char == "u":
        return theme_handler.get_success_color()
    return theme_handler.get_theme_color(color_name[1:])


def __parse(text: str) -> list[tuple[str, str]]:
    txt = "<@p>" + text + "</>"
    output: list[tuple[str, str]] = []
    i = 0
    tags: list[str] = []
    inside_tag = False
    in_closing_tag = False
    tag_text = ""
    text = ""
    special_chars = core.LocalManager.get_special_chars()
    while i < len(txt):
        char = txt[i]
        if char == "\\" and i + 1 < len(txt) and txt[i + 1] in special_chars:
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
                color = __parse_color(tag)
                output.append((text, color))
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


def color_print(text: str, end: str = "\n"):
    print(colorize(text), end=end)


def color_print_key(key: str, end: str = "\n", escape: bool = True, **kwargs: Any):
    color_print(core.localize(key, escape=escape, **kwargs), end)


def __fg(color: str):
    color = color_hex.hex_to_ansi(color)
    esc = "\x1b["
    code = esc + "38;5;"
    end = "m"
    return code + color.lower() + end


def __stylize(text: str, style: str):
    esc = "\x1b["
    end = "m"
    terminator = esc + "0" + end
    return style + f"{text}{terminator}"


def colorize(text: str) -> str:
    text_data = __parse(text)
    out: str = ""

    for txt, color in text_data:
        if not color:
            out += txt
            continue

        out += __stylize(txt, __fg(color))

    return out


def color_input(text: str) -> str:
    return input(colorize(text))


def color_input_key(key: str, escape: bool = True, **kwargs: Any) -> str:
    return color_input(core.localize(key, escape, **kwargs))
