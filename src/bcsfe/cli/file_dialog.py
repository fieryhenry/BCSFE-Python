from bcsfe import core
from bcsfe.cli import color
from typing import Optional


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
            color.ColoredText.localize("tkinter_not_found")

    def __init__(self):
        self.load_tk()
        if self.tk is not None:
            try:
                self.root = self.tk.Tk()
            except self.tk.TclError:
                self.tk = None
                self.filedialog = None
                color.ColoredText.localize("tkinter_not_found")
                return

            self.root.withdraw()
            self.root.wm_attributes("-topmost", 1)  # type: ignore

    def get_file(
        self,
        title: str,
        filetypes: Optional[list[tuple[str, str]]] = None,
        initialdir: str = "",
        initialfile: str = "",
    ) -> Optional[str]:
        if filetypes is None:
            filetypes = []
        title = core.core_data.local_manager.get_key(title)
        if self.filedialog is None:
            color.ColoredText.localize(title)
            path = color.ColoredInput().localize(
                "tkinter_not_found_enter_path_file", initialfile=initialfile
            )
            return path.strip().strip("'").strip('"') if path else None
        return (
            self.filedialog.askopenfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile,
            )
            or None
        )

    def get_directory(self, title: str, initialdir: str = "") -> Optional[str]:
        title = core.core_data.local_manager.get_key(title)
        if self.filedialog is None:
            color.ColoredText.localize(title)
            path = color.ColoredInput().localize(
                "tkinter_not_found_enter_path_dir", initialdir=initialdir
            )
            return path.strip().strip("'").strip('"') if path else None

        return self.filedialog.askdirectory(title=title, initialdir=initialdir) or None

    def save_file(
        self,
        title: str,
        filetypes: Optional[list[tuple[str, str]]] = None,
        initialdir: str = "",
        initialfile: str = "",
    ) -> Optional[str]:
        """Save file dialog

        Args:
            title (str): Title of dialog.
            filetypes (Optional[list[tuple[str, str]]], optional): File types. Defaults to None.
            initialdir (str, optional): Initial directory. Defaults to "".
            initialfile (str, optional): Initial file. Defaults to "".

        Returns:
            Optional[str]: Path to file.
        """
        if filetypes is None:
            filetypes = []
        title = core.core_data.local_manager.get_key(title)
        if self.filedialog is None:
            color.ColoredText.localize(title)
            path = color.ColoredInput().localize(
                "tkinter_not_found_enter_path_file", initialfile=initialfile
            )
            return path.strip().strip("'").strip('"') if path else None
        return (
            self.filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile,
            )
            or None
        )
