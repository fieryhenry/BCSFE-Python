from typing import Any
from bcsfe.core import io


class Popup:
    def __init__(self, seen: bool):
        self.seen = seen

    @staticmethod
    def read(stream: io.data.Data) -> "Popup":
        seen = stream.read_bool()
        return Popup(seen)

    def write(self, stream: io.data.Data):
        stream.write_bool(self.seen)

    def serialize(self) -> dict[str, Any]:
        return {"seen": self.seen}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Popup":
        return Popup(data["seen"])

    def __repr__(self) -> str:
        return f"Popup(seen={self.seen!r})"

    def __str__(self) -> str:
        return self.__repr__()


class Popups:
    def __init__(self, popups: dict[int, Popup]):
        self.popups = popups

    @staticmethod
    def read(stream: io.data.Data) -> "Popups":
        total = stream.read_int()
        popups: dict[int, Popup] = {}
        for _ in range(total):
            key = stream.read_int()
            popups[key] = Popup.read(stream)
        return Popups(popups)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.popups))
        for key, popup in self.popups.items():
            stream.write_int(key)
            popup.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "popups": {key: popup.serialize() for key, popup in self.popups.items()},
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Popups":
        return Popups(
            {
                int(key): Popup.deserialize(popup)
                for key, popup in data["popups"].items()
            }
        )

    def __repr__(self) -> str:
        return f"Popups(popups={self.popups!r})"

    def __str__(self) -> str:
        return self.__repr__()
