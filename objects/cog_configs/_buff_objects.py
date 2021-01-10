from objects import CustomConfigObject, convert_dict_list_json, convert_dict, TypeObjects, TypeList


class Buff(CustomConfigObject):
    """
    Object representing a Buff.
    This object represents a Buff that will be used given a day of the week.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, name="", image_url=""):
        """
        :param name: The name of the Buff.
        :param image_url: The URL to be used as a thumbnail of a buff. This can be a URL linking to a image of a buff or any image.
        """
        self.name: str = name
        self.image_url: str = image_url


class Week(CustomConfigObject):
    """
    Object representing a collection of Buffs.
    This object stores the indexes of buffs that will be used given a day of the week.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, name="", monday: int = -1, tuesday: int = -1, wednesday: int = -1, thursday: int = -1, friday: int = -1, saturday: int = -1, sunday: int = -1):
        """
        :param name: The name of the week.

        :param monday: The index of the buff for Monday.
        :param tuesday: The index of the buff for Tuesday.
        :param wednesday: The index of the buff for Wednesday.
        :param thursday: The index of the buff for Thursday.
        :param friday: The index of the buff for Friday.
        :param saturday: The index of the buff for Saturday.
        :param sunday: The index of the buff for Sunday.
        """
        self.name: str = name
        self.monday: int = monday
        self.tuesday: int = tuesday
        self.wednesday: int = wednesday
        self.thursday: int = thursday
        self.friday: int = friday
        self.saturday: int = saturday
        self.sunday: int = sunday

    def get_value(self, index: int) -> int:
        """
        Returns the Buff index given a date index.

        :param index: The day index ranging from 0 for Monday to 6 for Sunday.
        :return: The index of Buff for the day given or -1 if key error.
        """

        try:
            return {
                0: self.monday,
                1: self.tuesday,
                2: self.wednesday,
                3: self.thursday,
                4: self.friday,
                5: self.saturday,
                6: self.sunday,
            }[index]
        except KeyError:
            return -1


class BuffManagerConfig(CustomConfigObject):
    """
    The configuration object for the Buff Manager extension.
    This object stores only the config information for a discord server that has the Buff Manager extension enabled.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, *, mm_channel_id=-1, mm_hour=-1,
                 tdb_ids=None, tmb_ids=None,
                 twb_ids=None, nwb_id=None,
                 buff_list=None, weeks=None):

        """
        :param mm_channel_id: The Discord channel id where the morning message will be posted.
        :param mm_hour: The hour when the morning message is posted.

        :param tdb_ids: A collection of Discord Role ids that allow users to execute the tdb command.
        :param tmb_ids: A collection of Discord Role ids that allow users to execute the tmb command.
        :param twb_ids: A collection of Discord Role ids that allow users to execute the twb command.
        :param nwb_id: A collection of Discord Role ids that allow users to execute the nwb command.

        :param buff_list: A key, value collection of the Buff objects used by the server.
        :param weeks: A key, value collection of the Week objects used by the server.
        """
        self.mm_channel_id: TypeObjects.Channel = mm_channel_id if mm_channel_id else TypeObjects.Channel()
        self.mm_hour: int = mm_hour if mm_hour else 0

        self.tdb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else tdb_ids
        self.tmb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else tmb_ids
        self.twb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else twb_ids
        self.nwb_ids: TypeList = TypeList(t=TypeObjects.Role) if not tdb_ids else nwb_id

        self.buff_list: dict = {} if buff_list is None else buff_list
        self.buff_list: dict = convert_dict(self.buff_list, Buff)
        self.weeks: dict = {} if weeks is None else weeks
        self.weeks: dict = convert_dict(self.weeks, Week)

    @classmethod
    def from_json(cls, data):
        obj: BuffManagerConfig = super().from_json(data)

        convert_dict_list_json(obj.buff_list, Buff)
        convert_dict_list_json(obj.weeks, Week)

        return obj
