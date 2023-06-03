import base64
import enum
from io import BytesIO
import struct
import typing
from typing import Any, Literal, Optional, Union
from bcsfe.core.io import bc_csv, path
import datetime


class PaddingType(enum.Enum):
    PKCS7 = enum.auto()
    ZERO = enum.auto()
    NONE = enum.auto()


class Data:
    def __init__(self, data: Union[bytes, str, None, int, bool, "Data"] = None):
        if isinstance(data, str):
            self.data = data.encode("utf-8")
        elif isinstance(data, bytes):
            self.data = data
        elif isinstance(data, bool):
            value = 1 if data else 0
            self.data = str(value).encode("utf-8")
        elif isinstance(data, int):
            self.data = str(data).encode("utf-8")
        elif isinstance(data, Data):
            self.data = data.data
        elif data is None:
            self.data = b""
        else:
            raise TypeError(
                f"data must be bytes, str, int, bool, Data, or None, not {type(data)}"
            )
        self.pos = 0
        self.set_little_endiness()

    def set_endiness(self, endiness: Literal["<", ">"]):
        self.endiness = endiness

    def set_little_endiness(self):
        self.set_endiness("<")

    def set_big_endiness(self):
        self.set_endiness(">")

    def is_empty(self) -> bool:
        return len(self.data) == 0

    def to_file(self, path: "path.Path"):
        with open(path.path, "wb") as f:
            f.write(self.data)

    def copy(self) -> "Data":
        return Data(self.data)

    @staticmethod
    def from_file(path: "path.Path") -> "Data":
        with open(path.path, "rb") as f:
            return Data(f.read())

    def set_pos(self, pos: int):
        if pos < 0:
            pos = len(self.data) + pos
        self.pos = pos

    def reset_pos(self):
        self.pos = 0

    def clear(self):
        self.data = b""
        self.pos = 0

    def get_pos(self) -> int:
        return self.pos

    def to_hex(self) -> str:
        return self.data.hex()

    def __len__(self) -> int:
        return len(self.data)

    def __add__(self, other: "Data") -> "Data":
        return Data(self.data + other.data)

    @typing.overload
    def __getitem__(self, key: int) -> int:
        pass

    @typing.overload
    def __getitem__(self, key: slice) -> "Data":
        pass

    def __getitem__(self, key: Union[int, slice]) -> Union[int, "Data"]:
        if isinstance(key, int):
            return self.data[key]
        elif isinstance(key, slice):  # type: ignore
            return Data(self.data[key])
        else:
            raise TypeError("key must be int or slice")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Data):
            return self.data == other.data
        else:
            return False

    def get_bytes(self) -> bytes:
        return self.data

    def read_bytes(self, length: int) -> bytes:
        result = self.data[self.pos : self.pos + length]
        self.pos += length
        return result

    def read_int(self) -> int:
        result = struct.unpack(f"{self.endiness}i", self.read_bytes(4))[0]
        return result

    def read_variable_length_int(self) -> int:
        i = 0
        for _ in range(4):
            i3 = i << 7
            read = self.read_ubyte()
            i = i3 | (read & 0x7F)
            if read & 0x80 == 0:
                return i
        return i

    def write_variable_length_int(self, value: int):
        i2 = 0
        i3 = 0
        while value >= 128:
            i2 |= ((value & 0x7F) | 0x8000) << (i3 * 8)
            i3 += 1
            value >>= 7
        i4 = i2 | (value << (i3 * 8))
        i5 = i3 + 1
        for i6 in range(i5):
            self.write_ubyte((i4 >> (((i5 - i6) - 1) * 8)) & 0xFF)

    def read_int_list(self, length: Optional[int] = None) -> list[int]:
        if length is None:
            length = self.read_int()
        result: list[int] = []
        for _ in range(length):
            result.append(self.read_int())
        return result

    def read_bool_list(self, length: Optional[int] = None) -> list[bool]:
        if length is None:
            length = self.read_int()
        result: list[bool] = []
        for _ in range(length):
            result.append(self.read_bool())
        return result

    def read_string_list(self, length: Optional[int] = None) -> list[str]:
        if length is None:
            length = self.read_int()
        result: list[str] = []
        for _ in range(length):
            result.append(self.read_string())
        return result

    def read_byte_list(self, length: Optional[int] = None) -> list[int]:
        if length is None:
            length = self.read_int()
        result: list[int] = []
        for _ in range(length):
            result.append(self.read_byte())
        return result

    def read_short_list(self, length: Optional[int] = None) -> list[int]:
        if length is None:
            length = self.read_int()
        result: list[int] = []
        for _ in range(length):
            result.append(self.read_short())
        return result

    def read_uint(self) -> int:
        result = struct.unpack(f"{self.endiness}I", self.read_bytes(4))[0]
        return result

    def read_short(self) -> int:
        result = struct.unpack(f"{self.endiness}h", self.read_bytes(2))[0]
        return result

    def read_ushort(self) -> int:
        result = struct.unpack(f"{self.endiness}H", self.read_bytes(2))[0]
        return result

    def read_byte(self) -> int:
        result = struct.unpack(f"{self.endiness}b", self.read_bytes(1))[0]
        return result

    def read_ubyte(self) -> int:
        result = struct.unpack(f"{self.endiness}B", self.read_bytes(1))[0]
        return result

    def read_float(self) -> float:
        result = struct.unpack(f"{self.endiness}f", self.read_bytes(4))[0]
        return result

    def read_double(self) -> float:
        result = struct.unpack(f"{self.endiness}d", self.read_bytes(8))[0]
        return result

    def read_string(self, length: Optional[int] = None) -> str:
        if length is None:
            length = self.read_int()
        result = self.read_bytes(length).decode("utf-8")
        return result

    def read_long(self) -> int:
        result = struct.unpack(f"{self.endiness}q", self.read_bytes(8))[0]
        return result

    def read_ulong(self) -> int:
        result = struct.unpack(f"{self.endiness}Q", self.read_bytes(8))[0]
        return result

    def read_date(self):
        year = self.read_int()
        month = self.read_int()
        day = self.read_int()
        hour = self.read_int()
        minute = self.read_int()
        second = self.read_int()
        return datetime.datetime(year, month, day, hour, minute, second)

    def write_date(self, date: datetime.datetime):
        self.write_int(date.year)
        self.write_int(date.month)
        self.write_int(date.day)
        self.write_int(date.hour)
        self.write_int(date.minute)
        self.write_int(date.second)

    def write_bytes(self, data: bytes):
        self.data += data
        self.pos += len(data)

    def write_int(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}i", value))

    def write_uint(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}I", value))

    def write_short(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}h", value))

    def write_ushort(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}H", value))

    def write_byte(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}b", value))

    def write_ubyte(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}B", value))

    def write_float(self, value: float):
        self.write_bytes(struct.pack(f"{self.endiness}f", value))

    def write_double(self, value: float):
        self.write_bytes(struct.pack(f"{self.endiness}d", value))

    def write_string(self, value: str, write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        self.write_bytes(value.encode("utf-8"))

    def write_long(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}q", value))

    def write_ulong(self, value: int):
        self.write_bytes(struct.pack(f"{self.endiness}Q", value))

    def write_int_list(self, value: list[int], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_int(item)

    def write_bool_list(self, value: list[bool], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_bool(item)

    def write_string_list(self, value: list[str], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_string(item)

    def write_byte_list(self, value: list[int], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_byte(item)

    def write_short_list(self, value: list[int], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_short(item)

    def read_bool(self) -> bool:
        return self.read_byte() != 0

    def write_bool(self, value: bool):
        self.write_byte(int(value))

    def read_int_tuple(self) -> tuple[int, int]:
        return self.read_int(), self.read_int()

    def write_int_tuple(self, value: tuple[int, int]):
        self.write_int(value[0])
        self.write_int(value[1])

    def read_int_tuple_list(
        self, length: Optional[int] = None
    ) -> list[tuple[int, int]]:
        if length is None:
            length = self.read_int()
        result: list[tuple[int, int]] = []
        for _ in range(length):
            result.append(self.read_int_tuple())
        return result

    def write_int_tuple_list(
        self, value: list[tuple[int, int]], write_length: bool = True
    ):
        if write_length:
            self.write_int(len(value))
        for item in value:
            self.write_int_tuple(item)

    def read_int_bool_dict(self, length: Optional[int] = None) -> dict[int, bool]:
        if length is None:
            length = self.read_int()
        result: dict[int, bool] = {}
        for _ in range(length):
            key = self.read_int()
            value = self.read_bool()
            result[key] = value
        return result

    def write_int_bool_dict(self, value: dict[int, bool], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for key, item in value.items():
            self.write_int(key)
            self.write_bool(item)

    def read_int_int_dict(self, length: Optional[int] = None) -> dict[int, int]:
        if length is None:
            length = self.read_int()
        result: dict[int, int] = {}
        for _ in range(length):
            key = self.read_int()
            value = self.read_int()
            result[key] = value
        return result

    def write_int_int_dict(self, value: dict[int, int], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for key, item in value.items():
            self.write_int(key)
            self.write_int(item)

    def read_int_double_dict(self, length: Optional[int] = None) -> dict[int, float]:
        if length is None:
            length = self.read_int()
        result: dict[int, float] = {}
        for _ in range(length):
            key = self.read_int()
            value = self.read_double()
            result[key] = value
        return result

    def write_int_double_dict(self, value: dict[int, float], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for key, item in value.items():
            self.write_int(key)
            self.write_double(item)

    def read_short_bool_dict(self, length: Optional[int] = None) -> dict[int, bool]:
        if length is None:
            length = self.read_int()
        result: dict[int, bool] = {}
        for _ in range(length):
            key = self.read_short()
            value = self.read_bool()
            result[key] = value
        return result

    def write_short_bool_dict(self, value: dict[int, bool], write_length: bool = True):
        if write_length:
            self.write_int(len(value))
        for key, item in value.items():
            self.write_short(key)
            self.write_bool(item)

    def pad_pkcs7(self, block_size: int = 16) -> "Data":
        pad = block_size - (len(self.data) % block_size)
        return Data(self.data + bytes([pad] * pad))

    def unpad_pkcs7(self) -> "Data":
        try:
            pad = self.data[-1]
        except IndexError:
            raise ValueError("Cannot unpad empty data")
        if pad > len(self.data):
            raise ValueError("Invalid padding")
        if self.data[-pad:] != bytes([pad] * pad):
            raise ValueError("Invalid padding")
        return Data(self.data[:-pad])

    def pad_zeroes(self, block_size: int = 16) -> "Data":
        pad = block_size - (len(self.data) % block_size)
        return Data(self.data + bytes([0] * pad))

    def unpad_zeroes(self) -> "Data":
        try:
            pad = self.data[-1]
        except IndexError:
            raise ValueError("Cannot unpad empty data")
        if pad > len(self.data):
            raise ValueError("Invalid padding")
        if self.data[-pad:] != bytes([0] * pad):
            raise ValueError("Invalid padding")
        return Data(self.data[:-pad])

    def pad(self, padding_type: "PaddingType", block_size: int = 16) -> "Data":
        if padding_type == PaddingType.PKCS7:
            return self.pad_pkcs7(block_size)
        elif padding_type == PaddingType.ZERO:
            return self.pad_zeroes(block_size)
        else:
            raise TypeError("Invalid padding type")

    def split(self, separator: bytes) -> list["Data"]:
        data_list: list[Data] = []
        for line in self.data.split(separator):
            data_list.append(Data(line))
        return data_list

    def to_int(self) -> int:
        return int(self.data.decode())

    def to_int_little(self) -> int:
        return int.from_bytes(self.data, "little")

    def to_str(self) -> str:
        return self.data.decode()

    def to_bool(self) -> bool:
        return bool(self.to_int())

    @staticmethod
    def int_list_data_list(int_list: list[int]) -> list["Data"]:
        data_list: list[Data] = []
        for integer in int_list:
            data_list.append(Data(str(integer)))
        return data_list

    @staticmethod
    def string_list_data_list(string_list: list[Any]) -> list["Data"]:
        data_list: list[Data] = []
        for string in string_list:
            data_list.append(Data(str(string)))
        return data_list

    @staticmethod
    def data_list_int_list(data_list: list["Data"]) -> list[int]:
        int_list: list[int] = []
        for data in data_list:
            int_list.append(data.to_int())
        return int_list

    @staticmethod
    def data_list_string_list(data_list: list["Data"]) -> list[str]:
        string_list: list[str] = []
        for data in data_list:
            string_list.append(data.to_str())
        return string_list

    def to_bytes(self) -> bytes:
        return self.data

    @staticmethod
    def from_many(others: list["Data"], joiner: Optional["Data"] = None) -> "Data":
        data_lst: list[bytes] = []
        for other in others:
            data_lst.append(other.data)
        if joiner is None:
            return Data(b"".join(data_lst))
        else:
            return Data(joiner.data.join(data_lst))

    @staticmethod
    def from_int_list(
        int_list: list[int], endianess: Literal["little", "big"]
    ) -> "Data":
        bytes_data = b""
        for integer in int_list:
            bytes_data += integer.to_bytes(4, endianess)
        return Data(bytes_data)

    def strip(self) -> "Data":
        return Data(self.data.strip())

    def replace(self, old_data: "Data", new_data: "Data") -> "Data":
        return Data(self.data.replace(old_data.data, new_data.data))

    def set(self, value: Union[bytes, str, None, int, bool]) -> None:
        self.data = Data(value).data

    def to_bytes_io(self) -> BytesIO:
        return BytesIO(self.data)

    def __repr__(self) -> str:
        return f"Data({self.data!r})"

    def __str__(self) -> str:
        return self.to_str()

    def to_base_64(self) -> str:
        return base64.b64encode(self.data).decode()

    @staticmethod
    def from_base_64(string: str) -> "Data":
        return Data(base64.b64decode(string))

    def to_csv(self, *args: Any, **kwargs: Any) -> "bc_csv.CSV":
        return bc_csv.CSV(self, *args, **kwargs)

    def search(self, search_data: "Data", start: int = 0) -> int:
        return self.data.find(search_data.data, start)


class PaddedInt:
    def __init__(self, value: int, size: int):
        self.value = value
        self.size = size

    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.value).zfill(self.size)

    def __repr__(self):
        return f"PaddedInt({self.value}, {self.size})"

    def to_str(self):
        return str(self)
