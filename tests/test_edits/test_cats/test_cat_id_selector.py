"""Test cat id selector"""

from pytest import MonkeyPatch
from BCSFE_Python.edits.cats import cat_id_selector


def test_get_all_cats():
    """Test that the ids are correct"""
    save_stats = {"cats": [1, 1, 1, 0, 1]}
    ids = cat_id_selector.get_all_cats(save_stats)
    assert ids == [0, 1, 2, 3, 4]


def test_select_range(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["1-5"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [1, 2, 3, 4, 5]
    assert ids == actual_ids


def test_select_current():
    """Test that the ids are correct"""

    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_current_cats(save_stats)
    actual_ids = [0, 1, 2, 4]
    assert ids == actual_ids


def test_select_rarity(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["1"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    ids = cat_id_selector.select_cats_rarity(False)
    actual_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 643]
    assert ids == actual_ids


def test_select_range_reverse(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["5-1"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [1, 2, 3, 4, 5]
    assert ids == actual_ids


def test_select_range_mult(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["1-5 7-10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [1, 2, 3, 4, 5, 7, 8, 9, 10]
    assert ids == actual_ids


def test_select_range_spaces(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["1 4 7 2"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [1, 4, 7, 2]
    assert ids == actual_ids


def test_select_range_comb(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["1 4 7 2 8-10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [1, 4, 7, 2, 8, 9, 10]
    assert ids == actual_ids


def test_select_range_all(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["all"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))
    save_stats = {"cats": [1, 1, 1, 0, 1]}

    ids = cat_id_selector.select_cats_range(save_stats)
    actual_ids = [0, 1, 2, 3, 4]
    assert ids == actual_ids


def test_gatya_banner(monkeypatch: MonkeyPatch):
    """Test that the ids are correct"""

    inputs = ["602"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    ids = cat_id_selector.select_cats_gatya_banner(False)
    ids.sort()
    actual_ids = [
        448,
        449,
        450,
        451,
        455,
        461,
        463,
        478,
        481,
        493,
        544,
        612,
        138,
        259,
        330,
        195,
        496,
        358,
        376,
        502,
        526,
        533,
        564,
        229,
        30,
        31,
        32,
        33,
        35,
        36,
        39,
        40,
        61,
        150,
        151,
        152,
        153,
        199,
        307,
        377,
        522,
        37,
        38,
        41,
        42,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        55,
        56,
        58,
        106,
        145,
        146,
        147,
        148,
        149,
        197,
        198,
        308,
        325,
        495,
        271,
        523,
    ]
    actual_ids.sort()
    assert ids == actual_ids
