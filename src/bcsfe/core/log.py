"""Module for handling logging"""
import traceback
from bcsfe import core
import time


class Logger:
    def __init__(self):
        """
        Initializes a Logger object
        """
        self.log_file = core.Path.get_documents_folder().add("bcsfe.log")
        self.log_data = self.log_file.read(True).split(b"\n")

    def get_time(self) -> str:
        """
        Returns the current time in the format: "HH:MM:SS"

        Returns:
            str: The current time
        """
        return time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())

    def log_debug(self, message: str):
        """
        Logs a debug message

        Args:
            message (str): The message to log
        """
        self.log_data.append(core.Data(f"[DEBUG]::{self.get_time()} - {message}"))
        self.write()

    def log_info(self, message: str):
        """
        Logs an info message

        Args:
            message (str): The message to log
        """
        self.log_data.append(core.Data(f"[INFO]::{self.get_time()} - {message}"))
        self.write()

    def log_warning(self, message: str):
        """
        Logs a warning message

        Args:
            message (str): The message to log
        """
        self.log_data.append(core.Data(f"[WARNING]::{self.get_time()} - {message}"))
        self.write()

    def log_error(self, message: str):
        """
        Logs an error message

        Args:
            message (str): The message to log
        """
        self.log_data.append(core.Data(f"[ERROR]::{self.get_time()} - {message}"))
        self.write()

    def log_exception(self, exception: Exception, extra_msg: str = ""):
        tb = traceback.format_exc()
        if tb == "NoneType: None\n":
            try:
                raise exception
            except Exception:
                tb = traceback.format_exc()

        self.log_error(
            f"{extra_msg}: {exception.__class__.__name__}: {exception}\n{tb}"
        )

    def write(self):
        """
        Writes the log data to the log file
        """
        self.log_file.write(core.Data.from_many(self.log_data, core.Data("\n")).strip())

    def log_no_file_found(self, file_name: str):
        """
        Logs that a file was not found

        Args:
            fileName (str): The name of the file
        """
        self.log_warning(f"Could not find {file_name}")

    @staticmethod
    def get_traceback() -> str:
        """
        Gets the traceback of the last exception

        Returns:
            str: The traceback
        """
        tb = traceback.format_exc()
        if tb == "NoneType: None\n":
            return ""
        return tb
