from __future__ import annotations
from bcsfe.cli import dialog_creator, main, color, file_dialog
from bcsfe import core


class ServerCLI:
    def __init__(self):
        pass

    def download_save(
        self,
    ) -> tuple[core.Path, core.CountryCode] | None:
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
        uuid = dialog_creator.StringInput().get_input_locale_while(
            "enter_uuid", {}
        )
        if uuid is None:
            return None
        gv = core.GameVersion(120200)  # not important

        color.ColoredText.localize(
            "downloading_save_file",
            transfer_code=transfer_code,
            confirmation_code=confirmation_code,
            country_code=cc,
            uuid=uuid,
        )

        server_handler, result = core.ServerHandler.from_codes(
            transfer_code,
            confirmation_code,
            cc,
            gv,
            save_backup=False,
        )
        if server_handler is None and result is not None:
            color.ColoredText.localize("invalid_codes_error")
            if dialog_creator.YesNoInput().get_input_once(
                "display_response_debug_info_q"
            ):
                if result.response is not None:
                    color.ColoredText.localize(
                        "response_text_display",
                        url=result.url,
                        request_headers=result.headers,
                        request_body=result.data,
                        response_headers=result.response.headers,
                        response_body=result.response.text,
                    )
            return
        if server_handler is None:
            return

        save_file = server_handler.save_file
        path = core.Path("/home/container/saves").add(f"SAVE_DATA-{uuid}")

        save_file.to_file(path)

        color.ColoredText.localize("save_downloaded", path=path.to_str())

        return path, cc
