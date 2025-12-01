from __future__ import annotations
import base64
from typing import Any
from bcsfe import core, __version__, cli
import datetime

from bcsfe.cli.color import ColoredText
from bcsfe.core.io.config import ConfigKey


class SaveError(Exception):
    pass


class CantDetectSaveCCError(SaveError):
    pass


class SaveFileInvalid(SaveError):
    pass


class FailedToLoadError(SaveError):
    pass


class FailedToSaveError(SaveError):
    pass


class SaveFile:
    def __init__(
        self,
        dt: core.Data | None = None,
        cc: core.CountryCode | None = None,
        load: bool = True,
        gv: core.GameVersion | None = None,
        package_name: str | None = None,
    ):
        self.package_name = package_name
        self.save_path: core.Path | None = None
        if dt is None:
            self.data = core.Data()
        else:
            self.data = dt
        detected_cc = self.detect_cc()
        if detected_cc is None:
            if cc is None:
                raise CantDetectSaveCCError(
                    core.core_data.local_manager.get_key("cant_detect_cc")
                )
            self.cc = cc
        else:
            self.cc = detected_cc

        self.used_storage = False

        self.localizable: core.Localizable | None = None

        self.init_save(gv)

        if dt is not None and load:
            self.load_wrapper()

    def get_localizable(self) -> core.Localizable:
        if self.localizable is None:
            self.localizable = core.Localizable(self)
        return self.localizable

    def load_save_file(self, other: SaveFile):
        self.data = other.data
        self.cc = other.cc
        self.game_version = other.game_version
        self.init_save(other.game_version)
        self.load_wrapper()

    def detect_cc(self) -> core.CountryCode | None:
        for cc in core.CountryCode.get_all():
            self.cc = cc
            if self.verify_hash():
                return cc
        return None

    def get_salt(self) -> str:
        """Get the salt for the save file. This is used for hashing the save file.

        Returns:
            str: The salt
        """
        salt = f"battlecats{self.cc.get_patching_code()}"
        return salt

    def get_current_hash(self) -> str:
        """Get the current hash for the save file. This is used for hashing the save file.

        Returns:
            str: The current hash
        """
        self.data.reset_pos()
        self.data.set_pos(-32)
        hash = self.data.read_string(32)
        return hash

    def get_new_hash(self, existing_hash: bool = True) -> str:
        """Get the new hash for the save file. This is used for hashing the save file.

        Returns:
            str: The new hash
        """
        salt = self.get_salt()
        self.data.reset_pos()
        if existing_hash:
            data_to_hash = self.data.read_bytes(len(self.data) - 32)
        else:
            data_to_hash = self.data.read_bytes(len(self.data))
        salted_data = core.Data(salt.encode("utf-8") + data_to_hash)
        hash = core.Hash(core.HashAlgorithm.MD5).get_hash(salted_data)
        return hash.to_hex()

    def set_hash(self, add: bool = False):
        """Set the hash of the save file."""
        hash = self.get_new_hash(existing_hash=not add)
        if not add:
            self.data.set_pos(-32)
        else:
            self.data.set_pos(len(self.data))
        self.data.write_string(hash, write_length=False)

    def verify_hash(self) -> bool:
        """Verify the hash of the save file.

        Returns:
            bool: Whether the hash is valid
        """
        return self.get_current_hash() == self.get_new_hash()

    def load_wrapper(self):
        try:
            self.load()
        except Exception as e:
            ignore_error = core.core_data.config.get_bool(ConfigKey.IGNORE_PARSE_ERROR)
            if not ignore_error:
                raise FailedToLoadError(
                    core.core_data.local_manager.get_key("failed_to_load_save")
                ) from e
            else:
                from traceback import format_exc

                ColoredText.localize("parse_ignored_error", error=format_exc())

    def set_gv(self, gv: core.GameVersion):
        self.game_version = gv

    def set_cc(self, cc: core.CountryCode):
        self.cc = cc
        self.set_package_name(None)

    def set_package_name(self, package_name: str | None):
        self.package_name = package_name

    def load(self):
        """Load the save file. For most of this stuff I have no idea what it is used for"""

        self.data.reset_pos()
        self.dst_index = 0

        self.dsts: list[bool] = []

        self.game_version: core.GameVersion = core.GameVersion(self.data.read_int())

        if self.game_version >= 10 or self.not_jp():
            self.ub1 = self.data.read_bool()

        self.mute_bgm = self.data.read_bool()
        self.mute_se = self.data.read_bool()

        self.catfood = self.data.read_int()
        self.current_energy = self.data.read_int()

        year = self.data.read_int()
        self.year = self.data.read_int()

        month = self.data.read_int()
        self.month = self.data.read_int()

        day = self.data.read_int()
        self.day = self.data.read_int()

        self.timestamp = self.data.read_double()

        hour = self.data.read_int()
        minute = self.data.read_int()
        second = self.data.read_int()

        self.read_dst()

        self.date = datetime.datetime(year, month, day, hour, minute, second)

        self.ui1 = self.data.read_int()
        self.stamp_value_save = self.data.read_int()
        self.ui2 = self.data.read_int()

        self.upgrade_state = self.data.read_int()

        self.xp = self.data.read_int()
        self.tutorial_state = self.data.read_int()

        self.ui3 = self.data.read_int()
        self.koreaSuperiorTreasureState = self.data.read_int()

        self.unlock_popups_11 = self.data.read_int_list(3)
        self.ui5 = self.data.read_int()
        self.unlock_enemy_guide = self.data.read_int()
        self.ui6 = self.data.read_int()
        self.ub0 = self.data.read_bool()
        self.ui7 = self.data.read_int()
        self.cleared_eoc_1 = self.data.read_int()
        self.ui8 = self.data.read_int()
        self.unlocked_ending = self.data.read_int()

        self.lineups = core.LineUps.read(self.data, self.game_version)

        self.stamp_data = core.StampData.read(self.data)
        self.story = core.StoryChapters.read(self.data)

        if 20 <= self.game_version and self.game_version <= 25:
            self.enemy_guide = self.data.read_int_list(231)
        else:
            self.enemy_guide = self.data.read_int_list()

        self.cats = core.Cats.read_unlocked(self.data, self.game_version)
        self.cats.read_upgrade(self.data, self.game_version)
        self.cats.read_current_form(self.data, self.game_version)

        self.special_skills = core.SpecialSkills.read_upgrades(self.data)
        if self.game_version <= 25:
            self.menu_unlocks = self.data.read_int_list(5)
            self.unlock_popups_0 = self.data.read_int_list(5)
        elif self.game_version == 26:
            self.menu_unlocks = self.data.read_int_list(6)
            self.unlock_popups_0 = self.data.read_int_list(6)
        else:
            self.menu_unlocks = self.data.read_int_list()
            self.unlock_popups_0 = self.data.read_int_list()

        self.battle_items = core.BattleItems.read_items(self.data)

        if self.game_version <= 26:
            self.new_dialogs_2 = self.data.read_int_list(17)
        else:
            self.new_dialogs_2 = self.data.read_int_list()

        self.uil1 = self.data.read_int_list(length=20)
        self.moneko_bonus = self.data.read_int_list(length=1)
        self.daily_reward_initialized = self.data.read_int_list(length=1)

        self.battle_items.read_locked_items(self.data)

        self.read_dst()
        self.date_2 = self.data.read_date()

        self.story.read_treasure_festival(self.data)

        self.read_dst()
        self.date_3 = self.data.read_date()

        if self.game_version <= 37:
            self.ui0 = self.data.read_int()

        self.stage_unlock_cat_value = self.data.read_int()
        self.show_ending_value = self.data.read_int()
        self.chapter_clear_cat_unlock = self.data.read_int()
        self.ui9 = self.data.read_int()
        self.ios_android_month = self.data.read_int()
        self.ui10 = self.data.read_int()
        self.save_data_4_hash = self.data.read_string()

        self.mysale = core.MySale.read_bonus_hash(self.data)
        self.chara_flags = self.data.read_int_list(length=2)

        if self.game_version <= 37:
            self.uim1 = self.data.read_int()
            self.ubm1 = self.data.read_bool()

        self.chara_flags_2 = self.data.read_int_list(length=2)

        self.normal_tickets = self.data.read_int()
        self.rare_tickets = self.data.read_int()

        self.cats.read_gatya_seen(self.data, self.game_version)
        self.special_skills.read_gatya_seen(self.data)
        self.cats.read_storage(self.data, self.game_version)

        self.event_stages = core.EventChapters.read(self.data, self.game_version)
        self.itf1_ending = self.data.read_int()
        self.continue_flag = self.data.read_int()
        if 20 <= self.game_version:
            self.unlock_popups_8 = self.data.read_int_list(length=36)

        if 20 <= self.game_version and self.game_version <= 25:
            self.unit_drops = self.data.read_int_list(length=110)
        elif 26 <= self.game_version:
            self.unit_drops = self.data.read_int_list()

        self.gatya = core.Gatya.read_rare_normal_seed(self.data, self.game_version)

        self.get_event_data = self.data.read_bool()
        self.achievements = self.data.read_bool_list(length=7)

        self.os_value = self.data.read_int()

        self.read_dst()
        self.date_4 = self.data.read_date()

        self.gatya.read2(self.data)

        if self.not_jp():
            self.player_id = self.data.read_string()

        self.order_ids = self.data.read_string_list()

        if self.not_jp():
            self.g_timestamp = self.data.read_double()
            self.g_servertimestamp = self.data.read_double()
            self.m_gettimesave = self.data.read_double()
            self.usl1 = self.data.read_string_list()
            self.energy_notification = self.data.read_bool()
            self.full_gameversion = self.data.read_int()

        self.lineups.read_2(self.data, self.game_version)
        self.event_stages.read_legend_restrictions(self.data, self.game_version)

        if self.game_version <= 37:
            self.uil2 = self.data.read_int_list(length=7)
            self.uil3 = self.data.read_int_list(length=7)
            self.uil4 = self.data.read_int_list(length=7)

        self.g_timestamp_2 = self.data.read_double()
        self.g_servertimestamp_2 = self.data.read_double()
        self.m_gettimesave_2 = self.data.read_double()
        self.unknown_timestamp = self.data.read_double()
        self.gatya.read_trade_progress(self.data)

        if self.game_version <= 37:
            self.usl2 = self.data.read_string_list()

        if self.not_jp():
            self.m_dGetTimeSave2 = self.data.read_double()
            self.ui11 = 0
        else:
            self.ui11 = self.data.read_int()

        if 20 <= self.game_version and self.game_version <= 25:
            self.ubl1 = self.data.read_bool_list(length=12)
        elif 26 <= self.game_version and self.game_version < 39:
            self.ubl1 = self.data.read_bool_list()

        self.cats.read_max_upgrade_levels(self.data, self.game_version)
        self.special_skills.read_max_upgrade_levels(self.data)

        self.user_rank_rewards = core.UserRankRewards.read(self.data, self.game_version)

        if not self.not_jp():
            self.m_dGetTimeSave2 = self.data.read_double()

        self.cats.read_unlocked_forms(self.data, self.game_version)

        self.transfer_code = self.data.read_string()
        self.confirmation_code = self.data.read_string()
        self.transfer_flag = self.data.read_bool()

        if 20 <= self.game_version:
            self.item_reward_stages = core.ItemRewardChapters.read(
                self.data, self.game_version
            )

            self.timed_score_stages = core.TimedScoreChapters.read(
                self.data, self.game_version
            )
            self.inquiry_code = self.data.read_string()
            self.officer_pass = core.OfficerPass.read(self.data)
            self.has_account = self.data.read_byte()
            self.backup_state = self.data.read_int()

            if self.not_jp():
                self.ub2 = self.data.read_bool()

            assert self.data.read_int() == 44

            self.itf1_complete = self.data.read_int()

            self.story.read_itf_timed_scores(self.data)

            self.title_chapter_bg = self.data.read_int()

            if self.game_version > 26:
                self.combo_unlocks = self.data.read_int_list()

            self.combo_unlocked_10k_ur = self.data.read_bool()

            assert self.data.read_int() == 45

        if 21 <= self.game_version:
            assert self.data.read_int() == 46

            self.gatya.read_event_seed(self.data, self.game_version)
            if self.game_version < 34:
                self.event_capsules = self.data.read_int_list(length=100)
                self.event_capsules_counter = self.data.read_int_list(length=100)
            else:
                self.event_capsules = self.data.read_int_list()
                self.event_capsules_counter = self.data.read_int_list()

            assert self.data.read_int() == 47

        if 22 <= self.game_version:
            assert self.data.read_int() == 48

        if 23 <= self.game_version:
            if not self.not_jp():
                self.energy_notification = self.data.read_bool()

            self.m_dGetTimeSave3 = self.data.read_double()
            if self.game_version < 26:
                self.gatya_seen_lucky_drops = self.data.read_int_list(length=44)
            else:
                self.gatya_seen_lucky_drops = self.data.read_int_list()
            self.show_ban_message = self.data.read_bool()
            self.catfood_beginner_purchased = self.data.read_bool_list(length=3)
            self.next_week_timestamp = self.data.read_double()
            self.catfood_beginner_expired = self.data.read_bool_list(length=3)
            self.rank_up_sale_value = self.data.read_int()

            assert self.data.read_int() == 49

        if 24 <= self.game_version:
            assert self.data.read_int() == 50

        if 25 <= self.game_version:
            assert self.data.read_int() == 51

        if 26 <= self.game_version:
            self.cats.read_catguide_collected(self.data)

            assert self.data.read_int() == 52

        if 27 <= self.game_version:
            self.time_since_time_check_cumulative = self.data.read_double()
            self.server_timestamp = self.data.read_double()
            self.last_checked_energy_recovery_time = self.data.read_double()
            self.time_since_check = self.data.read_double()
            self.last_checked_expedition_time = self.data.read_double()

            self.catfruit = self.data.read_int_list()
            self.cats.read_fourth_forms(self.data)
            self.cats.read_catseyes_used(self.data)
            self.catseyes = self.data.read_int_list()
            self.catamins = self.data.read_int_list()
            self.gamatoto = core.Gamatoto.read(self.data)

            self.unlock_popups_6 = self.data.read_bool_list()
            self.ex_stages = core.ExChapters.read(self.data)

            assert self.data.read_int() == 53

        if 29 <= self.game_version:
            self.gamatoto.read_2(self.data)
            assert self.data.read_int() == 54
            self.item_pack = core.ItemPack.read(self.data)
            assert self.data.read_int() == 54

        if self.game_version >= 30:
            self.gamatoto.read_skin(self.data)
            self.platinum_tickets = self.data.read_int()
            self.logins = core.LoginBonus.read(self.data, self.game_version)
            if self.game_version < 101000:
                self.reset_item_reward_flags = self.data.read_bool_list()

            self.reward_remaining_time = self.data.read_double()
            self.last_checked_reward_time = self.data.read_double()
            self.announcements = self.data.read_int_tuple_list(length=16)
            self.backup_counter = self.data.read_int()
            self.ui12 = self.data.read_int()
            self.ui13 = self.data.read_int()
            self.ui14 = self.data.read_int()

            assert self.data.read_int() == 55

        if self.game_version >= 31:
            self.ub3 = self.data.read_bool()
            self.item_reward_stages.read_item_obtains(self.data)
            self.gatya.read_stepup(self.data)

            self.backup_frame = self.data.read_int()

            assert self.data.read_int() == 56

        if self.game_version >= 32:
            self.ub4 = self.data.read_bool()
            self.cats.read_favorites(self.data)

            assert self.data.read_int() == 57

        if self.game_version >= 33:
            self.dojo = core.Dojo.read_chapters(self.data)
            self.dojo.read_item_locks(self.data)

            assert self.data.read_int() == 58

        if self.game_version >= 34:
            self.last_checked_zombie_time = self.data.read_double()
            self.outbreaks = core.Outbreaks.read_chapters(self.data)
            self.outbreaks.read_2(self.data)
            self.scheme_items = core.SchemeItems.read(self.data)

        if self.game_version >= 35:
            self.outbreaks.read_current_outbreaks(self.data, self.game_version)
            self.first_locks = self.data.read_int_bool_dict()
            self.energy_penalty_timestamp = self.data.read_double()

            assert self.data.read_int() == 60

        if self.game_version >= 36:
            self.cats.read_chara_new_flags(self.data)
            self.shown_maxcollab_mg = self.data.read_bool()
            self.item_pack.read_displayed_packs(self.data)

            assert self.data.read_int() == 61

        if self.game_version >= 38:
            self.unlock_popups = core.UnlockPopups.read(self.data)
            assert self.data.read_int() == 63

        if self.game_version >= 39:
            self.ototo = core.Ototo.read(self.data)
            self.ototo.read_2(self.data, self.game_version)
            self.last_checked_castle_time = self.data.read_double()

            assert self.data.read_int() == 64

        if self.game_version >= 40:
            self.beacon_base = core.BeaconEventListScene.read(self.data)

            assert self.data.read_int() == 65

        if self.game_version >= 41:
            self.tower = core.TowerChapters.read(self.data)
            self.missions = core.Missions.read(self.data, self.game_version)
            self.tower.read_item_obtain_states(self.data)

            assert self.data.read_int() == 66

        if self.game_version >= 42:
            self.dojo.read_ranking(self.data, self.game_version)
            self.item_pack.read_three_days(self.data)
            self.challenge = core.ChallengeChapters.read(self.data)
            self.challenge.read_scores(self.data)
            self.challenge.read_popup(self.data)

            assert self.data.read_int() == 67

        if self.game_version >= 43:
            self.missions.read_weekly_missions(self.data)
            self.dojo.ranking.read_did_win_rewards(self.data)
            self.event_update_flags = self.data.read_bool()

            assert self.data.read_int() == 68

        if self.game_version >= 44:
            self.event_stages.read_dicts(self.data)
            self.cotc_1_complete = self.data.read_int()

            assert self.data.read_int() == 69

        if self.game_version >= 46:
            self.gamatoto.read_collab_data(self.data)

            assert self.data.read_int() == 71

        if self.game_version < 90300:
            self.map_resets = core.MapResets.read(self.data)

            assert self.data.read_int() == 72

        if self.game_version >= 51:
            self.uncanny = core.UncannyChapters.read(self.data)
            assert self.data.read_int() == 76

        if self.game_version >= 77:
            self.catamin_stages = core.UncannyChapters.read(self.data)

            self.lucky_tickets = self.data.read_int_list()

            self.ub5 = self.data.read_bool()

            assert self.data.read_int() == 77

        if self.game_version >= 80000:
            self.officer_pass.read_gold_pass(self.data, self.game_version)
            self.cats.read_talents(self.data)
            self.np = self.data.read_int()
            self.ub6 = self.data.read_bool()

            assert self.data.read_int() == 80000

        if self.game_version >= 80200:
            self.ub7 = self.data.read_bool()
            self.leadership = self.data.read_short()
            self.officer_pass.read_cat_data(self.data)

            assert self.data.read_int() == 80200

        if self.game_version >= 80300:
            self.filibuster_stage_id = self.data.read_byte()
            self.filibuster_stage_enabled = self.data.read_bool()

            assert self.data.read_int() == 80300

        if self.game_version >= 80500:
            self.stage_ids_10s = self.data.read_int_list()

            assert self.data.read_int() == 80500

        if self.game_version >= 80600:
            length = self.data.read_short()
            self.uil6 = self.data.read_int_list(length=length)
            self.legend_quest = core.LegendQuestChapters.read(self.data)
            self.ush1 = self.data.read_short()
            self.uby1 = self.data.read_byte()

            assert self.data.read_int() == 80600

        if self.game_version >= 80700:
            length = self.data.read_int()
            self.uiid1: dict[int, list[int]] = {}
            for _ in range(length):
                key = self.data.read_int()
                value = self.data.read_int_list()
                self.uiid1[key] = value

            assert self.data.read_int() == 80700

        if self.game_version >= 100600:
            if self.is_en():
                self.uby2 = self.data.read_byte()
                assert self.data.read_int() == 100600

        if self.game_version >= 81000:
            self.restart_pack = self.data.read_byte()
            assert self.data.read_int() == 81000

        if self.game_version >= 90000:
            self.medals = core.Medals.read(self.data)
            self.wildcat_slots = core.GamblingEvent.read(self.data, self.game_version)

            assert self.data.read_int() == 90000

        if self.game_version >= 90100:
            self.ush2 = self.data.read_short()
            self.ush3 = self.data.read_short()
            self.ui15 = self.data.read_int()
            self.ud1 = self.data.read_double()

            assert self.data.read_int() == 90100

        if self.game_version >= 90300:
            length = self.data.read_short()
            self.utl1: list[tuple[int, int, int, int, int, int, int]] = []
            for _ in range(length):
                i1 = self.data.read_int()
                i2 = self.data.read_int()
                i3 = self.data.read_short()
                i4 = self.data.read_int()
                i5 = self.data.read_int()
                i6 = self.data.read_int()
                i7 = self.data.read_short()
                self.utl1.append((i1, i2, i3, i4, i5, i6, i7))

            length = self.data.read_short()
            self.uidd1 = self.data.read_int_double_dict(length)

            self.gauntlets = core.GauntletChapters.read(self.data)

            assert self.data.read_int() == 90300

        if self.game_version >= 90400:
            self.enigma_clears = core.GauntletChapters.read(self.data)
            self.enigma = core.Enigma.read(self.data, self.game_version)
            self.cleared_slots = core.ClearedSlots.read(self.data)

            assert self.data.read_int() == 90400

        if self.game_version >= 90500:
            self.collab_gauntlets = core.GauntletChapters.read(self.data)
            self.ub8 = self.data.read_bool()
            self.ud2 = self.data.read_double()
            self.ud3 = self.data.read_double()
            self.ui16 = self.data.read_int()
            if self.game_version >= 100300:
                self.uby3 = self.data.read_byte()
                self.ub9 = self.data.read_bool()
                self.ud4 = self.data.read_double()
                self.ud5 = self.data.read_double()

            if self.game_version >= 130700:
                length = self.data.read_short()
                self.uiid3: dict[int, int] = {}
                for _ in range(length):
                    key = self.data.read_int()
                    value = self.data.read_byte()
                    self.uiid3[key] = value

                length = self.data.read_short()
                self.uidd2: dict[int, float] = {}
                for _ in range(length):
                    key = self.data.read_int()
                    value = self.data.read_double()
                    self.uidd2[key] = value

            if self.game_version >= 140100:
                length = self.data.read_short()
                self.uidd3: dict[int, float] = {}
                for _ in range(length):
                    key = self.data.read_int()
                    value = self.data.read_double()
                    self.uidd3[key] = value

            assert self.data.read_int() == 90500

        if self.game_version >= 90700:
            self.talent_orbs = core.TalentOrbs.read(self.data, self.game_version)
            length = self.data.read_short()
            self.uidiid2: dict[int, dict[int, int]] = {}
            for _ in range(length):
                key = self.data.read_short()
                length = self.data.read_byte()
                for _ in range(length):
                    key2 = self.data.read_byte()
                    value = self.data.read_short()
                    if key not in self.uidiid2:
                        self.uidiid2[key] = {}
                    self.uidiid2[key][key2] = value
                if length == 0:
                    self.uidiid2[key] = {}

            self.ub10 = self.data.read_bool()

            assert self.data.read_int() == 90700

        if self.game_version >= 90800:
            length = self.data.read_short()
            self.uil7 = self.data.read_int_list(length)
            self.ubl2 = self.data.read_bool_list(10)

            assert self.data.read_int() == 90800

        if self.game_version >= 90900:
            self.cat_shrine = core.CatShrine.read(self.data)
            self.ud6 = self.data.read_double()
            self.ud7 = self.data.read_double()

            assert self.data.read_int() == 90900

        if self.game_version >= 91000:
            self.lineups.read_slot_names(self.data, self.game_version)

            assert self.data.read_int() == 91000

        if self.game_version >= 100000:
            self.legend_tickets = self.data.read_int()
            length = self.data.read_byte()
            self.uiil1: list[tuple[int, int]] = []
            for _ in range(length):
                i1 = self.data.read_byte()
                i2 = self.data.read_int()
                self.uiil1.append((i1, i2))

            self.ub11 = self.data.read_bool()
            self.ub12 = self.data.read_bool()

            self.password_refresh_token = self.data.read_string()

            self.ub13 = self.data.read_bool()
            self.uby4 = self.data.read_byte()
            self.uby5 = self.data.read_byte()
            self.ud8 = self.data.read_double()
            self.ud9 = self.data.read_double()

            assert self.data.read_int() == 100000

        if self.game_version >= 100100:
            self.date_int = self.data.read_int()

            assert self.data.read_int() == 100100

        if self.game_version >= 100300:
            self.battle_items.read_endless_items(self.data)

            assert self.data.read_int() == 100300

        if self.game_version >= 100400:
            length = self.data.read_byte()
            self.event_capsules_2 = self.data.read_int_list(length)
            self.two_battle_lines = self.data.read_bool()

            assert self.data.read_int() == 100400

        if self.game_version >= 100600:
            self.ud10 = self.data.read_double()
            self.platinum_shards = self.data.read_int()
            self.ub15 = self.data.read_bool()

            assert self.data.read_int() == 100600

        if self.game_version >= 100700:
            self.cat_scratcher = core.GamblingEvent.read(self.data, self.game_version)

            assert self.data.read_int() == 100700

        if self.game_version >= 100900:
            self.aku = core.AkuChapters.read(self.data)
            self.ub16 = self.data.read_bool()
            self.ub17 = self.data.read_bool()

            length = self.data.read_short()
            self.ushdshd2: dict[int, list[int]] = {}
            for _ in range(length):
                key = self.data.read_short()
                length = self.data.read_short()
                for _ in range(length):
                    value = self.data.read_short()
                    if key not in self.ushdshd2:
                        self.ushdshd2[key] = []
                    self.ushdshd2[key].append(value)
                if length == 0:
                    self.ushdshd2[key] = []

            length = self.data.read_short()
            self.ushdd: dict[int, float] = {}
            for _ in range(length):
                key = self.data.read_short()
                value = self.data.read_double()
                self.ushdd[key] = value

            length = self.data.read_short()
            self.ushdd2: dict[int, float] = {}
            for _ in range(length):
                key = self.data.read_short()
                value = self.data.read_double()
                self.ushdd2[key] = value

            self.ub18 = self.data.read_bool()

            assert self.data.read_int() == 100900

        if self.game_version >= 101000:
            self.uby6 = self.data.read_byte()

            assert self.data.read_int() == 101000

        if self.game_version >= 110000:
            length = self.data.read_short()
            self.uidtii: dict[int, tuple[int, int]] = {}
            for _ in range(length):
                key = self.data.read_int()
                value = (
                    self.data.read_byte(),
                    self.data.read_byte(),
                )
                self.uidtii[key] = value

            assert self.data.read_int() == 110000

        if self.game_version >= 110500:
            self.behemoth_culling = core.GauntletChapters.read(self.data)
            self.ub19 = self.data.read_bool()

            assert self.data.read_int() == 110500

        if self.game_version >= 110600:
            self.ub20 = self.data.read_bool()

            assert self.data.read_int() == 110600

        if self.game_version >= 110700:
            length = self.data.read_int()
            self.uidtff: dict[int, tuple[float, float]] = {}
            for _ in range(length):
                key = self.data.read_int()
                value = (
                    self.data.read_double(),
                    self.data.read_double(),
                )
                self.uidtff[key] = value

            if self.not_jp():
                self.ub20 = self.data.read_bool()

            assert self.data.read_int() == 110700

        if self.game_version >= 110800:
            self.cat_shrine.read_dialogs(self.data)
            self.ub21 = self.data.read_bool()
            self.dojo_3x_speed = self.data.read_bool()
            self.ub22 = self.data.read_bool()
            self.ub23 = self.data.read_bool()

            assert self.data.read_int() == 110800

        if self.game_version >= 111000:
            self.ui17 = self.data.read_int()
            self.ush4 = self.data.read_short()
            self.uby7 = self.data.read_byte()
            self.uby8 = self.data.read_byte()
            self.ub24 = self.data.read_bool()
            self.uby9 = self.data.read_byte()

            length = self.data.read_byte()
            self.ushl1 = self.data.read_short_list(length)

            length = self.data.read_short()
            self.ushl2 = self.data.read_short_list(length)

            length = self.data.read_short()
            self.ushl3 = self.data.read_short_list(length)

            self.ui18 = self.data.read_int()
            self.ui19 = self.data.read_int()
            self.ui20 = self.data.read_int()
            self.ush5 = self.data.read_short()
            self.ush6 = self.data.read_short()
            self.ush7 = self.data.read_short()
            self.ush8 = self.data.read_short()
            self.uby10 = self.data.read_byte()
            self.ub25 = self.data.read_bool()
            self.ub26 = self.data.read_bool()
            self.ub27 = self.data.read_bool()
            self.ub28 = self.data.read_bool()
            self.ub29 = self.data.read_bool()
            self.ub30 = self.data.read_bool()
            self.uby11 = self.data.read_byte()

            length = self.data.read_short()
            self.ushl4 = self.data.read_short_list(length)

            self.ubl3 = self.data.read_bool_list(14)

            length = self.data.read_byte()
            self.labyrinth_medals = self.data.read_short_list(length)

            assert self.data.read_int() == 111000

        if self.game_version >= 120000:
            self.zero_legends = core.ZeroLegendsChapters.read(self.data)
            self.uby12 = self.data.read_byte()

            assert self.data.read_int() == 120000

        if self.game_version >= 120100:
            length = self.data.read_short()
            self.ushl6 = self.data.read_short_list(length)

            assert self.data.read_int() == 120100

        if self.game_version >= 120200:
            self.ub31 = self.data.read_bool()
            self.ush9 = self.data.read_short()
            length = self.data.read_byte()
            self.ushshd: dict[int, int] = {}
            for _ in range(length):
                key = self.data.read_short()
                value = self.data.read_short()
                self.ushshd[key] = value

            assert self.data.read_int() == 120200

        if self.game_version >= 120400:
            self.ud11 = self.data.read_double()
            self.ud12 = self.data.read_double()

            assert self.data.read_int() == 120400

        if self.game_version >= 120500:
            self.ub32 = self.data.read_bool()
            self.ub33 = self.data.read_bool()
            self.ub34 = self.data.read_bool()

            self.ui21 = self.data.read_int()
            self.golden_cpu_count = self.data.read_byte()

            assert self.data.read_int() == 120500

        if self.game_version >= 120600:
            self.sound_effects_volume = self.data.read_byte()
            self.background_music_volume = self.data.read_byte()

            assert self.data.read_int() == 120600

        if (self.not_jp() and self.game_version >= 120700) or (
            self.is_jp() and self.game_version >= 130000
        ):
            length = self.data.read_byte()
            self.ustl1: list[tuple[str, str]] = []
            for _ in range(length):
                s1 = self.data.read_string()
                s2 = self.data.read_string()
                self.ustl1.append((s1, s2))

            if self.not_jp():
                assert self.data.read_int() == 120700
            else:
                assert self.data.read_int() == 130000

        if self.game_version >= 130100:
            length = self.data.read_int()
            self.utl3: list[tuple[int, int]] = []
            for _ in range(length):
                i1 = self.data.read_int()
                i2 = self.data.read_long()
                self.utl3.append((i1, i2))

            assert self.data.read_int() == 130100

        if self.game_version >= 130301:
            length = self.data.read_int()
            self.ustid1: dict[str, tuple[int, float]] = {}
            for _ in range(length):
                key = self.data.read_string()
                value_1 = self.data.read_int()
                value_2 = self.data.read_double()
                self.ustid1[key] = (value_1, value_2)

            assert self.data.read_int() == 130301

        if self.game_version >= 130400:
            self.ud13 = self.data.read_double()
            self.ud14 = self.data.read_double()

            assert self.data.read_int() == 130400

        if self.game_version >= 130500:
            self.utl4: list[tuple[int, list[tuple[int, int, int, list[int]]]]] = []
            length1 = self.data.read_short()
            for _ in range(length1):
                id = self.data.read_byte()
                length2 = self.data.read_byte()
                ls2: list[tuple[int, int, int, list[int]]] = []
                for _ in range(length2):
                    v1 = self.data.read_byte()
                    v2 = self.data.read_byte()
                    v3 = self.data.read_byte()

                    length3 = self.data.read_short()
                    ls1: list[int] = []

                    for _ in range(length3):
                        val = self.data.read_short()
                        ls1.append(val)

                    ls2.append((v1, v2, v3, ls1))

                self.utl4.append((id, ls2))

            assert self.data.read_int() == 130500

        if self.game_version >= 130600:
            self.uby14 = self.data.read_byte()

            if self.not_jp():
                self.ush12 = self.data.read_short()

            assert self.data.read_int() == 130600

        if self.game_version >= 130700:
            if self.is_jp():
                self.ush12 = self.data.read_short()
            self.ud15 = self.data.read_double()
            self.uby15 = self.data.read_byte()
            self.uby16 = self.data.read_byte()

            self.ush11 = self.data.read_short()
            self.uby17 = self.data.read_byte()
            self.uby18 = self.data.read_byte()
            self.uby19 = self.data.read_byte()

            self.ud16 = self.data.read_double()

            length1 = self.data.read_short()

            self.ushd1: dict[int, tuple[int, int, dict[int, int]]] = {}

            for _ in range(length1):
                key = self.data.read_short()
                value = self.data.read_short()
                value_2 = self.data.read_int()

                length2 = self.data.read_short()

                data2: dict[int, int] = {}

                for _ in range(length2):
                    key2 = self.data.read_short()
                    value3 = self.data.read_short()

                    data2[key2] = value3

                self.ushd1[key] = (value, value_2, data2)

            assert self.data.read_int() == 130700

        if self.game_version >= 140000:
            self.ui22 = self.data.read_int()
            self.ud17 = self.data.read_double()
            self.uby20 = self.data.read_byte()

            length = self.data.read_byte()

            self.uild1: dict[int, list[int]] = {}

            for _ in range(length):
                key = self.data.read_int()
                length2 = self.data.read_byte()
                data3: list[int] = []
                for _ in range(length2):
                    value = self.data.read_byte()
                    data3.append(value)

                self.uild1[key] = data3

            self.dojo_chapters = core.ZeroLegendsChapters.read(self.data)

            length = self.data.read_short()

            self.uil9: list[int] = []
            for _ in range(length):
                self.uil9.append(self.data.read_int())

            self.ub35 = self.data.read_bool()
            self.ud18 = self.data.read_double()

            length = self.data.read_short()

            self.ushd2: dict[int, int] = {}

            for _ in range(length):
                key = self.data.read_short()
                value = self.data.read_byte()
                self.ushd2[key] = value

            assert self.data.read_int() == 140000

        if self.game_version >= 140100 and self.game_version < 140500:
            self.uby21 = self.data.read_byte()
            assert self.data.read_int() == 140100

        if self.game_version >= 140200:
            length = self.data.read_byte()

            self.uil10: list[
                tuple[
                    int,
                    int,
                    bool,
                    bool,
                    bool,
                    int,
                    int,
                    int,
                    bool,
                    bool,
                    bool,
                    str | None,
                    bool,
                ]
            ] = []

            for _ in range(length):
                val_1 = self.data.read_int()
                val_2 = self.data.read_int()
                val_3 = self.data.read_bool()
                val_4 = self.data.read_bool()
                val_5 = self.data.read_bool()
                val_6 = self.data.read_int()
                val_7 = self.data.read_int()
                val_8 = self.data.read_int()
                val_9 = self.data.read_bool()
                val_10 = self.data.read_bool()
                val_11 = self.data.read_bool()

                val_12 = None

                if self.game_version >= 140500:
                    # game seems to read more than just this, may break in the future
                    val_12 = self.data.read_string()

                val_13 = self.data.read_bool()

                self.uil10.append(
                    (
                        val_1,
                        val_2,
                        val_3,
                        val_4,
                        val_5,
                        val_6,
                        val_7,
                        val_8,
                        val_9,
                        val_10,
                        val_11,
                        val_12,
                        val_13,
                    )
                )

            length = self.data.read_byte()

            self.uid1: dict[int, float] = {}

            for _ in range(length):
                key = self.data.read_int()
                value = self.data.read_double()

                self.uid1[key] = value

            self.hundred_million_ticket = self.data.read_int()

            assert self.data.read_int() == 140200

        if self.game_version >= 140300:
            length = self.data.read_byte()
            self.uil11: list[int] = []
            for _ in range(length):
                val = self.data.read_byte()
                self.uil11.append(val)

            self.ub36 = self.data.read_bool()

            length = self.data.read_byte()

            self.treasure_chests: list[int] = []

            for _ in range(length):
                value = self.data.read_int()
                self.treasure_chests.append(value)

            self.ui23 = self.data.read_int()
            length = self.data.read_short()

            self.uil13: list[int] = []

            for _ in range(length):
                self.uil13.append(self.data.read_int())

            self.ub37 = self.data.read_bool()

            assert self.data.read_int() == 140300

        self.remaining_data = self.data.read_to_end(32)

    def save(self, data: core.Data):
        self.data = data
        self.dst_index = 0
        self.data.clear()
        self.data.enable_buffer()

        self.data.write_int(self.game_version.game_version)

        if self.game_version >= 10 or self.not_jp():
            self.data.write_bool(self.ub1)

        self.data.write_bool(self.mute_bgm)
        self.data.write_bool(self.mute_se)

        self.data.write_int(self.catfood)
        self.data.write_int(self.current_energy)

        self.data.write_int(self.date.year)
        self.data.write_int(self.year)

        self.data.write_int(self.date.month)
        self.data.write_int(self.month)

        self.data.write_int(self.date.day)
        self.data.write_int(self.day)

        self.data.write_double(self.timestamp)

        self.data.write_int(self.date.hour)
        self.data.write_int(self.date.minute)
        self.data.write_int(self.date.second)

        self.write_dst()

        self.data.write_int(self.ui1)
        self.data.write_int(self.stamp_value_save)
        self.data.write_int(self.ui2)

        self.data.write_int(self.upgrade_state)

        self.data.write_int(self.xp)
        self.data.write_int(self.tutorial_state)

        self.data.write_int(self.ui3)
        self.data.write_int(self.koreaSuperiorTreasureState)

        self.data.write_int_list(self.unlock_popups_11, write_length=False, length=3)
        self.data.write_int(self.ui5)
        self.data.write_int(self.unlock_enemy_guide)
        self.data.write_int(self.ui6)
        self.data.write_bool(self.ub0)
        self.data.write_int(self.ui7)
        self.data.write_int(self.cleared_eoc_1)
        self.data.write_int(self.ui8)
        self.data.write_int(self.unlocked_ending)

        self.lineups.write(self.data, self.game_version)

        self.stamp_data.write(self.data)

        self.story.write(self.data)

        if 20 <= self.game_version and self.game_version <= 25:
            self.data.write_int_list(self.enemy_guide, write_length=False, length=231)
        else:
            self.data.write_int_list(self.enemy_guide)

        self.cats.write_unlocked(self.data, self.game_version)
        self.cats.write_upgrade(self.data, self.game_version)
        self.cats.write_current_form(self.data, self.game_version)

        self.special_skills.write_upgrades(self.data)

        if self.game_version <= 25:
            self.data.write_int_list(self.menu_unlocks, write_length=False, length=5)
            self.data.write_int_list(self.unlock_popups_0, write_length=False, length=5)
        elif self.game_version <= 26:
            self.data.write_int_list(self.menu_unlocks, write_length=False, length=6)
            self.data.write_int_list(self.unlock_popups_0, write_length=False, length=6)
        else:
            self.data.write_int_list(self.menu_unlocks)
            self.data.write_int_list(self.unlock_popups_0)

        self.battle_items.write_items(self.data)

        if self.game_version <= 26:
            self.data.write_int_list(self.new_dialogs_2, write_length=False, length=17)
        else:
            self.data.write_int_list(self.new_dialogs_2)

        self.data.write_int_list(self.uil1, write_length=False, length=20)
        self.data.write_int_list(self.moneko_bonus, write_length=False, length=1)
        self.data.write_int_list(
            self.daily_reward_initialized, write_length=False, length=1
        )

        self.battle_items.write_locked_items(self.data)

        self.write_dst()
        self.data.write_date(self.date_2)

        self.story.write_treasure_festival(self.data)

        self.write_dst()
        self.data.write_date(self.date_3)

        if self.game_version <= 37:
            self.data.write_int(self.ui0)

        self.data.write_int(self.stage_unlock_cat_value)
        self.data.write_int(self.show_ending_value)
        self.data.write_int(self.chapter_clear_cat_unlock)
        self.data.write_int(self.ui9)
        self.data.write_int(self.ios_android_month)
        self.data.write_int(self.ui10)
        self.data.write_string(self.save_data_4_hash)

        self.mysale.write_bonus_hash(self.data)
        self.data.write_int_list(self.chara_flags, write_length=False, length=2)

        if self.game_version <= 37:
            self.data.write_int(self.uim1)
            self.data.write_bool(self.ubm1)

        self.data.write_int_list(self.chara_flags_2, write_length=False, length=2)

        self.data.write_int(self.normal_tickets)
        self.data.write_int(self.rare_tickets)

        self.cats.write_gatya_seen(self.data, self.game_version)
        self.special_skills.write_gatya_seen(self.data)
        self.cats.write_storage(self.data, self.game_version)

        self.event_stages.write(self.data, self.game_version)

        self.data.write_int(self.itf1_ending)
        self.data.write_int(self.continue_flag)

        if 20 <= self.game_version:
            self.data.write_int_list(
                self.unlock_popups_8, write_length=False, length=36
            )

        if 20 <= self.game_version and self.game_version <= 25:
            self.data.write_int_list(self.unit_drops, write_length=False, length=110)
        elif 26 <= self.game_version:
            self.data.write_int_list(self.unit_drops)

        self.gatya.write_rare_normal_seed(self.data)

        self.data.write_bool(self.get_event_data)
        self.data.write_bool_list(self.achievements, write_length=False, length=7)

        self.data.write_int(self.os_value)

        self.write_dst()
        self.data.write_date(self.date_4)

        self.gatya.write2(self.data)

        if self.not_jp():
            self.data.write_string(self.player_id)

        self.data.write_string_list(self.order_ids)

        if self.not_jp():
            self.data.write_double(self.g_timestamp)
            self.data.write_double(self.g_servertimestamp)
            self.data.write_double(self.m_gettimesave)
            self.data.write_string_list(self.usl1)
            self.data.write_bool(self.energy_notification)
            self.data.write_int(self.full_gameversion)

        self.lineups.write_2(self.data, self.game_version)
        self.event_stages.write_legend_restrictions(self.data, self.game_version)

        if self.game_version <= 37:
            self.data.write_int_list(self.uil2, write_length=False, length=7)
            self.data.write_int_list(self.uil3, write_length=False, length=7)
            self.data.write_int_list(self.uil4, write_length=False, length=7)

        self.data.write_double(self.g_timestamp_2)
        self.data.write_double(self.g_servertimestamp_2)
        self.data.write_double(self.m_gettimesave_2)
        self.data.write_double(self.unknown_timestamp)

        self.gatya.write_trade_progress(self.data)

        if self.game_version <= 37:
            self.data.write_string_list(self.usl2)

        if self.not_jp():
            self.data.write_double(self.m_dGetTimeSave2)
        else:
            self.data.write_int(self.ui11)

        if 20 <= self.game_version and self.game_version <= 25:
            self.data.write_bool_list(self.ubl1, write_length=False, length=12)
        elif 26 <= self.game_version and self.game_version < 39:
            self.data.write_bool_list(self.ubl1)

        self.cats.write_max_upgrade_levels(self.data, self.game_version)
        self.special_skills.write_max_upgrade_levels(self.data)

        self.user_rank_rewards.write(self.data, self.game_version)

        if self.is_jp():
            self.data.write_double(self.m_dGetTimeSave2)

        self.cats.write_unlocked_forms(self.data, self.game_version)

        self.data.write_string(self.transfer_code)
        self.data.write_string(self.confirmation_code)
        self.data.write_bool(self.transfer_flag)

        if 20 <= self.game_version:
            self.item_reward_stages.write(self.data, self.game_version)
            self.timed_score_stages.write(self.data, self.game_version)

            self.data.write_string(self.inquiry_code)
            self.officer_pass.write(self.data)
            self.data.write_byte(self.has_account)
            self.data.write_int(self.backup_state)

            if self.not_jp():
                self.data.write_bool(self.ub2)

            self.data.write_int(44)
            self.data.write_int(self.itf1_complete)
            self.story.write_itf_timed_scores(self.data)
            self.data.write_int(self.title_chapter_bg)

            if self.game_version > 26:
                self.data.write_int_list(self.combo_unlocks)

            self.data.write_bool(self.combo_unlocked_10k_ur)

            self.data.write_int(45)

        if 21 <= self.game_version:
            self.data.write_int(46)
            self.gatya.write_event_seed(self.data)
            if self.game_version < 34:
                self.data.write_int_list(
                    self.event_capsules, write_length=False, length=100
                )
                self.data.write_int_list(
                    self.event_capsules_counter, write_length=False, length=100
                )
            else:
                self.data.write_int_list(self.event_capsules)
                self.data.write_int_list(self.event_capsules_counter)

            self.data.write_int(47)

        if 22 <= self.game_version:
            self.data.write_int(48)

        if 23 <= self.game_version:
            if self.is_jp():
                self.data.write_bool(self.energy_notification)

            self.data.write_double(self.m_dGetTimeSave3)
            if self.game_version < 26:
                self.data.write_int_list(
                    self.gatya_seen_lucky_drops,
                    write_length=False,
                    length=44,
                )
            else:
                self.data.write_int_list(self.gatya_seen_lucky_drops)
            self.data.write_bool(self.show_ban_message)
            self.data.write_bool_list(
                self.catfood_beginner_purchased,
                write_length=False,
                length=3,
            )
            self.data.write_double(self.next_week_timestamp)
            self.data.write_bool_list(
                self.catfood_beginner_expired, write_length=False, length=3
            )
            self.data.write_int(self.rank_up_sale_value)
            self.data.write_int(49)

        if 24 <= self.game_version:
            self.data.write_int(50)

        if 25 <= self.game_version:
            self.data.write_int(51)

        if 26 <= self.game_version:
            self.cats.write_catguide_collected(self.data)
            self.data.write_int(52)

        if 27 <= self.game_version:
            self.data.write_double(self.time_since_time_check_cumulative)
            self.data.write_double(self.server_timestamp)
            self.data.write_double(self.last_checked_energy_recovery_time)
            self.data.write_double(self.time_since_check)
            self.data.write_double(self.last_checked_expedition_time)

            self.data.write_int_list(self.catfruit)
            self.cats.write_fourth_forms(self.data)
            self.cats.write_catseyes_used(self.data)
            self.data.write_int_list(self.catseyes)
            self.data.write_int_list(self.catamins)
            self.gamatoto.write(self.data)

            self.data.write_bool_list(self.unlock_popups_6)
            self.ex_stages.write(self.data)

            self.data.write_int(53)

        if 29 <= self.game_version:
            self.gamatoto.write_2(self.data)
            self.data.write_int(54)
            self.item_pack.write(self.data)
            self.data.write_int(54)

        if self.game_version >= 30:
            self.gamatoto.write_skin(self.data)
            self.data.write_int(self.platinum_tickets)
            self.logins.write(self.data, self.game_version)

            if self.game_version < 101000:
                self.data.write_bool_list(self.reset_item_reward_flags)

            self.data.write_double(self.reward_remaining_time)
            self.data.write_double(self.last_checked_reward_time)

            self.data.write_int_tuple_list(
                self.announcements, write_length=False, length=16
            )
            self.data.write_int(self.backup_counter)
            self.data.write_int(self.ui12)
            self.data.write_int(self.ui13)
            self.data.write_int(self.ui13)
            self.data.write_int(55)

        if self.game_version >= 31:
            self.data.write_bool(self.ub3)
            self.item_reward_stages.write_item_obtains(self.data)
            self.gatya.write_stepup(self.data)

            self.data.write_int(self.backup_frame)
            self.data.write_int(56)

        if self.game_version >= 32:
            self.data.write_bool(self.ub4)
            self.cats.write_favorites(self.data)
            self.data.write_int(57)

        if self.game_version >= 33:
            self.dojo.write_chapters(self.data)
            self.dojo.write_item_locks(self.data)
            self.data.write_int(58)

        if self.game_version >= 34:
            self.data.write_double(self.last_checked_zombie_time)
            self.outbreaks.write_chapters(self.data)
            self.outbreaks.write_2(self.data)
            self.scheme_items.write(self.data)

        if self.game_version >= 35:
            self.outbreaks.write_current_outbreaks(self.data, self.game_version)
            self.data.write_int_bool_dict(self.first_locks)
            self.data.write_double(self.energy_penalty_timestamp)
            self.data.write_int(60)

        if self.game_version >= 36:
            self.cats.write_chara_new_flags(self.data)
            self.data.write_bool(self.shown_maxcollab_mg)
            self.item_pack.write_displayed_packs(self.data)
            self.data.write_int(61)

        if self.game_version >= 38:
            self.unlock_popups.write(self.data)
            self.data.write_int(63)

        if self.game_version >= 39:
            self.ototo.write(self.data)
            self.ototo.write_2(self.data, self.game_version)
            self.data.write_double(self.last_checked_castle_time)
            self.data.write_int(64)

        if self.game_version >= 40:
            self.beacon_base.write(self.data)
            self.data.write_int(65)

        if self.game_version >= 41:
            self.tower.write(self.data)
            self.missions.write(self.data, self.game_version)
            self.tower.write_item_obtain_states(self.data)
            self.data.write_int(66)

        if self.game_version >= 42:
            self.dojo.write_ranking(self.data, self.game_version)
            self.item_pack.write_three_days(self.data)
            self.challenge.write(self.data)
            self.challenge.write_scores(self.data)
            self.challenge.write_popup(self.data)
            self.data.write_int(67)

        if self.game_version >= 43:
            self.missions.write_weekly_missions(self.data)
            self.dojo.ranking.write_did_win_rewards(self.data)
            self.data.write_bool(self.event_update_flags)
            self.data.write_int(68)

        if self.game_version >= 44:
            self.event_stages.write_dicts(self.data)
            self.data.write_int(self.cotc_1_complete)
            self.data.write_int(69)

        if self.game_version >= 46:
            self.gamatoto.write_collab_data(self.data)
            self.data.write_int(71)

        if self.game_version < 90300:
            self.map_resets.write(self.data)
            self.data.write_int(72)

        if self.game_version >= 51:
            self.uncanny.write(self.data)
            self.data.write_int(76)

        if self.game_version >= 77:
            self.catamin_stages.write(self.data)
            self.data.write_int_list(self.lucky_tickets)
            self.data.write_bool(self.ub5)
            self.data.write_int(77)

        if self.game_version >= 80000:
            self.officer_pass.write_gold_pass(self.data, self.game_version)
            self.cats.write_talents(self.data)
            self.data.write_int(self.np)
            self.data.write_bool(self.ub6)
            self.data.write_int(80000)

        if self.game_version >= 80200:
            self.data.write_bool(self.ub7)
            self.data.write_short(self.leadership)
            self.officer_pass.write_cat_data(self.data)
            self.data.write_int(80200)

        if self.game_version >= 80300:
            self.data.write_byte(self.filibuster_stage_id)
            self.data.write_bool(self.filibuster_stage_enabled)
            self.data.write_int(80300)

        if self.game_version >= 80500:
            self.data.write_int_list(self.stage_ids_10s)
            self.data.write_int(80500)

        if self.game_version >= 80600:
            self.data.write_short(len(self.uil6))
            self.data.write_int_list(self.uil6, write_length=False)
            self.legend_quest.write(self.data)
            self.data.write_short(self.ush1)
            self.data.write_byte(self.uby1)
            self.data.write_int(80600)

        if self.game_version >= 80700:
            self.data.write_int(len(self.uiid1))
            for key, value in self.uiid1.items():
                self.data.write_int(key)
                self.data.write_int_list(value)
            self.data.write_int(80700)

        if self.game_version >= 100600:
            if self.is_en():
                self.data.write_byte(self.uby2)
                self.data.write_int(100600)

        if self.game_version >= 81000:
            self.data.write_byte(self.restart_pack)
            self.data.write_int(81000)

        if self.game_version >= 90000:
            self.medals.write(self.data)
            self.wildcat_slots.write(self.data, self.game_version)

            self.data.write_int(90000)

        if self.game_version >= 90100:
            self.data.write_short(self.ush2)
            self.data.write_short(self.ush3)
            self.data.write_int(self.ui15)
            self.data.write_double(self.ud1)
            self.data.write_int(90100)

        if self.game_version >= 90300:
            self.data.write_short(len(self.utl1))
            for tuple_ in self.utl1:
                tuple_len = len(tuple_)
                i1, i2, i3, i4, i5, i6, i7 = 0, 0, 0, 0, 0, 0, 0
                if tuple_len >= 1:
                    i1 = tuple_[0]
                if tuple_len >= 2:
                    i2 = tuple_[1]
                if tuple_len >= 3:
                    i3 = tuple_[2]
                if tuple_len >= 4:
                    i4 = tuple_[3]
                if tuple_len >= 5:
                    i5 = tuple_[4]
                if tuple_len >= 6:
                    i6 = tuple_[5]
                if tuple_len >= 7:
                    i7 = tuple_[6]

                self.data.write_int(i1)
                self.data.write_int(i2)
                self.data.write_short(i3)
                self.data.write_int(i4)
                self.data.write_int(i5)
                self.data.write_int(i6)
                self.data.write_short(i7)

            self.data.write_short(len(self.uidd1))
            self.data.write_int_double_dict(self.uidd1, write_length=False)
            self.gauntlets.write(self.data)
            self.data.write_int(90300)

        if self.game_version >= 90400:
            self.enigma_clears.write(self.data)
            self.enigma.write(self.data, self.game_version)
            self.cleared_slots.write(self.data)
            self.data.write_int(90400)

        if self.game_version >= 90500:
            self.collab_gauntlets.write(self.data)
            self.data.write_bool(self.ub8)
            self.data.write_double(self.ud2)
            self.data.write_double(self.ud3)
            self.data.write_int(self.ui16)
            if self.game_version >= 100300:
                self.data.write_byte(self.uby3)
                self.data.write_bool(self.ub9)
                self.data.write_double(self.ud4)
                self.data.write_double(self.ud5)

            if self.game_version >= 130700:
                self.data.write_short(len(self.uiid3))
                for key, value in self.uiid3.items():
                    self.data.write_int(key)
                    self.data.write_byte(value)

                self.data.write_short(len(self.uidd2))
                for key, value in self.uidd2.items():
                    self.data.write_int(key)
                    self.data.write_double(value)

            if self.game_version >= 140100:
                self.data.write_short(len(self.uidd3))
                for key, value in self.uidd3.items():
                    self.data.write_int(key)
                    self.data.write_double(value)

            self.data.write_int(90500)

        if self.game_version >= 90700:
            self.talent_orbs.write(self.data, self.game_version)
            self.data.write_short(len(self.uidiid2))
            for key, value in self.uidiid2.items():
                self.data.write_short(key)
                self.data.write_byte(len(value))
                for key2, value2 in value.items():
                    self.data.write_byte(key2)
                    self.data.write_short(value2)

            self.data.write_bool(self.ub10)
            self.data.write_int(90700)

        if self.game_version >= 90800:
            self.data.write_short(len(self.uil7))
            self.data.write_int_list(self.uil7, write_length=False)
            self.data.write_bool_list(self.ubl2, write_length=False, length=10)
            self.data.write_int(90800)

        if self.game_version >= 90900:
            self.cat_shrine.write(self.data)
            self.data.write_double(self.ud6)
            self.data.write_double(self.ud7)
            self.data.write_int(90900)

        if self.game_version >= 91000:
            self.lineups.write_slot_names(self.data, self.game_version)
            self.data.write_int(91000)

        if self.game_version >= 100000:
            self.data.write_int(self.legend_tickets)
            self.data.write_byte(len(self.uiil1))
            for key, value in self.uiil1:
                self.data.write_byte(key)
                self.data.write_int(value)

            self.data.write_bool(self.ub11)
            self.data.write_bool(self.ub12)

            self.data.write_string(self.password_refresh_token)

            self.data.write_bool(self.ub13)
            self.data.write_byte(self.uby4)
            self.data.write_byte(self.uby5)
            self.data.write_double(self.ud8)
            self.data.write_double(self.ud9)

            self.data.write_int(100000)

        if self.game_version >= 100100:
            self.data.write_int(self.date_int)
            self.data.write_int(100100)

        if self.game_version >= 100300:
            self.battle_items.write_endless_items(self.data)

            self.data.write_int(100300)

        if self.game_version >= 100400:
            self.data.write_byte(len(self.event_capsules_2))
            self.data.write_int_list(self.event_capsules_2, write_length=False)
            self.data.write_bool(self.two_battle_lines)
            self.data.write_int(100400)

        if self.game_version >= 100600:
            self.data.write_double(self.ud10)
            self.data.write_int(self.platinum_shards)
            self.data.write_bool(self.ub15)
            self.data.write_int(100600)

        if self.game_version >= 100700:
            self.cat_scratcher.write(self.data, self.game_version)

            self.data.write_int(100700)

        if self.game_version >= 100900:
            self.aku.write(self.data)
            self.data.write_bool(self.ub16)
            self.data.write_bool(self.ub17)

            self.data.write_short(len(self.ushdshd2))
            for key, value in self.ushdshd2.items():
                self.data.write_short(key)
                self.data.write_short(len(value))
                for item in value:
                    self.data.write_short(item)

            self.data.write_short(len(self.ushdd))
            for key, value in self.ushdd.items():
                self.data.write_short(key)
                self.data.write_double(value)

            self.data.write_short(len(self.ushdd2))
            for key, value in self.ushdd2.items():
                self.data.write_short(key)
                self.data.write_double(value)

            self.data.write_bool(self.ub18)
            self.data.write_int(100900)

        if self.game_version >= 101000:
            self.data.write_byte(self.uby6)
            self.data.write_int(101000)

        if self.game_version >= 110000:
            self.data.write_short(len(self.uidtii))
            for key, value in self.uidtii.items():
                self.data.write_int(key)
                self.data.write_byte(value[0])
                self.data.write_byte(value[1])

            self.data.write_int(110000)

        if self.game_version >= 110500:
            self.behemoth_culling.write(self.data)
            self.data.write_bool(self.ub19)
            self.data.write_int(110500)

        if self.game_version >= 110600:
            self.data.write_bool(self.ub20)
            self.data.write_int(110600)

        if self.game_version >= 110700:
            self.data.write_int(len(self.uidtff))
            for key, value in self.uidtff.items():
                self.data.write_int(key)
                self.data.write_double(value[0])
                self.data.write_double(value[1])

            if self.not_jp():
                self.data.write_bool(self.ub20)
            self.data.write_int(110700)

        if self.game_version >= 110800:
            self.cat_shrine.write_dialogs(self.data)
            self.data.write_bool(self.ub21)
            self.data.write_bool(self.dojo_3x_speed)
            self.data.write_bool(self.ub22)
            self.data.write_bool(self.ub23)

            self.data.write_int(110800)

        if self.game_version >= 111000:
            self.data.write_int(self.ui17)
            self.data.write_short(self.ush4)
            self.data.write_byte(self.uby7)
            self.data.write_byte(self.uby8)
            self.data.write_bool(self.ub24)
            self.data.write_byte(self.uby9)

            self.data.write_byte(len(self.ushl1))
            self.data.write_short_list(self.ushl1, write_length=False)

            self.data.write_short(len(self.ushl2))
            self.data.write_short_list(self.ushl2, write_length=False)

            self.data.write_short(len(self.ushl3))
            self.data.write_short_list(self.ushl3, write_length=False)

            self.data.write_int(self.ui18)
            self.data.write_int(self.ui19)
            self.data.write_int(self.ui20)
            self.data.write_short(self.ush5)
            self.data.write_short(self.ush6)
            self.data.write_short(self.ush7)
            self.data.write_short(self.ush8)
            self.data.write_byte(self.uby10)
            self.data.write_bool(self.ub25)
            self.data.write_bool(self.ub26)
            self.data.write_bool(self.ub27)
            self.data.write_bool(self.ub28)
            self.data.write_bool(self.ub29)
            self.data.write_bool(self.ub30)
            self.data.write_byte(self.uby11)

            self.data.write_short(len(self.ushl4))
            self.data.write_short_list(self.ushl4, write_length=False)

            self.data.write_bool_list(self.ubl3, write_length=False, length=14)

            self.data.write_byte(len(self.labyrinth_medals))
            self.data.write_short_list(self.labyrinth_medals, write_length=False)

            self.data.write_int(111000)

        if self.game_version >= 120000:
            self.zero_legends.write(self.data)
            self.data.write_byte(self.uby12)

            self.data.write_int(120000)

        if self.game_version >= 120100:
            self.data.write_short(len(self.ushl6))
            self.data.write_short_list(self.ushl6, write_length=False)

            self.data.write_int(120100)

        if self.game_version >= 120200:
            self.data.write_bool(self.ub31)
            self.data.write_short(self.ush9)
            self.data.write_byte(len(self.ushshd))
            for key, value in self.ushshd.items():
                self.data.write_short(key)
                self.data.write_short(value)

            self.data.write_int(120200)

        if self.game_version >= 120400:
            self.data.write_double(self.ud11)
            self.data.write_double(self.ud12)

            self.data.write_int(120400)

        if self.game_version >= 120500:
            self.data.write_bool(self.ub32)
            self.data.write_bool(self.ub33)
            self.data.write_bool(self.ub34)
            self.data.write_int(self.ui21)
            self.data.write_byte(self.golden_cpu_count)

            self.data.write_int(120500)

        if self.game_version >= 120600:
            self.data.write_byte(self.sound_effects_volume)
            self.data.write_byte(self.background_music_volume)

            self.data.write_int(120600)

        if (self.not_jp() and self.game_version >= 120700) or (
            self.is_jp() and self.game_version >= 130000
        ):
            self.data.write_byte(len(self.ustl1))
            for str1, str2 in self.ustl1:
                self.data.write_string(str1)
                self.data.write_string(str2)

            if self.not_jp():
                self.data.write_int(120700)
            else:
                self.data.write_int(130000)

        if self.game_version >= 130100:
            self.data.write_int(len(self.utl3))
            for i, long in self.utl3:
                self.data.write_int(i)
                self.data.write_long(long)

            self.data.write_int(130100)

        if self.game_version >= 130301:
            self.data.write_int(len(self.ustid1))
            for key, (v1, v2) in self.ustid1.items():
                self.data.write_string(key)
                self.data.write_int(v1)
                self.data.write_double(v2)

            self.data.write_int(130301)

        if self.game_version >= 130400:
            self.data.write_double(self.ud13)
            self.data.write_double(self.ud14)

            self.data.write_int(130400)

        if self.game_version >= 130500:
            self.data.write_short(len(self.utl4))
            for id, ls2 in self.utl4:
                self.data.write_byte(id)
                self.data.write_byte(len(ls2))
                for v1, v2, v3, ls1 in ls2:
                    self.data.write_byte(v1)
                    self.data.write_byte(v2)
                    self.data.write_byte(v3)

                    self.data.write_short(len(ls1))

                    for val in ls1:
                        self.data.write_short(val)

            self.data.write_int(130500)

        if self.game_version >= 130600:
            self.data.write_byte(self.uby14)

            if self.not_jp():
                self.data.write_short(self.ush12)

            self.data.write_int(130600)

        if self.game_version >= 130700:
            if self.is_jp():
                self.data.write_short(self.ush12)

            self.data.write_double(self.ud15)
            self.data.write_byte(self.uby15)
            self.data.write_byte(self.uby16)

            self.data.write_short(self.ush11)
            self.data.write_byte(self.uby17)
            self.data.write_byte(self.uby18)
            self.data.write_byte(self.uby19)

            self.data.write_double(self.ud16)

            self.data.write_short(len(self.ushd1))

            for key, (value, value_2, data_2) in self.ushd1.items():
                self.data.write_short(key)
                self.data.write_short(value)
                self.data.write_int(value_2)

                self.data.write_short(len(data_2))

                for key2, value3 in data_2.items():
                    self.data.write_short(key2)
                    self.data.write_short(value3)

            self.data.write_int(130700)
        if self.game_version >= 140000:
            self.data.write_int(self.ui22)
            self.data.write_double(self.ud17)
            self.data.write_byte(self.uby20)

            self.data.write_byte(len(self.uild1))

            for key, value in self.uild1.items():
                self.data.write_int(key)
                self.data.write_byte(len(value))
                for val in value:
                    self.data.write_byte(val)

            self.dojo_chapters.write(self.data)

            self.data.write_short(len(self.uil9))
            for val in self.uil9:
                self.data.write_int(val)

            self.data.write_bool(self.ub35)
            self.data.write_double(self.ud18)

            self.data.write_short(len(self.ushd2))

            for key, value in self.ushd2.items():
                self.data.write_short(key)
                self.data.write_byte(value)

            self.data.write_int(140000)

        if self.game_version >= 140100 and self.game_version < 140500:
            self.data.write_byte(self.uby21)
            self.data.write_int(140100)

        if self.game_version >= 140200:
            self.data.write_byte(len(self.uil10))

            for v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11, v12, v13 in self.uil10:
                self.data.write_int(v1)
                self.data.write_int(v2)
                self.data.write_bool(v3)
                self.data.write_bool(v4)
                self.data.write_bool(v5)
                self.data.write_int(v6)
                self.data.write_int(v7)
                self.data.write_int(v8)
                self.data.write_bool(v9)
                self.data.write_bool(v10)
                self.data.write_bool(v11)
                if self.game_version >= 140500:
                    # game seems to write more than this, may not work with all saves
                    self.data.write_string(v12 or "")

                self.data.write_bool(v13)

            self.data.write_byte(len(self.uid1))

            for key, value in self.uid1.items():
                self.data.write_int(key)
                self.data.write_double(value)

            self.data.write_int(self.hundred_million_ticket)
            self.data.write_int(140200)

        if self.game_version >= 140300:
            self.data.write_byte(len(self.uil11))
            for val in self.uil11:
                self.data.write_byte(val)

            self.data.write_bool(self.ub36)

            self.data.write_byte(len(self.treasure_chests))

            for val in self.treasure_chests:
                self.data.write_int(val)

            self.data.write_int(self.ui23)
            self.data.write_short(len(self.uil13))

            for val in self.uil13:
                self.data.write_int(val)

            self.data.write_bool(self.ub37)
            self.data.write_int(140300)

        self.data.write_bytes(self.remaining_data)

        self.data.end_buffer()

    def to_data(self) -> core.Data:
        dt = core.Data()
        self.save_wrapper(dt)
        self.set_hash(add=True)
        return dt

    def save_wrapper(self, data: core.Data) -> None:
        try:
            self.save(data)
        except Exception as e:
            raise FailedToSaveError(
                core.core_data.local_manager.get_key("failed_to_save_save")
            ) from e

    def to_file_thread(self, path: core.Path):
        core.Thread("to_file", self.to_file, [path]).start()

    def to_file(self, path: core.Path) -> None:
        path.parent().generate_dirs()
        dt = self.to_data()
        dt.to_file(path)

    @staticmethod
    def get_temp_path() -> core.Path:
        save_temp_path = core.Path.get_documents_folder().add("save.temp")
        save_temp_path.parent().generate_dirs()
        return save_temp_path

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "editor_version": __version__,
            "cc": self.cc.get_code(),
            "dsts": self.dsts,
            "game_version": self.game_version.game_version,
            "ub1": self.ub1,
            "mute_bgm": self.mute_bgm,
            "mute_se": self.mute_se,
            "catfood": self.catfood,
            "current_energy": self.current_energy,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "timestamp": self.timestamp,
            "date": self.date.timestamp(),
            "ui1": self.ui1,
            "stamp_value_save": self.stamp_value_save,
            "ui2": self.ui2,
            "upgrade_state": self.upgrade_state,
            "xp": self.xp,
            "tutorial_state": self.tutorial_state,
            "ui3": self.ui3,
            "koreaSuperiorTreasureState": self.koreaSuperiorTreasureState,
            "unlock_popups_11": self.unlock_popups_11,
            "ui5": self.ui5,
            "unlock_enemy_guide": self.unlock_enemy_guide,
            "ui6": self.ui6,
            "ub0": self.ub0,
            "ui7": self.ui7,
            "cleared_eoc_1": self.cleared_eoc_1,
            "ui8": self.ui8,
            "unlocked_ending": self.unlocked_ending,
            "lineups": self.lineups.serialize(),
            "stamp_data": self.stamp_data.serialize(),
            "story": self.story.serialize(),
            "enemy_guide": self.enemy_guide,
            "cats": self.cats.serialize(),
            "special_skills": self.special_skills.serialize(),
            "menu_unlocks": self.menu_unlocks,
            "unlock_popups_0": self.unlock_popups_0,
            "battle_items": self.battle_items.serialize(),
            "new_dialogs_2": self.new_dialogs_2,
            "uil1": self.uil1,
            "moneko_bonus": self.moneko_bonus,
            "daily_reward_initialized": self.daily_reward_initialized,
            "date_2": self.date_2.timestamp(),
            "date_3": self.date_3.timestamp(),
            "ui0": self.ui0,
            "stage_unlock_cat_value": self.stage_unlock_cat_value,
            "show_ending_value": self.show_ending_value,
            "chapter_clear_cat_unlock": self.chapter_clear_cat_unlock,
            "ui9": self.ui9,
            "ios_android_month": self.ios_android_month,
            "ui10": self.ui10,
            "save_data_4_hash": self.save_data_4_hash,
            "mysale": self.mysale.serialize(),
            "chara_flags": self.chara_flags,
            "uim1": self.uim1,
            "ubm1": self.ubm1,
            "chara_flags_2": self.chara_flags_2,
            "normal_tickets": self.normal_tickets,
            "rare_tickets": self.rare_tickets,
            "event_stages": self.event_stages.serialize(),
            "itf1_ending": self.itf1_ending,
            "continue_flag": self.continue_flag,
            "unlock_popups_8": self.unlock_popups_8,
            "unit_drops": self.unit_drops,
            "gatya": self.gatya.serialize(),
            "get_event_data": self.get_event_data,
            "achievements": self.achievements,
            "os_value": self.os_value,
            "date_4": self.date_4.timestamp(),
            "player_id": self.player_id,
            "order_ids": self.order_ids,
            "g_timestamp": self.g_timestamp,
            "g_servertimestamp": self.g_servertimestamp,
            "m_gettimesave": self.m_gettimesave,
            "usl1": self.usl1,
            "energy_notification": self.energy_notification,
            "full_gameversion": self.full_gameversion,
            "uil2": self.uil2,
            "uil3": self.uil3,
            "uil4": self.uil4,
            "g_timestamp_2": self.g_timestamp_2,
            "g_servertimestamp_2": self.g_servertimestamp_2,
            "m_gettimesave_2": self.m_gettimesave_2,
            "unknown_timestamp": self.unknown_timestamp,
            "usl2": self.usl2,
            "m_dGetTimeSave2": self.m_dGetTimeSave2,
            "ui11": self.ui11,
            "ubl1": self.ubl1,
            "user_rank_rewards": self.user_rank_rewards.serialize(),
            "transfer_code": self.transfer_code,
            "confirmation_code": self.confirmation_code,
            "transfer_flag": self.transfer_flag,
            "item_reward_stages": self.item_reward_stages.serialize(),
            "timed_score_stages": self.timed_score_stages.serialize(),
            "inquiry_code": self.inquiry_code,
            "officer_pass": self.officer_pass.serialize(),
            "has_account": self.has_account,
            "backup_state": self.backup_state,
            "ub2": self.ub2,
            "itf1_complete": self.itf1_complete,
            "title_chapter_bg": self.title_chapter_bg,
            "combo_unlocks": self.combo_unlocks,
            "combo_unlocked_10k_ur": self.combo_unlocked_10k_ur,
            "event_capsules": self.event_capsules,
            "event_capsules_counter": self.event_capsules_counter,
            "m_dGetTimeSave3": self.m_dGetTimeSave3,
            "gatya_seen_lucky_drops": self.gatya_seen_lucky_drops,
            "banned": self.show_ban_message,
            "catfood_beginner_purchased": self.catfood_beginner_purchased,
            "next_week_timestamp": self.next_week_timestamp,
            "catfood_beginner_expired": self.catfood_beginner_expired,
            "rank_up_sale_value": self.rank_up_sale_value,
            "time_since_time_check_cumulative": self.time_since_time_check_cumulative,
            "server_timestamp": self.server_timestamp,
            "last_checked_energy_recovery_time": self.last_checked_energy_recovery_time,
            "time_since_check": self.time_since_check,
            "last_checked_expedition_time": self.last_checked_expedition_time,
            "catfruit": self.catfruit,
            "catseyes": self.catseyes,
            "catamins": self.catamins,
            "gamatoto": self.gamatoto.serialize(),
            "unlock_popups_6": self.unlock_popups_6,
            "ex_stages": self.ex_stages.serialize(),
            "item_pack": self.item_pack.serialize(),
            "platinum_tickets": self.platinum_tickets,
            "logins": self.logins.serialize(),
            "reset_item_reward_flags": self.reset_item_reward_flags,
            "reward_remaining_time": self.reward_remaining_time,
            "last_checked_reward_time": self.last_checked_reward_time,
            "announcements": self.announcements,
            "backup_counter": self.backup_counter,
            "ui12": self.ui12,
            "ui13": self.ui13,
            "ui14": self.ui14,
            "ub3": self.ub3,
            "backup_frame": self.backup_frame,
            "ub4": self.ub4,
            "dojo": self.dojo.serialize(),
            "last_checked_zombie_time": self.last_checked_zombie_time,
            "outbreaks": self.outbreaks.serialize(),
            "scheme_items": self.scheme_items.serialize(),
            "first_locks": self.first_locks,
            "energy_penalty_timestamp": self.energy_penalty_timestamp,
            "shown_maxcollab_mg": self.shown_maxcollab_mg,
            "unlock_popups": self.unlock_popups.serialize(),
            "ototo": self.ototo.serialize(),
            "last_checked_castle_time": self.last_checked_castle_time,
            "beacon_base": self.beacon_base.serialize(),
            "tower": self.tower.serialize(),
            "missions": self.missions.serialize(),
            "challenge": self.challenge.serialize(),
            "event_update_flags": self.event_update_flags,
            "cotc_1_complete": self.cotc_1_complete,
            "map_resets": self.map_resets.serialize(),
            "uncanny": self.uncanny.serialize(),
            "catamin_stages": self.catamin_stages.serialize(),
            "lucky_tickets": self.lucky_tickets,
            "ub5": self.ub5,
            "np": self.np,
            "ub6": self.ub6,
            "ub7": self.ub7,
            "leadership": self.leadership,
            "filibuster_stage_id": self.filibuster_stage_id,
            "filibuster_stage_enabled": self.filibuster_stage_enabled,
            "stage_ids_10s": self.stage_ids_10s,
            "uil6": self.uil6,
            "legend_quest": self.legend_quest.serialize(),
            "ush1": self.ush1,
            "uby1": self.uby1,
            "uiid1": self.uiid1,
            "uby2": self.uby2,
            "restart_pack": self.restart_pack,
            "medals": self.medals.serialize(),
            "wildcat_slots": self.wildcat_slots.serialize(),
            "ush2": self.ush2,
            "ush3": self.ush3,
            "ui15": self.ui15,
            "ud1": self.ud1,
            "utl1": self.utl1,
            "uidd1": self.uidd1,
            "gauntlets": self.gauntlets.serialize(),
            "enigma_clears": self.enigma_clears.serialize(),
            "enigma": self.enigma.serialize(),
            "cleared_slots": self.cleared_slots.serialize(),
            "collab_gauntlets": self.collab_gauntlets.serialize(),
            "ub8": self.ub8,
            "ud2": self.ud2,
            "ud3": self.ud3,
            "ui16": self.ui16,
            "uby3": self.uby3,
            "ub9": self.ub9,
            "ud4": self.ud4,
            "ud5": self.ud5,
            "uiid3": self.uiid3,
            "uidd2": self.uidd2,
            "uidd3": self.uidd3,
            "talent_orbs": self.talent_orbs.serialize(),
            "uidiid2": self.uidiid2,
            "ub10": self.ub10,
            "uil7": self.uil7,
            "ubl2": self.ubl2,
            "cat_shrine": self.cat_shrine.serialize(),
            "ud6": self.ud6,
            "ud7": self.ud7,
            "legend_tickets": self.legend_tickets,
            "uiil1": self.uiil1,
            "ub11": self.ub11,
            "ub12": self.ub12,
            "password_refresh_token": self.password_refresh_token,
            "ub13": self.ub13,
            "uby4": self.uby4,
            "uby5": self.uby5,
            "ud8": self.ud8,
            "ud9": self.ud9,
            "date_int": self.date_int,
            "event_capsules_2": self.event_capsules_2,
            "two_battle_lines": self.two_battle_lines,
            "ud10": self.ud10,
            "platinum_shards": self.platinum_shards,
            "ub15": self.ub15,
            "cat_scratcher": self.cat_scratcher.serialize(),
            "aku": self.aku.serialize(),
            "ub16": self.ub16,
            "ub17": self.ub17,
            "ushdshd2": self.ushdshd2,
            "ushdd": self.ushdd,
            "ushdd2": self.ushdd2,
            "ub18": self.ub18,
            "uby6": self.uby6,
            "uidtii": self.uidtii,
            "behemoth_culling": self.behemoth_culling.serialize(),
            "ub19": self.ub19,
            "ub20": self.ub20,
            "uidtff": self.uidtff,
            "ub21": self.ub21,
            "dojo_3x_speed": self.dojo_3x_speed,
            "ub22": self.ub22,
            "ub23": self.ub23,
            "ui17": self.ui17,
            "ush4": self.ush4,
            "uby7": self.uby7,
            "uby8": self.uby8,
            "ub24": self.ub24,
            "uby9": self.uby9,
            "ushl1": self.ushl1,
            "ushl2": self.ushl2,
            "ushl3": self.ushl3,
            "ui18": self.ui18,
            "ui19": self.ui19,
            "ui20": self.ui20,
            "ush5": self.ush5,
            "ush6": self.ush6,
            "ush7": self.ush7,
            "ush8": self.ush8,
            "uby10": self.uby10,
            "ub25": self.ub25,
            "ub26": self.ub26,
            "ub27": self.ub27,
            "ub28": self.ub28,
            "ub29": self.ub29,
            "ub30": self.ub30,
            "uby11": self.uby11,
            "ushl4": self.ushl4,
            "ubl3": self.ubl3,
            "labyrinth_medals": self.labyrinth_medals,
            "zero_legends": self.zero_legends.serialize(),
            "uby12": self.uby12,
            "ushl6": self.ushl6,
            "ub31": self.ub31,
            "ush9": self.ush9,
            "ushshd": self.ushshd,
            "ud11": self.ud11,
            "ud12": self.ud12,
            "ub32": self.ub32,
            "ub33": self.ub33,
            "ub34": self.ub34,
            "ui21": self.ui21,
            "golden_cpu_count": self.golden_cpu_count,
            "sound_effects_volume": self.sound_effects_volume,
            "background_music_volume": self.background_music_volume,
            "ustl1": self.ustl1,
            "utl3": self.utl3,
            "ustid1": self.ustid1,
            "ud13": self.ud13,
            "ud14": self.ud14,
            "utl4": self.utl4,
            "uby14": self.uby14,
            "ush12": self.ush12,
            "ud15": self.ud15,
            "uby15": self.uby15,
            "uby16": self.uby16,
            "ush11": self.ush11,
            "uby17": self.uby17,
            "uby18": self.uby18,
            "uby19": self.uby19,
            "ud16": self.ud16,
            "ushd1": self.ushd1,
            "ui22": self.ui22,
            "ud17": self.ud17,
            "uby20": self.uby20,
            "uild1": self.uild1,
            "dojo_chapters": self.dojo_chapters.serialize(),
            "uil9": self.uil9,
            "ub35": self.ub35,
            "ud18": self.ud18,
            "ushd2": self.ushd2,
            "uby21": self.uby21,
            "uil10": self.uil10,
            "uid1": self.uid1,
            "hundred_million_ticket": self.hundred_million_ticket,
            "uil11": self.uil11,
            "ub36": self.ub36,
            "treasure_chests": self.treasure_chests,
            "ui23": self.ui23,
            "uil13": self.uil13,
            "ub37": self.ub37,
            "remaining_data": base64.b64encode(self.remaining_data).decode("utf-8"),
        }
        return data

    @staticmethod
    def from_dict(data: dict[str, Any], warn: bool = True) -> SaveFile:
        editor_version = data.get("editor_version", "0.0.0")
        if editor_version != __version__ and warn:
            cli.color.ColoredText.localize(
                "editor_version_mismatch",
                json_version=editor_version,
                editor_version=__version__,
            )
        cc = data.get("cc")
        if cc is not None:
            cc = core.CountryCode(cc)
        else:
            cc = None
        save_file = SaveFile(cc=cc)
        save_file.dsts = data.get("dsts", [])
        save_file.game_version = core.GameVersion(data.get("game_version", 0))
        save_file.ub1 = data.get("ub1", False)
        save_file.mute_bgm = data.get("mute_bgm", False)
        save_file.mute_se = data.get("mute_se", False)
        save_file.catfood = data.get("catfood", 0)
        save_file.current_energy = data.get("current_energy", 0)
        save_file.year = data.get("year", 0)
        save_file.month = data.get("month", 0)
        save_file.day = data.get("day", 0)
        save_file.timestamp = data.get("timestamp", 0.0)
        save_file.date = datetime.datetime.fromtimestamp(data.get("date", 0))
        save_file.ui1 = data.get("ui1", 0)
        save_file.stamp_value_save = data.get("stamp_value_save", 0)
        save_file.ui2 = data.get("ui2", 0)
        save_file.upgrade_state = data.get("upgrade_state", 0)
        save_file.xp = data.get("xp", 0)
        save_file.tutorial_state = data.get("tutorial_state", 0)
        save_file.ui3 = data.get("ui3", 0)
        save_file.koreaSuperiorTreasureState = data.get("koreaSuperiorTreasureState", 0)
        save_file.unlock_popups_11 = data.get("unlock_popups_11", [])
        save_file.ui5 = data.get("ui5", 0)
        save_file.unlock_enemy_guide = data.get("unlock_enemy_guide", 0)
        save_file.ui6 = data.get("ui6", 0)
        save_file.ub0 = data.get("ub0", False)
        save_file.ui7 = data.get("ui7", 0)
        save_file.cleared_eoc_1 = data.get("cleared_eoc_1", 0)
        save_file.ui8 = data.get("ui8", 0)
        save_file.unlocked_ending = data.get("unlocked_ending", 0)
        save_file.lineups = core.LineUps.deserialize(data.get("lineups", {}))
        save_file.stamp_data = core.StampData.deserialize(data.get("stamp_data", {}))
        save_file.story = core.StoryChapters.deserialize(data.get("story", []))
        save_file.enemy_guide = data.get("enemy_guide", [])
        save_file.cats = core.Cats.deserialize(data.get("cats", {}))
        save_file.special_skills = core.SpecialSkills.deserialize(
            data.get("special_skills", [])
        )
        save_file.menu_unlocks = data.get("menu_unlocks", [])
        save_file.unlock_popups_0 = data.get("unlock_popups_0", [])
        save_file.battle_items = core.BattleItems.deserialize(
            data.get("battle_items", {})
        )
        save_file.new_dialogs_2 = data.get("new_dialogs_2", [])
        save_file.uil1 = data.get("uil1", [])
        save_file.moneko_bonus = data.get("moneko_bonus", [])
        save_file.daily_reward_initialized = data.get("daily_reward_initialized", [])
        save_file.date_2 = datetime.datetime.fromtimestamp(data.get("date_2", 0))
        save_file.date_3 = datetime.datetime.fromtimestamp(data.get("date_3", 0))
        save_file.ui0 = data.get("ui0", 0)
        save_file.stage_unlock_cat_value = data.get("stage_unlock_cat_value", 0)
        save_file.show_ending_value = data.get("show_ending_value", 0)
        save_file.chapter_clear_cat_unlock = data.get("chapter_clear_cat_unlock", 0)
        save_file.ui9 = data.get("ui9", 0)
        save_file.ios_android_month = data.get("ios_android_month", 0)
        save_file.ui10 = data.get("ui10", 0)
        save_file.save_data_4_hash = data.get("save_data_4_hash", "")
        save_file.mysale = core.MySale.deserialize(data.get("mysale", {}))
        save_file.chara_flags = data.get("chara_flags", [])
        save_file.uim1 = data.get("uim1", 0)
        save_file.ubm1 = data.get("ubm1", False)
        save_file.chara_flags_2 = data.get("chara_flags_2", [])
        save_file.normal_tickets = data.get("normal_tickets", 0)
        save_file.rare_tickets = data.get("rare_tickets", 0)
        save_file.event_stages = core.EventChapters.deserialize(
            data.get("event_stages", {})
        )
        save_file.itf1_ending = data.get("itf1_ending", 0)
        save_file.continue_flag = data.get("continue_flag", 0)
        save_file.unlock_popups_8 = data.get("unlock_popups_8", [])
        save_file.unit_drops = data.get("unit_drops", [])
        save_file.gatya = core.Gatya.deserialize(data.get("gatya", {}))
        save_file.get_event_data = data.get("get_event_data", False)
        save_file.achievements = data.get("achievements", [])
        save_file.os_value = data.get("os_value", 0)
        save_file.date_4 = datetime.datetime.fromtimestamp(data.get("date_4", 0))
        save_file.player_id = data.get("player_id", "")
        save_file.order_ids = data.get("order_ids", [])
        save_file.g_timestamp = data.get("g_timestamp", 0.0)
        save_file.g_servertimestamp = data.get("g_servertimestamp", 0.0)
        save_file.m_gettimesave = data.get("m_gettimesave", 0.0)
        save_file.usl1 = data.get("usl1", [])
        save_file.energy_notification = data.get("energy_notification", False)
        save_file.full_gameversion = data.get("full_gameversion", 0)
        save_file.uil2 = data.get("uil2", [])
        save_file.uil3 = data.get("uil3", [])
        save_file.uil4 = data.get("uil4", [])
        save_file.g_timestamp_2 = data.get("g_timestamp_2", 0.0)
        save_file.g_servertimestamp_2 = data.get("g_servertimestamp_2", 0.0)
        save_file.m_gettimesave_2 = data.get("m_gettimesave_2", 0.0)
        save_file.unknown_timestamp = data.get("unknown_timestamp", 0.0)
        save_file.usl2 = data.get("usl2", [])
        save_file.m_dGetTimeSave2 = data.get("m_dGetTimeSave2", 0.0)
        save_file.ui11 = data.get("ui11", 0)
        save_file.ubl1 = data.get("ubl1", [])
        save_file.user_rank_rewards = core.UserRankRewards.deserialize(
            data.get("user_rank_rewards", [])
        )
        save_file.transfer_code = data.get("transfer_code", "")
        save_file.confirmation_code = data.get("confirmation_code", "")
        save_file.transfer_flag = data.get("transfer_flag", False)
        save_file.item_reward_stages = core.ItemRewardChapters.deserialize(
            data.get("item_reward_stages", {})
        )
        save_file.timed_score_stages = core.TimedScoreChapters.deserialize(
            data.get("timed_score_stages", [])
        )
        save_file.inquiry_code = data.get("inquiry_code", "")
        save_file.officer_pass = core.OfficerPass.deserialize(
            data.get("officer_pass", {})
        )
        save_file.has_account = data.get("has_account", False)
        save_file.backup_state = data.get("backup_state", 0)
        save_file.ub2 = data.get("ub2", False)
        save_file.itf1_complete = data.get("itf1_complete", 0)
        save_file.title_chapter_bg = data.get("title_chapter_bg", 0)
        save_file.combo_unlocks = data.get("combo_unlocks", [])
        save_file.combo_unlocked_10k_ur = data.get("combo_unlocked_10k_ur", False)
        save_file.event_capsules = data.get("event_capsules", [])
        save_file.event_capsules_counter = data.get("event_capsules_counter", [])
        save_file.m_dGetTimeSave3 = data.get("m_dGetTimeSave3", 0.0)
        save_file.gatya_seen_lucky_drops = data.get("gatya_seen_lucky_drops", [])
        save_file.show_ban_message = data.get("banned", False)
        save_file.catfood_beginner_purchased = data.get(
            "catfood_beginner_purchased", []
        )
        save_file.next_week_timestamp = data.get("next_week_timestamp", 0.0)
        save_file.catfood_beginner_expired = data.get("catfood_beginner_expired", [])
        save_file.rank_up_sale_value = data.get("rank_up_sale_value", 0)
        save_file.time_since_time_check_cumulative = data.get(
            "time_since_time_check_cumulative", 0.0
        )
        save_file.server_timestamp = data.get("server_timestamp", 0.0)
        save_file.last_checked_energy_recovery_time = data.get(
            "last_checked_energy_recovery_time", 0.0
        )
        save_file.time_since_check = data.get("time_since_check", 0.0)
        save_file.last_checked_expedition_time = data.get(
            "last_checked_expedition_time", 0.0
        )
        save_file.catfruit = data.get("catfruit", [])
        save_file.catseyes = data.get("catseyes", [])
        save_file.catamins = data.get("catamins", [])
        save_file.gamatoto = core.Gamatoto.deserialize(data.get("gamatoto", {}))
        save_file.unlock_popups_6 = data.get("unlock_popups_6", [])
        save_file.ex_stages = core.ExChapters.deserialize(data.get("ex_stages", []))
        save_file.item_pack = core.ItemPack.deserialize(data.get("item_pack", {}))
        save_file.platinum_tickets = data.get("platinum_tickets", 0)
        save_file.logins = core.LoginBonus.deserialize(data.get("logins", {}))
        save_file.reset_item_reward_flags = data.get("reset_item_reward_flags", [])
        save_file.reward_remaining_time = data.get("reward_remaining_time", 0.0)
        save_file.last_checked_reward_time = data.get("last_checked_reward_time", 0.0)
        save_file.announcements = data.get("announcements", [])
        save_file.backup_counter = data.get("backup_counter", 0)
        save_file.ui12 = data.get("ui12", 0)
        save_file.ui13 = data.get("ui13", 0)
        save_file.ui14 = data.get("ui14", 0)
        save_file.ub3 = data.get("ub3", False)
        save_file.backup_frame = data.get("backup_frame", 0)
        save_file.ub4 = data.get("ub4", False)
        save_file.dojo = core.Dojo.deserialize(data.get("dojo", {}))
        save_file.last_checked_zombie_time = data.get("last_checked_zombie_time", 0.0)
        save_file.outbreaks = core.Outbreaks.deserialize(data.get("outbreaks", {}))
        save_file.scheme_items = core.SchemeItems.deserialize(
            data.get("scheme_items", {})
        )
        save_file.first_locks = data.get("first_locks", {})
        save_file.energy_penalty_timestamp = data.get("energy_penalty_timestamp", 0.0)
        save_file.shown_maxcollab_mg = data.get("shown_maxcollab_mg", False)
        save_file.unlock_popups = core.UnlockPopups.deserialize(
            data.get("unlock_popups", {})
        )
        save_file.ototo = core.Ototo.deserialize(data.get("ototo", {}))
        save_file.last_checked_castle_time = data.get("last_checked_castle_time", 0.0)
        save_file.beacon_base = core.BeaconEventListScene.deserialize(
            data.get("beacon_base", {})
        )
        save_file.tower = core.TowerChapters.deserialize(data.get("tower", {}))
        save_file.missions = core.Missions.deserialize(data.get("missions", {}))
        save_file.challenge = core.ChallengeChapters.deserialize(
            data.get("challenge", {})
        )
        save_file.event_update_flags = data.get("event_update_flags", [])
        save_file.cotc_1_complete = data.get("cotc_1_complete", False)
        save_file.map_resets = core.MapResets.deserialize(data.get("map_resets", {}))
        save_file.uncanny = core.UncannyChapters.deserialize(data.get("uncanny", {}))
        save_file.catamin_stages = core.UncannyChapters.deserialize(
            data.get("catamin_stages", {})
        )
        save_file.lucky_tickets = data.get("lucky_tickets", [])
        save_file.ub5 = data.get("ub5", False)
        save_file.np = data.get("np", 0)
        save_file.ub6 = data.get("ub6", False)
        save_file.ub7 = data.get("ub7", False)
        save_file.leadership = data.get("leadership", 0)
        save_file.filibuster_stage_id = data.get("filibuster_stage_id", 0)
        save_file.filibuster_stage_enabled = data.get("filibuster_stage_enabled", False)
        save_file.stage_ids_10s = data.get("stage_ids_10s", [])
        save_file.uil6 = data.get("uil6", [])
        save_file.legend_quest = core.LegendQuestChapters.deserialize(
            data.get("legend_quest", {})
        )
        save_file.ush1 = data.get("ush1", 0)
        save_file.uby1 = data.get("uby1", 0)
        save_file.uiid1 = data.get("uiid1", {})
        save_file.uby2 = data.get("uby2", 0)
        save_file.restart_pack = data.get("restart_pack", 0)
        save_file.medals = core.Medals.deserialize(data.get("medals", {}))
        save_file.wildcat_slots = core.GamblingEvent.deserialize(
            data.get("wildcat_slots", {})
        )
        save_file.ush2 = data.get("ush2", 0)
        save_file.ush3 = data.get("ush3", 0)
        save_file.ui15 = data.get("ui15", 0)
        save_file.ud1 = data.get("ud1", 0.0)
        save_file.utl1 = data.get("utl1", [])
        save_file.uidd1 = data.get("uidd1", {})
        save_file.gauntlets = core.GauntletChapters.deserialize(
            data.get("gauntlets", {})
        )
        save_file.enigma_clears = core.GauntletChapters.deserialize(
            data.get("enigma_clears", {})
        )
        save_file.enigma = core.Enigma.deserialize(data.get("enigma", {}))
        save_file.cleared_slots = core.ClearedSlots.deserialize(
            data.get("cleared_slots", {})
        )
        save_file.collab_gauntlets = core.GauntletChapters.deserialize(
            data.get("collab_gauntlets", {})
        )
        save_file.ub8 = data.get("ub8", False)
        save_file.ud2 = data.get("ud2", 0.0)
        save_file.ud3 = data.get("ud3", 0.0)
        save_file.ui16 = data.get("ui16", 0)
        save_file.uby3 = data.get("uby3", 0)
        save_file.ub9 = data.get("ub9", False)
        save_file.ud4 = data.get("ud4", 0.0)
        save_file.ud5 = data.get("ud5", 0.0)
        save_file.uiid3 = data.get("uiid3", {})
        save_file.uidd2 = data.get("uidd2", {})
        save_file.uidd3 = data.get("uidd3", {})
        save_file.talent_orbs = core.TalentOrbs.deserialize(data.get("talent_orbs", {}))
        save_file.uidiid2 = data.get("uidiid2", {})
        save_file.ub10 = data.get("ub10", False)
        save_file.uil7 = data.get("uil7", [])
        save_file.ubl2 = data.get("ubl2", [])
        save_file.cat_shrine = core.CatShrine.deserialize(data.get("cat_shrine", {}))
        save_file.ud6 = data.get("ud6", 0.0)
        save_file.ud7 = data.get("ud7", 0)
        save_file.legend_tickets = data.get("legend_tickets", 0)
        save_file.uiil1 = data.get("uiil1", [])
        save_file.ub11 = data.get("ub11", False)
        save_file.ub12 = data.get("ub12", False)
        save_file.password_refresh_token = data.get("password_refresh_token", "")
        save_file.ub13 = data.get("ub13", False)
        save_file.uby4 = data.get("uby4", 0)
        save_file.uby5 = data.get("uby5", 0)
        save_file.ud8 = data.get("ud8", 0.0)
        save_file.ud9 = data.get("ud9", 0.0)
        save_file.date_int = data.get("date_int", 0)
        save_file.event_capsules_2 = data.get("event_capsules_2", [])
        save_file.two_battle_lines = data.get("two_battle_lines", False)
        save_file.ud10 = data.get("ud10", 0.0)
        save_file.platinum_shards = data.get("platinum_shards", 0)
        save_file.ub15 = data.get("ub15", False)
        save_file.cat_scratcher = core.GamblingEvent.deserialize(
            data.get("cat_scratcher", {})
        )
        save_file.aku = core.AkuChapters.deserialize(data.get("aku", {}))
        save_file.ub16 = data.get("ub16", False)
        save_file.ub17 = data.get("ub17", False)
        save_file.ushdshd2 = data.get("ushdshd2", {})
        save_file.ushdd = data.get("ushdd", {})
        save_file.ushdd2 = data.get("ushdd2", {})
        save_file.ub18 = data.get("ub18", False)
        save_file.uby6 = data.get("uby6", 0)
        save_file.uidtii = data.get("uidtii", {})
        save_file.behemoth_culling = core.GauntletChapters.deserialize(
            data.get("behemoth_culling", {})
        )
        save_file.ub19 = data.get("ub19", False)
        save_file.ub20 = data.get("ub20", False)
        save_file.uidtff = data.get("uidtff", {})
        save_file.ub21 = data.get("ub21", False)
        save_file.dojo_3x_speed = data.get("dojo_3x_speed", False)
        save_file.ub22 = data.get("ub22", False)
        save_file.ub23 = data.get("ub23", False)
        save_file.ui17 = data.get("ui17", 0)
        save_file.ush4 = data.get("ush4", 0)
        save_file.uby7 = data.get("uby7", 0)
        save_file.uby8 = data.get("uby8", 0)
        save_file.ub24 = data.get("ub24", False)
        save_file.uby9 = data.get("uby9", 0)
        save_file.ushl1 = data.get("ushl1", [])
        save_file.ushl2 = data.get("ushl2", [])
        save_file.ushl3 = data.get("ushl3", [])
        save_file.ui18 = data.get("ui18", 0)
        save_file.ui19 = data.get("ui19", 0)
        save_file.ui20 = data.get("ui20", 0)
        save_file.ush5 = data.get("ush5", 0)
        save_file.ush6 = data.get("ush6", 0)
        save_file.ush7 = data.get("ush7", 0)
        save_file.ush8 = data.get("ush8", 0)
        save_file.uby10 = data.get("uby10", 0)
        save_file.ub25 = data.get("ub25", False)
        save_file.ub26 = data.get("ub26", False)
        save_file.ub27 = data.get("ub27", False)
        save_file.ub28 = data.get("ub28", False)
        save_file.ub29 = data.get("ub29", False)
        save_file.ub30 = data.get("ub30", False)
        save_file.uby11 = data.get("uby11", 0)
        save_file.ushl4 = data.get("ushl4", [])
        save_file.ubl3 = data.get("ubl3", [])
        save_file.labyrinth_medals = data.get("labyrinth_medals", [])
        save_file.zero_legends = core.ZeroLegendsChapters.deserialize(
            data.get("zero_legends", [])
        )
        save_file.uby12 = data.get("uby12", 0)
        save_file.ushl6 = data.get("ushl6", [])
        save_file.ub31 = data.get("ub31", False)
        save_file.ush9 = data.get("ush9", 0)
        save_file.ushshd = data.get("ushshd", {})
        save_file.ud11 = data.get("ud11", 0.0)
        save_file.ud12 = data.get("ud12", 0.0)
        save_file.ub32 = data.get("ub32", False)
        save_file.ub33 = data.get("ub33", False)
        save_file.ub34 = data.get("ub34", False)
        save_file.ui21 = data.get("ui21", 0)
        save_file.golden_cpu_count = data.get("golden_cpu_count", 0)
        save_file.sound_effects_volume = data.get("sound_effects_volume", 0)
        save_file.background_music_volume = data.get("background_music_volume", 0)
        save_file.ustl1 = data.get("ustl1", [])
        save_file.utl3 = data.get("utl3", [])
        save_file.ustid1 = data.get("ustid1", {})
        save_file.ud13 = data.get("ud13", 0.0)
        save_file.ud14 = data.get("ud14", 0.0)
        save_file.utl4 = data.get("utl4", [])
        save_file.uby14 = data.get("uby14", 0)
        save_file.ush12 = data.get("ush12", 0)
        save_file.ud15 = data.get("ud15", 0.0)
        save_file.uby15 = data.get("uby15", 0)
        save_file.uby16 = data.get("uby16", 0)
        save_file.ush11 = data.get("ush11", 0)
        save_file.uby17 = data.get("uby17", 0)
        save_file.uby18 = data.get("uby18", 0)
        save_file.uby19 = data.get("uby19", 0)
        save_file.ud16 = data.get("ud16", 0.0)
        save_file.ushd1 = data.get("ushd1", {})
        save_file.ui22 = data.get("ui22", 0)
        save_file.ud17 = data.get("ud17", 0.0)
        save_file.uby20 = data.get("uby20", 0)
        save_file.uild1 = data.get("uild1", {})
        save_file.dojo_chapters = core.ZeroLegendsChapters.deserialize(
            data.get("dojo_chapters", [])
        )
        save_file.uil9 = data.get("uil9", [])
        save_file.ub35 = data.get("ub35", False)
        save_file.ud18 = data.get("ud18", 0.0)
        save_file.ushd2 = data.get("ushd2", {})
        save_file.uil10 = data.get("uil10", [])
        save_file.uid1 = data.get("uid1", {})
        save_file.hundred_million_ticket = data.get("hundred_million_ticket", 0)
        save_file.uil11 = data.get("uil11", [])
        save_file.ub36 = data.get("ub36", False)
        save_file.treasure_chests = data.get("treasure_chests", [])
        save_file.ui23 = data.get("ui23", 0)
        save_file.uil13 = data.get("uil13", [])
        save_file.ub37 = data.get("ub37", False)

        save_file.remaining_data = base64.b64decode(data.get("remaining_data", ""))

        return save_file

    def init_save(self, gv: core.GameVersion | None = None):
        self.dsts = []
        self.dst_index = 0
        if gv is None:
            gv = core.GameVersion(120200)
        self.set_gv(gv)

        self.ubm1 = False
        self.ubm = False
        self.ub0 = False
        self.ub1 = False
        self.ub2 = False
        self.ub3 = False
        self.ub4 = False
        self.ub5 = False
        self.ub6 = False
        self.ub7 = False
        self.ub8 = False
        self.ub9 = False
        self.ub10 = False
        self.ub11 = False
        self.ub12 = False
        self.ub13 = False
        self.ub15 = False
        self.ub16 = False
        self.ub17 = False
        self.ub18 = False
        self.ub19 = False
        self.ub20 = False
        self.ub21 = False
        self.ub22 = False
        self.ub23 = False
        self.ub24 = False
        self.ub25 = False
        self.ub26 = False
        self.ub27 = False
        self.ub28 = False
        self.ub29 = False
        self.ub30 = False
        self.ub31 = False
        self.ub32 = False
        self.ub33 = False
        self.ub34 = False
        self.ub35 = False
        self.ub36 = False
        self.ub37 = False

        self.mute_bgm = False
        self.mute_se = False
        self.get_event_data = False
        self.energy_notification = False
        self.transfer_flag = False
        self.combo_unlocked_10k_ur = False
        self.show_ban_message = False
        self.shown_maxcollab_mg = False
        self.event_update_flags = False
        self.filibuster_stage_enabled = False
        self.dojo_3x_speed = False
        self.two_battle_lines = False

        self.uim1 = 0
        self.ui0 = 0
        self.ui1 = 0
        self.ui2 = 0
        self.ui3 = 0
        self.ui4 = 0
        self.ui5 = 0
        self.ui6 = 0
        self.ui7 = 0
        self.ui8 = 0
        self.ui9 = 0
        self.ui10 = 0
        self.ui11 = 0
        self.ui12 = 0
        self.ui13 = 0
        self.ui14 = 0
        self.ui15 = 0
        self.ui16 = 0
        self.ui17 = 0
        self.ui18 = 0
        self.ui19 = 0
        self.ui20 = 0
        self.ui21 = 0
        self.ui22 = 0
        self.ui23 = 0

        self.catfood = 0
        self.current_energy = 0
        self.year = 0
        self.month = 0
        self.day = 0
        self.stamp_value_save = 0
        self.upgrade_state = 0
        self.xp = 0
        self.tutorial_state = 0
        self.koreaSuperiorTreasureState = 0
        self.unlock_enemy_guide = 0
        self.cleared_eoc_1 = 0
        self.unlocked_ending = 0
        self.stage_unlock_cat_value = 0
        self.show_ending_value = 0
        self.chapter_clear_cat_unlock = 0
        self.ios_android_month = 0
        self.normal_tickets = 0
        self.rare_tickets = 0
        self.itf1_ending = 0
        self.continue_flag = 0
        self.os_value = 0
        self.full_gameversion = 0
        self.backup_state = 0
        self.itf1_complete = 0
        self.title_chapter_bg = 0
        self.rank_up_sale_value = 0
        self.platinum_tickets = 0
        self.backup_counter = 0
        self.backup_frame = 0
        self.cotc_1_complete = 0
        self.np = 0
        self.legend_tickets = 0
        self.date_int = 0
        self.platinum_shards = 0
        self.sound_effects_volume = 0
        self.background_music_volume = 0
        self.hundred_million_ticket = 0

        self.ud1 = 0.0
        self.ud2 = 0.0
        self.ud3 = 0.0
        self.ud4 = 0.0
        self.ud5 = 0.0
        self.ud6 = 0.0
        self.ud7 = 0.0
        self.ud8 = 0.0
        self.ud9 = 0.0
        self.ud10 = 0.0
        self.ud11 = 0.0
        self.ud12 = 0.0
        self.ud13 = 0.0
        self.ud14 = 0.0
        self.ud15 = 0.0
        self.ud16 = 0.0
        self.ud17 = 0.0
        self.ud18 = 0.0

        self.timestamp = 0.0
        self.g_timestamp = 0.0
        self.g_servertimestamp = 0.0
        self.m_gettimesave = 0.0
        self.g_timestamp_2 = 0.0
        self.g_servertimestamp_2 = 0.0
        self.m_gettimesave_2 = 0.0
        self.unknown_timestamp = 0.0
        self.m_dGetTimeSave2 = 0.0
        self.m_dGetTimeSave3 = 0.0
        self.next_week_timestamp = 0.0
        self.time_since_time_check_cumulative = 0.0
        self.server_timestamp = 0.0
        self.last_checked_energy_recovery_time = 0.0
        self.time_since_check = 0.0
        self.last_checked_expedition_time = 0.0
        self.reward_remaining_time = 0.0
        self.last_checked_reward_time = 0.0
        self.last_checked_zombie_time = 0.0
        self.energy_penalty_timestamp = 0.0
        self.last_checked_castle_time = 0.0

        self.date = datetime.datetime.fromtimestamp(0)
        self.date_2 = datetime.datetime.fromtimestamp(0)
        self.date_3 = datetime.datetime.fromtimestamp(0)
        self.date_4 = datetime.datetime.fromtimestamp(0)

        self.uil1 = [0] * 20
        self.uil2 = [0] * 7
        self.uil3 = [0] * 7
        self.uil4 = [0] * 7
        self.stage_ids_10s = []
        self.uil6 = []
        self.uil7 = []
        self.event_capsules_2 = []
        self.uil9 = []
        self.uil10 = []
        self.uil11 = []
        self.treasure_chests = []
        self.uil13 = []

        self.uiil1 = []

        self.usl1 = []
        self.usl2 = []

        self.ustl1 = []

        if 20 <= gv and gv <= 25:
            self.ubl1 = [False] * 12
        else:
            self.ubl1 = []

        self.ubl2 = [False] * 10
        self.ubl3 = [False] * 14

        self.ushl1 = []
        self.ushl2 = []
        self.ushl3 = []
        self.ushl4 = []
        self.ushl6 = []

        self.utl1 = []
        self.utl3 = []
        self.utl4 = []

        self.unlock_popups_11 = [0] * 3
        if 20 <= gv and gv <= 25:
            self.enemy_guide = [0] * 231
        else:
            self.enemy_guide = []

        if gv <= 25:
            self.menu_unlocks = [0] * 5
            self.unlock_popups_0 = [0] * 5
        elif gv <= 26:
            self.menu_unlocks = [0] * 6
            self.unlock_popups_0 = [0] * 6
        else:
            self.menu_unlocks = []
            self.unlock_popups_0 = []

        if gv <= 26:
            self.new_dialogs_2 = [0] * 17
        else:
            self.new_dialogs_2 = []

        self.moneko_bonus = [0] * 1
        self.daily_reward_initialized = [0] * 1
        self.chara_flags = [0] * 2
        self.chara_flags_2 = [0] * 2

        self.unlock_popups_8 = [0] * 36

        if 20 <= gv and gv <= 25:
            self.unit_drops = [0] * 10
        else:
            self.unit_drops = []

        self.achievements = [False] * 7
        self.order_ids = []
        self.combo_unlocks = []
        if gv < 34:
            self.event_capsules = [0] * 100
            self.event_capsules_counter = [0] * 100
        else:
            self.event_capsules = []
            self.event_capsules_counter = []

        if gv < 26:
            self.gatya_seen_lucky_drops = [0] * 44
        else:
            self.gatya_seen_lucky_drops = []
        self.catfood_beginner_purchased = [False] * 3
        self.catfood_beginner_expired = [False] * 3
        self.catfruit = []
        self.catseyes = []
        self.catamins = []
        self.unlock_popups_6 = []
        self.reset_item_reward_flags = []
        self.announcements = [(0, 0)] * 16
        self.lucky_tickets = []
        self.labyrinth_medals = []

        self.save_data_4_hash = ""
        self.player_id = ""
        self.transfer_code: str = ""
        self.confirmation_code: str = ""
        self.inquiry_code: str = ""
        self.password_refresh_token: str = ""

        self.uby1 = 0
        self.uby2 = 0
        self.uby3 = 0
        self.uby4 = 0
        self.uby5 = 0
        self.uby6 = 0
        self.uby7 = 0
        self.uby8 = 0
        self.uby9 = 0
        self.uby10 = 0
        self.uby11 = 0
        self.uby12 = 0
        self.golden_cpu_count = 0
        self.uby14 = 0
        self.uby15 = 0
        self.uby16 = 0
        self.uby17 = 0
        self.uby18 = 0
        self.uby19 = 0
        self.uby20 = 0
        self.uby21 = 0

        self.has_account = 0
        self.filibuster_stage_id = 0
        self.restart_pack = 0

        self.ush1 = 0
        self.ush2 = 0
        self.ush3 = 0
        self.ush4 = 0
        self.ush5 = 0
        self.ush6 = 0
        self.ush7 = 0
        self.ush8 = 0
        self.ush9 = 0
        self.ush10 = 0
        self.ush11 = 0
        self.ush12 = 0

        self.leadership = 0

        self.lineups = core.LineUps.init(self.game_version)
        self.stamp_data = core.StampData.init()
        self.story = core.StoryChapters.init()
        self.cats = core.Cats.init(self.game_version)
        self.special_skills = core.SpecialSkills.init()
        self.battle_items = core.BattleItems.init()
        self.mysale = core.MySale.init()
        self.event_stages = core.EventChapters.init(self.game_version)
        self.gatya = core.Gatya.init()
        self.user_rank_rewards = core.UserRankRewards.init(self.game_version)
        self.item_reward_stages = core.ItemRewardChapters.init(self.game_version)
        self.timed_score_stages = core.TimedScoreChapters.init(self.game_version)
        self.officer_pass = core.OfficerPass.init()
        self.gamatoto = core.Gamatoto.init()
        self.ex_stages = core.ExChapters.init()
        self.item_pack = core.ItemPack.init()
        self.logins = core.LoginBonus.init(self.game_version)
        self.dojo = core.Dojo.init()
        self.outbreaks = core.Outbreaks.init()
        self.scheme_items = core.SchemeItems.init()
        self.unlock_popups = core.UnlockPopups.init()
        self.ototo = core.Ototo.init(self.game_version)
        self.beacon_base = core.BeaconEventListScene.init()
        self.tower = core.TowerChapters.init()
        self.missions = core.Missions.init()
        self.challenge = core.ChallengeChapters.init()
        self.map_resets = core.MapResets.init()
        self.uncanny = core.UncannyChapters.init()
        self.catamin_stages = core.UncannyChapters.init()
        self.legend_quest = core.LegendQuestChapters.init()
        self.medals = core.Medals.init()
        self.gauntlets = core.GauntletChapters.init()
        self.enigma_clears = core.GauntletChapters.init()
        self.enigma = core.Enigma.init()
        self.cleared_slots = core.ClearedSlots.init()
        self.collab_gauntlets = core.GauntletChapters.init()
        self.talent_orbs = core.TalentOrbs.init()
        self.cat_shrine = core.CatShrine.init()
        self.aku = core.AkuChapters.init()
        self.behemoth_culling = core.GauntletChapters.init()
        self.zero_legends = core.ZeroLegendsChapters.init()
        self.dojo_chapters = core.ZeroLegendsChapters.init()
        self.wildcat_slots = core.GamblingEvent.init()
        self.cat_scratcher = core.GamblingEvent.init()

        self.uiid1 = {}
        self.uidd1 = {}
        self.uidiid2 = {}
        self.ushdshd2 = {}
        self.ushdd = {}
        self.ushdd2 = {}
        self.uidtii = {}
        self.uidtff = {}
        self.ushshd = {}
        self.ustid1 = {}
        self.uiid3 = {}
        self.uidd2 = {}
        self.uidd3 = {}
        self.ushd1 = {}
        self.uild1 = {}
        self.ushd2 = {}
        self.uid1 = {}

        self.first_locks = {}

        self.remaining_data = b""

    def is_jp(self) -> bool:
        return self.cc == core.CountryCodeType.JP

    def not_jp(self) -> bool:
        return self.cc != core.CountryCodeType.JP

    def is_en(self) -> bool:
        return self.cc == core.CountryCodeType.EN

    def should_read_dst(self) -> bool:
        if self.is_jp():
            return False
        return self.game_version >= 49

    def read_dst(self):
        if self.should_read_dst():
            self.dsts.append(self.data.read_bool())

    def write_dst(self):
        if self.should_read_dst():
            try:
                self.data.write_bool(self.dsts[self.dst_index])
            except IndexError:
                self.data.write_bool(False)
            self.dst_index += 1

    def calculate_user_rank(self):
        user_rank = 0
        for cat in self.cats.cats:
            if not cat.unlocked:
                continue
            user_rank += cat.upgrade.base + 1
            user_rank += cat.upgrade.plus

        for i, skill in enumerate(self.special_skills.skills):
            if i == 1:
                continue
            user_rank += skill.upgrade.base + 1
            user_rank += skill.upgrade.plus

        return user_rank

    @staticmethod
    def get_string_identifier(identifier: str) -> str:
        return f"_bcsfe:{identifier}"

    def store_string(self, identifier: str, string: str, overwrite: bool = True):
        if overwrite:
            for i, order in enumerate(self.order_ids):
                if order.startswith(SaveFile.get_string_identifier(identifier)):
                    self.order_ids[i] = (
                        f"{SaveFile.get_string_identifier(identifier)}:{string}"
                    )
                    return
        self.order_ids.append(f"{SaveFile.get_string_identifier(identifier)}:{string}")

    def get_string(self, identifier: str) -> str | None:
        for order in self.order_ids:
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                return order.split(":")[2]
        return None

    def get_strings(self, identifier: str) -> list[str]:
        strings: list[str] = []
        for order in self.order_ids:
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                strings.append(order.split(":")[2])

        return strings

    def remove_string(self, identifier: str):
        for i, order in enumerate(self.order_ids):
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                self.order_ids.pop(i)
                return

    def remove_strings(self, identifier: str):
        new_order_ids: list[str] = []
        for order in self.order_ids:
            if not order.startswith(SaveFile.get_string_identifier(identifier)):
                new_order_ids.append(order)
        self.order_ids = new_order_ids

    def store_dict(
        self,
        identifier: str,
        dictionary: dict[str, str],
        overwrite: bool = True,
    ):
        if overwrite:
            for i, order in enumerate(self.order_ids):
                if order.startswith(SaveFile.get_string_identifier(identifier)):
                    self.order_ids.pop(i)

        for key, value in dictionary.items():
            self.order_ids.append(
                f"{SaveFile.get_string_identifier(identifier)}:{key}:{value}"
            )

    def get_dict(self, identifier: str) -> dict[str, str] | None:
        dictionary: dict[str, str] = {}
        for order in self.order_ids:
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                dictionary[order.split(":")[2]] = order.split(":")[3]

        return dictionary

    def remove_dict(self, identifier: str):
        new_order_ids: list[str] = []
        for order in self.order_ids:
            if not order.startswith(SaveFile.get_string_identifier(identifier)):
                new_order_ids.append(order)
        self.order_ids = new_order_ids

    @staticmethod
    def get_saves_path() -> core.Path:
        return core.Path.get_documents_folder().add("saves").generate_dirs()

    def get_default_path(self) -> core.Path:
        core.Thread("check-backups", SaveFile.check_backups, []).start()
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        local_path = (
            self.get_saves_path()
            .add("backups")
            .add(f"{self.cc.get_code()}")
            .add(self.inquiry_code)
        )
        local_path.generate_dirs()
        local_path = local_path.add(date)

        return local_path

    @staticmethod
    def check_backups():
        max_backups = core.core_data.config.get_int(core.ConfigKey.MAX_BACKUPS)
        if max_backups == -1:
            return
        saves_path = SaveFile.get_saves_path().add("backups")
        saves_path.generate_dirs()
        all_saves: list[tuple[core.Path, datetime.datetime]] = []
        for cc in saves_path.get_dirs():
            for inquiry in cc.get_dirs():
                for save in inquiry.get_paths_dir():
                    name = save.basename()
                    try:
                        date = datetime.datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
                    except ValueError:
                        continue
                    all_saves.append((save, date))

        all_saves.sort(key=lambda x: x[1], reverse=True)
        for i, save_info in enumerate(all_saves):
            if i >= max_backups:
                save_info[0].remove()

        for cc in saves_path.get_dirs():
            dirs = cc.get_dirs()
            if len(dirs) == 0:
                cc.remove()
            for inquiry in dirs:
                saves = inquiry.get_paths_dir()
                if len(saves) == 0:
                    inquiry.remove()

    def unlock_equip_menu(self):
        self.menu_unlocks[2] = max(self.menu_unlocks[2], 1)

    def get_xp(self) -> int:
        return self.xp

    def set_xp(self, xp: int):
        self.xp = xp

    def get_catfood(self) -> int:
        return self.catfood

    def set_catfood(self, catfood: int):
        self.catfood = catfood

    def get_normal_tickets(self) -> int:
        return self.normal_tickets

    def set_normal_tickets(self, normal_tickets: int):
        self.normal_tickets = normal_tickets

    def get_rare_tickets(self) -> int:
        return self.rare_tickets

    def set_rare_tickets(self, rare_tickets: int):
        self.rare_tickets = rare_tickets

    def get_platinum_tickets(self) -> int:
        return self.platinum_tickets

    def set_platinum_tickets(self, platinum_tickets: int):
        self.platinum_tickets = platinum_tickets

    def get_legend_tickets(self) -> int:
        return self.legend_tickets

    def set_legend_tickets(self, legend_tickets: int):
        self.legend_tickets = legend_tickets

    def get_platinum_shards(self) -> int:
        return self.platinum_shards

    def set_platinum_shards(self, platinum_shards: int):
        self.platinum_shards = platinum_shards

    def get_np(self) -> int:
        return self.np

    def set_np(self, np: int):
        self.np = np

    def get_leadership(self) -> int:
        return self.leadership

    def set_leadership(self, leadership: int):
        self.leadership = leadership

    def max_rank_up_sale(self):
        self.rank_up_sale_value = 0x7FFFFFFF
