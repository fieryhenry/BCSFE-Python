from __future__ import annotations
from bcsfe import core
from bcsfe.cli import dialog_creator


class Material:
    def __init__(self, amount: int):
        self.amount = amount

    @staticmethod
    def init() -> Material:
        return Material(0)

    @staticmethod
    def read(stream: core.Data) -> Material:
        amount = stream.read_int()
        return Material(amount)

    def write(self, stream: core.Data):
        stream.write_int(self.amount)

    def serialize(self) -> int:
        return self.amount

    @staticmethod
    def deserialize(data: int) -> Material:
        return Material(data)

    def __repr__(self) -> str:
        return f"Material(amount={self.amount!r})"

    def __str__(self) -> str:
        return self.__repr__()


class BaseMaterials:
    def __init__(self, materials: list[Material]):
        self.materials = materials

    @staticmethod
    def init() -> BaseMaterials:
        return BaseMaterials([])

    @staticmethod
    def read(stream: core.Data) -> BaseMaterials:
        total = stream.read_int()
        materials: list[Material] = []
        for _ in range(total):
            materials.append(Material.read(stream))
        return BaseMaterials(materials)

    def write(self, stream: core.Data):
        stream.write_int(len(self.materials))
        for material in self.materials:
            material.write(stream)

    def serialize(self) -> list[int]:
        return [material.serialize() for material in self.materials]

    @staticmethod
    def deserialize(data: list[int]) -> BaseMaterials:
        return BaseMaterials(
            [Material.deserialize(material) for material in data]
        )

    def __repr__(self) -> str:
        return f"Materials(materials={self.materials!r})"

    def __str__(self) -> str:
        return self.__repr__()

    def edit_base_materials(self, save_file: core.SaveFile):
        names = core.core_data.get_gatya_item_names(save_file).names
        items = core.core_data.get_gatya_item_buy(save_file).get_by_category(7)
        if items is None:
            return
        if names is None:
            return
        names = [names[item.id] for item in items]
        base_materials = [
            base_material.amount for base_material in self.materials
        ]
        values = dialog_creator.MultiEditor.from_reduced(
            "base_materials",
            names,
            base_materials,
            core.core_data.max_value_manager.get("base_materials"),
            group_name_localized=True,
        ).edit()
        self.materials = [Material(value) for value in values]
