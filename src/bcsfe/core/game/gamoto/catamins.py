from bcsfe.core import io


class Catamin:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(stream: io.data.Data) -> "Catamin":
        amount = stream.read_int()
        return Catamin(amount)

    def write(self, stream: io.data.Data):
        stream.write_int(self.amount)

    def serialize(self) -> dict[str, int]:
        return {"amount": self.amount}

    @staticmethod
    def deserialize(data: dict[str, int]) -> "Catamin":
        return Catamin(data["amount"])

    def __repr__(self):
        return f"Catamin({self.amount})"

    def __str__(self):
        return f"Catamin({self.amount})"


class Catamins:
    def __init__(self, catamins: list[Catamin]):
        self.catamins = catamins

    @staticmethod
    def read(stream: io.data.Data) -> "Catamins":
        total = stream.read_int()
        catamins: list[Catamin] = []
        for _ in range(total):
            catamins.append(Catamin.read(stream))
        return Catamins(catamins)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.catamins))
        for catamin in self.catamins:
            catamin.write(stream)

    def serialize(self) -> dict[str, list[dict[str, int]]]:
        return {"catamins": [catamin.serialize() for catamin in self.catamins]}

    @staticmethod
    def deserialize(data: dict[str, list[dict[str, int]]]) -> "Catamins":
        return Catamins([Catamin.deserialize(catamin) for catamin in data["catamins"]])

    def __repr__(self):
        return f"Catamins({self.catamins})"

    def __str__(self):
        return f"Catamins({self.catamins})"
