from objects import CustomConfigObject, convert_dict_list, TypeObjects, TypeList


class Buff(CustomConfigObject):
    """ Object representing a Buff.

    This object represents a Buff that will be used given a day of the week.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, *, name="", image_url=""):
        """
        Parameters
        ------------
        name: :class: 'str'
            The name of the Buff.
        image_url: :class: 'str'
            The URL to be used as a thumbnail of a buff. This can be a URL linking to a image of a buff or any image.
        """
        self.name: str = name
        self.image_url: str = image_url


class Week(CustomConfigObject):
    """ Object representing a collection of Buffs.

    This object stores the indexes of buffs that will be used given a day of the week.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, *, name="", Monday=-1, Tuesday=-1, Wednesday=-1, Thursday=-1, Friday=-1, Saturday=-1, Sunday=-1):
        """
        :param name: The name of the week.
        :type name: str

        :param Monday: The index of the buff for Monday.
        :type Monday: int
        :param Tuesday: The index of the buff for Tuesday.
        :type Tuesday: int
        :param Wednesday: The index of the buff for Wednesday.
        :type Wednesday: int
        :param Thursday: The index of the buff for Thursday.
        :type Thursday: int
        :param Friday: The index of the buff for Friday.
        :type Friday: int
        :param Saturday: The index of the buff for Saturday.
        :type Saturday: int
        :param Sunday: The index of the buff for Sunday.
        :type Sunday: int
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
        """ Returns the Buff index given a date index.

        :param index: The day index ranging from 0 for Monday to 6 for Sunday.
        :type index: int
        :return: The index of Buff for the day given or -1 if key error.
        :rtype: int
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
    """ The configuration object for the Buff Manager extension.

    This object stores only the config information for a discord server that has the Buff Manager extension enabled.
    This object purely holds information and does not do any form of verification.
    """

    def __init__(self, *, mm_channel_id=-1, mm_hour=-1,
                 tdb_ids=None, tmb_ids=None,
                 twb_ids=None, nwb_id=None,
                 buff_list=None, weeks=None):

        """
        :param mm_channel_id: The Discord channel id where the morning message will be posted.
        :type mm_channel_id: int
        :param mm_hour: The hour when the morning message is posted.
        :type mm_hour: int

        :param tdb_ids: A collection of Discord Role ids that allow users to execute the tdb command.
        :type tdb_ids: TypeList
        :param tmb_ids: A collection of Discord Role ids that allow users to execute the tmb command.
        :type tmb_ids: TypeList
        :param twb_ids: A collection of Discord Role ids that allow users to execute the twb command.
        :type twb_ids: TypeList
        :param nwb_id: A collection of Discord Role ids that allow users to execute the nwb command.
        :type nwb_id: TypeList

        :param buff_list: A key, value collection of the Buff objects used by the server.
        :type buff_list: dict
        :param weeks: A key, value collection of the Week objects used by the server.
        :type weeks: dict
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
