from __future__ import annotations
import csv as csv_module
import enum
from typing import Any
import typing
from bcsfe import core


class DelimeterType(enum.Enum):
    COMMA = ","
    TAB = "\t"
    PIPE = "|"


class Delimeter:
    def __init__(self, de: DelimeterType | str):
        if isinstance(de, str):
            self.delimiter = DelimeterType(de)
        else:
            self.delimiter = de

    @staticmethod
    def from_country_code_res(cc: core.CountryCode) -> Delimeter:
        if cc.get_cc_lang() == core.CountryCodeType.JP:
            return Delimeter(DelimeterType.COMMA)
        return Delimeter(DelimeterType.PIPE)

    def __str__(self) -> str:
        return self.delimiter.value


class Cell:
    def __init__(self, dt: core.Data):
        self.data = dt

    def to_str(self) -> str:
        return self.data.to_str()

    def to_int(self) -> int:
        return self.data.to_int()

    def to_bool(self) -> bool:
        return self.data.to_bool()

    def __repr__(self) -> str:
        return f"Cell({self.data})"

    def __str__(self) -> str:
        return self.data.to_str()


class Row:
    def __init__(self, cells: list[Cell]):
        self.cells = cells
        self.index = 0

    @typing.overload
    def __getitem__(self, index: int) -> Cell: ...

    @typing.overload
    def __getitem__(self, index: slice) -> Row: ...

    def __getitem__(self, index: int | slice) -> Cell | Row:
        if isinstance(index, int):
            try:
                return self.cells[index]
            except IndexError:
                return Cell(core.Data(""))
        try:
            return Row(self.cells[index])
        except IndexError:
            return Row([])

    def __len__(self) -> int:
        return len(self.cells)

    @staticmethod
    def from_list(dt: list[core.Data]) -> Row:
        cells: list[Cell] = []
        for item in dt:
            cells.append(Cell(item))
        return Row(cells)

    def __repr__(self) -> str:
        return f"Row({self.cells})"

    def __str__(self) -> str:
        return self.__repr__()

    def __iter__(self):
        self.index = 0
        return iter(self.cells)

    def __next__(self):
        if self.index >= len(self.cells):
            raise StopIteration
        else:
            self.index += 1
            return self.cells[self.index - 1]

    def next(self):
        return next(self)

    def next_opt(self) -> Cell | None:
        if self.done():
            return None
        return self.next()

    def done(self):
        return self.index >= len(self.cells)

    def next_int(self) -> int:
        return self.next().to_int()

    def next_str(self) -> str:
        return self.next().to_str()

    def next_bool(self) -> bool:
        return self.next().to_bool()

    def next_int_opt(self) -> int | None:
        val = self.next_opt()
        if val is None:
            return None
        return val.to_int()

    def next_str_opt(self) -> str | None:
        val = self.next_opt()
        if val is None:
            return None
        return val.to_str()

    def next_bool_opt(self) -> bool | None:
        val = self.next_opt()
        if val is None:
            return None
        return val.to_bool()

    def to_str_list(self) -> list[str]:
        return [cell.to_str() for cell in self.cells]

    def to_int_list(self) -> list[int]:
        return [cell.to_int() for cell in self.cells]


class CSV:
    def __init__(
        self,
        file_data: core.Data,
        delimiter: Delimeter | str = Delimeter(DelimeterType.COMMA),
        remove_padding: bool = True,
        remove_comments: bool = True,
        remove_empty: bool = True,
    ):
        self.file_data = file_data
        if remove_padding:
            data = self.file_data.unpad_pkcs7()
            if data is None:
                self.file_data = self.file_data
            else:
                self.file_data = data

        self.delimiter = delimiter
        self.remove_comments = remove_comments
        self.remove_empty = remove_empty
        self.index = 0
        self.parse()

    def parse(self):
        reader = csv_module.reader(
            self.file_data.data.decode("utf-8").splitlines(),
            delimiter=str(self.delimiter),
        )
        self.lines: list[Row] = []
        for row in reader:
            new_row: list[core.Data] = []
            full_row = f"{str(self.delimiter)}".join(row)
            if self.remove_comments:
                full_row = full_row.split("//")[0]
            row = full_row.split(str(self.delimiter))
            if row or not self.remove_empty:
                for item in row:
                    item = item.strip()
                    if item or not self.remove_empty:
                        new_row.append(core.Data(item))
                if new_row or not self.remove_empty:
                    self.lines.append(Row.from_list(new_row))

    def get_row(self, index: int) -> Row:
        try:
            return self.lines[index]
        except IndexError:
            return Row([])

    def __getitem__(self, index: int) -> Row:
        return self.get_row(index)

    def __len__(self) -> int:
        return len(self.lines)

    @staticmethod
    def from_file(
        pt: core.Path, delimiter: Delimeter = Delimeter(DelimeterType.COMMA)
    ) -> CSV:
        return CSV(pt.read(), delimiter)

    def add_line(self, line: list[Any] | Any):
        if not isinstance(line, list):
            line = [line]
        new_line: list[core.Data] = []
        for item in line:
            new_line.append(core.Data(str(item)))
        self.lines.append(Row.from_list(new_line))

    def set_line(self, index: int, line: list[Any]):
        new_line: list[core.Data] = []
        for item in line:
            new_line.append(core.Data(item))
        try:
            self.lines[index] = Row.from_list(new_line)
        except IndexError:
            self.lines.append(Row.from_list(new_line))

    def to_data(self) -> core.Data:
        csv: list[str] = []
        for line in self.lines:
            for i, item in enumerate(line):
                csv.append(str(item))
                if i != len(line) - 1:
                    csv.append(str(self.delimiter))
            csv.append("\r\n")
        return core.Data("".join(csv))

    def read_line(self) -> Row | None:
        try:
            line = self.lines[self.index]
        except IndexError:
            return None

        self.index += 1
        return line

    def reset_index(self):
        self.index = 0

    def has_line(self) -> bool:
        return self.index < len(self.lines)

    def __iter__(self):
        return self

    def __next__(self) -> Row:
        line = self.read_line()
        if line is None:
            raise StopIteration
        return line

    def extend(self, length: int, sub_length: int = 0):
        for _ in range(length):
            if sub_length == 0:
                self.lines.append(Row.from_list([]))
            else:
                self.lines.append(Row.from_list([core.Data("")] * sub_length))
