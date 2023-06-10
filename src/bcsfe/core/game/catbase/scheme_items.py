from bcsfe.core import io


class SchemeItems:
    def __init__(self, to_obtain: list[int], received: list[int]):
        self.to_obtain = to_obtain
        self.received = received

    @staticmethod
    def init() -> "SchemeItems":
        return SchemeItems([], [])

    @staticmethod
    def read(stream: io.data.Data) -> "SchemeItems":
        total = stream.read_int()
        to_obtain: list[int] = []
        for _ in range(total):
            to_obtain.append(stream.read_int())

        total = stream.read_int()
        received: list[int] = []
        for _ in range(total):
            received.append(stream.read_int())

        return SchemeItems(to_obtain, received)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.to_obtain))
        for item in self.to_obtain:
            stream.write_int(item)

        stream.write_int(len(self.received))
        for item in self.received:
            stream.write_int(item)

    def serialize(self) -> dict[str, list[int]]:
        return {"to_obtain": self.to_obtain, "received": self.received}

    @staticmethod
    def deserialize(data: dict[str, list[int]]) -> "SchemeItems":
        return SchemeItems(data.get("to_obtain", []), data.get("received", []))

    def __repr__(self) -> str:
        return f"SchemeItems(to_obtain={self.to_obtain!r}, received={self.received!r})"

    def __str__(self) -> str:
        return self.__repr__()
