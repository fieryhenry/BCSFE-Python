from bcsfe.core import io


class Fruit:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def read(stream: io.data.Data) -> "Fruit":
        amount = stream.read_int()
        return Fruit(amount)

    def write(self, stream: io.data.Data):
        stream.write_int(self.amount)

    def serialize(self) -> dict[str, int]:
        return {"amount": self.amount}

    @staticmethod
    def deserialize(data: dict[str, int]) -> "Fruit":
        return Fruit(data["amount"])

    def __repr__(self):
        return f"Fruit({self.amount})"

    def __str__(self):
        return f"Fruit({self.amount})"


class Matatabi:
    def __init__(self, fruits: list[Fruit]):
        self.fruits = fruits

    @staticmethod
    def read(stream: io.data.Data) -> "Matatabi":
        total = stream.read_int()
        fruits: list[Fruit] = []
        for _ in range(total):
            fruits.append(Fruit.read(stream))
        return Matatabi(fruits)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.fruits))
        for fruit in self.fruits:
            fruit.write(stream)

    def serialize(self) -> dict[str, list[dict[str, int]]]:
        return {"fruits": [fruit.serialize() for fruit in self.fruits]}

    @staticmethod
    def deserialize(data: dict[str, list[dict[str, int]]]) -> "Matatabi":
        return Matatabi([Fruit.deserialize(fruit) for fruit in data["fruits"]])

    def __repr__(self):
        return f"Matatabi({self.fruits})"

    def __str__(self):
        return f"Matatabi({self.fruits})"
