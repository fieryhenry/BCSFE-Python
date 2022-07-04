"""Handler for parsing csv files"""

from typing import Union
from . import helper


def remove_pkcs7_padding(data: bytes) -> bytes:
    """Remove PKCS#7 padding"""

    if len(data) % 16 != 0:
        raise ValueError("Invalid data length")
    padding_size = data[-1]
    if padding_size < 1 or padding_size > 16:
        raise ValueError("Invalid padding size")
    if data[-padding_size:] != bytes([padding_size] * padding_size):
        raise ValueError("Invalid padding")
    return data[:-padding_size]


def remove_comments(data: str) -> str:
    """Remove in-line comments from a file"""

    comments = ["#", "//"]
    data = data.split("\n")
    for comment in comments:
        data = [line.split(comment)[0] for line in data]
    data = "\n".join(data)
    return data


def parse_csv(
    file_path: str,
    delimiter: str = ",",
    remove_padding: bool = True,
    parse_int: bool = True,
    r_comments: bool = True,
    r_empty: bool = True,
) -> Union[list[list[str]], list[list[int]]]:
    """Parse csv file with error handling and return list of lists and remove padding"""

    data = helper.read_file_bytes(file_path)
    if remove_padding:
        data = remove_pkcs7_padding(data)

    lines = data.decode("utf-8")
    if r_comments:
        lines = remove_comments(lines)
    lines = lines.split("\n")
    lines = [line.strip().split(delimiter) for line in lines]
    if r_empty:
        lines = helper.remove_empty_items(lines)
    if parse_int:
        lines = helper.parse_int_list_list(lines)
    return lines
