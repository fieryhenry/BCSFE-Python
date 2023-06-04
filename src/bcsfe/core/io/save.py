from typing import Any, Optional, Union
from bcsfe.core.io import data
from bcsfe.core import country_code, game_version, game, crypto
import datetime


class CantDetectCCError(Exception):
    pass


class SaveFile:
    def __init__(
        self,
        data: data.Data,
        cc: Optional[country_code.CountryCode] = None,
    ):
        self.data = data
        if cc is None:
            self.cc = self.detect_cc()
        else:
            self.cc = cc

        self.load()

    def detect_cc(self) -> country_code.CountryCode:
        for cc in country_code.CountryCode.get_all():
            self.cc = cc
            if self.verify_hash():
                return cc
        raise CantDetectCCError("Please specify a country code")

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
        data_to_hash = data.Data(salt.encode("utf-8") + data_to_hash)
        hash = crypto.Hash(crypto.HashAlgorithm.MD5).get_hash(data_to_hash)
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

    def load(self):
        """Load the save file. For most of this stuff I have no idea what it is used for"""

        self.data.reset_pos()
        self.dst_index = 0

        self.dsts: list[bool] = []

        self.game_version = game_version.GameVersion(self.data.read_int())

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

        self.eoc_chapter_clear_state = self.data.read_int()

        self.xp = self.data.read_int()
        self.tutorial_state = self.data.read_int()

        self.ui3 = self.data.read_int()
        self.tutorial_state_2 = self.data.read_int()

        self.unlock_popups_11 = self.data.read_int_list(3)
        self.ui5 = self.data.read_int()
        self.unlock_enemy_guide = self.data.read_int()
        self.ui6 = self.data.read_int()
        self.ub0 = self.data.read_bool()
        self.ui7 = self.data.read_int()
        self.cleared_eoc_1 = self.data.read_int()
        self.ui8 = self.data.read_int()
        self.unlocked_ending = self.data.read_int()

        self.lineups = game.battle.slots.LineUps.read(self.data, self.game_version)

        self.stamp_data = game.catbase.stamp.StampData.read(self.data)

        self.story = game.map.story.Chapters.read(self.data)

        if 20 <= self.game_version and self.game_version <= 25:
            self.enemy_guide = self.data.read_int_list(231)
        else:
            self.enemy_guide = self.data.read_int_list()

        self.cats = game.catbase.cat.Cats.read_unlocked(self.data, self.game_version)
        self.cats.read_upgrade(self.data, self.game_version)
        self.cats.read_current_form(self.data, self.game_version)

        self.special_skills = game.catbase.special_skill.Skills.read_upgrades(self.data)
        if self.game_version <= 25:
            self.menu_unlocks = self.data.read_int_list(5)
            self.unlock_popups_0 = self.data.read_int_list(5)
        elif self.game_version == 26:
            self.menu_unlocks = self.data.read_int_list(6)
            self.unlock_popups_0 = self.data.read_int_list(6)
        else:
            self.menu_unlocks = self.data.read_int_list()
            self.unlock_popups_0 = self.data.read_int_list()

        self.battle_items = game.battle.battle_items.BattleItems.read_items(self.data)

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
        else:
            self.ui0 = 0

        self.stage_unlock_cat_value = self.data.read_int()
        self.show_ending_value = self.data.read_int()
        self.chapter_clear_cat_unlock = self.data.read_int()
        self.ui9 = self.data.read_int()
        self.ios_android_month = self.data.read_int()
        self.ui10 = self.data.read_int()
        self.save_data_4_hash = self.data.read_string()

        self.mysale = game.catbase.my_sale.MySale.read_bonus_hash(self.data)
        self.chara_flags = self.data.read_int_list(length=2)

        if self.game_version <= 37:
            self.uim1 = self.data.read_int()
            self.ubm1 = self.data.read_bool()
        else:
            self.uim1 = 0
            self.ubm1 = False

        self.chara_flags_2 = self.data.read_int_list(length=2)

        self.normal_tickets = self.data.read_int()
        self.rare_tickets = self.data.read_int()

        self.cats.read_gatya_seen(self.data, self.game_version)
        self.special_skills.read_gatya_seen(self.data)
        self.cats.read_storage(self.data, self.game_version)

        self.event_stages = game.map.event.EventChapters.read(
            self.data, self.game_version
        )
        self.itf1_ending = self.data.read_int()
        self.continue_flag = self.data.read_int()
        if 20 <= self.game_version:
            self.unlock_popups_8 = self.data.read_int_list(length=36)
        else:
            self.unlock_popups_8 = []

        if 20 <= self.game_version and self.game_version <= 25:
            self.unit_drops = self.data.read_int_list(length=110)
        elif 26 <= self.game_version:
            self.unit_drops = self.data.read_int_list()
        else:
            self.unit_drops = []

        self.gatya = game.catbase.gatya.Gatya.read_rare_normal_seed(
            self.data, self.game_version
        )

        self.get_event_data = self.data.read_bool()
        self.achievements = self.data.read_bool_list(length=7)

        self.os_value = self.data.read_int()

        self.read_dst()
        self.date_4 = self.data.read_date()

        self.gatya.read2(self.data)

        if self.not_jp():
            self.player_id = self.data.read_string()
        else:
            self.player_id = ""

        self.order_ids = self.data.read_string_list()

        if self.not_jp():
            self.g_timestamp = self.data.read_double()
            self.g_servertimestamp = self.data.read_double()
            self.m_gettimesave = self.data.read_double()
            self.usl1 = self.data.read_string_list()
            self.energy_notification = self.data.read_bool()
            self.full_gameversion = self.data.read_int()
        else:
            self.usl1 = []
            self.g_timestamp = 0.0
            self.g_servertimestamp = 0.0
            self.m_gettimesave = 0.0
            self.full_gameversion = 0

        self.lineups.read_2(self.data, self.game_version)
        self.event_stages.read_legend_restrictions(self.data, self.game_version)

        if self.game_version <= 37:
            self.uil2 = self.data.read_int_list(length=7)
            self.uil3 = self.data.read_int_list(length=7)
            self.uil4 = self.data.read_int_list(length=7)
        else:
            self.uil2 = []
            self.uil3 = []
            self.uil4 = []

        self.g_timestamp_2 = self.data.read_double()
        self.g_servertimestamp_2 = self.data.read_double()
        self.m_gettimesave_2 = self.data.read_double()
        self.unknown_timestamp = self.data.read_double()
        self.gatya.read_trade_progress(self.data)

        if self.game_version <= 37:
            self.usl2 = self.data.read_string_list()
        else:
            self.usl2 = []

        if self.not_jp():
            self.m_dGetTimeSave2 = self.data.read_double()
            self.ui11 = 0
        else:
            self.ui11 = self.data.read_int()

        if 20 <= self.game_version and self.game_version <= 25:
            self.ubl1 = self.data.read_bool_list(length=12)
        elif 26 <= self.game_version and self.game_version < 39:
            self.ubl1 = self.data.read_bool_list()
        else:
            self.ubl1 = []

        self.cats.read_max_upgrade_levels(self.data, self.game_version)
        self.special_skills.read_max_upgrade_levels(self.data)

        self.user_rank_rewards = game.catbase.user_rank_rewards.Rewards.read(
            self.data, self.game_version
        )

        if not self.not_jp():
            self.m_dGetTimeSave2 = self.data.read_double()

        self.cats.read_unlocked_forms(self.data, self.game_version)

        self.transfer_code = self.data.read_string()
        self.confirmation_code = self.data.read_string()
        self.transfer_flag = self.data.read_bool()

        if 20 <= self.game_version:
            self.item_reward_stages = game.map.item_reward_stage.Chapters.read(
                self.data, self.game_version
            )

            self.timed_score_stages = game.map.timed_score.Chapters.read(
                self.data, self.game_version
            )

            self.inquiry_code = self.data.read_string()
            self.officer_pass = game.catbase.officer_pass.OfficerPass.read(self.data)
            self.has_account = self.data.read_byte()
            self.backup_state = self.data.read_int()

            if self.not_jp():
                self.ub2 = self.data.read_bool()
            else:
                self.ub2 = False

            self.gv_44 = self.data.read_int()

            self.itf1_complete = self.data.read_int()

            self.story.read_itf_timed_scores(self.data)

            self.title_chapter_bg = self.data.read_int()

            if self.game_version <= 26:
                self.combo_unlocks = []
            else:
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
            self.banned = self.data.read_bool()
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

            self.catfruit = game.catbase.catfruit.Matatabi.read(self.data)
            self.cats.read_forth_forms(self.data)
            self.cats.read_catseyes_used(self.data)
            self.catseyes = game.catbase.catseyes.Catseyes.read(self.data)
            self.catamins = game.gamoto.catamins.Catamins.read(self.data)
            self.gamatoto = game.gamoto.gamatoto.Gamatoto.read(self.data)

            self.unlock_popups_6 = self.data.read_bool_list()
            self.ex_stages = game.map.ex_stage.Chapters.read(self.data)

            self.gv_53 = self.data.read_int()
        if 29 <= self.game_version:
            self.gamatoto.read_2(self.data)
            self.gv_54 = self.data.read_int()
            self.item_pack = game.catbase.item_pack.ItemPack.read(self.data)
            self.gv_54 = self.data.read_int()
        if self.game_version >= 30:
            self.gamatoto.read_skin(self.data)
            self.platinum_tickets = self.data.read_int()
            self.logins = game.catbase.login_bonuses.LoginBonus.read(
                self.data, self.game_version
            )
            if self.game_version < 101000:
                self.reset_item_reward_flags = self.data.read_bool_list()
            else:
                self.reset_item_reward_flags = []

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
            self.dojo = game.map.dojo.Dojo.read_chapters(self.data)
            self.dojo.read_item_locks(self.data)
            self.gv_58 = self.data.read_int()

        if self.game_version >= 34:
            self.last_checked_zombie_time = self.data.read_double()
            self.outbreaks = game.map.outbreaks.Outbreaks.read_chapters(self.data)
            self.outbreaks.read_2(self.data)
            self.scheme_items = game.catbase.scheme_items.SchemeItems.read(self.data)

        if self.game_version >= 35:
            self.outbreaks.read_current_outbreaks(self.data, self.game_version)
            self.first_locks = self.data.read_int_bool_dict()
            self.account_created_timestamp = self.data.read_double()
            self.gv_60 = self.data.read_int()

        if self.game_version >= 36:
            self.cats.read_chara_new_flags(self.data)
            self.shown_maxcollab_mg = self.data.read_bool()
            self.item_pack.read_displayed_packs(self.data)
            self.gv_61 = self.data.read_int()

        if self.game_version >= 38:
            self.unlock_popups = game.catbase.unlock_popups.Popups.read(self.data)
            self.gv_63 = self.data.read_int()

        if self.game_version >= 39:
            self.ototo = game.gamoto.ototo.Ototo.read(self.data)
            self.ototo.read_2(self.data, self.game_version)
            self.last_checked_castle_time = self.data.read_double()
            self.gv_64 = self.data.read_int()

        if self.game_version >= 40:
            self.beacon_base = game.catbase.beacon_base.BeaconEventListScene.read(
                self.data
            )
            self.gv_65 = self.data.read_int()

        if self.game_version >= 41:
            self.tower = game.map.tower.Tower.read(self.data)
            self.missions = game.catbase.mission.Missions.read(
                self.data, self.game_version
            )
            self.tower.read_item_obtain_states(self.data)
            self.gv_66 = self.data.read_int()

        if self.game_version >= 42:
            self.dojo.read_ranking(self.data)
            self.item_pack.read_three_days(self.data)
            self.challenge = game.map.challenge.Challenge.read(self.data)
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
            self.map_resets = game.map.map_reset.MapResets.read(self.data)
            self.gv_72 = self.data.read_int()
        else:
            self.map_resets = game.map.map_reset.MapResets({})
            self.gv_72 = 72

        if self.game_version >= 51:
            self.uncanny = game.map.uncanny.Uncanny.read(self.data)
            self.gv_76 = self.data.read_int()

        if self.game_version >= 77:
            self.uncanny_2 = game.map.uncanny.Uncanny.read(self.data)

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
            self.legend_quest = game.map.legend_quest.Chapters.read(self.data)
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
            else:
                self.uby2 = 0
                self.gv_100600 = 100600

        if self.game_version >= 81000:
            self.restart_pack = self.data.read_byte()
            self.gv_81000 = self.data.read_int()

        if self.game_version >= 90000:
            self.medals = game.catbase.medals.Medals.read(self.data)
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

            self.gauntlets = game.map.gauntlets.Chapters.read(self.data)

            self.gv_90300 = self.data.read_int()

        if self.game_version >= 90400:
            self.gauntlets_2 = game.map.gauntlets.Chapters.read(self.data)
            self.enigma = game.map.enigma.Enigma.read(self.data)
            self.cleared_slots = game.battle.cleared_slots.ClearedSlots.read(self.data)

            self.gv_90400 = self.data.read_int()

        if self.game_version >= 90500:
            self.collab_gauntlets = game.map.gauntlets.Chapters.read(self.data)
            self.ub8 = self.data.read_bool()
            self.ud2 = self.data.read_double()
            self.ud3 = self.data.read_double()
            self.ui16 = self.data.read_int()
            if 100299 < self.game_version:
                self.uby3 = self.data.read_byte()
                self.ub9 = self.data.read_bool()
                self.ud4 = self.data.read_double()
                self.ud5 = self.data.read_double()
            else:
                self.uby3 = 0
                self.ub9 = False
                self.ud4 = 0.0
                self.ud5 = 0.0

            self.gv_90500 = self.data.read_int()

        if self.game_version >= 90700:
            self.talent_orbs = game.catbase.talent_orbs.TalentOrbs.read(
                self.data, self.game_version
            )
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
            self.cat_shrine = game.gamoto.cat_shrine.CatShrine.read(self.data)
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
            self.ub14 = self.data.read_bool()

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
            self.aku = game.map.aku.Chapters.read(self.data)
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
            self.behemoth_culling = game.map.gauntlets.Chapters.read(self.data)
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
            else:
                self.ub20 = False

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
            self.ushl5 = self.data.read_short_list(length)

            self.gv_111000 = self.data.read_int()

        if self.game_version >= 120000:
            self.zero_legends = game.map.zero_legends.Chapters.read(self.data)
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

    def save(self, data: data.Data):
        self.data = data
        self.dst_index = 0
        self.data.clear()

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

        self.data.write_int(self.eoc_chapter_clear_state)

        self.data.write_int(self.xp)
        self.data.write_int(self.tutorial_state)

        self.data.write_int(self.ui3)
        self.data.write_int(self.tutorial_state_2)

        self.data.write_int_list(self.unlock_popups_11, write_length=False)
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
            self.data.write_int_list(self.enemy_guide, write_length=False)
        else:
            self.data.write_int_list(self.enemy_guide)

        self.cats.write_unlocked(self.data, self.game_version)
        self.cats.write_upgrade(self.data, self.game_version)
        self.cats.write_current_form(self.data, self.game_version)

        self.special_skills.write_upgrades(self.data)

        if self.game_version <= 26:
            self.data.write_int_list(self.menu_unlocks, write_length=False)
            self.data.write_int_list(self.unlock_popups_0, write_length=False)
        else:
            self.data.write_int_list(self.menu_unlocks)
            self.data.write_int_list(self.unlock_popups_0)

        self.battle_items.write_items(self.data)

        if self.game_version <= 26:
            self.data.write_int_list(self.new_dialogs_2, write_length=False)
        else:
            self.data.write_int_list(self.new_dialogs_2)

        self.data.write_int_list(self.uil1, write_length=False)
        self.data.write_int_list(self.moneko_bonus, write_length=False)
        self.data.write_int_list(self.daily_reward_initialized, write_length=False)

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
        self.data.write_int_list(self.chara_flags, write_length=False)

        if self.game_version <= 37:
            self.data.write_int(self.uim1)
            self.data.write_bool(self.ubm1)

        self.data.write_int_list(self.chara_flags_2, write_length=False)

        self.data.write_int(self.normal_tickets)
        self.data.write_int(self.rare_tickets)

        self.cats.write_gatya_seen(self.data, self.game_version)
        self.special_skills.write_gatya_seen(self.data)
        self.cats.write_storage(self.data, self.game_version)

        self.event_stages.write(self.data, self.game_version)

        self.data.write_int(self.itf1_ending)
        self.data.write_int(self.continue_flag)

        if 20 <= self.game_version:
            self.data.write_int_list(self.unlock_popups_8, write_length=False)

        if 20 <= self.game_version and self.game_version <= 25:
            self.data.write_int_list(self.unit_drops, write_length=False)
        elif 26 <= self.game_version:
            self.data.write_int_list(self.unit_drops)

        self.gatya.write_rare_normal_seed(self.data)

        self.data.write_bool(self.get_event_data)
        self.data.write_bool_list(self.achievements, write_length=False)

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
            self.data.write_int_list(self.uil2, write_length=False)
            self.data.write_int_list(self.uil3, write_length=False)
            self.data.write_int_list(self.uil4, write_length=False)

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
            self.data.write_bool_list(self.ubl1, write_length=False)
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
                self.data.write_int_list(self.event_capsules_1, write_length=False)
                self.data.write_int_list(self.event_capsules_2, write_length=False)
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
                    self.gatya_seen_lucky_drops, write_length=False
                )
            else:
                self.data.write_int_list(self.gatya_seen_lucky_drops)
            self.data.write_bool(self.banned)
            self.data.write_bool_list(
                self.catfood_beginner_purchased, write_length=False
            )
            self.data.write_double(self.next_week_timestamp)
            self.data.write_bool_list(self.catfood_beginner_expired, write_length=False)
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

            self.catfruit.write(self.data)
            self.cats.write_forth_forms(self.data)
            self.cats.write_catseyes_used(self.data)
            self.catseyes.write(self.data)
            self.catamins.write(self.data)
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

            self.data.write_int_tuple_list(self.announcements, write_length=False)
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
            self.data.write_double(self.account_created_timestamp)
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
            for i1, i2, i3, i4, i5, i6, i7 in self.utl1:
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
            self.data.write_bool_list(self.ubl2, write_length=False)
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
            for b1, b2, i1, f1, f2 in self.utl2:
                self.data.write_bool(b1)
                self.data.write_bool(b2)
                self.data.write_byte(i1)
                self.data.write_double(f1)
                self.data.write_double(f2)

            self.data.write_int(self.gv_100300)

        if self.game_version >= 100400:
            self.data.write_byte(len(self.uil8))
            self.data.write_int_list(self.uil8, write_length=False)
            self.data.write_bool(self.ub14)
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

            self.data.write_bool_list(self.ubl3, write_length=False)

            self.data.write_byte(len(self.ushl5))
            self.data.write_short_list(self.ushl5, write_length=False)

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

    def to_data(self) -> "data.Data":
        dt = data.Data()
        self.save(dt)
        self.set_hash(add=True)
        return dt

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
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
            "date": self.date.strftime("%Y-%m-%d %H:%M:%S"),
            "ui1": self.ui1,
            "stamp_value_save": self.stamp_value_save,
            "ui2": self.ui2,
            "eoc_chapter_clear_state": self.eoc_chapter_clear_state,
            "xp": self.xp,
            "tutorial_state": self.tutorial_state,
            "ui3": self.ui3,
            "tutorial_state_2": self.tutorial_state_2,
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
            "date_2": self.date_2.strftime("%Y-%m-%d %H:%M:%S"),
            "date_3": self.date_3.strftime("%Y-%m-%d %H:%M:%S"),
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
            "date_4": self.date_4.strftime("%Y-%m-%d %H:%M:%S"),
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
            "banned": self.banned,
            "catfood_beginner_purchased": self.catfood_beginner_purchased,
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
            "catfruit": self.catfruit.serialize(),
            "catseyes": self.catseyes.serialize(),
            "catamins": self.catamins.serialize(),
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
            "first_locks": self.first_locks,
            "account_created_timestamp": self.account_created_timestamp,
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
            "gv_100600": self.gv_100600,
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
            "ub14": self.ub14,
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
            "ub20": self.ub20,
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
            "ushl5": self.ushl5,
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
        }
        return data

    def not_jp(self) -> bool:
        return self.cc != country_code.CountryCode.JP

    def is_en(self) -> bool:
        return self.cc == country_code.CountryCode.EN

    def should_read_dst(self) -> bool:
        return self.not_jp() and self.game_version >= 49

    def read_dst(self):
        if self.should_read_dst():
            self.dsts.append(self.data.read_bool())

    def write_dst(self):
        if self.should_read_dst():
            self.data.write_bool(self.dsts[self.dst_index])
            self.dst_index += 1

    def test_save(self):
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

        except AssertionError:
            raise
        except Exception:
            pass

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
        for i, order in enumerate(self.order_ids):
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                self.order_ids.pop(i)

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
        for i, order in enumerate(self.order_ids):
            if order.startswith(SaveFile.get_string_identifier(identifier)):
                self.order_ids.pop(i)
                return
