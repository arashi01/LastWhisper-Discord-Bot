from copy import deepcopy
from uuid import uuid4


class Day:
    def __init__(self, buff: str = "", image_url: str = "", uuid: str = None, *_, **__):
        self.uuid: str = uuid if uuid else str(uuid4())
        self.buff: str = buff
        self.image_url: image_url = image_url

    def to_json(self) -> dict:
        dct: dict = deepcopy(self.__dict__)
        return dct


class Week:
    def __init__(self, days: tuple[str, str, str, str, str, str, str] = (), message: str = None, uuid: str = None, *_, **__):
        self.uuid: str = uuid if uuid else str(uuid4())
        self.days: tuple[str, str, str, str, str, str, str] = days
        self.message: str = message

    def to_json(self) -> dict:
        dct: dict = deepcopy(self.__dict__)
        return dct


class ServerConfig:
    def __init__(self, message_channel_id: str = None, message_sent_hour: str = None, days: list[Day] = None, weeks: list[Week] = None, *_, **__):
        self.message_channel_id: str = message_channel_id
        self.message_sent_hour: str = message_sent_hour
        self.days = days if days else []
        self.weeks = weeks if weeks else []

    @classmethod
    def from_dict(cls, data: dict):
        obj: ServerConfig = cls(**data)

        days: list[Day] = []
        for day in obj.days:
            days.append(Day(**day))
        obj.days = days

        weeks: list[Week] = []
        for week in obj.weeks:
            weeks.append(Week(**week))
        obj.weeks = weeks

        return obj

    def to_json(self) -> dict:
        d: dict = deepcopy(self.__dict__)

        days: list[dict] = []
        for day in d["days"]:
            days.append(day.to_json())
        d["days"] = days

        weeks: list[dict] = []
        for week in d["weeks"]:
            weeks.append(week.to_json())
        d["weeks"] = weeks

        return d
