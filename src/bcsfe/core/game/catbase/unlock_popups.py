from __future__ import annotations
from bcsfe import core


class Popup:
    def __init__(self, seen: bool):
        self.seen = seen

    @staticmethod
    def init() -> Popup:
        return Popup(False)

    @staticmethod
    def read(stream: core.Data) -> Popup:
        seen = stream.read_bool()
        return Popup(seen)

    def write(self, stream: core.Data):
        stream.write_bool(self.seen)

    def serialize(self) -> bool:
        return self.seen

    @staticmethod
    def deserialize(data: bool) -> Popup:
        return Popup(data)

    def __repr__(self) -> str:
        return f"Popup(seen={self.seen!r})"

    def __str__(self) -> str:
        return self.__repr__()


class UnlockPopups:
    def __init__(self, popups: dict[int, Popup]):
        self.popups = popups

    @staticmethod
    def init() -> UnlockPopups:
        return UnlockPopups({})

    @staticmethod
    def read(stream: core.Data) -> UnlockPopups:
        total = stream.read_int()
        popups: dict[int, Popup] = {}
        for _ in range(total):
            key = stream.read_int()
            popups[key] = Popup.read(stream)
        return UnlockPopups(popups)

    def write(self, stream: core.Data):
        stream.write_int(len(self.popups))
        for key, popup in self.popups.items():
            stream.write_int(key)
            popup.write(stream)

    def serialize(self) -> dict[int, bool]:
        return {key: popup.serialize() for key, popup in self.popups.items()}

    @staticmethod
    def deserialize(data: dict[int, bool]) -> UnlockPopups:
        return UnlockPopups(
            {int(key): Popup.deserialize(popup) for key, popup in data.items()}
        )

    def __repr__(self) -> str:
        return f"Popups(popups={self.popups!r})"

    def __str__(self) -> str:
        return self.__repr__()
