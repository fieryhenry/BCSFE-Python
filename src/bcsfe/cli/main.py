from __future__ import annotations

"""Main class for the CLI."""

import sys
import traceback
from typing import Any, NoReturn
from bcsfe.cli import (
    file_dialog,
    color,
    feature_handler,
    save_management,
    dialog_creator,
)
from bcsfe import core


class Main:
    """Main class for the CLI."""

    def __init__(self):
        self.save_file = None
        self.exit = False
        self.save_path = None
        self.fh = None

    def wipe_temp_save(self):
        """Wipe the temp save."""
        core.SaveFile.get_temp_path().remove()

    def main(self, input_path: str | None = None):
        """Main function for the CLI."""
        self.wipe_temp_save()
        core.GameDataGetter.delete_old_versions(5)
        self.check_update()
        print()
        self.print_start_text()
        while not self.exit:
            stop = self.load_save_options(input_path)
            if stop:
                break

    def check_update(self):
        """Check for updates."""

        updater = core.Updater()
        has_pre_release = updater.has_enabled_pre_release()
        local_version = updater.get_local_version()
        latest_version = updater.get_latest_version(has_pre_release)

        if latest_version is None:
            color.ColoredText.localize("update_check_fail")
            return

        color.ColoredText.localize(
            "version_line",
            local_version=local_version,
            latest_version=latest_version,
        )

        is_local_beta = "b" in local_version
        is_latest_beta = "b" in latest_version

        local_no_beta = local_version.split("b")[0]
        latest_no_beta = latest_version.split("b")[0]

        if latest_no_beta > local_no_beta:
            update_needed = True
        elif latest_no_beta < local_no_beta:
            update_needed = False
        else:
            if latest_version == local_version:
                update_needed = False
            else:
                if is_local_beta and is_latest_beta:
                    update_needed = latest_version > local_version
                elif is_local_beta:
                    update_needed = True
                else:
                    update_needed = False

        show_message = core.core_data.config.get(core.ConfigKey.SHOW_UPDATE_MESSAGE)
        if not show_message:
            update_needed = False

        if update_needed:
            update = dialog_creator.YesNoInput(True).get_input_once(
                "update_available", {"latest_version": latest_version}
            )
            if update is None:
                return

            if update:
                if updater.update(latest_version):
                    color.ColoredText.localize("update_success")
                else:
                    color.ColoredText.localize("update_fail")
                sys.exit()
            else:
                disable_message = dialog_creator.YesNoInput(False).get_input_once(
                    "disable_update_message"
                )
                if disable_message is None:
                    return

                core.core_data.config.set(
                    core.ConfigKey.SHOW_UPDATE_MESSAGE, not disable_message
                )

    def print_start_text(self):
        external_theme = core.ExternalThemeManager.get_external_theme_config()
        external_locale = core.ExternalLocaleManager.get_external_locale_config()
        if external_theme is None:
            theme_text = core.core_data.local_manager.get_key(
                "theme_text",
                theme_path=core.ThemeHandler.get_theme_path(
                    core.core_data.theme_manager.theme_code
                ),
                theme_version=core.core_data.theme_manager.get_version(),
                theme_author=core.core_data.theme_manager.get_author(),
                theme_name=core.core_data.theme_manager.get_name(),
                escape=False,
            )
        else:
            theme_text = core.core_data.local_manager.get_key(
                "theme_text",
                theme_name=external_theme.name,
                theme_version=external_theme.version,
                theme_author=external_theme.author,
                theme_path=core.ThemeHandler.get_theme_path(
                    external_theme.get_full_name()
                ),
                escape=False,
            )
        if external_locale is None:
            authors = core.core_data.local_manager.authors
            locale_text = core.core_data.local_manager.get_key(
                "default_locale_text_authors",
                path=core.core_data.local_manager.path,
                authors=", ".join(authors),
                name=core.core_data.local_manager.name,
                escape=False,
            )
        else:
            locale_text = core.core_data.local_manager.get_key(
                "locale_text",
                locale_name=external_locale.name,
                locale_version=external_locale.version,
                locale_author=external_locale.author,
                locale_path=core.LocalManager.get_locale_folder(
                    external_locale.get_full_name()
                ),
                escape=False,
            )
        color.ColoredText.localize(
            "welcome",
            config_path=core.core_data.config.get_config_path(),
            locale_text=locale_text,
            theme_text=theme_text,
            escape=False,
        )
        print()

    def load_save_options(self, input_path: str | None = None):
        """Load save options."""
        save_file, stop = save_management.SaveManagement.select_save(True, input_path)
        if save_file is None:
            return stop
        self.save_file = save_file

        self.feature_handler()
        return False

    def feature_handler(self):
        """Run the feature handler."""
        if self.save_file is None:
            return
        self.fh = feature_handler.FeatureHandler(self.save_file)
        self.fh.select_features_run()

    @staticmethod
    def save_save_dialog(save_file: core.SaveFile) -> core.Path | None:
        """Save save file dialog.

        Args:
            save_file (core.SaveFile): Save file to save.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file(
            "save_save_dialog",
            initialdir=core.SaveFile.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
        )
        if path is None:
            return None
        path = core.Path(path)
        path.parent().generate_dirs()
        save_file.save_path = path
        return path

    @staticmethod
    def save_json_dialog(json_data: dict[str, Any]) -> core.Path | None:
        """Save json file dialog.

        Args:
            json_data (dict): Json data to save.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().save_file(
            "save_json_dialog",
            initialfile="SAVE_DATA.json",
            initialdir=core.SaveFile.get_saves_path().to_str(),
        )
        if path is None:
            return None
        path = core.Path(path)
        path.parent().generate_dirs()
        core.JsonFile.from_object(json_data).to_data().to_file(path)
        return path

    @staticmethod
    def load_save_file() -> core.Path | None:
        """Load save file from file dialog.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file(
            "select_save_file",
            initialdir=core.SaveFile.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
            ignore_json=True,
        )
        if path is None:
            return None
        path = core.Path(path)
        return path

    @staticmethod
    def load_save_data_json() -> tuple[core.Path, core.CountryCode] | None:
        """Load save data from json file.

        Returns:
            core.Path: Path to save file.
        """
        path = file_dialog.FileDialog().get_file(
            "load_save_data_json",
            initialfile="SAVE_DATA.json",
            initialdir=core.SaveFile.get_saves_path().to_str(),
        )
        if path is None:
            return None
        path = core.Path(path)
        if not path.exists():
            return None
        try:
            json_data = core.JsonFile.from_data(path.read()).to_object()
        except core.JSONDecodeError:
            color.ColoredText.localize(
                "load_json_fail", error=core.core_data.logger.get_traceback()
            )
            return None
        try:
            save_file = core.SaveFile.from_dict(json_data)
        except core.SaveError:
            color.ColoredText.localize(
                "load_json_fail", error=core.core_data.logger.get_traceback()
            )
            return None
        path = Main.save_save_dialog(save_file)
        if path is None:
            return None
        save_file.to_file(path)
        return path, save_file.cc

    @staticmethod
    def exit_editor(
        save_file: core.SaveFile | None = None, check_temp: bool = True
    ) -> NoReturn:
        """Exit the editor."""
        save_file_temp = None
        if check_temp:
            temp_path = core.SaveFile.get_temp_path()
            if temp_path.exists():
                try:
                    save_file_temp = core.SaveFile(temp_path.read())
                except core.SaveError as e:
                    tb = traceback.format_exc()
                    color.ColoredText.localize(
                        "save_temp_fail", error=str(e), traceback=tb
                    )
                    Main.leave()

        if save_file is None:
            save_file = save_file_temp
        if save_file is None:
            if check_temp:
                color.ColoredText.localize("save_temp_not_found")
            Main.leave()
        if save_file_temp is None:
            save_file_temp = save_file

        try:
            print()
            color.ColoredText.localize("checking_for_changes")
            if save_file.save_path is None:
                same = False
            else:
                same = save_file.save_path.read() == save_file.to_data()
        except core.SaveError:
            same = False

        if not same:
            color.ColoredText.localize("changes_found")
            print()
            save = color.ColoredInput().localize("save_before_exit") == "y"
            if save:
                save_management.SaveManagement.save_save(save_file)
        else:
            color.ColoredText.localize("no_changes")

        Main.leave()

    @staticmethod
    def leave() -> NoReturn:
        """Leave the editor."""
        color.ColoredText.localize("leave")
        sys.exit()
