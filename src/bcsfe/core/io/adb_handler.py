from bcsfe.core import io, country_code
import tempfile
import datetime


class DeviceIDNotSet(Exception):
    pass


class CCNotSet(Exception):
    pass


class AdbHandler:
    def __init__(self, adb_path: io.path.Path):
        self.adb_path = adb_path
        self.start_server()
        self.root()
        self.device_id = None
        self.cc = None

    def start_server(self):
        self.adb_path.run("start-server")

    def kill_server(self):
        self.adb_path.run("kill-server")

    def root(self):
        self.adb_path.run("root")

    def get_connected_devices(self) -> list[str]:
        devices = self.adb_path.run("devices").result.split("\n")
        devices = [device.split("\t")[0] for device in devices[1:-2]]
        return devices

    def set_device(self, device_id: str):
        self.device_id = device_id

    def set_cc(self, cc: country_code.CountryCode):
        self.cc = cc

    def get_device(self) -> str:
        if self.device_id is None:
            raise DeviceIDNotSet("Device ID is not set")
        return self.device_id

    def get_cc(self) -> country_code.CountryCode:
        if self.cc is None:
            raise CCNotSet("Country code is not set")
        return self.cc

    def get_device_name(self) -> str:
        return self.adb_path.run(
            f"-s {self.get_device()} shell getprop ro.product.model"
        ).result.strip()

    def pull_file(self, device_path: io.path.Path, local_path: io.path.Path):
        self.adb_path.run(
            f"-s {self.get_device()} pull {device_path} {local_path}"
        ).result

    def push_file(self, local_path: io.path.Path, device_path: io.path.Path):
        self.adb_path.run(f"-s {self.get_device()} push {local_path} {device_path}")

    def get_packages(self) -> list[str]:
        return self.adb_path.run(
            f"-s {self.get_device()} shell pm list packages"
        ).result.split("\n")

    def get_package_name(self, package: str) -> str:
        return package.split(":")[1]

    def get_battlecats_packages(self) -> list[str]:
        packages = self.get_packages()
        return [
            self.get_package_name(package)
            for package in packages
            if "jp.co.ponos.battlecats" in package
        ]

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
        return io.path.Path(
            f"/data/data/{self.get_battlecats_package_name()}",
        )

    def get_battlecats_save_path(self) -> io.path.Path:
        return self.get_battlecats_path().add("files").add("SAVE_DATA")

    def save_battlecats_save(self, local_path: io.path.Path):
        self.pull_file(self.get_battlecats_save_path(), local_path)

    def load_battlecats_save(self, local_path: io.path.Path):
        self.push_file(local_path, self.get_battlecats_save_path())

    def close_game(self):
        self.adb_path.run(
            f"-s {self.get_device()} shell am force-stop {self.get_battlecats_package_name()}"
        )

    def run_game(self):
        self.adb_path.run(
            f"-s {self.get_device()} shell monkey -p {self.get_battlecats_package_name()} -c android.intent.category.LAUNCHER 1"
        )

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
            .add(f"{self.get_device_name()}")
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
