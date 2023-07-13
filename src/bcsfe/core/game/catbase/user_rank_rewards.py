from bcsfe import core


class Reward:
    def __init__(self, claimed: bool):
        self.claimed = claimed

    @staticmethod
    def init() -> "Reward":
        return Reward(False)

    @staticmethod
    def read(stream: "core.Data") -> "Reward":
        return Reward(stream.read_bool())

    def write(self, stream: "core.Data"):
        stream.write_bool(self.claimed)

    def serialize(self) -> bool:
        return self.claimed

    @staticmethod
    def deserialize(data: bool) -> "Reward":
        return Reward(data)

    def __repr__(self) -> str:
        return f"Reward(claimed={self.claimed})"

    def __str__(self) -> str:
        return self.__repr__()


class UserRankRewards:
    def __init__(self, rewards: list[Reward]):
        self.rewards = rewards

    @staticmethod
    def init(gv: "core.GameVersion") -> "UserRankRewards":
        if gv >= 30:
            total = 0
        else:
            total = 50
        rewards = [Reward.init() for _ in range(total)]
        return UserRankRewards(rewards)

    @staticmethod
    def read(stream: "core.Data", gv: "core.GameVersion") -> "UserRankRewards":
        if gv >= 30:
            total = stream.read_int()
        else:
            total = 50
        rewards: list[Reward] = []
        for _ in range(total):
            rewards.append(Reward.read(stream))
        return UserRankRewards(rewards)

    def write(self, stream: "core.Data", gv: "core.GameVersion"):
        if gv >= 30:
            stream.write_int(len(self.rewards))
        for reward in self.rewards:
            reward.write(stream)

    def serialize(self) -> list[bool]:
        return [reward.serialize() for reward in self.rewards]

    @staticmethod
    def deserialize(data: list[bool]) -> "UserRankRewards":
        return UserRankRewards([Reward.deserialize(reward) for reward in data])

    def __repr__(self) -> str:
        return f"Rewards(rewards={self.rewards})"

    def __str__(self) -> str:
        return self.__repr__()
