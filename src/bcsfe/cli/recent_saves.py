from __future__ import annotations
from typing import Any

from bcsfe import core
import datetime
import json
from bcsfe.cli import color, dialog_creator


class RecentSave:
    def __init__(
        self,
        path: core.Path,
        cc: core.CountryCode,
        gv: core.GameVersion,
        inquiry: str,
        time: datetime.datetime,
        name: core.Path,
    ):
        self.path = path
        self.cc = cc
        self.gv = gv
        self.inquiry = inquiry
        self.time = time
        self.name = name

    @staticmethod
    def from_dict(data: dict[str, Any]) -> RecentSave | None:
        path = data.get("path")
        cc = data.get("cc")
        gv = data.get("gv")
        inquiry = data.get("inquiry")
        time_stamp = data.get("timestamp")
        name = data.get("name")
        if (
            path is None
            or cc is None
            or gv is None
            or inquiry is None
            or time_stamp is None
            or name is None
        ):
            return None

        return RecentSave(
            core.Path(path),
            core.CountryCode(cc),
            core.GameVersion.from_string(gv),
            inquiry,
            datetime.datetime.fromtimestamp(time_stamp),
            core.Path(name),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path.to_str(),
            "cc": self.cc.get_code(),
            "gv": self.gv.to_string(),
            "inquiry": self.inquiry,
            "timestamp": self.time.timestamp(),
            "name": self.name.to_str(),
        }


class RecentSaves:
    def __init__(self, saves: list[RecentSave]):
        self.saves = saves

    @staticmethod
    def from_json(data: list[dict[str, Any]]) -> RecentSaves:
        res: list[RecentSave] = []

        for item in data:
            save = RecentSave.from_dict(item)
            if save is not None:
                res.append(save)

        return RecentSaves(res)

    def to_json(self) -> list[dict[str, Any]]:
        return [save.to_dict() for save in self.saves][-10:]  # only store 10

    @staticmethod
    def from_path(path: core.Path) -> RecentSaves | None:
        json_data = json.loads(path.read().to_str())

        return RecentSaves.from_json(json_data)

    def to_path(self, path: core.Path):
        data = json.dumps(self.to_json(), indent=4)

        path.write(core.Data(data))

    @staticmethod
    def read_default() -> RecentSaves:
        path = RecentSaves.get_path()
        if path.exists():
            return RecentSaves.from_path(path) or RecentSaves([])
        return RecentSaves([])

    @staticmethod
    def get_path() -> core.Path:
        return core.Path.get_documents_folder().add("recent_saves.json")

    def save_default(self):
        path = RecentSaves.get_path()
        self.to_path(path)

    def select(self) -> RecentSave | None:
        if not self.saves:
            color.ColoredText.localize("no_recent_saves")
            return None
        items: list[str] = []
        for save in self.saves:
            items.append(
                core.localize(
                    "recent_save",
                    path=save.path,
                    cc=save.cc,
                    gv=save.gv,
                    inquiry_code=save.inquiry,
                    year=save.time.year,
                    month=str(save.time.month).zfill(2),
                    day=str(save.time.day).zfill(2),
                    hour=str(save.time.hour).zfill(2),
                    minute=str(save.time.minute).zfill(2),
                    second=str(save.time.second).zfill(2),
                    name=save.name,
                )
            )
        items.reverse()

        resp = dialog_creator.ChoiceInput.from_reduced(
            items, localize_options=False, dialog="select_recent"
        ).single_choice()
        if resp is None:
            return None

        resp = len(self.saves) - resp

        return self.saves[resp]
