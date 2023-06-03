from bcsfe.core.game.catbase import upgrade
from bcsfe.core import io

from typing import Any


class Skill:
    def __init__(self, upgrade: upgrade.Upgrade):
        self.upgrade = upgrade

    @staticmethod
    def read_upgrade(stream: io.data.Data) -> "Skill":
        up = upgrade.Upgrade.read(stream)
        return Skill(up)

    def write_upgrade(self, stream: io.data.Data):
        self.upgrade.write(stream)

    def read_seen(self, stream: io.data.Data):
        self.seen = stream.read_int()

    def write_seen(self, stream: io.data.Data):
        stream.write_int(self.seen)

    def read_max_upgrade_level(self, stream: io.data.Data):
        level = upgrade.Upgrade.read(stream)
        self.max_upgrade_level = level

    def write_max_upgrade_level(self, stream: io.data.Data):
        self.max_upgrade_level.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "upgrade": self.upgrade.serialize(),
            "seen": self.seen,
            "max_upgrade_level": self.max_upgrade_level.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Skill":
        skill = Skill(upgrade.Upgrade.deserialize(data["upgrade"]))
        skill.seen = data["seen"]
        skill.max_upgrade_level = upgrade.Upgrade.deserialize(data["max_upgrade_level"])
        return skill

    def __repr__(self) -> str:
        return f"Skill(upgrade={self.upgrade}, seen={self.seen}, max_upgrade_level={self.max_upgrade_level})"

    def __str__(self) -> str:
        return self.__repr__()


class Skills:
    def __init__(self, skills: list[Skill]):
        self.skills = skills

    def get_valid_skills(self) -> list[Skill]:
        new_skills: list[Skill] = []
        for i, skill in enumerate(self.skills):
            if i == 1:
                continue
            new_skills.append(skill)

        return new_skills

    @staticmethod
    def read_upgrades(stream: io.data.Data) -> "Skills":
        total_skills = 11

        skills: list[Skill] = []
        for _ in range(total_skills):
            skills.append(Skill.read_upgrade(stream))

        return Skills(skills)

    def write_upgrades(self, stream: io.data.Data):
        for skill in self.skills:
            skill.write_upgrade(stream)

    def read_gatya_seen(self, stream: io.data.Data):
        for skill in self.get_valid_skills():
            skill.read_seen(stream)

    def write_gatya_seen(self, stream: io.data.Data):
        for skill in self.get_valid_skills():
            skill.write_seen(stream)

    def read_max_upgrade_levels(self, stream: io.data.Data):
        for skill in self.skills:
            skill.read_max_upgrade_level(stream)

    def write_max_upgrade_levels(self, stream: io.data.Data):
        for skill in self.skills:
            skill.write_max_upgrade_level(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "skills": [skill.serialize() for skill in self.skills],
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Skills":
        skills = Skills([])
        for skill in data["skills"]:
            skills.skills.append(Skill.deserialize(skill))

        return skills

    def __repr__(self) -> str:
        return f"Skills(skills={self.skills})"

    def __str__(self) -> str:
        return f"Skills(skills={self.skills})"
