"""Test basic item editing"""

from pytest import MonkeyPatch
from BCSFE_Python.edits.basic import basic_items


def test_cf_normal(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["y", "10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    save_stats = {"cat_food": {"Value": 50}}

    save_stats = basic_items.edit_cat_food(save_stats)
    assert save_stats["cat_food"]["Value"] == 10


def test_catfood_leave(monkeypatch: MonkeyPatch):
    """Test that the value is left unchanged"""

    inputs = ["n", "10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    save_stats = {"cat_food": {"Value": 50}}

    save_stats = basic_items.edit_cat_food(save_stats)
    assert save_stats["cat_food"]["Value"] == 50


def test_iq_normal(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["abcdefghi"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    save_stats = {"inquiry_code": "123456789"}

    save_stats = basic_items.edit_inquiry_code(save_stats)
    assert save_stats["inquiry_code"] == "abcdefghi"
