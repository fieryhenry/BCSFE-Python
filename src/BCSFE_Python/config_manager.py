from typing import Any
import yaml

from . import helper


def read_config() -> dict[Any, Any]:
    """
    Reads the config file and returns a dictionary with the config data.
    """
    with open(helper.get_file("config.yaml"), "r", encoding="utf-8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return {}
    return config


def get_config_value(key: str) -> Any:
    """
    Returns the value of the given key in the config file.
    """
    config = read_config()
    return config[key]


def get_config_value_category(category: str, key: str) -> Any:
    """
    Returns the value of the given key in the config file.
    """
    config = read_config()
    return config[category][key]
