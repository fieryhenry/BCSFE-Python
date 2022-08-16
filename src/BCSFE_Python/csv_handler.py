"""Handler for parsing CSV files."""


from typing import Any


def remove_pkcs7_padding(data: bytes) -> bytes:
    """Remove pkcs7 padding from data."""

    if len(data) % 16 != 0:
        raise Exception("Invalid data length")

    padding_length = data[-1]
    if padding_length > 16:
        raise Exception("Invalid padding length")
    if data[-padding_length:] != bytes([padding_length] * padding_length):
        raise Exception("Invalid padding")

    return data[:-padding_length]


def remove_comments(data: str) -> str:
    """Remove in-line comments from data."""

    data_ls = data.split("\n")
    data_ls = [line.split("//")[0] for line in data_ls]
    data_ls = [line.strip() for line in data_ls]
    data_ls = [line for line in data_ls if line != ""]
    return "\n".join(data_ls)


def parse_csv(data: str, delimeter: str = ",") -> list[list[str]]:
    """Parse CSV data."""

    data = remove_comments(data)
    data_ls = data.split("\n")
    data_ls_ls = [line.split(delimeter) for line in data_ls]
    data_ls_ls = remove_empty_items(data_ls_ls)
    data_ls_ls = [line for line in data_ls_ls if line != []]
    return data_ls_ls


def remove_empty_items(data: list[list[Any]]) -> list[list[Any]]:
    """Remove empty items from a list of lists."""

    data_ls: list[list[Any]] = []
    for line in data:
        line_ls: list[Any] = []
        for item in line:
            if item != "":
                line_ls.append(item)
        data_ls.append(line_ls)
    return data_ls
