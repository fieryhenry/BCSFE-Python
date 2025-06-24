from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color, dialog_creator


class FileDialog:
    def load_tk(self):
        try:
            import tkinter as tk
            from tkinter import filedialog

            self.tk = tk
            self.filedialog = filedialog
        except ImportError:
            self.tk = None
            self.filedialog = None

    def __init__(self):
        self.load_tk()
        if self.tk is not None:
            try:
                self.root = self.tk.Tk()
            except self.tk.TclError:
                self.tk = None
                self.filedialog = None
                return

            self.root.withdraw()
            self.root.wm_attributes("-topmost", 1)  # type: ignore

    def select_files_in_dir(
        self, path: core.Path, ignore_json: bool
    ) -> str | None:
        """Print current files in directory.

        Args:
            path (core.Path): Path to directory.
        """
        color.ColoredText.localize("current_files_dir", dir=path)
        path.generate_dirs()
        files = path.get_files()
        if not files:
            color.ColoredText.localize("no_files_dir")

        files.sort(key=lambda file: file.basename())

        # remove files with .json extension
        if ignore_json:
            files = [file for file in files if file.get_extension() != "json"]

        files_str_ls = [file.basename() for file in files]
        options = files_str_ls + [core.localize("other_dir"), core.localize("another_path")]

        choice = dialog_creator.ChoiceInput.from_reduced(
            options,
            dialog="select_files_dir",
            single_choice=True,
            localize_options=False,
        ).single_choice()
        if choice is None:
            return

        choice -= 1
        if choice == len(files):
            path_input = color.ColoredInput().localize("enter_path_dir")
            path_obj = core.Path(path_input)
            if path_obj.is_relative():
                path_obj = path.add(path_obj)
            if not path_obj.exists():
                color.ColoredText.localize("path_not_exists", path=path_obj)
                return self.select_files_in_dir(path, ignore_json)
            return self.select_files_in_dir(path_obj, ignore_json)
        if choice == len(files) + 1:
            path_input = color.ColoredInput().localize("enter_path")
            return path_input or None
        return files[choice].to_str()

    def use_tk(self) -> bool:
        return (
            self.tk is not None
            and self.filedialog is not None
            and core.core_data.config.get_bool(core.ConfigKey.USE_FILE_DIALOG)
        )

    def get_file(
        self,
        title: str,
        initialdir: str,
        initialfile: str,
        filetypes: list[tuple[str, str]] | None = None,
        ignore_json: bool = False,
    ) -> str | None:
        if filetypes is None:
            filetypes = []
        title = core.core_data.local_manager.get_key(title)
        color.ColoredText.localize(title)
        if not self.use_tk():
            curr_path = core.Path(initialdir).add(initialfile)
            file = self.select_files_in_dir(curr_path.parent(), ignore_json)
            if file is None:
                return None
            path_obj = core.Path(file)
            if path_obj.exists():
                return file
            color.ColoredText.localize("path_not_exists", path=path_obj)
            return None

        return (
            self.filedialog.askopenfilename(  # type: ignore
                title=title,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile,
            )
            or None
        )

    def save_file(
        self,
        title: str,
        initialdir: str,
        initialfile: str,
        filetypes: list[tuple[str, str]] | None = None,
    ) -> str | None:
        """Save file dialog

        Args:
            title (str): Title of dialog.
            filetypes (list[tuple[str, str]] | None, optional): File types. Defaults to None.
            initialdir (str, optional): Initial directory. Defaults to "".
            initialfile (str, optional): Initial file. Defaults to "".

        Returns:
            str | None: Path to file.
        """
        if filetypes is None:
            filetypes = []
        title = core.core_data.local_manager.get_key(title)
        color.ColoredText.localize(title)
        if not self.use_tk():
            def_path = core.Path(initialdir).add(initialfile).to_str()
            path = color.ColoredInput().localize(
                "enter_path_default", default=def_path
            )
            return path.strip().strip("'").strip('"') if path else def_path
        return (
            self.filedialog.asksaveasfilename(  # type: ignore
                title=title,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile,
            )
            or None
        )
