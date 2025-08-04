from __future__ import annotations
from typing import Any, Callable
from bcsfe import core
from bcsfe.cli import dialog_creator, color, edits, save_management, main


class FeatureHandler:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file

    def get_features(self):
        cat_features = {"cats": edits.cat_editor.CatEditor.edit_cats}
        if core.core_data.config.get_bool(core.ConfigKey.SEPARATE_CAT_EDIT_OPTIONS):
            cat_features = {
                "unlock_remove_cats": edits.cat_editor.CatEditor.unlock_remove_cats_run,
                "upgrade_cats": edits.cat_editor.CatEditor.upgrade_cats_run,
                "true_form_remove_form_cats": edits.cat_editor.CatEditor.true_form_remove_form_cats_run,
                "force_true_form_cats": edits.cat_editor.CatEditor.force_true_form_cats_run,
                "fourth_form_remove_form_cats": edits.cat_editor.CatEditor.fourth_form_remove_form_cats_run,
                "force_fourth_form_cats": edits.cat_editor.CatEditor.force_fourth_form_cats_run,
                "upgrade_talents_remove_talents_cats": edits.cat_editor.CatEditor.upgrade_talents_remove_talents_cats_run,
                "unlock_remove_cat_guide": edits.cat_editor.CatEditor.unlock_cat_guide_remove_guide_run,
            }

        cat_features["special_skills"] = (
            edits.basic_items.BasicItems.edit_special_skills
        )

        features: dict[str, Any] = {
            "save_management": {
                "save_save": save_management.SaveManagement.save_save,
                "save_upload": save_management.SaveManagement.save_upload,
                "save_save_file": save_management.SaveManagement.save_save_dialog,
                "save_save_documents": save_management.SaveManagement.save_save_documents,
                "waydroid_push": save_management.SaveManagement.waydroid_push,
                "waydroid_push_rerun": save_management.SaveManagement.waydroid_push_rerun,
                "adb_push": save_management.SaveManagement.adb_push,
                "adb_push_rerun": save_management.SaveManagement.adb_push_rerun,
                "export_save": save_management.SaveManagement.export_save,
                "load_save": save_management.SaveManagement.load_save,
                "init_save": save_management.SaveManagement.init_save,
                "convert_region": save_management.SaveManagement.convert_save_cc,
                "convert_version": save_management.SaveManagement.convert_save_gv,
            },
            "items": {
                "catfood": edits.basic_items.BasicItems.edit_catfood,
                "xp": edits.basic_items.BasicItems.edit_xp,
                "normal_tickets": edits.basic_items.BasicItems.edit_normal_tickets,
                "rare_tickets": edits.basic_items.BasicItems.edit_rare_tickets,
                "rare_ticket_trade_feature_name": edits.rare_ticket_trade.RareTicketTrade.rare_ticket_trade,
                "platinum_tickets": edits.basic_items.BasicItems.edit_platinum_tickets,
                "legend_tickets": edits.basic_items.BasicItems.edit_legend_tickets,
                "platinum_shards": edits.basic_items.BasicItems.edit_platinum_shards,
                "np": edits.basic_items.BasicItems.edit_np,
                "leadership": edits.basic_items.BasicItems.edit_leadership,
                "battle_items": edits.basic_items.BasicItems.edit_battle_items,
                "catseyes": edits.basic_items.BasicItems.edit_catseyes,
                "catfruit": edits.basic_items.BasicItems.edit_catfruit,
                "talent_orbs": core.game.catbase.talent_orbs.SaveOrbs.edit_talent_orbs,
                "catamins": edits.basic_items.BasicItems.edit_catamins,
                "scheme_items": edits.basic_items.BasicItems.edit_scheme_items,
                "labyrinth_medals": edits.basic_items.BasicItems.edit_labyrinth_medals,
                "100_million_tickets": edits.basic_items.BasicItems.edit_100_million_ticket,
                "event_tickets": edits.event_tickets.EventTickets.edit,
                "treasure_chests": edits.basic_items.BasicItems.edit_treasure_chests,
            },
            "cats_special_skills": cat_features,
            "levels": {
                "clear_tutorial": edits.clear_tutorial.clear_tutorial,
                "clear_story": core.game.map.story.StoryChapters.clear_story,
                "challenge_score": core.game.map.challenge.edit_challenge_score,
                "dojo_score": core.game.map.dojo.edit_dojo_score,
                "enigma": core.game.map.enigma.edit_enigma,
                "unlock_aku_realm": edits.aku_realm.unlock_aku_realm,
                "story_treasures": core.game.map.story.StoryChapters.edit_treasures,
                "outbreaks": core.game.map.outbreaks.Outbreaks.edit_outbreaks,
                "aku_chapters": core.game.map.aku.AkuChapters.edit_aku_chapters,
                "itf_timed_scores": core.game.map.story.StoryChapters.edit_itf_timed_scores,
                "filibuster_reclearing": edits.basic_items.BasicItems.allow_filibuster_stage_reclearing,
                "sol": core.game.map.event.EventChapters.edit_sol_chapters,
                "event": core.game.map.event.EventChapters.edit_event_chapters,
                "collab": core.game.map.event.EventChapters.edit_collab_chapters,
                "gauntlets": core.game.map.gauntlets.GauntletChapters.edit_gauntlets,
                "collab_gauntlets": core.game.map.gauntlets.GauntletChapters.edit_collab_gauntlets,
                "uncanny": core.game.map.uncanny.UncannyChapters.edit_uncanny,
                "behemoth_culling": core.game.map.gauntlets.GauntletChapters.edit_behemoth_culling,
                "legend_quest": core.game.map.legend_quest.LegendQuestChapters.edit_legend_quest,
                "towers": core.game.map.tower.TowerChapters.edit_towers,
                "zero_legends": core.game.map.zero_legends.ZeroLegendsChapters.edit_zero_legends,
            },
            "gamototo": {
                "engineers": edits.basic_items.BasicItems.edit_engineers,
                "base_materials": edits.basic_items.BasicItems.edit_base_materials,
                "gamatoto_xp_level": core.game.gamoto.gamatoto.edit_xp,
                "gamatoto_helpers": core.game.gamoto.gamatoto.edit_helpers,
                "ototo_cat_cannon": core.game.gamoto.ototo.edit_cannon,
                "cat_shrine": core.game.gamoto.cat_shrine.CatShrine.edit_catshrine,
            },
            "account": {
                "unban_account": save_management.SaveManagement.unban_account,
                "upload_items": save_management.SaveManagement.upload_items,
                "inquiry_code": edits.basic_items.BasicItems.edit_inquiry_code,
                "password_refresh_token": edits.basic_items.BasicItems.edit_password_refresh_token,
            },
            "gatya": {
                "rare_gatya_seed": edits.basic_items.BasicItems.edit_rare_gatya_seed,
                "normal_gatya_seed": edits.basic_items.BasicItems.edit_normal_gatya_seed,
                "event_gatya_seed": edits.basic_items.BasicItems.edit_event_gatya_seed,
            },
            "fixes": {
                "fix_gamatoto_crash": edits.fixes.Fixes.fix_gamatoto_crash,
                "fix_ototo_crash": edits.fixes.Fixes.fix_ototo_crash,
                "fix_time_errors": edits.fixes.Fixes.fix_time_errors,
                "unlock_equip_menu": edits.basic_items.BasicItems.unlock_equip_menu,
                "fix_officer_pass_crash": core.OfficerPass.fix_crash,
            },
            "other": {
                "unlocked_slots": edits.basic_items.BasicItems.edit_unlocked_slots,
                "restart_pack": edits.basic_items.BasicItems.set_restart_pack,
                "special_skills": edits.basic_items.BasicItems.edit_special_skills,
                "playtime": core.game.catbase.playtime.edit,
                "enemy_guide": edits.enemy_editor.EnemyEditor.edit_enemy_guide,
                "user_rank_rewards": core.game.catbase.user_rank_rewards.edit_user_rank_rewards,
                "unlock_equip_menu": edits.basic_items.BasicItems.unlock_equip_menu,
                "gold_pass": core.game.catbase.nyanko_club.NyankoClub.edit_gold_pass,
                "medals": core.game.catbase.medals.Medals.edit_medals,
                "missions": core.game.catbase.mission.Missions.edit_missions,
            },
            "config": core.core_data.config.edit_config,
            "update_external": core.update_external_content,
            "exit": main.Main.exit_editor,
        }
        return features

    def get_feature(self, feature_name: str):
        feature_path = feature_name.split(".")
        feature_dict = self.get_features()
        feature = feature_dict
        for path in feature_path:
            feature = feature[path]

        return feature

    def search_features(
        self,
        name: str,
        parent_path: str = "",
        features: dict[str, Any] | None = None,
        found_features: dict[str, int] | None = None,
    ) -> dict[str, int]:
        name = name.lower()
        if features is None:
            features = self.get_features()
        if found_features is None:
            found_features = {}

        for feature_name_key, feature in features.items():
            feature_name = core.core_data.local_manager.get_key(feature_name_key)
            path = (
                f"{parent_path}.{feature_name_key}" if parent_path else feature_name_key
            )
            if isinstance(feature, dict):
                found_features.update(
                    self.search_features(
                        name,
                        path,
                        feature,  # type: ignore
                        found_features,
                    )
                )
            for alias in core.LocalManager.get_all_aliases(feature_name):
                if not name:
                    found_features[path] = 100
                    break
                alias = alias.lower()

                name = name.replace(" ", "")
                alias = alias.replace(" ", "")
                if alias in name or name in alias:
                    found_features[path] = 100
                break

        return found_features

    def display_features(self, features: list[str]):
        feature_names: list[str] = []
        for feature_name in features:
            feature_names.append(feature_name.split(".")[-1])
        print()
        dialog_creator.ListOutput(feature_names, [], "features", {}).display_locale(
            remove_alias=True
        )

    def select_features(self, features: list[str], parent_path: str = "") -> list[str]:
        if features != list(self.get_features().keys()):
            features.insert(0, "go_back")
        self.display_features(features)
        print()
        usr_input = color.ColoredInput().localize("select_features")
        selected_features: list[str] = []
        if usr_input.isdigit():
            usr_input = int(usr_input)
            if usr_input > len(features):
                color.ColoredText.localize("invalid_input")
            elif usr_input < 1:
                color.ColoredText.localize("invalid_input")
            else:
                feature_name_top = features[usr_input - 1]
                if feature_name_top == "go_back":
                    return list(self.get_features().keys())
                feature = self.get_feature(feature_name_top)
                if isinstance(feature, dict):
                    for feature_name in feature.keys():
                        feature_path = (
                            f"{parent_path}.{feature_name_top}.{feature_name}"
                            if parent_path
                            else f"{feature_name_top}.{feature_name}"
                        )
                        selected_features.append(feature_path)

                else:
                    feature_path = (
                        f"{parent_path}.{feature_name_top}"
                        if parent_path
                        else feature_name_top
                    )
                    selected_features.append(feature_path)

        else:
            feats = self.search_features(usr_input)
            kv_map = list(feats.items())
            kv_map.sort(key=lambda v: v[1], reverse=True)
            selected_features = [v[0] for v in kv_map]

        return selected_features

    def select_features_run(self):
        features = self.get_features()
        features = list(features.keys())
        self.save_file.to_file_thread(self.save_file.get_temp_path())
        edits.clear_tutorial.clear_tutorial(self.save_file, False)
        self.save_file.show_ban_message = False

        while True:
            features = self.select_features(features)

            new_features: list[str] = []
            found_strs: list[str] = []
            for feature_ in features:
                if feature_.split(".")[-1] in found_strs:
                    continue
                found_strs.append(feature_.split(".")[-1])
                new_features.append(feature_)

            features = new_features
            feature = None
            if len(features) == 1:
                feature = features[0]
            if len(features) == 2 and features[0] == "go_back":
                feature = features[1]

            if not feature:
                continue

            feature = self.get_feature(feature)

            if isinstance(feature, Callable):
                self.do_save_actions()

                feature(self.save_file)

                self.save_file.to_file_thread(self.save_file.get_temp_path())

                features = self.get_features()
                features = list(features.keys())

                core.core_data.game_data_getter = None  # reset game data getter so that if an old version is removed, it will download the new version

    def do_save_actions(self):
        if core.core_data.config.get_bool(core.ConfigKey.CLEAR_TUTORIAL_ON_LOAD):
            edits.clear_tutorial.clear_tutorial(self.save_file, False)
        if core.core_data.config.get_bool(core.ConfigKey.REMOVE_BAN_MESSAGE_ON_LOAD):
            self.save_file.show_ban_message = False
