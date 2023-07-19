from typing import Optional
from bcsfe.cli import dialog_creator, main, color
from bcsfe import core


class ServerCLI:
    def __init__(self):
        pass

    def download_save(
        self,
    ) -> Optional[tuple["core.Path", "core.CountryCode"]]:
        transfer_code = dialog_creator.StringInput().get_input_locale_while(
            "enter_transfer_code", {}
        )
        if transfer_code is None:
            return None
        confirmation_code = dialog_creator.StringInput().get_input_locale_while(
            "enter_confirmation_code", {}
        )
        if confirmation_code is None:
            return None
        cc = core.CountryCode.select()
        if cc is None:
            return None
        gv = core.GameVersion(120200)  # not important

        color.ColoredText.localize(
            "downloading_save_file",
            transfer_code=transfer_code,
            confirmation_code=confirmation_code,
            country_code=cc,
        )

        server_handler = core.ServerHandler.from_codes(
            transfer_code,
            confirmation_code,
            cc,
            gv,
        )
        if server_handler is None:
            color.ColoredText.localize("invalid_codes_error")
            return

        save_file = server_handler.save_file
        path = main.Main().save_save_dialog(save_file)
        if path is None:
            return None

        save_file.to_file(path)

        color.ColoredText.localize("save_downloaded", path=path.to_str())

        return path, cc
