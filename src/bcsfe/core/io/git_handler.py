from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color


class Repo:
    def __init__(self, url: str, output_error: bool = True):
        self.url = url
        self.output_error = output_error
        self.success = self.clone()

    def get_repo_name(self) -> str:
        return self.url.split("/")[-1]

    def get_path(self) -> core.Path:
        path = GitHandler.get_repo_folder().add(self.get_repo_name())
        path.generate_dirs()
        return path

    def run_cmd(self, cmd: str) -> bool:
        result = core.Command(cmd).run()
        success = result.exit_code == 0
        if not success and self.output_error:
            color.ColoredText.localize("failed_to_run_git_cmd", cmd=cmd)
        return success

    def clone_to_temp(self, path: core.Path) -> bool:
        cmd = f"git clone {self.url} {path}"
        return self.run_cmd(cmd)

    def clone(self) -> bool:
        if self.is_cloned():
            return True
        cmd = f"git clone {self.url} {self.get_path()}"
        success = self.run_cmd(cmd)
        if not success:
            self.get_path().remove()
        return success

    def pull(self) -> bool:
        cmd = f"git -C {self.get_path()} pull"
        return self.run_cmd(cmd)

    def fetch(self) -> bool:
        cmd = f"git -C {self.get_path()} fetch"
        return self.run_cmd(cmd)

    def get_file(self, file_path: core.Path) -> core.Data | None:
        path = self.get_path().add(file_path)
        try:
            return path.read()
        except FileNotFoundError:
            return None

    def get_temp_file(
        self, temp_folder: core.Path, file_path: core.Path
    ) -> core.Data:
        path = temp_folder.add(file_path)
        return path.read()

    def get_folder(self, folder_path: core.Path) -> core.Path | None:
        path = self.get_path().add(folder_path)
        if path.exists():
            return path
        return None

    def is_cloned(self) -> bool:
        return (
            len(self.get_path().get_dirs()) > 0
            or len(self.get_path().get_paths_dir()) > 0
        )


class GitHandler:
    @staticmethod
    def get_repo_folder() -> core.Path:
        repo_folder = core.Path.get_documents_folder().add("repos")
        repo_folder.generate_dirs()
        return repo_folder

    def get_repo(self, repo_url: str, output_error: bool = True) -> Repo | None:
        repo = Repo(repo_url)
        if repo.success:
            return repo
        if output_error:
            color.ColoredText.localize("failed_to_get_repo", url=repo_url)
        return None

    @staticmethod
    def is_git_installed() -> bool:
        cmd = "git --version"
        return core.Command(cmd).run().exit_code == 0
