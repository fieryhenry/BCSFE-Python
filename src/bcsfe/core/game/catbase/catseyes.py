from bcsfe.core import io


class Catsye:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(stream: io.data.Data) -> "Catsye":
        amount = stream.read_int()
        return Catsye(amount)

    def write(self, stream: io.data.Data):
        stream.write_int(self.amount)

    def serialize(self) -> dict[str, int]:
        return {"amount": self.amount}

    @staticmethod
    def deserialize(data: dict[str, int]) -> "Catsye":
        return Catsye(data["amount"])

    def __repr__(self):
        return f"Catsye({self.amount})"

    def __str__(self):
        return f"Catsye({self.amount})"


class Catseyes:
    def __init__(self, catseyes: list[Catsye]):
        self.catseyes = catseyes

    @staticmethod
    def read(stream: io.data.Data) -> "Catseyes":
        total = stream.read_int()
        catseyes: list[Catsye] = []
        for _ in range(total):
            catseyes.append(Catsye.read(stream))
        return Catseyes(catseyes)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.catseyes))
        for catseye in self.catseyes:
            catseye.write(stream)

    def serialize(self) -> dict[str, list[dict[str, int]]]:
        return {"catseyes": [catseye.serialize() for catseye in self.catseyes]}

    @staticmethod
    def deserialize(data: dict[str, list[dict[str, int]]]) -> "Catseyes":
        return Catseyes([Catsye.deserialize(catseye) for catseye in data["catseyes"]])

    def __repr__(self):
        return f"Catsyes({self.catseyes})"

    def __str__(self):
        return f"Catsyes({self.catseyes})"
