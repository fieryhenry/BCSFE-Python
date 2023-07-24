from typing import Any, Callable, Optional
from bcsfe import core
from bcsfe.cli import dialog_creator, color, edits, save_management, main


class FeatureHandler:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file

    def get_features(self):
        cat_features = edits.cat_editor.CatEditor.edit_cats
        if core.config.get_bool(core.ConfigKey.SEPARATE_CAT_EDIT_OPTIONS):
            cat_features = {
                "unlock_cats": edits.cat_editor.CatEditor.unlock_cats_run,
                "remove_cats": edits.cat_editor.CatEditor.remove_cats_run,
                "upgrade_cats": edits.cat_editor.CatEditor.upgrade_cats_run,
                "true_form_cats": edits.cat_editor.CatEditor.true_form_cats_run,
                "remove_true_form_cats": edits.cat_editor.CatEditor.remove_true_form_cats_run,
                "upgrade_talent_cats": edits.cat_editor.CatEditor.upgrade_talents_cats_run,
            }

        features: dict[str, Any] = {
            "save_management": {
                "save_save": save_management.SaveManagement.save_save,
                "save_upload": save_management.SaveManagement.save_upload,
                "save_save_file": save_management.SaveManagement.save_save_dialog,
                "adb_push": save_management.SaveManagement.adb_push,
                "adb_push_rerun": save_management.SaveManagement.adb_push_rerun,
                "export_save": save_management.SaveManagement.export_save,
                "load_save": save_management.SaveManagement.load_save,
                "init_save": save_management.SaveManagement.init_save,
            },
            "items": {
                "catfood": edits.basic_items.BasicItems.edit_catfood,
                "xp": edits.basic_items.BasicItems.edit_xp,
                "normal_tickets": edits.basic_items.BasicItems.edit_normal_tickets,
                "rare_tickets": edits.basic_items.BasicItems.edit_rare_tickets,
                "platinum_tickets": edits.basic_items.BasicItems.edit_platinum_tickets,
                "legend_tickets": edits.basic_items.BasicItems.edit_legend_tickets,
                "platinum_shards": edits.basic_items.BasicItems.edit_platinum_shards,
                "np": edits.basic_items.BasicItems.edit_np,
                "leadership": edits.basic_items.BasicItems.edit_leadership,
                "battle_items": edits.basic_items.BasicItems.edit_battle_items,
                "catseyes": edits.basic_items.BasicItems.edit_catseyes,
                "catfruit": edits.basic_items.BasicItems.edit_catfruit,
                "talent_orbs": edits.talent_orbs.SaveOrbs.edit_talent_orbs,
                "catamins": edits.basic_items.BasicItems.edit_catamins,
                "scheme_items": edits.basic_items.BasicItems.edit_scheme_items,
            },
            "cats": cat_features,
            "ototo": {
                "engineers": edits.basic_items.BasicItems.edit_engineers,
                "base_materials": edits.basic_items.BasicItems.edit_base_materials,
            },
            "account": {
                "unban_account": save_management.SaveManagement.unban_account,
                "upload_items": save_management.SaveManagement.upload_items,
            },
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
        features: Optional[dict[str, Any]] = None,
        found_features: Optional[set[str]] = None,
    ) -> set[str]:
        name = name.lower().replace(" ", "")
        if features is None:
            features = self.get_features()
        if found_features is None:
            found_features = set()

        for feature_name_key, feature in features.items():
            feature_name = core.local_manager.get_key(feature_name_key)
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
                if name in alias.lower().replace(" ", "") or name == "":
                    found_features.add(path)
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
            selected_features = list(self.search_features(usr_input))

        return selected_features

    def select_features_run(self):
        features = self.get_features()
        features = list(features.keys())
        self.save_file.to_file(self.save_file.get_temp_path())
        edits.clear_tutorial.clear_tutorial(self.save_file, False)
        self.save_file.show_ban_message = False

        while True:
            features = self.select_features(features)
            feature = None
            if len(features) == 1:
                feature = features[0]
            if len(features) == 2 and features[0] == "go_back":
                feature = features[1]

            if not feature:
                continue

            feature = self.get_feature(feature)

            if isinstance(feature, Callable):
                edits.clear_tutorial.clear_tutorial(self.save_file, False)
                self.save_file.show_ban_message = False

                feature(self.save_file)

                self.save_file.to_file(self.save_file.get_temp_path())

                features = self.get_features()
                features = list(features.keys())
