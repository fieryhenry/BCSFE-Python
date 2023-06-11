from tkinter import filedialog
import tkinter as tk
from bcsfe.core import locale_handler


class FileDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.wm_attributes("-topmost", 1)  # type: ignore

    def get_file(
        self,
        title: str,
        filetypes: list[tuple[str, str]] = [],
        initialdir: str = "",
        initialfile: str = "",
    ) -> str:
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
        filetypes: list[tuple[str, str]] = [],
        initialdir: str = "",
        initialfile: str = "",
    ) -> str:
        title = locale_handler.LocalManager().get_key(title)
        return filedialog.asksaveasfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initialdir,
            initialfile=initialfile,
        )
