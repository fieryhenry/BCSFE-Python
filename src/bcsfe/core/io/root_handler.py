from typing import Optional
from bcsfe import core
import tempfile


class CCNotSet(Exception):
    pass


class RootHandler:
    def __init__(self):
        self.cc = None

    def is_android(self) -> bool:
        return core.Path.get_root().add("system").exists()

    def get_cc(self) -> "core.CountryCode":
        if self.cc is None:
            raise CCNotSet("Country Code is not set")
        return self.cc

    def set_cc(self, cc: "core.CountryCode"):
        self.cc = cc

    def get_battlecats_packages(self) -> list[str]:
        packages = core.Path.get_root().add("data").add("data").get_dirs()
        packages = [
            package.basename()
            for package in packages
            if "jp.co.ponos.battlecats" in package.basename()
        ]
        return packages

    def get_battlecats_cc(self, package_name: str) -> "core.CountryCode":
        cc = package_name.replace("jp.co.ponos.battlecats", "")
        cc = core.CountryCode.from_patching_code(cc)
        return cc

    def get_battlecats_ccs(self) -> list["core.CountryCode"]:
        packages = self.get_battlecats_packages()
        return [self.get_battlecats_cc(package) for package in packages]

    def get_battlecats_package_name(self) -> str:
        cc = self.get_cc()
        return f"jp.co.ponos.battlecats{cc.get_patching_code()}"

    def get_battlecats_path(self) -> "core.Path":
        return (
            core.Path.get_root()
            .add("data")
            .add("data")
            .add(self.get_battlecats_package_name())
        )

    def get_battlecats_save_path(self) -> "core.Path":
        return self.get_battlecats_path().add("files").add("SAVE_DATA")

    def save_battlecats_save(self, local_path: "core.Path") -> "core.CommandResult":
        self.get_battlecats_save_path().copy(local_path)
        return core.CommandResult.create_success()

    def load_battlecats_save(self, local_path: "core.Path") -> "core.CommandResult":
        local_path.copy(self.get_battlecats_save_path())
        return core.CommandResult.create_success()

    def close_game(self) -> "core.CommandResult":
        cmd = core.Command(
            f"sudo pkill -f {self.get_battlecats_package_name()}",
        )
        return cmd.run()

    def run_game(self) -> "core.CommandResult":
        cmd = core.Command(
            f"sudo monkey -p {self.get_battlecats_package_name()} -c android.intent.category.LAUNCHER 1",
        )
        return cmd.run()

    def rerun_game(self) -> "core.CommandResult":
        success = self.close_game()
        if not success:
            return core.CommandResult.create_failure()
        success = self.run_game()
        if not success:
            return core.CommandResult.create_failure()

        return core.CommandResult.create_success()

    def save_locally(self) -> tuple[Optional["core.Path"], "core.CommandResult"]:
        local_path = core.Path.get_documents_folder().add("saves").add("SAVE_DATA")
        local_path.parent().generate_dirs()
        result = self.save_battlecats_save(local_path)
        if not result.success:
            return None, result

        return local_path, result

    def get_save_file(
        self,
    ) -> tuple[Optional["core.SaveFile"], "core.CommandResult"]:
        path, result = self.save_locally()
        if path is None:
            return None, result
        return core.SaveFile(path.read()), result

    def load_locally(self, local_path: "core.Path") -> "core.CommandResult":
        success = self.load_battlecats_save(local_path)
        if not success:
            return core.CommandResult.create_failure()

        success = self.rerun_game()
        if not success:
            return core.CommandResult.create_failure()

        return core.CommandResult.create_success()

    def load_save(
        self, save: "core.SaveFile", rerun_game: bool = True
    ) -> "core.CommandResult":
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = core.Path(temp_dir).add("SAVE_DATA")
            save.to_data().to_file(local_path)
            result = self.load_battlecats_save(local_path)
            if not result.success:
                return result
        if rerun_game:
            result = self.rerun_game()

        return result
