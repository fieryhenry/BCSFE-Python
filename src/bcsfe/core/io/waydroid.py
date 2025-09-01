from __future__ import annotations

from bcsfe import core
from bcsfe.cli import color
from bcsfe.core import io
from bcsfe.core.io.command import CommandResult


class WayDroidNotInstalledError(Exception):
    def __init__(self, result: CommandResult):
        self.result = result


class WayDroidHandler(io.root_handler.RootHandler):
    def __init__(self):
        self.check_waydroid_installed()

        self.adb_handler = io.adb_handler.AdbHandler(root=False)

        self.package_name = None

    def set_package_name(self, package_name: str):
        self.package_name = package_name
        self.adb_handler.set_package_name(self.package_name)

    @staticmethod
    def display_waydroid_not_installed(e: WayDroidNotInstalledError):
        color.ColoredText.localize("waydroid_not_installed", error=e)
        return

    @staticmethod
    def check_waydroid_installed():
        result = io.command.Command("waydroid -V").run()
        if not result.success:
            raise WayDroidNotInstalledError(result)

    def run_shell_cmd(self, command: str) -> core.CommandResult:
        cmd = "waydroid shell"
        use_pkexec = core.core_data.config.get_bool(core.ConfigKey.USE_PKEXEC_WAYDROID)
        if use_pkexec:
            cmd = "pkexec " + cmd
        return io.command.Command(cmd).run(f"{command}")

    def pull_file(
        self, device_path: core.Path, local_path: core.Path
    ) -> core.CommandResult:
        # copy file to sdcard

        result = self.run_shell_cmd(
            f"cp {device_path.to_str_forwards()} /sdcard/{device_path.basename()} && chmod o+rw /sdcard/{device_path.basename()}"
        )

        if not result.success:
            return result

        device_path = core.Path("/sdcard/").add(device_path.basename())

        # adb pull

        result = self.adb_handler.adb_pull_file(device_path, local_path)
        if not result.success:
            return result

        # delete /sdcard file again
        #
        return self.adb_handler.run_shell(f"rm /sdcard/{device_path.basename()}")

    def push_file(
        self, local_path: core.Path, device_path: core.Path
    ) -> core.CommandResult:
        original_device_path = device_path.copy_object()

        device_path = core.Path("/sdcard/").add(device_path.basename())

        # push to /sdcard with adb

        import time

        time.sleep(0.25)
        result = self.adb_handler.adb_push_file(local_path, device_path)

        if not result.success:
            return result

        result = self.run_shell_cmd(
            f"cp '/sdcard/{device_path.basename()}' '{original_device_path.to_str_forwards()}' && chmod o+rw '{original_device_path.to_str_forwards()}'"
        )

        if not result.success:
            return result

        # remove temp file
        #
        return self.adb_handler.run_shell(f"rm '/sdcard/{device_path.basename()}'")

    def get_battlecats_packages(self) -> list[str]:
        cmd = "find /data/data/ -name SAVE_DATA -mindepth 3 -maxdepth 3"
        result = self.run_shell_cmd(cmd)

        if not result.success:
            return []

        packages: list[str] = []

        for package in result.result.split("\n"):
            parts = package.split("/")
            if len(parts) < 4:
                continue

            packages.append(package.split("/")[3])

        return packages

    def save_battlecats_save(self, local_path: core.Path) -> core.CommandResult:
        return self.pull_file(self.get_battlecats_save_path(), local_path)

    def load_battlecats_save(self, local_path: core.Path) -> core.CommandResult:
        return self.push_file(local_path, self.get_battlecats_save_path())

    def run_game(self) -> core.CommandResult:
        return self.adb_handler.run_game()

    def close_game(self) -> core.CommandResult:
        return self.adb_handler.close_game()
