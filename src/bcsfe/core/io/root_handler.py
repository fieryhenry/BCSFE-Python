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

    def save_battlecats_save(self, local_path: io.path.Path):
        self.get_battlecats_save_path().copy(local_path)

    def load_battlecats_save(self, local_path: io.path.Path):
        self.get_battlecats_save_path().copy(local_path)

    def close_game(self):
        cmd = io.command.Command(
            f"am force-stop {self.get_battlecats_package_name()}",
        )
        cmd.run()

    def run_game(self):
        cmd = io.command.Command(
            f"monkey -p {self.get_battlecats_package_name()} 1",
        )
        cmd.run()

    def rerun_game(self):
        self.close_game()
        self.run_game()

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

    def load_locally(self, local_path: io.path.Path):
        self.load_battlecats_save(local_path)
        self.rerun_game()

    def load_save(self, save: io.save.SaveFile, rerun_game: bool = True):
        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = io.path.Path(temp_dir).add("SAVE_DATA")
            save.to_data().to_file(local_path)
            self.load_battlecats_save(local_path)
        if rerun_game:
            self.rerun_game()
