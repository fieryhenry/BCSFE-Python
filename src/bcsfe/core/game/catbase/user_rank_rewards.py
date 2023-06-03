from typing import Any
from bcsfe.core import game_version, io


class Reward:
    def __init__(self, claimed: bool):
        self.claimed = claimed

    @staticmethod
    def read(stream: io.data.Data) -> "Reward":
        return Reward(stream.read_bool())

    def write(self, stream: io.data.Data):
        stream.write_bool(self.claimed)

    def serialize(self) -> dict[str, Any]:
        return {"claimed": self.claimed}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Reward":
        return Reward(data["claimed"])

    def __repr__(self) -> str:
        return f"Reward(claimed={self.claimed})"

    def __str__(self) -> str:
        return self.__repr__()


class Rewards:
    def __init__(self, rewards: list[Reward]):
        self.rewards = rewards

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "Rewards":
        if gv >= 30:
            total = stream.read_int()
        else:
            total = 50
        rewards: list[Reward] = []
        for _ in range(total):
            rewards.append(Reward.read(stream))
        return Rewards(rewards)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv >= 30:
            stream.write_int(len(self.rewards))
        for reward in self.rewards:
            reward.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {"rewards": [reward.serialize() for reward in self.rewards]}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Rewards":
        return Rewards([Reward.deserialize(reward) for reward in data["rewards"]])

    def __repr__(self) -> str:
        return f"Rewards(rewards={self.rewards})"

    def __str__(self) -> str:
        return self.__repr__()
