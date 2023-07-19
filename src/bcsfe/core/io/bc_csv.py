import csv as csv_module
import enum
from typing import Any, Optional, Union
import typing
from bcsfe import core


class DelimeterType(enum.Enum):
    COMMA = ","
    TAB = "\t"
    PIPE = "|"


class Delimeter:
    def __init__(self, de: Union[DelimeterType, str]):
        if isinstance(de, str):
            self.delimeter = DelimeterType(de)
        else:
            self.delimeter = de

    @staticmethod
    def from_country_code_res(cc: "core.CountryCode") -> "Delimeter":
        if cc == core.CountryCodeType.JP:
            return Delimeter(DelimeterType.COMMA)
        else:
            return Delimeter(DelimeterType.PIPE)

    def __str__(self) -> str:
        return self.delimeter.value


class Cell:
    def __init__(self, dt: "core.Data"):
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
        return self.__repr__()


class Row:
    def __init__(self, cells: list[Cell]):
        self.cells = cells
        self.index = 0

    @typing.overload
    def __getitem__(self, index: int) -> Cell:
        ...

    @typing.overload
    def __getitem__(self, index: slice) -> list[Cell]:
        ...

    def __getitem__(self, index: Union[int, slice]) -> Union[Cell, list[Cell]]:
        try:
            return self.cells[index]
        except IndexError:
            return Cell(core.Data())

    def __len__(self) -> int:
        return len(self.cells)

    @staticmethod
    def from_list(dt: list["core.Data"]) -> "Row":
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

    def to_str_list(self) -> list[str]:
        return [cell.to_str() for cell in self.cells]

    def to_int_list(self) -> list[int]:
        return [cell.to_int() for cell in self.cells]


class CSV:
    def __init__(
        self,
        file_data: "core.Data",
        delimeter: Union[Delimeter, str] = Delimeter(DelimeterType.COMMA),
        remove_padding: bool = True,
        remove_comments: bool = True,
        remove_empty: bool = True,
    ):
        self.file_data = file_data
        if remove_padding:
            try:
                self.file_data = self.file_data.unpad_pkcs7()
            except ValueError:
                pass
        self.delimeter = delimeter
        self.remove_comments = remove_comments
        self.remove_empty = remove_empty
        self.index = 0
        self.parse()

    def parse(self):
        reader = csv_module.reader(
            self.file_data.data.decode("utf-8").splitlines(),
            delimiter=str(self.delimeter),
        )
        self.lines: list[Row] = []
        for row in reader:
            new_row: list["core.Data"] = []
            full_row = f"{str(self.delimeter)}".join(row)
            if self.remove_comments:
                full_row = full_row.split("//")[0]
            row = full_row.split(str(self.delimeter))
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

    @staticmethod
    def from_file(
        pt: "core.Path", delimeter: Delimeter = Delimeter(DelimeterType.COMMA)
    ) -> "CSV":
        return CSV(pt.read(), delimeter)

    def add_line(self, line: Union[list[Any], Any]):
        if not isinstance(line, list):
            line = [line]
        new_line: list["core.Data"] = []
        for item in line:
            new_line.append(core.Data(str(item)))
        self.lines.append(Row.from_list(new_line))

    def set_line(self, index: int, line: list[Any]):
        new_line: list["core.Data"] = []
        for item in line:
            new_line.append(core.Data(item))
        try:
            self.lines[index] = Row.from_list(new_line)
        except IndexError:
            self.lines.append(Row.from_list(new_line))

    def to_data(self) -> "core.Data":
        csv: list[str] = []
        for line in self.lines:
            for i, item in enumerate(line):
                csv.append(str(item))
                if i != len(line) - 1:
                    csv.append(str(self.delimeter))
            csv.append("\r\n")
        return core.Data("".join(csv))

    def read_line(self, lg: bool = False) -> Optional[Row]:
        if self.index >= len(self.lines):
            if lg:
                core.Logger().log_error("CSV read index out of range")
            return None
        line = self.lines[self.index]
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
