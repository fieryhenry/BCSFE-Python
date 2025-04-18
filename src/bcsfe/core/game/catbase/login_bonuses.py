from __future__ import annotations
from typing import Any
from bcsfe import core


class Login:
    def __init__(self, count: int):
        self.count = count

    @staticmethod
    def init() -> Login:
        return Login(0)

    @staticmethod
    def read(stream: core.Data) -> Login:
        count = stream.read_int()
        return Login(count)

    def write(self, stream: core.Data):
        stream.write_int(self.count)

    def serialize(self) -> int:
        return self.count

    @staticmethod
    def deserialize(data: int) -> Login:
        return Login(data)

    def __repr__(self):
        return f"Login({self.count})"

    def __str__(self):
        return f"Login({self.count})"


class Logins:
    def __init__(self, logins: list[Login]):
        self.logins = logins

    @staticmethod
    def init() -> Logins:
        return Logins([])

    @staticmethod
    def read(stream: core.Data) -> Logins:
        total = stream.read_int()
        logins: list[Login] = []
        for _ in range(total):
            logins.append(Login.read(stream))
        return Logins(logins)

    def write(self, stream: core.Data):
        stream.write_int(len(self.logins))
        for login in self.logins:
            login.write(stream)

    def serialize(self) -> list[int]:
        return [login.serialize() for login in self.logins]

    @staticmethod
    def deserialize(data: list[int]) -> Logins:
        return Logins([Login.deserialize(login) for login in data])

    def __repr__(self):
        return f"Logins({self.logins})"

    def __str__(self):
        return f"Logins({self.logins})"


class LoginSets:
    def __init__(self, logins: list[Logins]):
        self.logins = logins

    @staticmethod
    def init() -> LoginSets:
        return LoginSets([])

    @staticmethod
    def read(stream: core.Data) -> LoginSets:
        total = stream.read_int()
        logins: list[Logins] = []
        for _ in range(total):
            logins.append(Logins.read(stream))
        return LoginSets(logins)

    def write(self, stream: core.Data):
        stream.write_int(len(self.logins))
        for login in self.logins:
            login.write(stream)

    def serialize(self) -> list[list[int]]:
        return [login.serialize() for login in self.logins]

    @staticmethod
    def deserialize(data: list[list[int]]) -> LoginSets:
        return LoginSets([Logins.deserialize(login) for login in data])

    def __repr__(self):
        return f"LoginSets({self.logins})"

    def __str__(self):
        return f"LoginSets({self.logins})"


class LoginBonus:
    def __init__(
        self,
        old_logins: LoginSets | None = None,
        logins: dict[int, Login] | None = None,
    ):
        self.old_logins = old_logins
        self.logins = logins

    @staticmethod
    def init(gv: core.GameVersion) -> LoginBonus:
        if gv < 80000:
            return LoginBonus(old_logins=LoginSets.init())
        else:
            return LoginBonus(logins={})

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> LoginBonus:
        if gv < 80000:
            logins_old = LoginSets.read(stream)
            return LoginBonus(logins_old)
        else:
            total = stream.read_int()
            logins: dict[int, Login] = {}
            for _ in range(total):
                id = stream.read_int()
                logins[id] = Login.read(stream)
            return LoginBonus(logins=logins)

    def write(self, stream: core.Data, gv: core.GameVersion):
        if gv < 80000 and self.old_logins is not None:
            self.old_logins.write(stream)
        elif gv >= 80000 and self.logins is not None:
            stream.write_int(len(self.logins))
            for id, login in self.logins.items():
                stream.write_int(id)
                login.write(stream)

    def serialize(
        self,
    ) -> dict[str, Any]:
        if self.old_logins is not None:
            return {"old_logins": self.old_logins.serialize()}
        elif self.logins is not None:
            return {
                "logins": {
                    id: login.serialize() for id, login in self.logins.items()
                }
            }
        else:
            return {}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> LoginBonus:
        if "old_logins" in data:
            return LoginBonus(
                old_logins=LoginSets.deserialize(data["old_logins"])
            )
        elif "logins" in data:
            return LoginBonus(
                logins={
                    int(id): Login.deserialize(login)
                    for id, login in data["logins"].items()
                }
            )
        else:
            return LoginBonus()

    def __repr__(self):
        return f"LoginBonus({self.old_logins}, {self.logins})"

    def __str__(self):
        return f"LoginBonus({self.old_logins}, {self.logins})"

    def get_login(self, id: int) -> Login | None:
        if self.logins is not None:
            return self.logins.get(id)
        else:
            return None
