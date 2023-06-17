from tkinter import filedialog
import tkinter as tk
from bcsfe.core import locale_handler
from typing import Optional


class FileDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.wm_attributes("-topmost", 1)  # type: ignore

    def get_file(
        self,
        title: str,
        filetypes: Optional[list[tuple[str, str]]] = None,
        initialdir: str = "",
        initialfile: str = "",
    ) -> str:
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        title = locale_handler.LocalManager().get_key(title)
        return filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            initialfile=initialfile,
        )

    def get_directory(self, title: str, initialdir: str = "") -> str:
        title = locale_handler.LocalManager().get_key(title)
        return filedialog.askdirectory(title=title, initialdir=initialdir)

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
            filetypes = [("All files", "*.*")]
        title = locale_handler.LocalManager().get_key(title)
        return (
            filedialog.asksaveasfilename(
                title=title,
                filetypes=filetypes,
                initialdir=initialdir,
                initialfile=initialfile,
            )
            or None
        )
