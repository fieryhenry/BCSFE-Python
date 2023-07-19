from typing import Optional

from bcsfe import core


class PowerUpHelper:
    def __init__(self, cat: "core.Cat", save_file: "core.SaveFile"):
        self.cat = cat
        self.save_file = save_file
        self.unit_limit = self.save_file.cats.read_unitlimit(
            self.save_file
        ).get_unit_limit(self.cat.id)
        self.unit_buy = self.save_file.cats.read_unitbuy(self.save_file).get_unit_buy(
            self.cat.id
        )
        self.rank_gifts = self.save_file.user_rank_rewards.read_rank_gifts(
            self.save_file
        )

    def get_current_max_level(self) -> Optional[int]:
        if self.unit_buy is None:
            return None
        return min(
            self.unit_buy.original_max_levels[0] + self.get_max_upgrade_level_check(),
            self.unit_buy.max_upgrade_level_catseye,
        )

    def has_strict_upgrade(self) -> bool:
        return core.config.get_bool(core.ConfigKey.STRICT_UPGRADE)

    def get_upgrade_state_check(self) -> int:
        if not self.has_strict_upgrade():
            return 100000
        return self.save_file.upgrade_state

    def get_user_rank_check(self) -> int:
        if not self.has_strict_upgrade():
            return 1000000
        return self.save_file.calculate_user_rank()

    def get_max_upgrade_level_check(self) -> int:
        if self.unit_limit is None:
            return self.cat.max_upgrade_level.base

        rewards = self.save_file.user_rank_rewards
        self.cat.max_upgrade_level.base = 0

        strict_upgrade = self.has_strict_upgrade()

        for reward_id in range(len(rewards.rewards)):
            rank_gift = self.rank_gifts.get_by_id(reward_id)
            if rank_gift is None:
                continue
            user_rank_reward = rewards.rewards[reward_id]
            if not user_rank_reward.claimed and strict_upgrade:
                continue
            for present in rank_gift.rewards:
                if present[0] >= 1000 and present[0] <= 1599:
                    for limit in self.unit_limit.values:
                        if limit == present[0]:
                            self.cat.max_upgrade_level.increment_base(present[1])

        return self.cat.max_upgrade_level.base

    def can_power_up(self) -> bool:
        if self.unit_buy is None:
            return False
        base_level = self.cat.upgrade.get_base()
        current_max_level = self.get_current_max_level()
        if current_max_level is None:
            return False

        if base_level >= current_max_level or (
            (
                self.get_upgrade_state_check() > 1
                or base_level == self.unit_buy.unknown_22
            )
            and self.get_upgrade_state_check() < 2
        ):
            return (
                self.unit_buy.rarity != 0
                and base_level >= self.unit_buy.max_upgrade_level_no_catseye
                and base_level < self.unit_buy.max_upgrade_level_catseye
                and base_level < current_max_level
            )
        return True

    def can_use_catseye(self) -> bool:
        if self.unit_buy is None:
            return False

        base_level = self.cat.upgrade.get_base()
        return (
            self.unit_buy.rarity != 0
            and base_level >= self.unit_buy.max_upgrade_level_no_catseye
            and self.unit_buy.max_upgrade_level_no_catseye != -1
            and self.get_user_rank_check() >= 1600
        )

    def upgrade_cat(self, force: bool = False) -> bool:
        if force:
            self.cat.upgrade.upgrade()
            return True
        if self.unit_buy is None:
            return False
        current_max_level = self.get_current_max_level()
        if current_max_level is None:
            return False

        if self.can_power_up():
            self.cat.upgrade.upgrade()
            return True

        if (
            self.can_use_catseye()
            and self.unit_buy.max_upgrade_level_no_catseye <= current_max_level
        ):
            if self.cat.upgrade.get_base() < self.unit_buy.max_upgrade_level_catseye:
                self.cat.upgrade.upgrade()
                self.cat.catseyes_used += 1
                self.cat.max_upgrade_level.upgrade()
                return True
            return False
        return False

    def reset_upgrade(self):
        self.cat.upgrade.base = 0
        self.cat.catseyes_used = 0

    def upgrade_by(self, amount: int):
        for _ in range(amount):
            did_upgrade = self.upgrade_cat()
            if not did_upgrade:
                break

    def max_upgrade(self):
        while self.upgrade_cat():
            pass
