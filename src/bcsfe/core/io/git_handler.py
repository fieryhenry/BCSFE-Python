from typing import Optional
from bcsfe import core


class Repo:
    def __init__(self, url: str):
        self.url = url
        self.clone()

    def get_repo_name(self) -> str:
        return self.url.split("/")[-1]

    def get_path(self) -> "core.Path":
        path = GitHandler.get_repo_folder().add(self.get_repo_name())
        path.generate_dirs()
        return path

    def clone_to_temp(self, path: "core.Path") -> None:
        cmd = f"git clone {self.url} {path}"
        core.Command(cmd).run()

    def clone(self) -> None:
        if self.is_cloned():
            return
        cmd = f"git clone {self.url} {self.get_path()}"
        core.Command(cmd).run()

    def pull(self) -> None:
        cmd = f"git -C {self.get_path()} pull"
        core.Command(cmd).run()

    def fetch(self) -> None:
        cmd = f"git -C {self.get_path()} fetch"
        core.Command(cmd).run()

    def get_file(self, file_path: "core.Path") -> Optional["core.Data"]:
        path = self.get_path().add(file_path)
        try:
            return path.read()
        except FileNotFoundError:
            return None

    def get_temp_file(
        self, temp_folder: "core.Path", file_path: "core.Path"
    ) -> "core.Data":
        path = temp_folder.add(file_path)
        return path.read()

    def get_folder(self, folder_path: "core.Path") -> Optional["core.Path"]:
        path = self.get_path().add(folder_path)
        if path.exists():
            return path
        return None

    def is_cloned(self) -> bool:
        return (
            len(self.get_path().get_dirs()) > 0 or len(self.get_path().get_files()) > 0
        )


class GitHandler:
    @staticmethod
    def get_repo_folder() -> "core.Path":
        repo_folder = core.Path.get_documents_folder().add("repos")
        repo_folder.generate_dirs()
        return repo_folder

    def get_repo(self, repo_url: str) -> "Repo":
        repo = Repo(repo_url)
        return repo

    @staticmethod
    def is_git_installed() -> bool:
        cmd = "git --version"
        return core.Command(cmd).run().exit_code == 0
