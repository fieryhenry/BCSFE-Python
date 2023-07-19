from typing import Optional
from bcsfe import core


class RankGift:
    def __init__(self, threshold: int, rewards: list[tuple[int, int]]):
        self.threshold = threshold
        self.rewards = rewards


class RankGifts:
    def __init__(self, save_file: "core.SaveFile"):
        self.save_file = save_file
        self.rank_gift = self.read_rank_gift()

    def read_rank_gift(self) -> list[RankGift]:
        rank_gift: list[RankGift] = []
        gdg = core.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "rankGift.csv")
        if data is None:
            return rank_gift
        csv = core.CSV(data)
        for line in csv:
            rewards: list[tuple[int, int]] = []
            for col in range(1, len(line), 2):
                value = line[col].to_int()
                if value == -1:
                    break
                rewards.append((value, line[col + 1].to_int()))
            rank_gift.append(RankGift(line[0].to_int(), rewards))
        return rank_gift

    def get_rank_gift(self, user_rank: int) -> RankGift:
        for rank_gift in self.rank_gift:
            if rank_gift.threshold == user_rank:
                return rank_gift
        raise ValueError(f"RankGift not found for rank {user_rank}")

    def get_all_rank_gifts(self, user_rank: int) -> list[RankGift]:
        return [
            rank_gift
            for rank_gift in self.rank_gift
            if rank_gift.threshold <= user_rank
        ]

    def get_by_id(self, id: int) -> Optional[RankGift]:
        if id >= len(self.rank_gift) or id < 0:
            return None
        return self.rank_gift[id]


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
        self.rank_gifts: Optional[RankGifts] = None

    def read_rank_gifts(self, save_file: "core.SaveFile") -> RankGifts:
        if self.rank_gifts is None:
            self.rank_gifts = RankGifts(save_file)
        return self.rank_gifts

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
