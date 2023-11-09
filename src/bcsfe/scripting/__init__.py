from typing import Optional
from bcsfe import core
from bcsfe.scripting import load_save, parser

from bcsfe.scripting.load_save import LoadSaveParser
from bcsfe.scripting.save_save import SaveSaveParser
from bcsfe.scripting.edits import EditsParser
from bcsfe.scripting.parser import (
    Parser,
    handle_string_field,
    handle_int_field,
    handle_bool_field,
    input_int,
    input_text,
    print_text,
)


class Context:
    def __init__(self):
        self.save: Optional["core.SaveFile"] = None

    def get_save(self) -> "core.SaveFile":
        if self.save is None:
            raise ParsingError(
                core.core_data.local_manager.get_key("s!_save_not_loaded")
            )
        return self.save


class ParsingError(Exception):
    pass


context = Context()

__all__ = ["load_save", "parser"]
