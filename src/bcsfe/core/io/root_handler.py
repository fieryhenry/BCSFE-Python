from bcsfe.core import io, country_code
import tempfile
import datetime


class CCNotSet(Exception):
    pass


class RootHandler:
    def __init__(self):
        self.cc = None

    def is_android(self) -> bool:
        return io.path.Path("/").add("system").exists()

    def get_cc(self) -> country_code.CountryCode:
        if self.cc is None:
            raise CCNotSet("Country Code is not set")
        return self.cc

    def set_cc(self, cc: country_code.CountryCode):
        self.cc = cc

    def get_battlecats_packages(self) -> list[str]:
        packages = io.path.Path("/").add("data").add("data").get_dirs()
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
            io.path.Path("/")
            .add("data")
            .add("data")
            .add(self.get_battlecats_package_name())
        )

    def get_battlecats_save_path(self) -> io.path.Path:
        return self.get_battlecats_path().add("files").add("SAVE_DATA")

    def save_battlecats_save(self, local_path: io.path.Path) -> bool:
        self.get_battlecats_save_path().copy(local_path)
        return True

    def load_battlecats_save(self, local_path: io.path.Path) -> bool:
        self.get_battlecats_save_path().copy(local_path)
        return True

    def close_game(self) -> bool:
        cmd = io.command.Command(
            f"sudo pkill -f {self.get_battlecats_package_name()}",
        )
        return cmd.run().success

    def run_game(self) -> bool:
        cmd = io.command.Command(
            f"sudo monkey -p {self.get_battlecats_package_name()} -c android.intent.category.LAUNCHER 1",
        )
        return cmd.run().success

    def rerun_game(self) -> bool:
        success = self.close_game()
        if not success:
            return False
        success = self.run_game()
        if not success:
            return False

        return True

    def save_locally(self) -> io.path.Path:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = io.path.Path(temp_dir).add("SAVE_DATA")
            self.save_battlecats_save(local_path)
            try:
                save_file = io.save.SaveFile(local_path.read())
                inquiry_code = save_file.inquiry_code
            except Exception:
                inquiry_code = "UNKNOWN"
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        local_path = (
            io.path.Path.get_appdata_folder()
            .add("saves")
            .add(f"{self.get_cc().get_code()}")
            .add(inquiry_code)
        )
        local_path.generate_dirs()
        self.save_battlecats_save(local_path)
        local_path = local_path.add("SAVE_DATA")
        local_path.rename(date)
        return local_path

    def get_save_file(self) -> io.save.SaveFile:
        path = self.save_locally()
        return io.save.SaveFile(path.read())

    def load_locally(self, local_path: io.path.Path) -> bool:
        success = self.load_battlecats_save(local_path)
        if not success:
            return False

        success = self.rerun_game()
        if not success:
            return False

        return True

    def load_save(self, save: io.save.SaveFile, rerun_game: bool = True) -> bool:
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = io.path.Path(temp_dir).add("SAVE_DATA")
            save.to_data().to_file(local_path)
            success = self.load_battlecats_save(local_path)
            if not success:
                return False
        if rerun_game:
            success = self.rerun_game()
            if not success:
                return False

        return True
