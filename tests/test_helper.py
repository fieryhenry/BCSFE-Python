"""Test helper module"""

from BCSFE_Python import helper


def test_str_to_gv():
    """Test that a game version with . is converted to an int representation"""
    assert helper.str_to_gv("1.0.0") == "10000"
    assert helper.str_to_gv("11.8.2") == "110802"
    assert helper.str_to_gv("1.7") == "10700"
    assert helper.str_to_gv("10.87") == "108700"


def test_gv_to_str():
    """Test that an int representation is converted to a game version with ."""
    assert helper.gv_to_str(10000) == "1.0.0"
    assert helper.gv_to_str(110802) == "11.8.2"
    assert helper.gv_to_str(10700) == "1.7.0"
    assert helper.gv_to_str(108700) == "10.87.0"
