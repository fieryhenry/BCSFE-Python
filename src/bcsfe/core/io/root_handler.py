from __future__ import annotations
from bcsfe import core
import tempfile


class PackageNameNotSet(Exception):
    pass


class RootHandler:
    def __init__(self):
        self.package_name = None

    def is_android(self) -> bool:
        return core.Path.get_root().add("system").exists()

    def set_package_name(self, package_name: str):
        self.package_name = package_name

    def is_rooted(self) -> bool:
        try:
            core.Path.get_root().add("data").add("data").get_dirs()
        except PermissionError:
            return False
        return True

    def get_battlecats_packages(self) -> list[str]:
        packages = core.Path.get_root().add("data").add("data").get_dirs()
        packages = [
            package.basename()
            for package in packages
            if package.add("files").add("SAVE_DATA").exists()
        ]
        return packages

    def get_package_name(self) -> str:
        if self.package_name is None:
            raise PackageNameNotSet("Package name is not set")
        return self.package_name

    def get_battlecats_path(self) -> core.Path:
        return core.Path.get_root().add("data").add("data").add(self.get_package_name())

    def get_battlecats_save_path(self) -> core.Path:
        return self.get_battlecats_path().add("files").add("SAVE_DATA")

    def save_battlecats_save(self, local_path: core.Path) -> core.CommandResult:
        self.get_battlecats_save_path().copy(local_path)
        return core.CommandResult.create_success()

    def load_battlecats_save(self, local_path: core.Path) -> core.CommandResult:
        local_path.copy(self.get_battlecats_save_path())
        return core.CommandResult.create_success()

    def close_game(self) -> core.CommandResult:
        cmd = core.Command(
            f"sudo pkill -f {self.get_package_name()}",
        )
        return cmd.run()

    def run_game(self) -> core.CommandResult:
        cmd = core.Command(
            f"sudo monkey -p {self.get_package_name()} -c android.intent.category.LAUNCHER 1",
        )
        return cmd.run()

    def rerun_game(self) -> core.CommandResult:
        result = self.close_game()
        if not result.success:
            return result
        result = self.run_game()
        if not result.success:
            return result

        return core.CommandResult.create_success()

    def save_locally(
        self, local_path: core.Path | None = None
    ) -> tuple[core.Path | None, core.CommandResult]:
        if local_path is None:
            local_path = core.Path.get_documents_folder().add("saves").add("SAVE_DATA")
        local_path.parent().generate_dirs()
        result = self.save_battlecats_save(local_path)
        if not result.success:
            return None, result

        return local_path, result

    def load_locally(self, local_path: core.Path) -> core.CommandResult:
        success = self.load_battlecats_save(local_path)
        if not success:
            return core.CommandResult.create_failure()

        success = self.rerun_game()
        if not success:
            return core.CommandResult.create_failure()

        return core.CommandResult.create_success()

    def load_save(
        self, save: core.SaveFile, rerun_game: bool = True
    ) -> core.CommandResult:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = core.Path(temp_dir).add("SAVE_DATA")
            save.to_data().to_file(local_path)
            result = self.load_battlecats_save(local_path)
            if not result.success:
                return result
        if rerun_game:
            result = self.rerun_game()

        return result
