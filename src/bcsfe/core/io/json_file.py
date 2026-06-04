from __future__ import annotations
import json
from typing import Any
from bcsfe import core


class JsonFile:
    def __init__(self, obj: Any):
        self.obj = obj

    @staticmethod
    def from_path(path: core.Path) -> JsonFile:
        return JsonFile(json.loads(path.read().data))

    @staticmethod
    def from_object(js: Any) -> JsonFile:
        return JsonFile(js)

    @staticmethod
    def from_data(data: core.Data) -> JsonFile:
        return JsonFile(json.loads(data.data))

    def to_data(self, indent: int | None = 4) -> core.Data:
        return core.Data(json.dumps(self.obj, indent=indent))

    def to_file(self, path: core.Path) -> None:
        path.write(self.to_data())

    def as_object(self) -> Any:
        return self.obj
