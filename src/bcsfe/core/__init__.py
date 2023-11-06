from typing import Any, Optional

from requests.exceptions import ConnectionError
from requests import Response
from json.decoder import JSONDecodeError
from bcsfe.cli import color

from bcsfe.core import (
    country_code,
    crypto,
    game,
    game_version,
    io,
    locale_handler,
    log,
    server,
    theme_handler,
    max_value_helper,
)
from bcsfe.core.country_code import CountryCode, CountryCodeType
from bcsfe.core.crypto import Hash, HashAlgorithm, Hmac, NyankoSignature, Random
from bcsfe.core.game.battle.battle_items import BattleItems
from bcsfe.core.game.battle.cleared_slots import ClearedSlots
from bcsfe.core.game.battle.slots import LineUps
from bcsfe.core.game.battle.enemy import Enemy, EnemyNames
from bcsfe.core.game.catbase.beacon_base import BeaconEventListScene
from bcsfe.core.game.catbase.cat import Cat, Cats, UnitBuy, TalentData
from bcsfe.core.game.catbase.gatya import Gatya
from bcsfe.core.game.catbase.gatya_item import GatyaItemBuy, GatyaItemNames
from bcsfe.core.game.catbase.item_pack import (
    ItemPack,
    Purchases,
    PurchaseSet,
    PurchasedPack,
)
from bcsfe.core.game.catbase.login_bonuses import LoginBonus
from bcsfe.core.game.catbase.matatabi import Matatabi
from bcsfe.core.game.catbase.drop_chara import CharaDrop
from bcsfe.core.game.catbase.medals import Medals, MedalNames
from bcsfe.core.game.catbase.mission import Missions, MissionNames, MissionConditions
from bcsfe.core.game.catbase.my_sale import MySale
from bcsfe.core.game.catbase.nyanko_club import NyankoClub
from bcsfe.core.game.catbase.officer_pass import OfficerPass
from bcsfe.core.game.catbase.powerup import PowerUpHelper
from bcsfe.core.game.catbase.scheme_items import SchemeItems
from bcsfe.core.game.catbase.special_skill import (
    SpecialSkills,
    AbilityData,
    AbilityDataItem,
)
from bcsfe.core.game.catbase.stamp import StampData
from bcsfe.core.game.catbase.talent_orbs import TalentOrb, TalentOrbs
from bcsfe.core.game.catbase.unlock_popups import UnlockPopups
from bcsfe.core.game.catbase.upgrade import Upgrade
from bcsfe.core.game.catbase.user_rank_rewards import (
    UserRankRewards,
    RankGifts,
    RankGiftDescriptions,
)
from bcsfe.core.game.catbase.playtime import PlayTime
from bcsfe.core.game.gamoto.base_materials import BaseMaterials
from bcsfe.core.game.gamoto.cat_shrine import CatShrine, CatShrineLevels
from bcsfe.core.game.gamoto.gamatoto import (
    Gamatoto,
    GamatotoLevels,
    GamatotoMembersName,
)
from bcsfe.core.game.gamoto.ototo import Ototo
from bcsfe.core.game.localizable import Localizable
from bcsfe.core.game.map.aku import AkuChapters
from bcsfe.core.game.map.challenge import ChallengeChapters
from bcsfe.core.game.map.chapters import Chapters
from bcsfe.core.game.map.dojo import Dojo
from bcsfe.core.game.map.enigma import Enigma
from bcsfe.core.game.map.event import EventChapters
from bcsfe.core.game.map.ex_stage import ExChapters
from bcsfe.core.game.map.gauntlets import GauntletChapters
from bcsfe.core.game.map.item_reward_stage import ItemRewardChapters
from bcsfe.core.game.map.legend_quest import LegendQuestChapters
from bcsfe.core.game.map.map_reset import MapResets
from bcsfe.core.game.map.outbreaks import Outbreaks
from bcsfe.core.game.map.story import StoryChapters, TreasureText, StageNames
from bcsfe.core.game.map.timed_score import TimedScoreChapters
from bcsfe.core.game.map.tower import TowerChapters
from bcsfe.core.game.map.uncanny import UncannyChapters
from bcsfe.core.game.map.zero_legends import ZeroLegendsChapters
from bcsfe.core.game.map.map_names import MapNames
from bcsfe.core.game_version import GameVersion
from bcsfe.core.io.adb_handler import AdbHandler
from bcsfe.core.io.bc_csv import CSV, Delimeter, Row
from bcsfe.core.io.command import Command, CommandResult
from bcsfe.core.io.config import Config, ConfigKey
from bcsfe.core.io.data import Data
from bcsfe.core.io.json_file import JsonFile
from bcsfe.core.io.path import Path
from bcsfe.core.io.save import SaveError, SaveFile, CantDetectSaveCCError
from bcsfe.core.io.thread_helper import thread_run_many, Thread
from bcsfe.core.io.yaml import YamlFile
from bcsfe.core.io.git_handler import GitHandler, Repo
from bcsfe.core.locale_handler import (
    LocalManager,
    ExternalLocaleManager,
    ExternalLocale,
)
from bcsfe.core.log import Logger
from bcsfe.core.server.client_info import ClientInfo
from bcsfe.core.server.game_data_getter import GameDataGetter
from bcsfe.core.server.headers import AccountHeaders
from bcsfe.core.server.managed_item import BackupMetaData, ManagedItem, ManagedItemType
from bcsfe.core.server.request import RequestHandler
from bcsfe.core.server.server_handler import ServerHandler
from bcsfe.core.server.updater import Updater
from bcsfe.core.theme_handler import ThemeHandler, ExternalTheme, ExternalThemeManager
from bcsfe.core.max_value_helper import MaxValueHelper


class CoreData:
    def init_data(self):
        self.config = Config()
        self.logger = Logger()
        self.local_manager = LocalManager()
        self.theme_manager = ThemeHandler()
        self.max_value_manager = MaxValueHelper()
        self.game_data_getter: Optional[GameDataGetter] = None
        self.gatya_item_names: Optional[GatyaItemNames] = None
        self.gatya_item_buy: Optional[GatyaItemBuy] = None
        self.chara_drop: Optional[CharaDrop] = None
        self.gamatoto_levels: Optional[GamatotoLevels] = None
        self.gamatoto_members_name: Optional[GamatotoMembersName] = None
        self.localizable: Optional[Localizable] = None
        self.abilty_data: Optional[AbilityData] = None
        self.enemy_names: Optional[EnemyNames] = None
        self.rank_gift_descriptions: Optional[RankGiftDescriptions] = None
        self.rank_gifts: Optional[RankGifts] = None
        self.treasure_text: Optional[TreasureText] = None
        self.cat_shrine_levels: Optional[CatShrineLevels] = None
        self.medal_names: Optional[MedalNames] = None
        self.mission_names: Optional[MissionNames] = None
        self.mission_conditions: Optional[MissionConditions] = None

    def get_game_data_getter(
        self, save: Optional[SaveFile] = None, cc: Optional[CountryCode] = None
    ) -> GameDataGetter:
        if self.game_data_getter is None:
            if cc is None and save is not None:
                cc = save.cc
            if cc is None:
                raise ValueError("cc must be provided if save is not provided")
            self.game_data_getter = GameDataGetter(cc)
        return self.game_data_getter

    def get_gatya_item_names(self, save: SaveFile) -> GatyaItemNames:
        if self.gatya_item_names is None:
            self.gatya_item_names = GatyaItemNames(save)
        return self.gatya_item_names

    def get_gatya_item_buy(self, save: SaveFile) -> GatyaItemBuy:
        if self.gatya_item_buy is None:
            self.gatya_item_buy = GatyaItemBuy(save)
        return self.gatya_item_buy

    def get_chara_drop(self, save: SaveFile) -> CharaDrop:
        if self.chara_drop is None:
            self.chara_drop = CharaDrop(save)
        return self.chara_drop

    def get_gamatoto_levels(self, save: SaveFile) -> GamatotoLevels:
        if self.gamatoto_levels is None:
            self.gamatoto_levels = GamatotoLevels(save)
        return self.gamatoto_levels

    def get_gamatoto_members_name(self, save: SaveFile) -> GamatotoMembersName:
        if self.gamatoto_members_name is None:
            self.gamatoto_members_name = GamatotoMembersName(save)
        return self.gamatoto_members_name

    def get_localizable(self, save: SaveFile) -> Localizable:
        if self.localizable is None:
            self.localizable = Localizable(save)
        return self.localizable

    def get_ability_data(self, save: SaveFile) -> AbilityData:
        if self.abilty_data is None:
            self.abilty_data = AbilityData(save)
        return self.abilty_data

    def get_enemy_names(self, save: SaveFile) -> EnemyNames:
        if self.enemy_names is None:
            self.enemy_names = EnemyNames(save)
        return self.enemy_names

    def get_rank_gift_descriptions(self, save: SaveFile) -> RankGiftDescriptions:
        if self.rank_gift_descriptions is None:
            self.rank_gift_descriptions = RankGiftDescriptions(save)
        return self.rank_gift_descriptions

    def get_rank_gifts(self, save: SaveFile) -> RankGifts:
        if self.rank_gifts is None:
            self.rank_gifts = RankGifts(save)
        return self.rank_gifts

    def get_treasure_text(self, save: SaveFile) -> TreasureText:
        if self.treasure_text is None:
            self.treasure_text = TreasureText(save)
        return self.treasure_text

    def get_cat_shrine_levels(self, save: SaveFile) -> CatShrineLevels:
        if self.cat_shrine_levels is None:
            self.cat_shrine_levels = CatShrineLevels(save)
        return self.cat_shrine_levels

    def get_medal_names(self, save: SaveFile) -> MedalNames:
        if self.medal_names is None:
            self.medal_names = MedalNames(save)
        return self.medal_names

    def get_mission_names(self, save: SaveFile) -> MissionNames:
        if self.mission_names is None:
            self.mission_names = MissionNames(save)
        return self.mission_names

    def get_mission_conditions(self, save: SaveFile) -> MissionConditions:
        if self.mission_conditions is None:
            self.mission_conditions = MissionConditions(save)
        return self.mission_conditions

    def get_lang(self, save: SaveFile) -> str:
        return self.get_localizable(save).get_lang() or "en"


def update_external_content(_: Any = None):
    """Updates external content."""

    color.ColoredText.localize("updating_external_content")
    print()
    ExternalThemeManager.update_all_external_themes()
    ExternalLocaleManager.update_all_external_locales()
    core_data.init_data()


def print_no_internet():
    color.ColoredText.localize("no_internet")


core_data = CoreData()
core_data.init_data()


__all__ = [
    "server",
    "io",
    "locale_handler",
    "country_code",
    "log",
    "game_version",
    "crypto",
    "game",
    "theme_handler",
    "max_value_helper",
    "AdbHandler",
    "CountryCode",
    "Path",
    "Data",
    "CSV",
]
