import enum
from typing import Optional, Union
from bcsfe.cli import dialog_creator


class CountryCodeType(enum.Enum):
    EN = "en"
    JP = "jp"
    KR = "kr"
    TW = "tw"


class CountryCode:
    def __init__(self, cc: Union[str, CountryCodeType]):
        self.value = cc.value if isinstance(cc, CountryCodeType) else cc
        self.value = self.value.lower()

    def get_code(self) -> str:
        return self.value

    def get_client_info_code(self) -> str:
        return self.get_code().replace("jp", "ja")

    def get_patching_code(self) -> str:
        return self.get_code().replace("jp", "")

    @staticmethod
    def from_patching_code(code: str) -> "CountryCode":
        if code == "":
            return CountryCode(CountryCodeType.JP)
        return CountryCode(code)

    @staticmethod
    def get_all() -> list["CountryCode"]:
        return [CountryCode(cc) for cc in CountryCodeType]

    @staticmethod
    def get_all_str() -> list[str]:
        ccts = CountryCode.get_all()
        return [cc.get_code() for cc in ccts]

    def __str__(self) -> str:
        return self.get_code()

    def __repr__(self) -> str:
        return self.get_code()

    def copy(self) -> "CountryCode":
        return self

    @staticmethod
    def select() -> Optional["CountryCode"]:
        index = dialog_creator.ChoiceInput(
            CountryCode.get_all_str(),
            CountryCode.get_all_str(),
            [],
            {},
            "country_code_select",
            True,
        ).get_input_locale_while()
        if index is None:
            return None
        index = index[0]
        return CountryCode.get_all()[index - 1]

    @staticmethod
    def select_from_ccs(ccs: list["CountryCode"]) -> Optional["CountryCode"]:
        index = dialog_creator.ChoiceInput(
            [cc.get_code() for cc in ccs],
            [cc.get_code() for cc in ccs],
            [],
            {},
            "country_code_select",
            True,
        ).get_input_locale_while()
        if not index:
            return None
        index = index[0]
        return ccs[index - 1]

    def __eq__(self, o: object) -> bool:
        if isinstance(o, CountryCode):
            return self.get_code() == o.get_code()
        elif isinstance(o, str):
            return self.get_code() == o
        elif isinstance(o, CountryCodeType):
            return self.get_code() == o.value
        return False
