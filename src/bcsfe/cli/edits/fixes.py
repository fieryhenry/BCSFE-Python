from __future__ import annotations
from bcsfe import core
from bcsfe.cli import color
import datetime


class Fixes:
    @staticmethod
    def fix_gamatoto_crash(save_file: core.SaveFile):
        save_file.gamatoto.skin = 2

        color.ColoredText.localize("fix_gamatoto_crash_success")

    @staticmethod
    def fix_ototo_crash(save_file: core.SaveFile):
        save_file.ototo.cannons = core.game.gamoto.ototo.Cannons.init(
            save_file.game_version
        )
        color.ColoredText.localize("fix_ototo_crash_success")

    @staticmethod
    def fix_time_errors(save_file: core.SaveFile):
        save_file.date_3 = datetime.datetime.now()
        save_file.timestamp = datetime.datetime.now().timestamp()
        save_file.energy_penalty_timestamp = datetime.datetime.now().timestamp()

        color.ColoredText.localize("fix_time_errors_success")

        # 10 = 62 / hgt1 = ahead by too much
        # 11 = 63 / hgt0 = behind by too much
        # 12 = 61 / hgt2 = ahead by too much

        # date_3 - controls gacha errors (hgt2)
        # can't be ahead of the device time

        # timestamp - controls gacha errors (hgt1, hgt0)
        # can't be ahead by more than 10 minutes to device time
        # can't be behind by more than 1.5 days to device time

        # penalty_timestamp - controls energy / gamatoto errors
        # can't by ahead of device time
        # can't be ahead by more than 1 day to device time
        # can't be behind by more than 1 day to device time
