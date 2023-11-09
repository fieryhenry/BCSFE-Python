from typing import Any
from bcsfe import scripting, core


class EditsParser:
    def __init__(self, edits: list[dict[str, Any]]):
        self.data = edits

    def edit(self):
        for edit in self.data:
            edit_name = list(edit.keys())[0]
            edit_contents = edit[edit_name]

            if edit_name == "print":
                scripting.print_text(edit_contents)
            if edit_name == "xp":
                amount = scripting.handle_int_field(edit_contents, "amount")
                if amount is None:
                    raise scripting.ParsingError("Missing amount")
                should_set = scripting.handle_bool_field(edit_contents, "should_set")
                if should_set:
                    scripting.context.get_save().xp = amount
                else:
                    scripting.context.get_save().xp += amount
