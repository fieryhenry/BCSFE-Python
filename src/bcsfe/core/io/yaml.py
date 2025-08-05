from __future__ import annotations
from typing import Any
from bcsfe import core
from bcsfe import cli
import yaml


class YamlFile:
    def __init__(self, path: core.Path, print_err: bool = True):
        self.path = path
        self.yaml: dict[str, Any] = {}
        if self.path.exists():
            self.data = path.read()
            try:
                yml = yaml.safe_load(self.data.data)
                if not isinstance(yml, dict):
                    self.yaml = {}
                    self.save(print_err)
                else:
                    self.yaml = yml
            except yaml.YAMLError:
                self.yaml = {}
                self.save(print_err)
        else:
            self.yaml = {}
            self.save(print_err)

    def save(self, print_err: bool = True) -> None:
        self.path.parent().generate_dirs()

        try:
            with open(self.path.path, "w", encoding="utf-8") as f:
                yaml.dump(self.yaml, f)
        except FileNotFoundError:
            if print_err:
                cli.color.ColoredText.localize("yaml_create_error", path=self.path.path)

    def __getitem__(self, key: str) -> Any:
        return self.yaml[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.yaml[key] = value

    def __delitem__(self, key: str) -> None:
        del self.yaml[key]

    def __contains__(self, key: str) -> bool:
        return key in self.yaml

    def __iter__(self):
        return iter(self.yaml)

    def __len__(self) -> int:
        return len(self.yaml)

    def __repr__(self) -> str:
        return self.yaml.__repr__()

    def __str__(self) -> str:
        return self.yaml.__str__()

    def get(self, key: str) -> Any:
        return self.yaml.get(key)

    def remove(self) -> None:
        self.path.remove()
        self.yaml = {}
