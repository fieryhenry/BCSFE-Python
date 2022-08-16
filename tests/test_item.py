"""Test item"""

from pytest import MonkeyPatch
from BCSFE_Python import item


def test_item_set(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 0, 15, "value")
    val.edit()
    assert val.value == 10


def test_item_set_max(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly, clamping to max"""

    inputs = ["10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 0, 5, "value")
    val.edit()
    assert val.value == 5


def test_item_set_positive(monkeypatch: MonkeyPatch):
    """Test that the value is set to a positive number"""

    inputs = ["-10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 1, 5, "value")
    val.edit()
    assert val.value == 0


def test_item_set_offset(monkeypatch: MonkeyPatch):
    """Test that the value is set with the offset"""

    inputs = ["10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 1, 15, "value", offset=1)
    val.edit()
    assert val.value == 9


def test_item_set_integer(monkeypatch: MonkeyPatch):
    """Test that the value is set to a an integer"""

    inputs = ["AAAA", "10"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 0, 50, "value")
    val.edit()
    assert val.value == 10


def test_item_set_no_max(monkeypatch: MonkeyPatch):
    """Test that the value is set to a an integer"""

    inputs = ["1111111111"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 0, None, "value")
    val.edit()
    assert val.value == 1111111111


def test_item_set_too_large(monkeypatch: MonkeyPatch):
    """Test that the value is set to a an integer"""

    inputs = ["1234343434343434343434"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", 0, None, "value")
    val.edit()
    assert val.value == 4294967295


def test_item_set_str(monkeypatch: MonkeyPatch):
    """Test that the value is set to a string"""

    inputs = ["AAAA"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.Item("name", "", 50, "value")
    val.edit()
    assert val.value == "AAAA"


def test_item_group_set(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "10", "15", "2"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [10, 15, 2]


def test_item_group_set_1(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1", "5"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [5, 1, 5]


def test_item_group_set_invalid(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["0", "5"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [0, 1, 5]


def test_item_group_set_all(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["4", "5"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [5, 5, 5]


def test_item_group_set_max(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "5", "51", "-1"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [5, 50, 0]


def test_item_group_set_order(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["3 2 1", "5", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"], [0, 1, 5], [50, 50, 50], "value", "name"
    )
    val.edit()
    assert val.values == [7, 6, 5]


def test_item_group_set_offset(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "5", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"],
        [0, 1, 5],
        [50, 50, 50],
        "value",
        "name",
        offset=1,
    )
    val.edit()
    assert val.values == [4, 5, 6]


def test_item_group_set_offset_negative(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "5", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"],
        [0, 1, 5],
        [50, 50, 50],
        "value",
        "name",
        offset=-1,
    )
    val.edit()
    assert val.values == [6, 7, 8]


def test_item_group_set_max_none(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "500000", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"],
        [0, 1, 5],
        None,
        "value",
        "name",
    )
    val.edit()
    assert val.values == [500000, 6, 7]


def test_item_group_set_max_singular(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "500000", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"],
        [0, 1, 5],
        5,
        "value",
        "name",
    )
    val.edit()
    assert val.values == [5, 5, 5]


def test_item_group_set_too_large(monkeypatch: MonkeyPatch):
    """Test that the value is set correctly"""

    inputs = ["1 2 3", "12333333333333333333", "6", "7"]
    monkeypatch.setattr("builtins.input", lambda: inputs.pop(0))

    val = item.create_item_group(
        ["name_1", "name_2", "name_3"],
        [0, 1, 5],
        None,
        "value",
        "name",
    )
    val.edit()
    assert val.values == [4294967295, 6, 7]
