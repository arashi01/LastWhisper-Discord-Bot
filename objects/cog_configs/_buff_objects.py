from objects import CustomConfigObject, convert_dict_list, TypeObjects, TypeList


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

    def __init__(self, name="", Monday: int = -1, Tuesday: int = -1, Wednesday: int = -1, Thursday: int = -1, Friday: int = -1, Saturday: int = -1, Sunday: int = -1):
        """
        :param name: The name of the week.

        :param Monday: The index of the buff for Monday.
        :param Tuesday: The index of the buff for Tuesday.
        :param Wednesday: The index of the buff for Wednesday.
        :param Thursday: The index of the buff for Thursday.
        :param Friday: The index of the buff for Friday.
        :param Saturday: The index of the buff for Saturday.
        :param Sunday: The index of the buff for Sunday.
        """

        self.name: str = name
        self.Monday: int = Monday
        self.Tuesday: int = Tuesday
        self.Wednesday: int = Wednesday
        self.Thursday: int = Thursday
        self.Friday: int = Friday
        self.Saturday: int = Saturday
        self.Sunday: int = Sunday

    def get_value(self, index: int) -> int:
        """
        Returns the Buff index given a date index.

        :param index: The day index ranging from 0 for Monday to 6 for Sunday.
        :return: The index of Buff for the day given or -1 if key error.
        """

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
        self.weeks: dict = {} if weeks is None else weeks

    @classmethod
    def from_json(cls, data):
        obj: BuffManagerConfig = super().from_json(data)

        convert_dict_list(obj.buff_list, Buff)
        convert_dict_list(obj.weeks, Week)

        return obj
