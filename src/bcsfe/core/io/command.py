from __future__ import annotations
import subprocess
import threading


class CommandResult:
    def __init__(self, result: str, exit_code: int):
        self.result = result
        self.exit_code = exit_code

    def __str__(self) -> str:
        return self.result

    def __repr__(self) -> str:
        return f"Result({self.result!r}, {self.exit_code!r})"

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    @staticmethod
    def create_success(result: str = "") -> CommandResult:
        return CommandResult(result, 0)

    @staticmethod
    def create_failure(result: str = "") -> CommandResult:
        return CommandResult(result, 1)


class Command:
    def __init__(self, command: str, display_output: bool = True):
        self.command = command
        self.display_output = display_output

    def run(self, inputData: str = "\n") -> CommandResult:
        self.process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            shell=True,
            universal_newlines=True,
        )
        output, _ = self.process.communicate(inputData)
        return_code = self.process.wait()
        return CommandResult(output, return_code)

    def run_in_thread(self, inputData: str = "\n") -> None:
        self.thread = threading.Thread(target=self.run, args=(inputData,))
        self.thread.start()
