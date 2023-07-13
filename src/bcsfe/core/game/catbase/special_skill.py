from bcsfe import core

from typing import Any


class Skill:
    def __init__(self, upg: "core.Upgrade"):
        self.upgrade = upg
        self.seen = 0
        self.max_upgrade_level = core.Upgrade(0, 0)

    @staticmethod
    def init() -> "Skill":
        return Skill(core.Upgrade(0, 0))

    @staticmethod
    def read_upgrade(stream: "core.Data") -> "Skill":
        up = core.Upgrade.read(stream)
        return Skill(up)

    def write_upgrade(self, stream: "core.Data"):
        self.upgrade.write(stream)

    def read_seen(self, stream: "core.Data"):
        self.seen = stream.read_int()

    def write_seen(self, stream: "core.Data"):
        stream.write_int(self.seen)

    def read_max_upgrade_level(self, stream: "core.Data"):
        level = core.Upgrade.read(stream)
        self.max_upgrade_level = level

    def write_max_upgrade_level(self, stream: "core.Data"):
        self.max_upgrade_level.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "upgrade": self.upgrade.serialize(),
            "seen": self.seen,
            "max_upgrade_level": self.max_upgrade_level.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Skill":
        skill = Skill(core.Upgrade.deserialize(data.get("upgrade", {})))
        skill.seen = data.get("seen", 0)
        skill.max_upgrade_level = core.Upgrade.deserialize(
            data.get("max_upgrade_level", {})
        )
        return skill

    def __repr__(self) -> str:
        return f"Skill(upgrade={self.upgrade}, seen={self.seen}, max_upgrade_level={self.max_upgrade_level})"

    def __str__(self) -> str:
        return self.__repr__()


class SpecialSkills:
    def __init__(self, skills: list[Skill]):
        self.skills = skills

    @staticmethod
    def init() -> "SpecialSkills":
        skills = [Skill.init() for _ in range(11)]
        return SpecialSkills(skills)

    def get_valid_skills(self) -> list[Skill]:
        new_skills: list[Skill] = []
        for i, skill in enumerate(self.skills):
            if i == 1:
                continue
            new_skills.append(skill)

        return new_skills

    @staticmethod
    def read_upgrades(stream: "core.Data") -> "SpecialSkills":
        total_skills = 11

        skills: list[Skill] = []
        for _ in range(total_skills):
            skills.append(Skill.read_upgrade(stream))

        return SpecialSkills(skills)

    def write_upgrades(self, stream: "core.Data"):
        for skill in self.skills:
            skill.write_upgrade(stream)

    def read_gatya_seen(self, stream: "core.Data"):
        for skill in self.get_valid_skills():
            skill.read_seen(stream)

    def write_gatya_seen(self, stream: "core.Data"):
        for skill in self.get_valid_skills():
            skill.write_seen(stream)

    def read_max_upgrade_levels(self, stream: "core.Data"):
        for skill in self.skills:
            skill.read_max_upgrade_level(stream)

    def write_max_upgrade_levels(self, stream: "core.Data"):
        for skill in self.skills:
            skill.write_max_upgrade_level(stream)

    def serialize(self) -> list[dict[str, Any]]:
        return [skill.serialize() for skill in self.skills]

    @staticmethod
    def deserialize(data: list[dict[str, Any]]) -> "SpecialSkills":
        skills = SpecialSkills([])
        for skill in data:
            skills.skills.append(Skill.deserialize(skill))

        return skills

    def __repr__(self) -> str:
        return f"Skills(skills={self.skills})"

    def __str__(self) -> str:
        return f"Skills(skills={self.skills})"
