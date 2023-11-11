from typing import Any, Callable, Optional
from bcsfe import scripting, core


class EditsParser:
    def __init__(self, edits: list[dict[str, Any]]):
        self.data = edits

    def set_int(
        self,
        edit_contents: dict[str, Any],
        set: Callable[[int], None],
        get: Callable[[], int],
        name: str,
        managed_item: Optional[core.ManagedItemType] = None,
    ):
        amount = scripting.handle_int_field(edit_contents, "amount")
        if amount is None:
            raise scripting.ParsingError(
                core.core_data.local_manager.get_key(
                    "s!_missing_amount_edit", name=name
                )
            )
        add = scripting.handle_bool_field(edit_contents, "add") or False
        original = get()
        if add:
            set(get() + amount)
        else:
            set(amount)
        if managed_item is not None:
            change = get() - original
            core.BackupMetaData(scripting.context.get_save()).add_managed_item(
                core.ManagedItem.from_change(change, managed_item)
            )

    def edit(self):
        for edit in self.data:
            edit_name = list(edit.keys())[0]
            edit_contents = edit[edit_name]

            if edit_name == "print":
                scripting.print_text(edit_contents)
            elif edit_name == "xp":
                self.set_int(
                    edit_contents,
                    scripting.context.get_save().set_xp,
                    scripting.context.get_save().get_xp,
                    "xp",
                )
            elif edit_name == "catfood":
                self.set_int(
                    edit_contents,
                    scripting.context.get_save().set_catfood,
                    scripting.context.get_save().get_catfood,
                    "catfood",
                    managed_item=core.ManagedItemType.CATFOOD,
                )
            else:
                raise scripting.ParsingError(
                    core.core_data.local_manager.get_key(
                        "s!_unknown_edit",
                        name=edit_name,
                        valid_edits=["print", "xp", "catfood"],
                    )
                )
