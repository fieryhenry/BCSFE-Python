from __future__ import annotations
from bcsfe.cli import dialog_creator, main, color, file_dialog
from bcsfe import core


class ServerCLI:
    def __init__(self):
        pass

    def download_save(
        self,
    ) -> tuple[core.Path, core.CountryCode] | None:
        transfer_code = dialog_creator.str_input_key("enter_transfer_code")
        if transfer_code is None:
            return None
        confirmation_code = dialog_creator.str_input_key("enter_confirmation_code")
        if confirmation_code is None:
            return None
        cc = core.CountryCode.select()
        if cc is None:
            return None
        gv = core.GameVersion(120200)  # not important

        color.color_print_key(
            "downloading_save_file",
            transfer_code=transfer_code,
            confirmation_code=confirmation_code,
            country_code=cc,
        )

        server_handler, result = core.ServerHandler.from_codes(
            transfer_code,
            confirmation_code,
            cc,
            gv,
        )
        if server_handler is None and result is not None:
            color.color_print_key("invalid_codes_error")
            if cc == "jp":
                color.color_print_key("jp_tw_mixup")
            # if dialog_creator.yes_no_key("display_response_debug_info_q"):
            #     if result.response is not None:
            #         color.color_print_key(
            #             "response_text_display",
            #             url=result.url,
            #             request_headers=result.headers,
            #             request_body=result.data,
            #             response_headers=result.response.headers,
            #             response_body=result.response.text,
            #         )
            return
        if server_handler is None:
            return

        save_file = server_handler.save_file
        if file_dialog.FileDialog().filedialog is None:
            path = core.SaveFile.get_saves_path().add("SAVE_DATA")
        else:
            path = main.Main().save_save_dialog(save_file)
        if path is None:
            return None

        try:
            save_file.to_file(path)
        except OSError as e:
            print(
                f"failed to write save file to: {path} due to: {e}. Skipping writing the save file to disk"
            )
            input("press enter to continue anyway")

        color.color_print_key("save_downloaded", path=path.to_str())

        return path, cc
