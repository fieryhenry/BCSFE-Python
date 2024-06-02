from __future__ import annotations
from bcsfe import core


class MapResetData:
    def __init__(
        self,
        yearly_end_timestamp: float,
        monthly_end_timestamp: float,
        weekly_end_timestamp: float,
        daily_end_timestamp: float,
    ):
        self.yearly_end_timestamp = yearly_end_timestamp
        self.monthly_end_timestamp = monthly_end_timestamp
        self.weekly_end_timestamp = weekly_end_timestamp
        self.daily_end_timestamp = daily_end_timestamp

    @staticmethod
    def init() -> MapResetData:
        return MapResetData(
            0.0,
            0.0,
            0.0,
            0.0,
        )

    @staticmethod
    def read(stream: core.Data) -> MapResetData:
        yearly_end_timestamp = stream.read_double()
        monthly_end_timestamp = stream.read_double()
        weekly_end_timestamp = stream.read_double()
        daily_end_timestamp = stream.read_double()
        return MapResetData(
            yearly_end_timestamp,
            monthly_end_timestamp,
            weekly_end_timestamp,
            daily_end_timestamp,
        )

    def write(self, stream: core.Data):
        stream.write_double(self.yearly_end_timestamp)
        stream.write_double(self.monthly_end_timestamp)
        stream.write_double(self.weekly_end_timestamp)
        stream.write_double(self.daily_end_timestamp)

    def serialize(self) -> dict[str, float]:
        return {
            "yearly_end_timestamp": self.yearly_end_timestamp,
            "monthly_end_timestamp": self.monthly_end_timestamp,
            "weekly_end_timestamp": self.weekly_end_timestamp,
            "daily_end_timestamp": self.daily_end_timestamp,
        }

    @staticmethod
    def deserialize(data: dict[str, float]) -> MapResetData:
        return MapResetData(
            data.get("yearly_end_timestamp", 0.0),
            data.get("monthly_end_timestamp", 0.0),
            data.get("weekly_end_timestamp", 0.0),
            data.get("daily_end_timestamp", 0.0),
        )

    def __str__(self) -> str:
        return f"MapResetData(yearly_end_timestamp={self.yearly_end_timestamp!r}, monthly_end_timestamp={self.monthly_end_timestamp!r}, weekly_end_timestamp={self.weekly_end_timestamp!r}, daily_end_timestamp={self.daily_end_timestamp!r})"

    def __repr__(self) -> str:
        return str(self)


class MapResets:
    def __init__(self, data: dict[int, list[MapResetData]]):
        self.data = data

    @staticmethod
    def init() -> MapResets:
        return MapResets({})

    @staticmethod
    def read(stream: core.Data) -> MapResets:
        data: dict[int, list[MapResetData]] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            value: list[MapResetData] = []
            for _ in range(stream.read_int()):
                value.append(MapResetData.read(stream))
            data[key] = value
        return MapResets(data)

    def write(self, stream: core.Data):
        stream.write_int(len(self.data))
        for key, value in self.data.items():
            stream.write_int(key)
            stream.write_int(len(value))
            for item in value:
                item.write(stream)

    def serialize(self) -> dict[int, list[dict[str, float]]]:
        return {
            key: [item.serialize() for item in value]
            for key, value in self.data.items()
        }

    @staticmethod
    def deserialize(data: dict[int, list[dict[str, float]]]) -> MapResets:
        return MapResets(
            {
                key: [MapResetData.deserialize(item) for item in value]
                for key, value in data.items()
            }
        )

    def __str__(self) -> str:
        return f"MapResets(data={self.data!r})"

    def __repr__(self) -> str:
        return str(self)
