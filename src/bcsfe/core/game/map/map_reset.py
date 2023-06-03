from bcsfe.core import io


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
    def read(stream: io.data.Data) -> "MapResetData":
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

    def write(self, stream: io.data.Data):
        stream.write_double(self.yearly_end_timestamp)
        stream.write_double(self.monthly_end_timestamp)
        stream.write_double(self.weekly_end_timestamp)
        stream.write_double(self.daily_end_timestamp)

    def __str__(self) -> str:
        return f"MapResetData(yearly_end_timestamp={self.yearly_end_timestamp!r}, monthly_end_timestamp={self.monthly_end_timestamp!r}, weekly_end_timestamp={self.weekly_end_timestamp!r}, daily_end_timestamp={self.daily_end_timestamp!r})"

    def __repr__(self) -> str:
        return str(self)


class MapResets:
    def __init__(self, data: dict[int, list[MapResetData]]):
        self.data = data

    @staticmethod
    def read(stream: io.data.Data) -> "MapResets":
        data: dict[int, list[MapResetData]] = {}
        for _ in range(stream.read_int()):
            key = stream.read_int()
            value: list[MapResetData] = []
            for _ in range(stream.read_int()):
                value.append(MapResetData.read(stream))
            data[key] = value
        return MapResets(data)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.data))
        for key, value in self.data.items():
            stream.write_int(key)
            stream.write_int(len(value))
            for item in value:
                item.write(stream)
