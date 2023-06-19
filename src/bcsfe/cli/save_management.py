from bcsfe.core import io, server
from bcsfe.cli import main, color


class SaveManagement:
    def __init__(self):
        pass

    @staticmethod
    def save_save(save_file: "io.save.SaveFile"):
        """Save the save file."""
        if save_file.save_path is None:
            save_file.save_path = main.Main.save_save_dialog(save_file)

        if save_file.save_path is None:
            return
        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_save_dialog(save_file: "io.save.SaveFile"):
        """Save the save file."""
        save_file.save_path = main.Main.save_save_dialog(save_file)
        if save_file.save_path is None:
            return
        save_file.to_file(save_file.save_path)

        color.ColoredText.localize("save_success", path=save_file.save_path)

    @staticmethod
    def save_upload(save_file: "io.save.SaveFile"):
        """Upload the save file."""
        result = server.server_handler.ServerHandler(save_file).get_codes()
        SaveManagement.save_save(save_file)
        if result is not None:
            transfer_code, confirmation_code = result
            color.ColoredText.localize(
                "upload_result",
                transfer_code=transfer_code,
                confirmation_code=confirmation_code,
            )
        else:
            color.ColoredText.localize("upload_fail")

    @staticmethod
    def unban_account(save_file: "io.save.SaveFile"):
        server_handler = server.server_handler.ServerHandler(save_file)
        success = server_handler.create_new_account()
        if success:
            color.ColoredText.localize("unban_success")
        else:
            color.ColoredText.localize("unban_fail")

    @staticmethod
    def adb_push(save_file: "io.save.SaveFile") -> "io.adb_handler.AdbHandler":
        """Push the save file to the device.

        Args:
            save_file (io.save.SaveFile): The save file to push.

        Returns:
            io.adb_handler.AdbHandler: The AdbHandler instance.
        """
        SaveManagement.save_save(save_file)
        adb_handler = io.adb_handler.AdbHandler()
        adb_handler.select_device()
        adb_handler.set_cc(save_file.cc)
        if save_file.save_path is None:
            return adb_handler
        result = adb_handler.load_battlecats_save(save_file.save_path)
        if result.success:
            color.ColoredText.localize("adb_push_success")
        else:
            color.ColoredText.localize("adb_push_fail", error=result.result)

        return adb_handler

    @staticmethod
    def adb_push_rerun(save_file: "io.save.SaveFile"):
        """Push the save file and rerun the game."""
        adb_handler = SaveManagement.adb_push(save_file)
        result = adb_handler.rerun_game()
        if result.success:
            color.ColoredText.localize("adb_rerun_success")
        else:
            color.ColoredText.localize("adb_rerun_fail", error=result.result)

    @staticmethod
    def export_save(save_file: "io.save.SaveFile"):
        """Export the save file to a json file."""
        data = save_file.to_dict()
        path = main.Main.save_json_dialog(data)
        if path is None:
            return
        data = io.json_file.JsonFile.from_object(data).to_data()
        data.to_file(path)
        color.ColoredText.localize("export_success", path=path)
