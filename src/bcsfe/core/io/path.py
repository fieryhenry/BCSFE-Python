from __future__ import annotations
import glob
import os
import shutil

from bcsfe import core
import re


class Path:
    def __init__(self, path: str = "", is_relative: bool = False):
        if isinstance(path, Path):
            path = path.path
        if is_relative:
            self.path = self.get_relative_path(path)
        else:
            self.path = path

    def is_relative(self) -> bool:
        return not os.path.isabs(self.path)

    @staticmethod
    def get_root() -> Path:
        return Path(os.sep)

    def get_relative_path(self, path: str) -> str:
        return os.path.join(self.get_files_folder().path, path)

    @staticmethod
    def get_files_folder() -> Path:
        file = Path(os.path.realpath(__file__))
        if file.get_extension() == "pyc":
            path = file.parent().parent().parent().parent().add("files")
        else:
            path = file.parent().parent().parent().add("files")
        return path

    def strip_trailing_slash(self) -> Path:
        return Path(self.path.rstrip("/"))

    def open(self):
        self.generate_dirs()
        if os.name == "nt":
            os.startfile(self.path)  # type: ignore
        elif os.name == "posix":
            cmd = f"dbus-send --session --dest=org.freedesktop.FileManager1 --type=method_call --print-reply /org/freedesktop/FileManager1 org.freedesktop.FileManager1.ShowItems array:string:'file://{self.path}' string:''"
            core.Command(cmd, display_output=False).run_in_thread()
        elif os.name == "mac":
            core.Command(f"open {self.path}", display_output=False).run()
        else:
            raise OSError("Unknown OS")

    def open_file(self):
        os_name = os.name
        if os_name == "nt":
            os.startfile(self.path)  # type: ignore
        elif os_name == "posix":
            cmd = f"xdg-open {self.path}"
            core.Command(cmd, display_output=False).run_in_thread()
        elif os_name == "mac":
            core.Command(f"open {self.path}", display_output=False).run()
        else:
            raise OSError("Unknown OS")

    def run(self, arg: str = "", display_output: bool = False) -> core.CommandResult:
        cmd_text = self.path + " " + arg
        cmd = core.Command(cmd_text, display_output=display_output)
        return cmd.run()

    def to_str(self) -> str:
        return self.path

    def to_str_forwards(self) -> str:
        return self.path.replace("\\", "/")

    @staticmethod
    def get_documents_folder(app_name: str = "bcsfe") -> Path:
        os_name = os.name
        if os_name == "nt":
            path = Path.join(os.environ["USERPROFILE"], "Documents", app_name)
        elif os_name == "posix":
            path = Path.join(os.environ["HOME"], "Documents", app_name)
        elif os_name == "mac":
            path = Path.join(os.environ["HOME"], "Documents", app_name)
        else:
            raise OSError("Unknown OS")
        path.generate_dirs()
        return path

    def is_empty(self) -> bool:
        return self.path == ""

    def generate_dirs(self: Path) -> Path:
        if self.is_empty():
            return self
        if not self.exists():
            try:
                self.__make_dirs()
            except OSError as e:
                print(e, self)
        return self

    def create(self) -> Path:
        if not self.exists():
            self.write(core.Data("test"))
        return self

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def __make_dirs(self) -> Path:
        os.makedirs(self.path)
        return self

    def basename(self) -> str:
        return os.path.basename(self.path)

    @staticmethod
    def join(*paths: str | Path) -> Path:
        _paths: list[str] = [str(path) for path in paths]
        return Path(os.path.join(*_paths))

    def add(self, *paths: str | Path) -> Path:
        _paths: list[str] = [str(path) for path in paths]
        return Path(os.path.join(self.path, *_paths))

    def strip_leading_slash(self) -> Path:
        return Path(self.path.lstrip("/").lstrip("\\"))

    def __str__(self) -> str:
        return self.path

    def __repr__(self) -> str:
        return self.path

    def remove_tree(self, ignoreErrors: bool = False) -> Path:
        if self.exists():
            shutil.rmtree(self.path, ignore_errors=ignoreErrors)
        return self

    def remove(self):
        if self.exists():
            if self.is_directory():
                self.remove_tree()
            else:
                os.remove(self.path)

    def has_files(self) -> bool:
        return len(os.listdir(self.path)) > 0

    def copy(self, target: Path):
        if self.exists():
            if self.is_directory():
                self.copy_tree(target)
            else:
                try:
                    target.parent().generate_dirs()
                    shutil.copy(self.path, target.path)
                except shutil.SameFileError:
                    pass
        else:
            raise FileNotFoundError(f"File not found: {self.path}")

    def copy_thread(self, target: Path):
        core.Thread("copy", self.copy, (target,)).start()

    def copy_tree(self, target: Path):
        if target.exists():
            target.remove_tree()
        if self.exists():
            target.parent().generate_dirs()
            shutil.copytree(self.path, target.path)

    def read(self, create: bool = False) -> core.Data:
        if self.exists():
            return core.Data.from_file(self)
        elif create:
            self.write(core.Data())
            return self.read()
        else:
            raise FileNotFoundError(f"File not found: {self.path}")

    def write(self, data: core.Data):
        data.to_file(self)

    def get_paths_dir(self, regex: str | None = None) -> list[Path]:
        if self.exists():
            if regex is None:
                return [self.add(file) for file in os.listdir(self.path)]
            else:
                files: list[Path] = []
                for file in os.listdir(self.path):
                    if re.search(regex, file):
                        files.append(self.add(file))
                return files
        return []

    def get_files(self, regex: str | None = None) -> list[Path]:
        return [file for file in self.get_paths_dir(regex) if file.is_file()]

    def is_file(self) -> bool:
        return os.path.isfile(self.path)

    def get_dirs(self) -> list["Path"]:
        return [file for file in self.get_paths_dir() if file.is_directory()]

    def glob(self, pattern: str, recursive: bool = False) -> list[Path]:
        return [
            Path(path)
            for path in glob.glob(self.add(pattern).path, recursive=recursive)
        ]

    def strip_path_from(self, path: Path) -> Path:
        return Path(self.path.replace(path.path, "")).strip_leading_slash()

    def is_directory(self) -> bool:
        return os.path.isdir(self.path)

    def change_name(self, name: str) -> Path:
        return self.parent().add(name)

    def rename(self, name: str, overwrite: bool = False):
        if not self.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        new_path = self.change_name(name)
        if new_path.path == self.path:
            return
        if new_path.exists():
            if overwrite:
                new_path.remove()
            else:
                raise FileExistsError(f"File already exists: {new_path}")
        os.rename(self.path, new_path.path)
        self.path = new_path.path

    def parent(self) -> Path:
        return Path(os.path.dirname(self.path))

    def change_extension(self, extension: str) -> Path:
        if extension.startswith("."):
            extension = extension[1:]
        return Path(self.path.rsplit(".", 1)[0] + "." + extension)

    def remove_extension(self) -> Path:
        return Path(self.path.rsplit(".", 1)[0])

    def get_extension(self) -> str:
        try:
            return self.path.rsplit(".", 1)[1]
        except IndexError:
            return ""

    def get_file_name(self) -> str:
        return os.path.basename(self.path)

    def get_file_name_path(self) -> Path:
        return Path(self.get_file_name())

    def get_file_name_without_extension(self) -> str:
        return self.get_file_name().rsplit(".", 1)[0]

    def get_file_size(self) -> int:
        return os.path.getsize(self.path)

    def get_absolute_path(self) -> Path:
        return Path(os.path.abspath(self.path))

    def copy_object(self) -> Path:
        return Path(self.path)
