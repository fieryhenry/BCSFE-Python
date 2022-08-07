"""Test talent orbs"""

from typing import Any
from pytest import MonkeyPatch

from BCSFE_Python.edits.basic import talent_orbs


def test_create_orb_list():
    """Test that the list of all possible talent orbs is created correctly"""

    types = talent_orbs.get_talent_orbs_types()
    assert len(types) == 155

    assert "Red D Attack" == types[0]
    assert "Red C Attack" == types[1]

    assert "Red D Defense" == types[5]

    assert "Floating D Attack" == types[10]

    assert "Red D Strong" == types[65]
    assert "Alien S Resistant" == types[139]


def test_edit_all_orbs(monkeypatch: MonkeyPatch):
    """Test that all talent orbs are edited correctly"""

    inputs = ["10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats: dict[str, Any] = {
        "talent_orbs": {
            51: 5,
            0: 10,
            98: 0,
            19: 1,
        }
    }
    types = talent_orbs.get_talent_orbs_types()
    save_stats = talent_orbs.edit_all_orbs(save_stats, types)

    assert len(save_stats["talent_orbs"]) == len(types)
    for i in range(len(types)):
        assert save_stats["talent_orbs"][i] == 10


def test_edit_all_orbs_invalid(monkeypatch: MonkeyPatch):
    """Test that all talent orbs are edited correctly"""

    inputs = ["aaa", "15"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats_b: dict[str, Any] = {
        "talent_orbs": {
            51: 5,
            0: 10,
            98: 0,
            19: 1,
        }
    }
    types = talent_orbs.get_talent_orbs_types()
    save_stats = talent_orbs.edit_all_orbs(save_stats_b, types)

    assert save_stats_b == save_stats
