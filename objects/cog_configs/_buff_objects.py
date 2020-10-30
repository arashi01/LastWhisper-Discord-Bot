from objects import CustomConfigObject, convert_dict_list, TypeObjects, TypeList
from enum import Enum, auto


class Buff(CustomConfigObject):

    def __init__(self, title: str = None, image_url: str = None):
        self.title = title
        self.image_url = image_url


class Week(CustomConfigObject):
    def __init__(self, name: str = "", monday: int = None, tuesday: int = None,
                 wednesday: int = None, thursday: int = None, friday: int = None, saturday: int = None,
                 sunday: int = None):

        self.name = name
        self.Monday = monday
        self.Tuesday = tuesday
        self.Wednesday = wednesday
        self.Thursday = thursday
        self.Friday = friday
        self.Saturday = saturday
        self.Sunday = sunday

    def get_value(self, index: int):
        try:
            return {
                0: self.Monday,
                1: self.Tuesday,
                2: self.Wednesday,
                3: self.Thursday,
                4: self.Friday,
                5: self.Saturday,
                6: self.Sunday,
            }[index]
        except KeyError:
            return None


class BuffManagerConfig(CustomConfigObject):
    def __init__(self,
                 mm_channel_id: TypeObjects.Channel = None, mm_hour: int = None,
                 tdb_ids: [TypeObjects.Role] = None, tmb_ids: [TypeObjects.Role] = None,
                 twb_ids: [TypeObjects.Role] = None, nwb_id: [TypeObjects.Role] = None,
                 buff_list: dict = None, weeks: dict = None):

        self.mm_channel_id: TypeObjects.Channel = mm_channel_id if mm_channel_id else TypeObjects.Channel()
        self.mm_hour: int = mm_hour if mm_hour else 0

        self.tdb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else tdb_ids
        self.tmb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else tmb_ids
        self.twb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else twb_ids
        self.nwb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else nwb_id

        self.buff_list: dict = {} if buff_list is None else buff_list
        self.weeks: dict = {} if weeks is None else weeks

    @classmethod
    def from_json(cls, data):
        obj: BuffManagerConfig = super().from_json(data)

        convert_dict_list(obj.buff_list, Buff)
        convert_dict_list(obj.weeks, Week)

        return obj
