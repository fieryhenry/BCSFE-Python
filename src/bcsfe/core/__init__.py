from typing import Optional

from requests.exceptions import ConnectionError
from requests import Response
from json.decoder import JSONDecodeError

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
from bcsfe.core.game.catbase.medals import Medals
from bcsfe.core.game.catbase.mission import Missions
from bcsfe.core.game.catbase.my_sale import MySale
from bcsfe.core.game.catbase.nyanko_club import NyankoClub
from bcsfe.core.game.catbase.officer_pass import OfficerPass
from bcsfe.core.game.catbase.powerup import PowerUpHelper
from bcsfe.core.game.catbase.scheme_items import SchemeItems
from bcsfe.core.game.catbase.special_skill import SpecialSkills
from bcsfe.core.game.catbase.stamp import StampData
from bcsfe.core.game.catbase.talent_orbs import TalentOrb, TalentOrbs
from bcsfe.core.game.catbase.unlock_popups import UnlockPopups
from bcsfe.core.game.catbase.upgrade import Upgrade
from bcsfe.core.game.catbase.user_rank_rewards import UserRankRewards
from bcsfe.core.game.gamoto.base_materials import BaseMaterials
from bcsfe.core.game.gamoto.cat_shrine import CatShrine
from bcsfe.core.game.gamoto.gamatoto import Gamatoto, GamatotoLevels
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
from bcsfe.core.game.map.story import StoryChapters
from bcsfe.core.game.map.timed_score import TimedScoreChapters
from bcsfe.core.game.map.tower import TowerChapters
from bcsfe.core.game.map.uncanny import UncannyChapters
from bcsfe.core.game.map.zero_legends import ZeroLegendsChapters
from bcsfe.core.game_version import GameVersion
from bcsfe.core.io.adb_handler import AdbHandler
from bcsfe.core.io.bc_csv import CSV, Delimeter, Row
from bcsfe.core.io.command import Command, CommandResult
from bcsfe.core.io.config import Config, ConfigKey
from bcsfe.core.io.data import Data
from bcsfe.core.io.json_file import JsonFile
from bcsfe.core.io.path import Path
from bcsfe.core.io.save import SaveError, SaveFile, CantDetectSaveCCError
from bcsfe.core.io.thread_helper import thread_run_many
from bcsfe.core.io.yaml import YamlFile
from bcsfe.core.locale_handler import LocalManager
from bcsfe.core.log import Logger
from bcsfe.core.server.client_info import ClientInfo
from bcsfe.core.server.game_data_getter import GameDataGetter
from bcsfe.core.server.headers import AccountHeaders
from bcsfe.core.server.managed_item import BackupMetaData, ManagedItem, ManagedItemType
from bcsfe.core.server.request import RequestHandler
from bcsfe.core.server.server_handler import ServerHandler
from bcsfe.core.server.updater import Updater
from bcsfe.core.theme_handler import ThemeHandler
from bcsfe.core.max_value_helper import MaxValueHelper

config = Config()
logger = Logger()
local_manager = LocalManager()
theme_manager = ThemeHandler()
max_value_manager = MaxValueHelper()
game_data_getter: Optional[GameDataGetter] = None
gatya_item_names: Optional[GatyaItemNames] = None
gatya_item_buy: Optional[GatyaItemBuy] = None
chara_drop: Optional[CharaDrop] = None
gamatoto_levels: Optional[GamatotoLevels] = None


def get_game_data_getter(save: SaveFile) -> GameDataGetter:
    global game_data_getter
    if game_data_getter is None:
        game_data_getter = GameDataGetter(save)
    return game_data_getter


def get_gatya_item_names(save: SaveFile) -> GatyaItemNames:
    global gatya_item_names
    if gatya_item_names is None:
        gatya_item_names = GatyaItemNames(save)
    return gatya_item_names


def get_gatya_item_buy(save: SaveFile) -> GatyaItemBuy:
    global gatya_item_buy
    if gatya_item_buy is None:
        gatya_item_buy = GatyaItemBuy(save)
    return gatya_item_buy


def get_chara_drop(save: SaveFile) -> CharaDrop:
    global chara_drop
    if chara_drop is None:
        chara_drop = CharaDrop(save)
    return chara_drop


def get_gamatoto_levels(save: SaveFile) -> GamatotoLevels:
    global gamatoto_levels
    if gamatoto_levels is None:
        gamatoto_levels = GamatotoLevels(save)
    return gamatoto_levels


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
]
