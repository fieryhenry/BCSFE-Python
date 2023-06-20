from typing import Optional
from bcsfe.core import io, country_code
import tempfile
import datetime


class CCNotSet(Exception):
    pass


class RootHandler:
    def __init__(self):
        self.cc = None

    def is_android(self) -> bool:
        return io.path.Path.get_root().add("system").exists()

    def get_cc(self) -> country_code.CountryCode:
        if self.cc is None:
            raise CCNotSet("Country Code is not set")
        return self.cc

    def set_cc(self, cc: country_code.CountryCode):
        self.cc = cc

    def get_battlecats_packages(self) -> list[str]:
        packages = io.path.Path.get_root().add("data").add("data").get_dirs()
        packages = [
            package.basename()
            for package in packages
            if "jp.co.ponos.battlecats" in package.basename()
        ]
        return packages

    def get_battlecats_cc(self, package_name: str) -> country_code.CountryCode:
        cc = package_name.replace("jp.co.ponos.battlecats", "")
        cc = country_code.CountryCode.from_patching_code(cc)
        return cc

    def get_battlecats_ccs(self) -> list[country_code.CountryCode]:
        packages = self.get_battlecats_packages()
        return [self.get_battlecats_cc(package) for package in packages]

    def get_battlecats_package_name(self) -> str:
        cc = self.get_cc()
        return f"jp.co.ponos.battlecats{cc.get_patching_code()}"

    def get_battlecats_path(self) -> io.path.Path:
        return (
            io.path.Path.get_root()
            .add("data")
            .add("data")
            .add(self.get_battlecats_package_name())
        )

    def get_battlecats_save_path(self) -> io.path.Path:
        return self.get_battlecats_path().add("files").add("SAVE_DATA")

    def save_battlecats_save(self, local_path: io.path.Path) -> "io.command.Result":
        self.get_battlecats_save_path().copy(local_path)
        return io.command.Result.create_success()

    def load_battlecats_save(self, local_path: io.path.Path) -> "io.command.Result":
        self.get_battlecats_save_path().copy(local_path)
        return io.command.Result.create_success()

    def close_game(self) -> "io.command.Result":
        cmd = io.command.Command(
            f"sudo pkill -f {self.get_battlecats_package_name()}",
        )
        return cmd.run()

    def run_game(self) -> "io.command.Result":
        cmd = io.command.Command(
            f"sudo monkey -p {self.get_battlecats_package_name()} -c android.intent.category.LAUNCHER 1",
        )
        return cmd.run()

    def rerun_game(self) -> "io.command.Result":
        success = self.close_game()
        if not success:
            return io.command.Result.create_failure()
        success = self.run_game()
        if not success:
            return io.command.Result.create_failure()

        return io.command.Result.create_success()

    def save_locally(self) -> tuple[Optional[io.path.Path], "io.command.Result"]:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = io.path.Path(temp_dir).add("SAVE_DATA")
            result = self.save_battlecats_save(local_path)
            if not result.success:
                return None, result

            try:
                save_file = io.save.SaveFile(local_path.read())
                inquiry_code = save_file.inquiry_code
            except Exception:
                inquiry_code = "UNKNOWN"

        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        local_path = (
            io.path.Path.get_appdata_folder()
            .add("saves")
            .add("backups")
            .add(f"{self.get_cc().get_code()}")
            .add(inquiry_code)
        )
        local_path.generate_dirs()
        self.save_battlecats_save(local_path)
        local_path = local_path.add("SAVE_DATA")
        local_path.rename(date)
        new_path = io.path.Path.get_appdata_folder().add("saves").add("SAVE_DATA")
        local_path.copy(new_path)
        return local_path, result

    def get_save_file(self) -> tuple[Optional[io.save.SaveFile], "io.command.Result"]:
        path, result = self.save_locally()
        if path is None:
            return None, result
        return io.save.SaveFile(path.read()), result

    def load_locally(self, local_path: io.path.Path) -> "io.command.Result":
        success = self.load_battlecats_save(local_path)
        if not success:
            return io.command.Result.create_failure()

        success = self.rerun_game()
        if not success:
            return io.command.Result.create_failure()

        return io.command.Result.create_success()

    def load_save(
        self, save: io.save.SaveFile, rerun_game: bool = True
    ) -> "io.command.Result":
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = io.path.Path(temp_dir).add("SAVE_DATA")
            save.to_data().to_file(local_path)
            result = self.load_battlecats_save(local_path)
            if not result.success:
                return result
        if rerun_game:
            result = self.rerun_game()

        return result
