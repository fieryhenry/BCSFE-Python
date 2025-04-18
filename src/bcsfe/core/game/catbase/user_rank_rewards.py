from __future__ import annotations
from bcsfe import core
from bcsfe.cli import dialog_creator, color


class RankGift:
    def __init__(
        self, index: int, threshold: int, rewards: list[tuple[int, int]]
    ):
        self.index = index
        self.threshold = threshold
        self.rewards = rewards

    def get_name(
        self, rank_gift_descriptions: RankGiftDescriptions
    ) -> str | None:
        return rank_gift_descriptions.get_name(self.threshold)


class RankGifts:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.rank_gift = self.read_rank_gift()

    def read_rank_gift(self) -> list[RankGift] | None:
        rank_gift: list[RankGift] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("DataLocal", "rankGift.csv")
        if data is None:
            return None
        csv = core.CSV(data)
        for i, line in enumerate(csv):
            rewards: list[tuple[int, int]] = []
            for col in range(1, len(line), 2):
                value = line[col].to_int()
                if value == -1:
                    break
                rewards.append((value, line[col + 1].to_int()))
            rank_gift.append(RankGift(i, line[0].to_int(), rewards))
        return rank_gift

    def get_rank_gift(self, user_rank: int) -> RankGift | None:
        if self.rank_gift is None:
            return None
        for rank_gift in self.rank_gift:
            if rank_gift.threshold == user_rank:
                return rank_gift
        return None

    def get_all_rank_gifts(self, user_rank: int) -> list[RankGift] | None:
        if self.rank_gift is None:
            return None
        return [
            rank_gift
            for rank_gift in self.rank_gift
            if rank_gift.threshold <= user_rank
        ]

    def get_by_id(self, id: int) -> RankGift | None:
        if self.rank_gift is None:
            return None
        if id >= len(self.rank_gift) or id < 0:
            return None
        return self.rank_gift[id]

    def get_all_unlocked(self, user_rank: int) -> list[RankGift] | None:
        if self.rank_gift is None:
            return None

        return [
            rank_gift
            for rank_gift in self.rank_gift
            if rank_gift.threshold <= user_rank
        ]


class RankGiftDescription:
    def __init__(self, index: int, threshold: int, description: str):
        self.index = index
        self.threshold = threshold
        self.description = description


class RankGiftDescriptions:
    def __init__(self, save_file: core.SaveFile):
        self.save_file = save_file
        self.rank_gift_descriptions = self.read_rank_gift_descriptions()

    def read_rank_gift_descriptions(self) -> list[RankGiftDescription] | None:
        rank_gift_descriptions: list[RankGiftDescription] = []
        gdg = core.core_data.get_game_data_getter(self.save_file)
        data = gdg.download("resLocal", "user_info.tsv")
        if data is None:
            return None
        csv = core.CSV(data, delimiter="\t")
        for i, line in enumerate(csv):
            rank_gift_descriptions.append(
                RankGiftDescription(i, line[0].to_int(), line[1].to_str())
            )
        return rank_gift_descriptions

    def get_name(self, user_rank: int) -> str | None:
        if self.rank_gift_descriptions is None:
            return None
        for rank_gift_description in self.rank_gift_descriptions:
            if rank_gift_description.threshold == user_rank:
                return rank_gift_description.description
        return None


class Reward:
    def __init__(self, claimed: bool):
        self.claimed = claimed

    @staticmethod
    def init() -> Reward:
        return Reward(False)

    @staticmethod
    def read(stream: core.Data) -> Reward:
        return Reward(stream.read_bool())

    def write(self, stream: core.Data):
        stream.write_bool(self.claimed)

    def serialize(self) -> bool:
        return self.claimed

    @staticmethod
    def deserialize(data: bool) -> Reward:
        return Reward(data)

    def __repr__(self) -> str:
        return f"Reward(claimed={self.claimed})"

    def __str__(self) -> str:
        return self.__repr__()


class UserRankRewards:
    def __init__(self, rewards: list[Reward]):
        self.rewards = rewards
        self.rank_gifts: RankGifts | None = None

    def read_rank_gifts(self, save_file: core.SaveFile) -> RankGifts:
        if self.rank_gifts is None:
            self.rank_gifts = RankGifts(save_file)
        return self.rank_gifts

    @staticmethod
    def init(gv: core.GameVersion) -> UserRankRewards:
        if gv >= 30:
            total = 0
        else:
            total = 50
        rewards = [Reward.init() for _ in range(total)]
        return UserRankRewards(rewards)

    @staticmethod
    def read(stream: core.Data, gv: core.GameVersion) -> UserRankRewards:
        if gv >= 30:
            total = stream.read_int()
        else:
            total = 50
        rewards: list[Reward] = []
        for _ in range(total):
            rewards.append(Reward.read(stream))
        return UserRankRewards(rewards)

    def write(self, stream: core.Data, gv: core.GameVersion):
        if gv >= 30:
            stream.write_int(len(self.rewards))
        for reward in self.rewards:
            reward.write(stream)

    def serialize(self) -> list[bool]:
        return [reward.serialize() for reward in self.rewards]

    @staticmethod
    def deserialize(data: list[bool]) -> UserRankRewards:
        return UserRankRewards([Reward.deserialize(reward) for reward in data])

    def __repr__(self) -> str:
        return f"Rewards(rewards={self.rewards})"

    def __str__(self) -> str:
        return self.__repr__()

    def set_claimed(self, index: int, claimed: bool):
        self.rewards[index].claimed = claimed

    def edit(self, save_file: core.SaveFile):
        claim_choice = dialog_creator.ChoiceInput.from_reduced(
            ["claim", "unclaim", "fix_claimed"],
            dialog="claim_or_unclaim_ur",
            single_choice=True,
        ).single_choice()

        if claim_choice is None:
            return

        claim_choice -= 1

        rank_gifts = core.core_data.get_rank_gifts(save_file)
        if rank_gifts.rank_gift is None:
            return

        user_rank = save_file.calculate_user_rank()

        if claim_choice == 2:
            for rank_gift in rank_gifts.rank_gift:
                reward = self.rewards[rank_gift.index]
                if rank_gift.threshold > user_rank:
                    reward.claimed = False

            color.ColoredText.localize("ur_fix_claimed_success")
            return

        selected_rank_gifts: list[RankGift] = rank_gifts.rank_gift.copy()
        descriptions = core.core_data.get_rank_gift_descriptions(save_file)

        selected_rank_gifts.sort(key=lambda rank_gift: rank_gift.threshold)

        new_selected_rank_gifts: list[RankGift] = []

        for rank_gift in selected_rank_gifts:
            reward = self.rewards[rank_gift.index]
            if reward.claimed and claim_choice == 0:
                continue
            if not reward.claimed and claim_choice == 1:
                continue
            if rank_gift.threshold > user_rank:
                continue
            new_selected_rank_gifts.append(rank_gift)

        selected_rank_gifts = new_selected_rank_gifts

        selected_descriptions: list[str] = []
        for rank_gift in selected_rank_gifts:
            name = rank_gift.get_name(descriptions)
            if name is None:
                return
            description = name.replace("<br>", " ")
            # remove span tags
            start = description.find("<")
            while start != -1:
                end = description.find(">")
                description = description[:start] + description[end + 1 :]
                start = description.find("<")

            selected_descriptions.append(
                core.core_data.local_manager.get_key(
                    "ur_string",
                    description=description,
                    rank=rank_gift.threshold,
                )
            )

        ids, _ = dialog_creator.ChoiceInput.from_reduced(
            selected_descriptions, dialog="select_ur"
        ).multiple_choice(localized_options=False)
        if ids is None:
            return
        for id in ids:
            index = selected_rank_gifts[id].index
            self.set_claimed(index, claim_choice == 0)

        if claim_choice == 0:
            color.ColoredText.localize("ur_claimed_success")
        else:
            color.ColoredText.localize("ur_unclaimed_success")


def edit_user_rank_rewards(save_file: core.SaveFile):
    user_rank_rewards = save_file.user_rank_rewards
    user_rank_rewards.edit(save_file)
