import base64
from typing import Any, Optional, Union
from bcsfe import core
import datetime


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
        dt: Optional["core.Data"] = None,
        cc: Optional["core.CountryCode"] = None,
        load: bool = True,
        gv: Optional["core.GameVersion"] = None,
    ):
        self.save_path: Optional[core.Path] = None
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
            self.real_cc = cc
        else:
            self.cc = detected_cc
            if cc is not None:
                self.real_cc = cc
            else:
                self.real_cc = detected_cc

        self.used_storage = False

        self.localizable: Optional[core.Localizable] = None

        self.init_save(gv)

        if dt is not None and load:
            self.load_wrapper()

    def get_localizable(self) -> "core.Localizable":
        if self.localizable is None:
            self.localizable = core.Localizable(self)
        return self.localizable

    def load_save_file(self, other: "SaveFile"):
        self.data = other.data
        self.cc = other.cc
        self.game_version = other.game_version
        self.init_save(other.game_version)
        self.load_wrapper()

    def detect_cc(self) -> Optional["core.CountryCode"]:
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
        data_to_hash = core.Data(salt.encode("utf-8") + data_to_hash)
        hash = core.Hash(core.HashAlgorithm.MD5).get_hash(data_to_hash)
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
            raise FailedToLoadError(
                core.core_data.local_manager.get_key("failed_to_load_save")
            ) from e
        if not self.verify_load():
            raise SaveFileInvalid(
                core.core_data.local_manager.get_key("failed_to_load_save_gv")
            )

    def set_gv(self, gv: "core.GameVersion"):
        self.game_version = gv

    def set_cc(self, cc: "core.CountryCode"):
        self.cc = cc
        self.real_cc = cc

    def load(self):
        """Load the save file. For most of this stuff I have no idea what it is used for"""

        self.data.reset_pos()
        self.dst_index = 0

        self.dsts: list[bool] = []

        self.game_version = core.GameVersion(self.data.read_int())

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

            self.gv_44 = self.data.read_int()

            self.itf1_complete = self.data.read_int()

            self.story.read_itf_timed_scores(self.data)

            self.title_chapter_bg = self.data.read_int()

            if self.game_version > 26:
                self.combo_unlocks = self.data.read_int_list()

            self.combo_unlocked_10k_ur = self.data.read_bool()

            self.gv_45 = self.data.read_int()

        if 21 <= self.game_version:
            self.gv_46 = self.data.read_int()
            self.gatya.read_event_seed(self.data, self.game_version)
            if self.game_version < 34:
                self.event_capsules_1 = self.data.read_int_list(length=100)
                self.event_capsules_2 = self.data.read_int_list(length=100)
            else:
                self.event_capsules_1 = self.data.read_int_list()
                self.event_capsules_2 = self.data.read_int_list()
            self.gv_47 = self.data.read_int()

        if 22 <= self.game_version:
            self.gv_48 = self.data.read_int()
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
            self.gv_49 = self.data.read_int()

        if 24 <= self.game_version:
            self.gv_50 = self.data.read_int()
        if 25 <= self.game_version:
            self.gv_51 = self.data.read_int()
        if 26 <= self.game_version:
            self.cats.read_catguide_collected(self.data)
            self.gv_52 = self.data.read_int()
        if 27 <= self.game_version:
            self.time_since_time_check_cumulative = self.data.read_double()
            self.server_timestamp = self.data.read_double()
            self.last_checked_energy_recovery_time = self.data.read_double()
            self.time_since_check = self.data.read_double()
            self.last_checked_expedition_time = self.data.read_double()

            self.catfruit = self.data.read_int_list()
            self.cats.read_forth_forms(self.data)
            self.cats.read_catseyes_used(self.data)
            self.catseyes = self.data.read_int_list()
            self.catamins = self.data.read_int_list()
            self.gamatoto = core.Gamatoto.read(self.data)

            self.unlock_popups_6 = self.data.read_bool_list()
            self.ex_stages = core.ExChapters.read(self.data)

            self.gv_53 = self.data.read_int()
        if 29 <= self.game_version:
            self.gamatoto.read_2(self.data)
            self.gv_54 = self.data.read_int()
            self.item_pack = core.ItemPack.read(self.data)
            self.gv_54 = self.data.read_int()
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
            self.gv_55 = self.data.read_int()

        if self.game_version >= 31:
            self.ub3 = self.data.read_bool()
            self.item_reward_stages.read_item_obtains(self.data)
            self.gatya.read_stepup(self.data)

            self.backup_frame = self.data.read_int()
            self.gv_56 = self.data.read_int()

        if self.game_version >= 32:
            self.ub4 = self.data.read_bool()
            self.cats.read_favorites(self.data)
            self.gv_57 = self.data.read_int()

        if self.game_version >= 33:
            self.dojo = core.Dojo.read_chapters(self.data)
            self.dojo.read_item_locks(self.data)
            self.gv_58 = self.data.read_int()

        if self.game_version >= 34:
            self.last_checked_zombie_time = self.data.read_double()
            self.outbreaks = core.Outbreaks.read_chapters(self.data)
            self.outbreaks.read_2(self.data)
            self.scheme_items = core.SchemeItems.read(self.data)

        if self.game_version >= 35:
            self.outbreaks.read_current_outbreaks(self.data, self.game_version)
            self.first_locks = self.data.read_int_bool_dict()
            self.energy_penalty_timestamp = self.data.read_double()
            self.gv_60 = self.data.read_int()

        if self.game_version >= 36:
            self.cats.read_chara_new_flags(self.data)
            self.shown_maxcollab_mg = self.data.read_bool()
            self.item_pack.read_displayed_packs(self.data)
            self.gv_61 = self.data.read_int()

        if self.game_version >= 38:
            self.unlock_popups = core.UnlockPopups.read(self.data)
            self.gv_63 = self.data.read_int()

        if self.game_version >= 39:
            self.ototo = core.Ototo.read(self.data)
            self.ototo.read_2(self.data, self.game_version)
            self.last_checked_castle_time = self.data.read_double()
            self.gv_64 = self.data.read_int()

        if self.game_version >= 40:
            self.beacon_base = core.BeaconEventListScene.read(self.data)
            self.gv_65 = self.data.read_int()

        if self.game_version >= 41:
            self.tower = core.TowerChapters.read(self.data)
            self.missions = core.Missions.read(self.data, self.game_version)
            self.tower.read_item_obtain_states(self.data)
            self.gv_66 = self.data.read_int()

        if self.game_version >= 42:
            self.dojo.read_ranking(self.data)
            self.item_pack.read_three_days(self.data)
            self.challenge = core.ChallengeChapters.read(self.data)
            self.challenge.read_scores(self.data)
            self.challenge.read_popup(self.data)
            self.gv_67 = self.data.read_int()

        if self.game_version >= 43:
            self.missions.read_weekly_missions(self.data)
            self.dojo.ranking.read_did_win_rewards(self.data)
            self.event_update_flags = self.data.read_bool()
            self.gv_68 = self.data.read_int()

        if self.game_version >= 44:
            self.event_stages.read_dicts(self.data)
            self.cotc_1_complete = self.data.read_int()
            self.gv_69 = self.data.read_int()

        if self.game_version >= 46:
            self.gamatoto.read_collab_data(self.data)
            self.gv_71 = self.data.read_int()

        if self.game_version < 90300:
            self.map_resets = core.MapResets.read(self.data)
            self.gv_72 = self.data.read_int()

        if self.game_version >= 51:
            self.uncanny = core.UncannyChapters.read(self.data)
            self.gv_76 = self.data.read_int()

        if self.game_version >= 77:
            self.uncanny_2 = core.UncannyChapters.read(self.data)

            self.event_capsules_3 = self.data.read_int_list()

            self.ub5 = self.data.read_bool()
            self.gv_77 = self.data.read_int()

        if self.game_version >= 80000:
            self.officer_pass.read_gold_pass(self.data, self.game_version)
            self.cats.read_talents(self.data)
            self.np = self.data.read_int()
            self.ub6 = self.data.read_bool()
            self.gv_80000 = self.data.read_int()

        if self.game_version >= 80200:
            self.ub7 = self.data.read_bool()
            self.leadership = self.data.read_short()
            self.officer_pass.read_cat_data(self.data)
            self.gv_80200 = self.data.read_int()

        if self.game_version >= 80300:
            self.filibuster_stage_id = self.data.read_byte()
            self.filibuster_stage_enabled = self.data.read_bool()
            self.gv_80300 = self.data.read_int()

        if self.game_version >= 80500:
            self.uil5 = self.data.read_int_list()
            self.gv_80500 = self.data.read_int()

        if self.game_version >= 80600:
            length = self.data.read_short()
            self.uil6 = self.data.read_int_list(length=length)
            self.legend_quest = core.LegendQuestChapters.read(self.data)
            self.ush1 = self.data.read_short()
            self.uby1 = self.data.read_byte()
            self.gv_80600 = self.data.read_int()

        if self.game_version >= 80700:
            length = self.data.read_int()
            self.uiid1: dict[int, list[int]] = {}
            for _ in range(length):
                key = self.data.read_int()
                value = self.data.read_int_list()
                self.uiid1[key] = value

            self.gv_80700 = self.data.read_int()

        if self.game_version >= 100600:
            if self.is_en():
                self.uby2 = self.data.read_byte()
                self.gv_100600 = self.data.read_int()

        if self.game_version >= 81000:
            self.restart_pack = self.data.read_byte()
            self.gv_81000 = self.data.read_int()

        if self.game_version >= 90000:
            self.medals = core.Medals.read(self.data)
            total = self.data.read_short()
            self.ushbd1 = self.data.read_short_bool_dict(total)
            length = self.data.read_short()
            self.uidiid1: dict[int, dict[int, int]] = {}
            for _ in range(length):
                key = self.data.read_short()
                length = self.data.read_short()
                for _ in range(length):
                    key2 = self.data.read_short()
                    value = self.data.read_short()
                    if key not in self.uidiid1:
                        self.uidiid1[key] = {}
                    self.uidiid1[key][key2] = value
                if length == 0:
                    self.uidiid1[key] = {}

            length = self.data.read_short()
            self.uiid2: dict[int, Union[int, float]] = {}
            for _ in range(length):
                key = self.data.read_short()
                if self.game_version < 90100:
                    value = self.data.read_double()
                else:
                    value = self.data.read_int()
                self.uiid2[key] = value

            self.gv_90000 = self.data.read_int()

        if self.game_version >= 90100:
            self.ush2 = self.data.read_short()
            self.ush3 = self.data.read_short()
            self.ui15 = self.data.read_int()
            self.ud1 = self.data.read_double()

            self.gv_90100 = self.data.read_int()

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

            self.gv_90300 = self.data.read_int()

        if self.game_version >= 90400:
            self.gauntlets_2 = core.GauntletChapters.read(self.data)
            self.enigma = core.Enigma.read(self.data)
            self.cleared_slots = core.ClearedSlots.read(self.data)

            self.gv_90400 = self.data.read_int()

        if self.game_version >= 90500:
            self.collab_gauntlets = core.GauntletChapters.read(self.data)
            self.ub8 = self.data.read_bool()
            self.ud2 = self.data.read_double()
            self.ud3 = self.data.read_double()
            self.ui16 = self.data.read_int()
            if 100299 < self.game_version:
                self.uby3 = self.data.read_byte()
                self.ub9 = self.data.read_bool()
                self.ud4 = self.data.read_double()
                self.ud5 = self.data.read_double()

            self.gv_90500 = self.data.read_int()

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

            self.gv_90700 = self.data.read_int()

        if self.game_version >= 90800:
            length = self.data.read_short()
            self.uil7 = self.data.read_int_list(length)
            self.ubl2 = self.data.read_bool_list(10)

            self.gv_90800 = self.data.read_int()

        if self.game_version >= 90900:
            self.cat_shrine = core.CatShrine.read(self.data)
            self.ud6 = self.data.read_double()
            self.ud7 = self.data.read_double()

            self.gv_90900 = self.data.read_int()

        if self.game_version >= 91000:
            self.lineups.read_slot_names(self.data, self.game_version)

            self.gv_91000 = self.data.read_int()

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

            self.gv_100000 = self.data.read_int()

        if self.game_version >= 100100:
            self.date_int = self.data.read_int()

            self.gv_100100 = self.data.read_int()

        if self.game_version >= 100300:
            self.utl2: list[tuple[bool, bool, int, float, float]] = []
            length = 6
            for _ in range(length):
                b1 = self.data.read_bool()
                b2 = self.data.read_bool()
                i1 = self.data.read_byte()
                f1 = self.data.read_double()
                f2 = self.data.read_double()
                self.utl2.append((b1, b2, i1, f1, f2))

            self.gv_100300 = self.data.read_int()

        if self.game_version >= 100400:
            length = self.data.read_byte()
            self.uil8 = self.data.read_int_list(length)
            self.two_battle_lines = self.data.read_bool()

            self.gv_100400 = self.data.read_int()

        if self.game_version >= 100600:
            self.ud10 = self.data.read_double()
            self.platinum_shards = self.data.read_int()
            self.ub15 = self.data.read_bool()

            self.gv_100600 = self.data.read_int()

        if self.game_version >= 100700:
            length = self.data.read_short()
            self.ushbd2 = self.data.read_short_bool_dict(length)

            length = self.data.read_short()
            self.ushdshd: dict[int, dict[int, int]] = {}
            for _ in range(length):
                key = self.data.read_short()
                length = self.data.read_short()
                for _ in range(length):
                    key2 = self.data.read_short()
                    value = self.data.read_short()
                    if key not in self.ushdshd:
                        self.ushdshd[key] = {}
                    self.ushdshd[key][key2] = value
                if length == 0:
                    self.ushdshd[key] = {}

            length = self.data.read_short()
            self.ushid: dict[int, Union[int, float]] = {}
            for _ in range(length):
                key = self.data.read_short()
                if self.game_version < 90100:
                    value = self.data.read_double()
                else:
                    value = self.data.read_int()
                self.ushid[key] = value

            self.gv_100700 = self.data.read_int()

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

            self.gv_100900 = self.data.read_int()

        if self.game_version >= 101000:
            self.uby6 = self.data.read_byte()

            self.gv_101000 = self.data.read_int()

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

            self.gv_110000 = self.data.read_int()

        if self.game_version >= 110500:
            self.behemoth_culling = core.GauntletChapters.read(self.data)
            self.ub19 = self.data.read_bool()

            self.gv_110500 = self.data.read_int()

        if self.game_version >= 110600:
            self.ub20 = self.data.read_bool()

            self.gv_110600 = self.data.read_int()

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

            self.gv_110700 = self.data.read_int()

        if self.game_version >= 110800:
            self.cat_shrine.read_dialogs(self.data)
            self.ub21 = self.data.read_bool()
            self.dojo_3x_speed = self.data.read_bool()
            self.ub22 = self.data.read_bool()
            self.ub23 = self.data.read_bool()

            self.gv_110800 = self.data.read_int()

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

            self.gv_111000 = self.data.read_int()

        if self.game_version >= 120000:
            self.zero_legends = core.ZeroLegendsChapters.read(self.data)
            self.uby12 = self.data.read_byte()

            self.gv_120000 = self.data.read_int()

        if self.game_version >= 120100:
            length = self.data.read_short()
            self.ushl6 = self.data.read_short_list(length)

            self.gv_120100 = self.data.read_int()

        if self.game_version >= 120200:
            self.ub31 = self.data.read_bool()
            self.ush9 = self.data.read_short()
            length = self.data.read_byte()
            self.ushshd: dict[int, int] = {}
            for _ in range(length):
                key = self.data.read_short()
                value = self.data.read_short()
                self.ushshd[key] = value

            self.gv_120200 = self.data.read_int()

        if self.game_version >= 120400:
            self.ud11 = self.data.read_double()
            self.ud12 = self.data.read_double()

            self.gv_120400 = self.data.read_int()

        if self.game_version >= 120500:
            self.ub32 = self.data.read_bool()
            self.ub33 = self.data.read_bool()
            self.ub34 = self.data.read_bool()

            self.ui21 = self.data.read_int()
            self.uby13 = self.data.read_byte()

            self.gv_120500 = self.data.read_int()

        if self.game_version >= 120600:
            self.sound_effects_volume = self.data.read_byte()
            self.background_music_volume = self.data.read_byte()

            self.gv_120600 = self.data.read_int()

        self.remaining_data = self.data.read_to_end(32)

    def save(self, data: "core.Data"):
        self.data = data
        self.dst_index = 0
        self.data.clear()
        self.data.enable_buffer()

        self.data.write_int(self.game_version.game_version)

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

        if not self.not_jp():
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

            self.data.write_int(self.gv_44)
            self.data.write_int(self.itf1_complete)
            self.story.write_itf_timed_scores(self.data)
            self.data.write_int(self.title_chapter_bg)

            if self.game_version > 26:
                self.data.write_int_list(self.combo_unlocks)

            self.data.write_bool(self.combo_unlocked_10k_ur)

            self.data.write_int(self.gv_45)

        if 21 <= self.game_version:
            self.data.write_int(self.gv_46)
            self.gatya.write_event_seed(self.data)
            if self.game_version < 34:
                self.data.write_int_list(
                    self.event_capsules_1, write_length=False, length=100
                )
                self.data.write_int_list(
                    self.event_capsules_2, write_length=False, length=100
                )
            else:
                self.data.write_int_list(self.event_capsules_1)
                self.data.write_int_list(self.event_capsules_2)

            self.data.write_int(self.gv_47)

        if 22 <= self.game_version:
            self.data.write_int(self.gv_48)

        if 23 <= self.game_version:
            if not self.not_jp():
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
            self.data.write_int(self.gv_49)

        if 24 <= self.game_version:
            self.data.write_int(self.gv_50)

        if 25 <= self.game_version:
            self.data.write_int(self.gv_51)

        if 26 <= self.game_version:
            self.cats.write_catguide_collected(self.data)
            self.data.write_int(self.gv_52)

        if 27 <= self.game_version:
            self.data.write_double(self.time_since_time_check_cumulative)
            self.data.write_double(self.server_timestamp)
            self.data.write_double(self.last_checked_energy_recovery_time)
            self.data.write_double(self.time_since_check)
            self.data.write_double(self.last_checked_expedition_time)

            self.data.write_int_list(self.catfruit)
            self.cats.write_forth_forms(self.data)
            self.cats.write_catseyes_used(self.data)
            self.data.write_int_list(self.catseyes)
            self.data.write_int_list(self.catamins)
            self.gamatoto.write(self.data)

            self.data.write_bool_list(self.unlock_popups_6)
            self.ex_stages.write(self.data)

            self.data.write_int(self.gv_53)

        if 29 <= self.game_version:
            self.gamatoto.write_2(self.data)
            self.data.write_int(self.gv_54)
            self.item_pack.write(self.data)
            self.data.write_int(self.gv_54)

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
            self.data.write_int(self.gv_55)

        if self.game_version >= 31:
            self.data.write_bool(self.ub3)
            self.item_reward_stages.write_item_obtains(self.data)
            self.gatya.write_stepup(self.data)

            self.data.write_int(self.backup_frame)
            self.data.write_int(self.gv_56)

        if self.game_version >= 32:
            self.data.write_bool(self.ub4)
            self.cats.write_favorites(self.data)
            self.data.write_int(self.gv_57)

        if self.game_version >= 33:
            self.dojo.write_chapters(self.data)
            self.dojo.write_item_locks(self.data)
            self.data.write_int(self.gv_58)

        if self.game_version >= 34:
            self.data.write_double(self.last_checked_zombie_time)
            self.outbreaks.write_chapters(self.data)
            self.outbreaks.write_2(self.data)
            self.scheme_items.write(self.data)

        if self.game_version >= 35:
            self.outbreaks.write_current_outbreaks(self.data, self.game_version)
            self.data.write_int_bool_dict(self.first_locks)
            self.data.write_double(self.energy_penalty_timestamp)
            self.data.write_int(self.gv_60)

        if self.game_version >= 36:
            self.cats.write_chara_new_flags(self.data)
            self.data.write_bool(self.shown_maxcollab_mg)
            self.item_pack.write_displayed_packs(self.data)
            self.data.write_int(self.gv_61)

        if self.game_version >= 38:
            self.unlock_popups.write(self.data)
            self.data.write_int(self.gv_63)

        if self.game_version >= 39:
            self.ototo.write(self.data)
            self.ototo.write_2(self.data, self.game_version)
            self.data.write_double(self.last_checked_castle_time)
            self.data.write_int(self.gv_64)

        if self.game_version >= 40:
            self.beacon_base.write(self.data)
            self.data.write_int(self.gv_65)

        if self.game_version >= 41:
            self.tower.write(self.data)
            self.missions.write(self.data, self.game_version)
            self.tower.write_item_obtain_states(self.data)
            self.data.write_int(self.gv_66)

        if self.game_version >= 42:
            self.dojo.write_ranking(self.data)
            self.item_pack.write_three_days(self.data)
            self.challenge.write(self.data)
            self.challenge.write_scores(self.data)
            self.challenge.write_popup(self.data)
            self.data.write_int(self.gv_67)

        if self.game_version >= 43:
            self.missions.write_weekly_missions(self.data)
            self.dojo.ranking.write_did_win_rewards(self.data)
            self.data.write_bool(self.event_update_flags)
            self.data.write_int(self.gv_68)

        if self.game_version >= 44:
            self.event_stages.write_dicts(self.data)
            self.data.write_int(self.cotc_1_complete)
            self.data.write_int(self.gv_69)

        if self.game_version >= 46:
            self.gamatoto.write_collab_data(self.data)
            self.data.write_int(self.gv_71)

        if self.game_version < 90300:
            self.map_resets.write(self.data)
            self.data.write_int(self.gv_72)

        if self.game_version >= 51:
            self.uncanny.write(self.data)
            self.data.write_int(self.gv_76)

        if self.game_version >= 77:
            self.uncanny_2.write(self.data)
            self.data.write_int_list(self.event_capsules_3)
            self.data.write_bool(self.ub5)
            self.data.write_int(self.gv_77)

        if self.game_version >= 80000:
            self.officer_pass.write_gold_pass(self.data, self.game_version)
            self.cats.write_talents(self.data)
            self.data.write_int(self.np)
            self.data.write_bool(self.ub6)
            self.data.write_int(self.gv_80000)

        if self.game_version >= 80200:
            self.data.write_bool(self.ub7)
            self.data.write_short(self.leadership)
            self.officer_pass.write_cat_data(self.data)
            self.data.write_int(self.gv_80200)

        if self.game_version >= 80300:
            self.data.write_byte(self.filibuster_stage_id)
            self.data.write_bool(self.filibuster_stage_enabled)
            self.data.write_int(self.gv_80300)

        if self.game_version >= 80500:
            self.data.write_int_list(self.uil5)
            self.data.write_int(self.gv_80500)

        if self.game_version >= 80600:
            self.data.write_short(len(self.uil6))
            self.data.write_int_list(self.uil6, write_length=False)
            self.legend_quest.write(self.data)
            self.data.write_short(self.ush1)
            self.data.write_byte(self.uby1)
            self.data.write_int(self.gv_80600)

        if self.game_version >= 80700:
            self.data.write_int(len(self.uiid1))
            for key, value in self.uiid1.items():
                self.data.write_int(key)
                self.data.write_int_list(value)
            self.data.write_int(self.gv_80700)

        if self.game_version >= 100600:
            if self.is_en():
                self.data.write_byte(self.uby2)
                self.data.write_int(self.gv_100600)

        if self.game_version >= 81000:
            self.data.write_byte(self.restart_pack)
            self.data.write_int(self.gv_81000)

        if self.game_version >= 90000:
            self.medals.write(self.data)
            self.data.write_short(len(self.ushbd1))
            self.data.write_short_bool_dict(self.ushbd1, write_length=False)
            self.data.write_short(len(self.uidiid1))
            for key, value in self.uidiid1.items():
                self.data.write_short(key)
                self.data.write_short(len(value))
                for key2, value2 in value.items():
                    self.data.write_short(key2)
                    self.data.write_short(value2)

            self.data.write_short(len(self.uiid2))
            for key, value in self.uiid2.items():
                self.data.write_short(key)
                if self.game_version < 90100:
                    self.data.write_double(value)
                else:
                    self.data.write_int(int(value))

            self.data.write_int(self.gv_90000)

        if self.game_version >= 90100:
            self.data.write_short(self.ush2)
            self.data.write_short(self.ush3)
            self.data.write_int(self.ui15)
            self.data.write_double(self.ud1)
            self.data.write_int(self.gv_90100)

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
            self.data.write_int(self.gv_90300)

        if self.game_version >= 90400:
            self.gauntlets_2.write(self.data)
            self.enigma.write(self.data)
            self.cleared_slots.write(self.data)
            self.data.write_int(self.gv_90400)

        if self.game_version >= 90500:
            self.collab_gauntlets.write(self.data)
            self.data.write_bool(self.ub8)
            self.data.write_double(self.ud2)
            self.data.write_double(self.ud3)
            self.data.write_int(self.ui16)
            if 100299 < self.game_version:
                self.data.write_byte(self.uby3)
                self.data.write_bool(self.ub9)
                self.data.write_double(self.ud4)
                self.data.write_double(self.ud5)

            self.data.write_int(self.gv_90500)

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
            self.data.write_int(self.gv_90700)

        if self.game_version >= 90800:
            self.data.write_short(len(self.uil7))
            self.data.write_int_list(self.uil7, write_length=False)
            self.data.write_bool_list(self.ubl2, write_length=False, length=10)
            self.data.write_int(self.gv_90800)

        if self.game_version >= 90900:
            self.cat_shrine.write(self.data)
            self.data.write_double(self.ud6)
            self.data.write_double(self.ud7)
            self.data.write_int(self.gv_90900)

        if self.game_version >= 91000:
            self.lineups.write_slot_names(self.data, self.game_version)
            self.data.write_int(self.gv_91000)

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

            self.data.write_int(self.gv_100000)

        if self.game_version >= 100100:
            self.data.write_int(self.date_int)
            self.data.write_int(self.gv_100100)

        if self.game_version >= 100300:
            for i in range(6):
                try:
                    item = self.utl2[i]
                except IndexError:
                    item = (False, False, 0, 0.0, 0.0)

                tuple_len = len(item)
                b1, b2, i1, f1, f2 = False, False, 0, 0.0, 0.0
                if tuple_len >= 1:
                    b1 = item[0]
                if tuple_len >= 2:
                    b2 = item[1]
                if tuple_len >= 3:
                    i1 = item[2]
                if tuple_len >= 4:
                    f1 = item[3]
                if tuple_len >= 5:
                    f2 = item[4]

                self.data.write_bool(b1)
                self.data.write_bool(b2)
                self.data.write_byte(i1)
                self.data.write_double(f1)
                self.data.write_double(f2)

            self.data.write_int(self.gv_100300)

        if self.game_version >= 100400:
            self.data.write_byte(len(self.uil8))
            self.data.write_int_list(self.uil8, write_length=False)
            self.data.write_bool(self.two_battle_lines)
            self.data.write_int(self.gv_100400)

        if self.game_version >= 100600:
            self.data.write_double(self.ud10)
            self.data.write_int(self.platinum_shards)
            self.data.write_bool(self.ub15)
            self.data.write_int(self.gv_100600)

        if self.game_version >= 100700:
            self.data.write_short(len(self.ushbd2))
            self.data.write_short_bool_dict(self.ushbd2, write_length=False)

            self.data.write_short(len(self.ushdshd))
            for key, value in self.ushdshd.items():
                self.data.write_short(key)
                self.data.write_short(len(value))
                for key2, value2 in value.items():
                    self.data.write_short(key2)
                    self.data.write_short(value2)

            self.data.write_short(len(self.ushid))
            for key, value in self.ushid.items():
                self.data.write_short(key)
                if self.game_version < 90100:
                    self.data.write_double(value)
                else:
                    self.data.write_int(int(value))

            self.data.write_int(self.gv_100700)

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
            self.data.write_int(self.gv_100900)

        if self.game_version >= 101000:
            self.data.write_byte(self.uby6)
            self.data.write_int(self.gv_101000)

        if self.game_version >= 110000:
            self.data.write_short(len(self.uidtii))
            for key, value in self.uidtii.items():
                self.data.write_int(key)
                self.data.write_byte(value[0])
                self.data.write_byte(value[1])

            self.data.write_int(self.gv_110000)

        if self.game_version >= 110500:
            self.behemoth_culling.write(self.data)
            self.data.write_bool(self.ub19)
            self.data.write_int(self.gv_110500)

        if self.game_version >= 110600:
            self.data.write_bool(self.ub20)
            self.data.write_int(self.gv_110600)

        if self.game_version >= 110700:
            self.data.write_int(len(self.uidtff))
            for key, value in self.uidtff.items():
                self.data.write_int(key)
                self.data.write_double(value[0])
                self.data.write_double(value[1])

            if self.not_jp():
                self.data.write_bool(self.ub20)
            self.data.write_int(self.gv_110700)

        if self.game_version >= 110800:
            self.cat_shrine.write_dialogs(self.data)
            self.data.write_bool(self.ub21)
            self.data.write_bool(self.dojo_3x_speed)
            self.data.write_bool(self.ub22)
            self.data.write_bool(self.ub23)

            self.data.write_int(self.gv_110800)

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

            self.data.write_int(self.gv_111000)

        if self.game_version >= 120000:
            self.zero_legends.write(self.data)
            self.data.write_byte(self.uby12)

            self.data.write_int(self.gv_120000)

        if self.game_version >= 120100:
            self.data.write_short(len(self.ushl6))
            self.data.write_short_list(self.ushl6, write_length=False)

            self.data.write_int(self.gv_120100)

        if self.game_version >= 120200:
            self.data.write_bool(self.ub31)
            self.data.write_short(self.ush9)
            self.data.write_byte(len(self.ushshd))
            for key, value in self.ushshd.items():
                self.data.write_short(key)
                self.data.write_short(value)

            self.data.write_int(self.gv_120200)

        if self.game_version >= 120400:
            self.data.write_double(self.ud11)
            self.data.write_double(self.ud12)

            self.data.write_int(self.gv_120400)

        if self.game_version >= 120500:
            self.data.write_bool(self.ub32)
            self.data.write_bool(self.ub33)
            self.data.write_bool(self.ub34)
            self.data.write_int(self.ui21)
            self.data.write_byte(self.uby13)

            self.data.write_int(self.gv_120500)

        if self.game_version >= 120600:
            self.data.write_byte(self.sound_effects_volume)
            self.data.write_byte(self.background_music_volume)

            self.data.write_int(self.gv_120600)

        self.data.write_bytes(self.remaining_data)

        self.data.end_buffer()

    def to_data(self) -> "core.Data":
        dt = core.Data()
        self.save_wrapper(dt)
        self.set_hash(add=True)
        return dt

    def save_wrapper(self, data: "core.Data") -> None:
        try:
            self.save(data)
        except Exception as e:
            raise FailedToSaveError(
                core.core_data.local_manager.get_key("failed_to_save_save")
            ) from e

    def to_file_thread(self, path: "core.Path"):
        core.Thread("to_file", self.to_file, [path]).start()

    def to_file(self, path: "core.Path") -> None:
        dt = self.to_data()
        dt.to_file(path)

    @staticmethod
    def get_temp_path() -> "core.Path":
        save_temp_path = core.Path.get_documents_folder().add("save.temp")
        save_temp_path.parent().generate_dirs()
        return save_temp_path

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
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
            "gv_44": self.gv_44,
            "itf1_complete": self.itf1_complete,
            "title_chapter_bg": self.title_chapter_bg,
            "combo_unlocks": self.combo_unlocks,
            "combo_unlocked_10k_ur": self.combo_unlocked_10k_ur,
            "gv_45": self.gv_45,
            "gv_46": self.gv_46,
            "event_capsules_1": self.event_capsules_1,
            "event_capsules_2": self.event_capsules_2,
            "gv_47": self.gv_47,
            "gv_48": self.gv_48,
            "m_dGetTimeSave3": self.m_dGetTimeSave3,
            "gatya_seen_lucky_drops": self.gatya_seen_lucky_drops,
            "banned": self.show_ban_message,
            "catfood_beginner_purchased": self.catfood_beginner_purchased,
            "next_week_timestamp": self.next_week_timestamp,
            "catfood_beginner_expired": self.catfood_beginner_expired,
            "rank_up_sale_value": self.rank_up_sale_value,
            "gv_49": self.gv_49,
            "gv_50": self.gv_50,
            "gv_51": self.gv_51,
            "gv_52": self.gv_52,
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
            "gv_53": self.gv_53,
            "gv_54": self.gv_54,
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
            "gv_55": self.gv_55,
            "ub3": self.ub3,
            "backup_frame": self.backup_frame,
            "gv_56": self.gv_56,
            "ub4": self.ub4,
            "gv_57": self.gv_57,
            "dojo": self.dojo.serialize(),
            "gv_58": self.gv_58,
            "last_checked_zombie_time": self.last_checked_zombie_time,
            "outbreaks": self.outbreaks.serialize(),
            "scheme_items": self.scheme_items.serialize(),
            "first_locks": self.first_locks,
            "energy_penalty_timestamp": self.energy_penalty_timestamp,
            "gv_60": self.gv_60,
            "shown_maxcollab_mg": self.shown_maxcollab_mg,
            "gv_61": self.gv_61,
            "unlock_popups": self.unlock_popups.serialize(),
            "gv_63": self.gv_63,
            "ototo": self.ototo.serialize(),
            "last_checked_castle_time": self.last_checked_castle_time,
            "gv_64": self.gv_64,
            "beacon_base": self.beacon_base.serialize(),
            "gv_65": self.gv_65,
            "tower": self.tower.serialize(),
            "missions": self.missions.serialize(),
            "gv_66": self.gv_66,
            "challenge": self.challenge.serialize(),
            "gv_67": self.gv_67,
            "event_update_flags": self.event_update_flags,
            "gv_68": self.gv_68,
            "cotc_1_complete": self.cotc_1_complete,
            "gv_69": self.gv_69,
            "gv_71": self.gv_71,
            "map_resets": self.map_resets.serialize(),
            "gv_72": self.gv_72,
            "uncanny": self.uncanny.serialize(),
            "gv_76": self.gv_76,
            "uncanny_2": self.uncanny_2.serialize(),
            "event_capsules_3": self.event_capsules_3,
            "ub5": self.ub5,
            "gv_77": self.gv_77,
            "np": self.np,
            "ub6": self.ub6,
            "gv_80000": self.gv_80000,
            "ub7": self.ub7,
            "leadership": self.leadership,
            "gv_80200": self.gv_80200,
            "filibuster_stage_id": self.filibuster_stage_id,
            "filibuster_stage_enabled": self.filibuster_stage_enabled,
            "gv_80300": self.gv_80300,
            "uil5": self.uil5,
            "gv_80500": self.gv_80500,
            "uil6": self.uil6,
            "legend_quest": self.legend_quest.serialize(),
            "ush1": self.ush1,
            "uby1": self.uby1,
            "gv_80600": self.gv_80600,
            "uiid1": self.uiid1,
            "gv_80700": self.gv_80700,
            "uby2": self.uby2,
            "restart_pack": self.restart_pack,
            "gv_81000": self.gv_81000,
            "medals": self.medals.serialize(),
            "ushbd1": self.ushbd1,
            "uidiid1": self.uidiid1,
            "uiid2": self.uiid2,
            "gv_90000": self.gv_90000,
            "ush2": self.ush2,
            "ush3": self.ush3,
            "ui15": self.ui15,
            "ud1": self.ud1,
            "gv_90100": self.gv_90100,
            "utl1": self.utl1,
            "uidd1": self.uidd1,
            "gauntlets": self.gauntlets.serialize(),
            "gv_90300": self.gv_90300,
            "gauntlets_2": self.gauntlets_2.serialize(),
            "enigma": self.enigma.serialize(),
            "cleared_slots": self.cleared_slots.serialize(),
            "gv_90400": self.gv_90400,
            "collab_gauntlets": self.collab_gauntlets.serialize(),
            "ub8": self.ub8,
            "ud2": self.ud2,
            "ud3": self.ud3,
            "ui16": self.ui16,
            "uby3": self.uby3,
            "ub9": self.ub9,
            "ud4": self.ud4,
            "ud5": self.ud5,
            "gv_90500": self.gv_90500,
            "talent_orbs": self.talent_orbs.serialize(),
            "uidiid2": self.uidiid2,
            "ub10": self.ub10,
            "gv_90700": self.gv_90700,
            "uil7": self.uil7,
            "ubl2": self.ubl2,
            "gv_90800": self.gv_90800,
            "cat_shrine": self.cat_shrine.serialize(),
            "ud6": self.ud6,
            "ud7": self.ud7,
            "gv_90900": self.gv_90900,
            "gv_91000": self.gv_91000,
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
            "gv_100000": self.gv_100000,
            "date_int": self.date_int,
            "gv_100100": self.gv_100100,
            "utl2": self.utl2,
            "gv_100300": self.gv_100300,
            "uil8": self.uil8,
            "two_battle_lines": self.two_battle_lines,
            "gv_100400": self.gv_100400,
            "ud10": self.ud10,
            "platinum_shards": self.platinum_shards,
            "ub15": self.ub15,
            "gv_100600": self.gv_100600,
            "ushbd2": self.ushbd2,
            "ushdshd": self.ushdshd,
            "ushid": self.ushid,
            "gv_100700": self.gv_100700,
            "aku": self.aku.serialize(),
            "ub16": self.ub16,
            "ub17": self.ub17,
            "ushdshd2": self.ushdshd2,
            "ushdd": self.ushdd,
            "ushdd2": self.ushdd2,
            "ub18": self.ub18,
            "gv_100900": self.gv_100900,
            "uby6": self.uby6,
            "gv_101000": self.gv_101000,
            "uidtii": self.uidtii,
            "gv_110000": self.gv_110000,
            "behemoth_culling": self.behemoth_culling.serialize(),
            "ub19": self.ub19,
            "gv_110500": self.gv_110500,
            "ub20": self.ub20,
            "gv_110600": self.gv_110600,
            "uidtff": self.uidtff,
            "gv_110700": self.gv_110700,
            "ub21": self.ub21,
            "dojo_3x_speed": self.dojo_3x_speed,
            "ub22": self.ub22,
            "ub23": self.ub23,
            "gv_110800": self.gv_110800,
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
            "gv_111000": self.gv_111000,
            "zero_legends": self.zero_legends.serialize(),
            "uby12": self.uby12,
            "gv_120000": self.gv_120000,
            "ushl6": self.ushl6,
            "gv_120100": self.gv_120100,
            "ub31": self.ub31,
            "ush9": self.ush9,
            "ushshd": self.ushshd,
            "gv_120200": self.gv_120200,
            "ud11": self.ud11,
            "ud12": self.ud12,
            "gv_120400": self.gv_120400,
            "ub32": self.ub32,
            "ub33": self.ub33,
            "ub34": self.ub34,
            "ui21": self.ui21,
            "uby13": self.uby13,
            "gv_120500": self.gv_120500,
            "sound_effects_volume": self.sound_effects_volume,
            "background_music_volume": self.background_music_volume,
            "gv_120600": self.gv_120600,
            "remaining_data": base64.b64encode(self.remaining_data).decode("utf-8"),
        }
        return data

    @staticmethod
    def from_dict(data: dict[str, Any]):
        cc = core.CountryCode(data.get("cc", None))
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
        save_file.gv_44 = data.get("gv_44", 44)
        save_file.itf1_complete = data.get("itf1_complete", 0)
        save_file.title_chapter_bg = data.get("title_chapter_bg", 0)
        save_file.combo_unlocks = data.get("combo_unlocks", [])
        save_file.combo_unlocked_10k_ur = data.get("combo_unlocked_10k_ur", False)
        save_file.gv_45 = data.get("gv_45", 45)
        save_file.gv_46 = data.get("gv_46", 46)
        save_file.event_capsules_1 = data.get("event_capsules_1", [])
        save_file.event_capsules_2 = data.get("event_capsules_2", [])
        save_file.gv_47 = data.get("gv_47", 47)
        save_file.gv_48 = data.get("gv_48", 48)
        save_file.m_dGetTimeSave3 = data.get("m_dGetTimeSave3", 0.0)
        save_file.gatya_seen_lucky_drops = data.get("gatya_seen_lucky_drops", [])
        save_file.show_ban_message = data.get("banned", False)
        save_file.catfood_beginner_purchased = data.get(
            "catfood_beginner_purchased", []
        )
        save_file.next_week_timestamp = data.get("next_week_timestamp", 0.0)
        save_file.catfood_beginner_expired = data.get("catfood_beginner_expired", [])
        save_file.rank_up_sale_value = data.get("rank_up_sale_value", 0)
        save_file.gv_49 = data.get("gv_49", 49)
        save_file.gv_50 = data.get("gv_50", 50)
        save_file.gv_51 = data.get("gv_51", 51)
        save_file.gv_52 = data.get("gv_52", 52)
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
        save_file.gv_53 = data.get("gv_53", 53)
        save_file.gv_54 = data.get("gv_54", 54)
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
        save_file.gv_55 = data.get("gv_55", 55)
        save_file.ub3 = data.get("ub3", False)
        save_file.backup_frame = data.get("backup_frame", 0)
        save_file.gv_56 = data.get("gv_56", 56)
        save_file.ub4 = data.get("ub4", False)
        save_file.gv_57 = data.get("gv_57", 57)
        save_file.dojo = core.Dojo.deserialize(data.get("dojo", {}))
        save_file.gv_58 = data.get("gv_58", 58)
        save_file.last_checked_zombie_time = data.get("last_checked_zombie_time", 0.0)
        save_file.outbreaks = core.Outbreaks.deserialize(data.get("outbreaks", {}))
        save_file.scheme_items = core.SchemeItems.deserialize(
            data.get("scheme_items", {})
        )
        save_file.first_locks = data.get("first_locks", {})
        save_file.energy_penalty_timestamp = data.get("energy_penalty_timestamp", 0.0)
        save_file.gv_60 = data.get("gv_60", 60)
        save_file.shown_maxcollab_mg = data.get("shown_maxcollab_mg", False)
        save_file.gv_61 = data.get("gv_61", 61)
        save_file.unlock_popups = core.UnlockPopups.deserialize(
            data.get("unlock_popups", {})
        )
        save_file.gv_63 = data.get("gv_63", 63)
        save_file.ototo = core.Ototo.deserialize(data.get("ototo", {}))
        save_file.last_checked_castle_time = data.get("last_checked_castle_time", 0.0)
        save_file.gv_64 = data.get("gv_64", 64)
        save_file.beacon_base = core.BeaconEventListScene.deserialize(
            data.get("beacon_base", {})
        )
        save_file.gv_65 = data.get("gv_65", 65)
        save_file.tower = core.TowerChapters.deserialize(data.get("tower", {}))
        save_file.missions = core.Missions.deserialize(data.get("missions", {}))
        save_file.gv_66 = data.get("gv_66", 66)
        save_file.challenge = core.ChallengeChapters.deserialize(
            data.get("challenge", {})
        )
        save_file.gv_67 = data.get("gv_67", 67)
        save_file.event_update_flags = data.get("event_update_flags", [])
        save_file.gv_68 = data.get("gv_68", 68)
        save_file.cotc_1_complete = data.get("cotc_1_complete", False)
        save_file.gv_69 = data.get("gv_69", 69)
        save_file.gv_71 = data.get("gv_71", 71)
        save_file.map_resets = core.MapResets.deserialize(data.get("map_resets", {}))
        save_file.gv_72 = data.get("gv_72", 72)
        save_file.uncanny = core.UncannyChapters.deserialize(data.get("uncanny", {}))
        save_file.gv_76 = data.get("gv_76", 76)
        save_file.uncanny_2 = core.UncannyChapters.deserialize(
            data.get("uncanny_2", {})
        )
        save_file.event_capsules_3 = data.get("event_capsules_3", [])
        save_file.ub5 = data.get("ub5", False)
        save_file.gv_77 = data.get("gv_77", 77)
        save_file.np = data.get("np", 0)
        save_file.ub6 = data.get("ub6", False)
        save_file.gv_80000 = data.get("gv_80000", 80000)
        save_file.ub7 = data.get("ub7", False)
        save_file.leadership = data.get("leadership", 0)
        save_file.gv_80200 = data.get("gv_80200", 80200)
        save_file.filibuster_stage_id = data.get("filibuster_stage_id", 0)
        save_file.filibuster_stage_enabled = data.get("filibuster_stage_enabled", False)
        save_file.gv_80300 = data.get("gv_80300", 80300)
        save_file.uil5 = data.get("uil5", [])
        save_file.gv_80500 = data.get("gv_80500", 80500)
        save_file.uil6 = data.get("uil6", [])
        save_file.legend_quest = core.LegendQuestChapters.deserialize(
            data.get("legend_quest", {})
        )
        save_file.ush1 = data.get("ush1", 0)
        save_file.uby1 = data.get("uby1", 0)
        save_file.gv_80600 = data.get("gv_80600", 80600)
        save_file.uiid1 = data.get("uiid1", {})
        save_file.gv_80700 = data.get("gv_80700", 80700)
        save_file.uby2 = data.get("uby2", 0)
        save_file.gv_100600 = data.get("gv_100600", 10600)
        save_file.restart_pack = data.get("restart_pack", 0)
        save_file.gv_81000 = data.get("gv_81000", 81000)
        save_file.medals = core.Medals.deserialize(data.get("medals", {}))
        save_file.ushbd1 = data.get("ushbd1", {})
        save_file.uidiid1 = data.get("uidiid1", {})
        save_file.uiid2 = data.get("uiid2", {})
        save_file.gv_90000 = data.get("gv_90000", 90000)
        save_file.ush2 = data.get("ush2", 0)
        save_file.ush3 = data.get("ush3", 0)
        save_file.ui15 = data.get("ui15", 0)
        save_file.ud1 = data.get("ud1", 0.0)
        save_file.gv_90100 = data.get("gv_90100", 90100)
        save_file.utl1 = data.get("utl1", [])
        save_file.uidd1 = data.get("uidd1", {})
        save_file.gauntlets = core.GauntletChapters.deserialize(
            data.get("gauntlets", {})
        )
        save_file.gv_90300 = data.get("gv_90300", 90300)
        save_file.gauntlets_2 = core.GauntletChapters.deserialize(
            data.get("gauntlets_2", {})
        )
        save_file.enigma = core.Enigma.deserialize(data.get("enigma", {}))
        save_file.cleared_slots = core.ClearedSlots.deserialize(
            data.get("cleared_slots", {})
        )
        save_file.gv_90400 = data.get("gv_90400", 90400)
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
        save_file.gv_90500 = data.get("gv_90500", 90500)
        save_file.talent_orbs = core.TalentOrbs.deserialize(data.get("talent_orbs", {}))
        save_file.uidiid2 = data.get("uidiid2", {})
        save_file.ub10 = data.get("ub10", False)
        save_file.gv_90700 = data.get("gv_90700", 90700)
        save_file.uil7 = data.get("uil7", [])
        save_file.ubl2 = data.get("ubl2", [])
        save_file.gv_90800 = data.get("gv_90800", 90800)
        save_file.cat_shrine = core.CatShrine.deserialize(data.get("cat_shrine", {}))
        save_file.ud6 = data.get("ud6", 0.0)
        save_file.ud7 = data.get("ud7", 0)
        save_file.gv_90900 = data.get("gv_90900", 90900)
        save_file.gv_91000 = data.get("gv_91000", 91000)
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
        save_file.gv_100000 = data.get("gv_100000", 100000)
        save_file.date_int = data.get("date_int", 0)
        save_file.gv_100100 = data.get("gv_100100", 100100)
        save_file.utl2 = data.get("utl2", [(False, False, 0, 0.0, 0.0)] * 6)
        save_file.gv_100300 = data.get("gv_100300", 100300)
        save_file.uil8 = data.get("uil8", [])
        save_file.two_battle_lines = data.get("two_battle_lines", False)
        save_file.gv_100400 = data.get("gv_100400", 100400)
        save_file.ud10 = data.get("ud10", 0.0)
        save_file.platinum_shards = data.get("platinum_shards", 0)
        save_file.ub15 = data.get("ub15", False)
        save_file.gv_100600 = data.get("gv_100600", 100600)
        save_file.ushbd2 = data.get("ushbd2", {})
        save_file.ushdshd = data.get("ushdshd", {})
        save_file.ushid = data.get("ushid", {})
        save_file.gv_100700 = data.get("gv_100700", 100700)
        save_file.aku = core.AkuChapters.deserialize(data.get("aku", {}))
        save_file.ub16 = data.get("ub16", False)
        save_file.ub17 = data.get("ub17", False)
        save_file.ushdshd2 = data.get("ushdshd2", {})
        save_file.ushdd = data.get("ushdd", {})
        save_file.ushdd2 = data.get("ushdd2", {})
        save_file.ub18 = data.get("ub18", False)
        save_file.gv_100900 = data.get("gv_100900", 100900)
        save_file.uby6 = data.get("uby6", 0)
        save_file.gv_101000 = data.get("gv_101000", 101000)
        save_file.uidtii = data.get("uidtii", {})
        save_file.gv_110000 = data.get("gv_110000", 110000)
        save_file.behemoth_culling = core.GauntletChapters.deserialize(
            data.get("behemoth_culling", {})
        )
        save_file.ub19 = data.get("ub19", False)
        save_file.gv_110500 = data.get("gv_110500", 110500)
        save_file.ub20 = data.get("ub20", False)
        save_file.gv_110600 = data.get("gv_110600", 110600)
        save_file.uidtff = data.get("uidtff", {})
        save_file.gv_110700 = data.get("gv_110700", 110700)
        save_file.ub21 = data.get("ub21", False)
        save_file.dojo_3x_speed = data.get("dojo_3x_speed", False)
        save_file.ub22 = data.get("ub22", False)
        save_file.ub23 = data.get("ub23", False)
        save_file.gv_110800 = data.get("gv_110800", 110800)
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
        save_file.gv_111000 = data.get("gv_111000", 111000)
        save_file.zero_legends = core.ZeroLegendsChapters.deserialize(
            data.get("zero_legends", [])
        )
        save_file.uby12 = data.get("uby12", 0)
        save_file.gv_120000 = data.get("gv_120000", 120000)
        save_file.ushl6 = data.get("ushl6", [])
        save_file.gv_120100 = data.get("gv_120100", 120100)
        save_file.ub31 = data.get("ub31", False)
        save_file.ush9 = data.get("ush9", 0)
        save_file.ushshd = data.get("ushshd", {})
        save_file.gv_120200 = data.get("gv_120200", 120200)
        save_file.ud11 = data.get("ud11", 0.0)
        save_file.ud12 = data.get("ud12", 0.0)
        save_file.gv_120400 = data.get("gv_120400", 120400)
        save_file.ub32 = data.get("ub32", False)
        save_file.ub33 = data.get("ub33", False)
        save_file.ub34 = data.get("ub34", False)
        save_file.ui21 = data.get("ui21", 0)
        save_file.uby13 = data.get("uby13", 0)
        save_file.gv_120500 = data.get("gv_120500", 120500)
        save_file.sound_effects_volume = data.get("sound_effects_volume", 0)
        save_file.background_music_volume = data.get("background_music_volume", 0)
        save_file.gv_120600 = data.get("gv_120600", 120600)

        save_file.remaining_data = base64.b64decode(data.get("remaining_data", ""))

        return save_file

    def init_save(self, gv: Optional["core.GameVersion"] = None):
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
        self.two_battle_lines = False
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

        self.gv_44 = 44
        self.gv_45 = 45
        self.gv_46 = 46
        self.gv_47 = 47
        self.gv_48 = 48
        self.gv_49 = 49
        self.gv_50 = 50
        self.gv_51 = 51
        self.gv_52 = 52
        self.gv_53 = 53
        self.gv_54 = 54
        self.gv_55 = 55
        self.gv_56 = 56
        self.gv_57 = 57
        self.gv_58 = 58
        self.gv_60 = 60
        self.gv_61 = 61
        self.gv_63 = 63
        self.gv_64 = 64
        self.gv_65 = 65
        self.gv_66 = 66
        self.gv_67 = 67
        self.gv_68 = 68
        self.gv_69 = 69
        self.gv_71 = 71
        self.gv_72 = 72
        self.gv_76 = 76
        self.gv_77 = 77
        self.gv_80000 = 80000
        self.gv_80200 = 80200
        self.gv_80300 = 80300
        self.gv_80500 = 80500
        self.gv_80600 = 80600
        self.gv_80700 = 80700
        self.gv_81000 = 81000
        self.gv_90000 = 90000
        self.gv_90100 = 90100
        self.gv_90200 = 90200
        self.gv_90300 = 90300
        self.gv_90400 = 90400
        self.gv_90500 = 90500
        self.gv_90700 = 90700
        self.gv_90800 = 90800
        self.gv_90900 = 90900
        self.gv_91000 = 91000
        self.gv_100000 = 100000
        self.gv_100100 = 100100
        self.gv_100300 = 100300
        self.gv_100400 = 100400
        self.gv_100600 = 100600
        self.gv_100700 = 100700
        self.gv_100900 = 100900
        self.gv_101000 = 101000
        self.gv_110000 = 110000
        self.gv_110500 = 110500
        self.gv_110600 = 110600
        self.gv_110700 = 110700
        self.gv_110800 = 110800
        self.gv_111000 = 111000
        self.gv_120000 = 120000
        self.gv_120100 = 120100
        self.gv_120200 = 120200
        self.gv_120400 = 120400
        self.gv_120500 = 120500
        self.gv_120600 = 120600

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
        self.uil5 = []
        self.uil6 = []
        self.uil7 = []
        self.uil8 = []

        self.uiil1 = []

        self.usl1 = []
        self.usl2 = []

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
        self.utl2 = [(False, False, 0, 0.0, 0.0)] * 6

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
            self.event_capsules_1 = [0] * 100
            self.event_capsules_2 = [0] * 100
        else:
            self.event_capsules_1 = []
            self.event_capsules_2 = []

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
        self.announcements: list[tuple[int, int]] = [(0, 0)] * 16
        self.event_capsules_3 = []
        self.labyrinth_medals = []

        self.save_data_4_hash = ""
        self.player_id = ""
        self.transfer_code = ""
        self.confirmation_code = ""
        self.inquiry_code = ""
        self.password_refresh_token = ""

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
        self.uby13 = 0

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
        self.uncanny_2 = core.UncannyChapters.init()
        self.legend_quest = core.LegendQuestChapters.init()
        self.medals = core.Medals.init()
        self.gauntlets = core.GauntletChapters.init()
        self.gauntlets_2 = core.GauntletChapters.init()
        self.enigma = core.Enigma.init()
        self.cleared_slots = core.ClearedSlots.init()
        self.collab_gauntlets = core.GauntletChapters.init()
        self.talent_orbs = core.TalentOrbs.init()
        self.cat_shrine = core.CatShrine.init()
        self.aku = core.AkuChapters.init()
        self.behemoth_culling = core.GauntletChapters.init()
        self.zero_legends = core.ZeroLegendsChapters.init()

        self.uiid1 = {}
        self.ushbd1 = {}
        self.uidiid1 = {}
        self.uiid2 = {}
        self.uidd1 = {}
        self.uidiid2 = {}
        self.ushbd2 = {}
        self.ushdshd = {}
        self.ushid = {}
        self.ushdshd2 = {}
        self.ushdd = {}
        self.ushdd2 = {}
        self.uidtii = {}
        self.uidtff = {}
        self.ushshd = {}

        self.first_locks = {}

        self.remaining_data = b""

    def not_jp(self) -> bool:
        return self.cc != core.CountryCodeType.JP

    def is_en(self) -> bool:
        return self.cc == core.CountryCodeType.EN

    def should_read_dst(self) -> bool:
        return self.not_jp() and self.game_version >= 49

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

    def verify_load(self):
        try:
            assert self.gv_44 == 44
            assert self.gv_45 == 45
            assert self.gv_46 == 46
            assert self.gv_47 == 47
            assert self.gv_48 == 48
            assert self.gv_49 == 49
            assert self.gv_50 == 50
            assert self.gv_51 == 51
            assert self.gv_52 == 52
            assert self.gv_53 == 53
            assert self.gv_54 == 54
            assert self.gv_55 == 55
            assert self.gv_56 == 56
            assert self.gv_57 == 57
            assert self.gv_58 == 58
            assert self.gv_60 == 60
            assert self.gv_61 == 61
            assert self.gv_63 == 63
            assert self.gv_64 == 64
            assert self.gv_65 == 65
            assert self.gv_66 == 66
            assert self.gv_67 == 67
            assert self.gv_68 == 68
            assert self.gv_69 == 69
            assert self.gv_71 == 71
            assert self.gv_72 == 72
            assert self.gv_76 == 76
            assert self.gv_77 == 77
            assert self.gv_80000 == 80000
            assert self.gv_80200 == 80200
            assert self.gv_80300 == 80300
            assert self.gv_80500 == 80500
            assert self.gv_80600 == 80600
            assert self.gv_80700 == 80700
            assert self.gv_81000 == 81000
            assert self.gv_90000 == 90000
            assert self.gv_90100 == 90100
            assert self.gv_90300 == 90300
            assert self.gv_90400 == 90400
            assert self.gv_90500 == 90500
            assert self.gv_90700 == 90700
            assert self.gv_90800 == 90800
            assert self.gv_90900 == 90900
            assert self.gv_91000 == 91000
            assert self.gv_100000 == 100000
            assert self.gv_100100 == 100100
            assert self.gv_100300 == 100300
            assert self.gv_100400 == 100400
            assert self.gv_100600 == 100600
            assert self.gv_100700 == 100700
            assert self.gv_100900 == 100900
            assert self.gv_101000 == 101000
            assert self.gv_110000 == 110000
            assert self.gv_110500 == 110500
            assert self.gv_110600 == 110600
            assert self.gv_110700 == 110700
            assert self.gv_110800 == 110800
            assert self.gv_111000 == 111000
            assert self.gv_120000 == 120000
            assert self.gv_120100 == 120100
            assert self.gv_120200 == 120200
            assert self.gv_120400 == 120400
            assert self.gv_120500 == 120500
            assert self.gv_120600 == 120600
        except AssertionError:
            return False
        return True

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
                    self.order_ids[
                        i
                    ] = f"{SaveFile.get_string_identifier(identifier)}:{string}"
                    return
        self.order_ids.append(f"{SaveFile.get_string_identifier(identifier)}:{string}")

    def get_string(self, identifier: str) -> Optional[str]:
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
        self, identifier: str, dictionary: dict[str, str], overwrite: bool = True
    ):
        if overwrite:
            for i, order in enumerate(self.order_ids):
                if order.startswith(SaveFile.get_string_identifier(identifier)):
                    self.order_ids.pop(i)

        for key, value in dictionary.items():
            self.order_ids.append(
                f"{SaveFile.get_string_identifier(identifier)}:{key}:{value}"
            )

    def get_dict(self, identifier: str) -> Optional[dict[str, str]]:
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
    def get_saves_path() -> "core.Path":
        return core.Path.get_documents_folder().add("saves")

    def get_default_path(self) -> "core.Path":
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
                for save in inquiry.get_files():
                    name = save.basename()
                    try:
                        date = datetime.datetime.strptime(name, "%Y-%m-%d_%H-%M-%S")
                    except ValueError:
                        continue
                    all_saves.append((save, date))

        all_saves.sort(key=lambda x: x[1], reverse=True)
        for i, save in enumerate(all_saves):
            if i >= max_backups:
                save[0].remove()

        for cc in saves_path.get_dirs():
            dirs = cc.get_dirs()
            if len(dirs) == 0:
                cc.remove()
            for inquiry in dirs:
                saves = inquiry.get_files()
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