from typing import Any
from bcsfe.core import game_version, io


class Stage:
    def __init__(self, claimed: bool):
        self.claimed = claimed

    @staticmethod
    def read(stream: io.data.Data) -> "Stage":
        return Stage(stream.read_bool())

    def write(self, stream: io.data.Data):
        stream.write_bool(self.claimed)

    def serialize(self) -> bool:
        return self.claimed

    @staticmethod
    def deserialize(data: bool) -> "Stage":
        return Stage(data)

    def __repr__(self) -> str:
        return f"Stage(claimed={self.claimed})"

    def __str__(self) -> str:
        return self.__repr__()


class SubChapter:
    def __init__(self, stages: list[Stage]):
        self.stages = stages

    @staticmethod
    def read(stream: io.data.Data, total_stages: int) -> "SubChapter":
        stages: list[Stage] = []
        for _ in range(total_stages):
            stages.append(Stage.read(stream))
        return SubChapter(stages)

    def write(self, stream: io.data.Data):
        for stage in self.stages:
            stage.write(stream)

    def serialize(self) -> list[bool]:
        return [stage.serialize() for stage in self.stages]

    @staticmethod
    def deserialize(data: list[bool]) -> "SubChapter":
        return SubChapter([Stage.deserialize(stage) for stage in data])

    def __repr__(self) -> str:
        return f"SubChapter(stages={self.stages})"

    def __str__(self) -> str:
        return self.__repr__()


class SubChapterStars:
    def __init__(self, sub_chapters: list[SubChapter]):
        self.sub_chapters = sub_chapters

    @staticmethod
    def read(
        stream: io.data.Data, total_stages: int, total_stars: int
    ) -> "SubChapterStars":
        sub_chapters: list[SubChapter] = []
        for _ in range(total_stars):
            sub_chapters.append(SubChapter.read(stream, total_stages))
        return SubChapterStars(sub_chapters)

    def write(self, stream: io.data.Data):
        for sub_chapter in self.sub_chapters:
            sub_chapter.write(stream)

    def serialize(self) -> list[list[bool]]:
        return [sub_chapter.serialize() for sub_chapter in self.sub_chapters]

    @staticmethod
    def deserialize(data: list[list[bool]]) -> "SubChapterStars":
        return SubChapterStars(
            [SubChapter.deserialize(sub_chapter) for sub_chapter in data]
        )

    def __repr__(self) -> str:
        return f"SubChapterStars(sub_chapters={self.sub_chapters})"

    def __str__(self) -> str:
        return self.__repr__()


class ItemObtain:
    def __init__(self, flag: bool):
        self.flag = flag

    @staticmethod
    def read(stream: io.data.Data) -> "ItemObtain":
        return ItemObtain(stream.read_bool())

    def write(self, stream: io.data.Data):
        stream.write_bool(self.flag)

    def serialize(self) -> bool:
        return self.flag

    @staticmethod
    def deserialize(data: bool) -> "ItemObtain":
        return ItemObtain(data)

    def __repr__(self) -> str:
        return f"ItemObtain(flag={self.flag})"

    def __str__(self) -> str:
        return self.__repr__()


class ItemObtainSet:
    def __init__(self, item_obtains: dict[int, ItemObtain]):
        self.item_obtains = item_obtains

    @staticmethod
    def read(stream: io.data.Data) -> "ItemObtainSet":
        item_obtains: dict[int, ItemObtain] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            item_obtains[key] = ItemObtain.read(stream)
        return ItemObtainSet(item_obtains)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.item_obtains))
        for item_id, item_obtain in self.item_obtains.items():
            stream.write_int(item_id)
            item_obtain.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "item_obtains": {
                item_id: item_obtain.serialize()
                for item_id, item_obtain in self.item_obtains.items()
            }
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "ItemObtainSet":
        return ItemObtainSet(
            {
                int(item_id): ItemObtain.deserialize(item_obtain)
                for item_id, item_obtain in data.get("item_obtains", {}).items()
            }
        )

    def __repr__(self) -> str:
        return f"ItemObtainSet(item_obtains={self.item_obtains})"

    def __str__(self) -> str:
        return self.__repr__()


class ItemObtainSets:
    def __init__(self, item_obtain_sets: dict[int, ItemObtainSet]):
        self.item_obtain_sets = item_obtain_sets

    @staticmethod
    def read(stream: io.data.Data) -> "ItemObtainSets":
        item_obtain_sets: dict[int, ItemObtainSet] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            item_obtain_sets[key] = ItemObtainSet.read(stream)
        return ItemObtainSets(item_obtain_sets)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.item_obtain_sets))
        for item_id, item_obtain_set in self.item_obtain_sets.items():
            stream.write_int(item_id)
            item_obtain_set.write(stream)

    def serialize(self) -> dict[int, Any]:
        return {
            item_id: item_obtain_set.serialize()
            for item_id, item_obtain_set in self.item_obtain_sets.items()
        }

    @staticmethod
    def deserialize(data: dict[int, Any]) -> "ItemObtainSets":
        return ItemObtainSets(
            {
                int(item_id): ItemObtainSet.deserialize(item_obtain_set)
                for item_id, item_obtain_set in data.items()
            }
        )

    def __repr__(self) -> str:
        return f"ItemObtainSets(item_obtain_sets={self.item_obtain_sets})"

    def __str__(self) -> str:
        return self.__repr__()


class UnobtainedItem:
    def __init__(self, unobtained: bool):
        self.unobtained = unobtained

    @staticmethod
    def read(stream: io.data.Data) -> "UnobtainedItem":
        return UnobtainedItem(stream.read_bool())

    def write(self, stream: io.data.Data):
        stream.write_bool(self.unobtained)

    def serialize(self) -> bool:
        return self.unobtained

    @staticmethod
    def deserialize(data: bool) -> "UnobtainedItem":
        return UnobtainedItem(data)

    def __repr__(self) -> str:
        return f"UnobtainedItem(unobtained={self.unobtained})"

    def __str__(self) -> str:
        return self.__repr__()


class UnobtainedItems:
    def __init__(self, unobtained_items: dict[int, UnobtainedItem]):
        self.unobtained_items = unobtained_items

    @staticmethod
    def read(stream: io.data.Data) -> "UnobtainedItems":
        unobtained_items: dict[int, UnobtainedItem] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            unobtained_items[key] = UnobtainedItem.read(stream)
        return UnobtainedItems(unobtained_items)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.unobtained_items))
        for item_id, unobtained_item in self.unobtained_items.items():
            stream.write_int(item_id)
            unobtained_item.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "unobtained_items": {
                item_id: unobtained_item.serialize()
                for item_id, unobtained_item in self.unobtained_items.items()
            }
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "UnobtainedItems":
        return UnobtainedItems(
            {
                int(item_id): UnobtainedItem.deserialize(unobtained_item)
                for item_id, unobtained_item in data.get("unobtained_items", {}).items()
            }
        )

    def __repr__(self) -> str:
        return f"UnobtainedItems(unobtained_items={self.unobtained_items})"

    def __str__(self) -> str:
        return self.__repr__()


class Chapters:
    def __init__(self, sub_chapters: list[SubChapterStars]):
        self.sub_chapters = sub_chapters

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "Chapters":
        if gv < 20:
            return Chapters([])
        if gv <= 33:
            total_subchapters = 50
            total_stages = 12
            total_stars = 3
        elif gv <= 34:
            total_subchapters = stream.read_int()
            total_stages = 12
            total_stars = 3
        else:
            total_subchapters = stream.read_int()
            total_stages = stream.read_int()
            total_stars = stream.read_int()
        sub_chapters: list[SubChapterStars] = []
        for _ in range(total_subchapters):
            sub_chapters.append(SubChapterStars.read(stream, total_stages, total_stars))
        return Chapters(sub_chapters)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv < 20:
            return
        if gv <= 33:
            pass
        elif gv <= 34:
            stream.write_int(len(self.sub_chapters))
        else:
            stream.write_int(len(self.sub_chapters))
            stream.write_int(len(self.sub_chapters[0].sub_chapters[0].stages))
            stream.write_int(len(self.sub_chapters[0].sub_chapters))
        for sub_chapter in self.sub_chapters:
            sub_chapter.write(stream)

    def read_item_obtains(self, stream: io.data.Data):
        self.item_obtains = ItemObtainSets.read(stream)
        self.unobtained_items = UnobtainedItems.read(stream)

    def write_item_obtains(self, stream: io.data.Data):
        self.item_obtains.write(stream)
        self.unobtained_items.write(stream)

    def serialize(self) -> dict[str, Any]:
        return {
            "sub_chapters": [
                sub_chapter.serialize() for sub_chapter in self.sub_chapters
            ],
            "item_obtains": self.item_obtains.serialize(),
            "unobtained_items": self.unobtained_items.serialize(),
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "Chapters":
        chapters = Chapters(
            [
                SubChapterStars.deserialize(sub_chapter)
                for sub_chapter in data.get("sub_chapters", [])
            ]
        )
        chapters.item_obtains = ItemObtainSets.deserialize(data.get("item_obtains", {}))
        chapters.unobtained_items = UnobtainedItems.deserialize(
            data.get("unobtained_items", {})
        )
        return chapters

    def __repr__(self) -> str:
        return f"Chapters(sub_chapters={self.sub_chapters}, item_obtains={self.item_obtains}, unobtained_items={self.unobtained_items})"

    def __str__(self) -> str:
        return self.__repr__()
