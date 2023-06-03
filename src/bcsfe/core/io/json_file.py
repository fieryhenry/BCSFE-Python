import json
from typing import Any
from bcsfe.core.io import data, path


class JsonFile:
    def __init__(self, data: "data.Data"):
        self.json = json.loads(data.data)

    @staticmethod
    def from_path(path: "path.Path") -> "JsonFile":
        return JsonFile(path.read())

    @staticmethod
    def from_object(js: Any) -> "JsonFile":
        return JsonFile(data.Data(json.dumps(js)))

    @staticmethod
    def from_data(data: "data.Data") -> "JsonFile":
        return JsonFile(data)

    def to_data(self) -> "data.Data":
        return data.Data(json.dumps(self.json, indent=4))

    def save(self, path: "path.Path") -> None:
        path.write(self.to_data())

    def get_json(self) -> Any:
        return self.json

    def get(self, key: str) -> Any:
        return self.json[key]

    def set(self, key: str, value: Any) -> None:
        self.json[key] = value

    def __str__(self) -> str:
        return str(self.json)

    def __getitem__(self, key: str) -> Any:
        return self.json[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.json[key] = value
