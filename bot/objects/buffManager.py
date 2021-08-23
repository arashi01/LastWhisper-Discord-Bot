from copy import deepcopy
from uuid import uuid4


class Buff:
    def __init__(self, buff: str = "", image_url: str = "", uuid: str = None, *_, **__):
        self.uuid: str = uuid if uuid else str(uuid4())
        self.buff: str = buff
        self.image_url: image_url = image_url

    @property
    def to_json(self) -> dict:
        dct: dict = deepcopy(self.__dict__)
        return dct


class Week:
    def __init__(self, days: tuple[str, str, str, str, str, str, str] = (), message: str = None, uuid: str = None, *_, **__):
        self.uuid: str = uuid if uuid else str(uuid4())
        self.days: tuple[str, str, str, str, str, str, str] = days
        self.message: str = message

    @property
    def to_json(self) -> dict:
        dct: dict = deepcopy(self.__dict__)
        return dct


class ServerConfig:
    def __init__(self, message: str = None, message_channel_id: str = None, message_sent_hour: str = None, message_weekday: int = None, buffs: list[Buff] = None, weeks: list[Week] = None, *_, **__):
        self.message: str = message
        self.message_channel_id: str = message_channel_id
        self.message_sent_hour: str = message_sent_hour
        self.message_weekday: int = message_weekday
        self.buffs = buffs if buffs else []
        self.weeks = weeks if weeks else []

    @classmethod
    def from_dict(cls, data: dict):
        obj: ServerConfig = cls(**data)

        buffs: list[Buff] = []
        for buff in obj.buffs:
            buffs.append(Buff(**buff))
        obj.buffs = buffs

        weeks: list[Week] = []
        for week in obj.weeks:
            weeks.append(Week(**week))
        obj.weeks = weeks

        return obj

    @property
    def to_json(self) -> dict:
        d: dict = deepcopy(self.__dict__)

        buffs: list[dict] = []
        for buff in d["buffs"]:
            buffs.append(buff.to_json())
        d["buffs"] = buffs

        weeks: list[dict] = []
        for week in d["weeks"]:
            weeks.append(week.to_json())
        d["weeks"] = weeks

        return d
