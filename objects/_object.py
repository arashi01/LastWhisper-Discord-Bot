from abc import ABC
from typing import TypeVar, Generic


class CustomConfigObject(ABC):
    """
    Represents an abstract object used by classes.
    This is meant to be an abstract class that is used as a base for other objects used throughout out the bot.
    """

    @classmethod
    def from_json(cls, data: dict):
        """
        From json dict to Class object.
        Converts json data dict to the object.

        :param data: The json dictionary.
        :return: A CustomConfigObject child.
        """
        obj = cls()

        for key, value in obj.__dict__.items():
            try:
                if isinstance(value, TypeObjects.Channel):
                    obj.__dict__[key] = TypeObjects.Channel(data[key])
                elif isinstance(value, TypeObjects.Member):
                    obj.__dict__[key] = TypeObjects.Member(data[key])
                elif isinstance(value, TypeObjects.Role):
                    obj.__dict__[key] = TypeObjects.Role(data[key])
                elif isinstance(value, TypeList):
                    obj.__dict__[key] = TypeList(value.t, list(map(value.t, data[key])))
                else:
                    obj.__dict__[key] = data[key]
            except KeyError:
                pass

        return obj

    @staticmethod
    def converter(obj) -> dict:
        """
        Converter for json parser
        Converts the object into a json parse friendly form.

        :param obj: The object being parsed.
        :return: dict of
        """
        return obj.__dict__

    def __getitem__(self, item) -> any:
        return self.__dict__[item]

    def __setitem__(self, key, value) -> None:
        self.__dict__[key] = value


class TypeObjects(object):
    """ Class container of the special type objects used. """

    class Channel(int):
        """ Represents a channel id """
        pass

    class Member(int):
        """ Represents a member id """
        pass

    class Role(int):
        """ Represents a role id """
        pass


def convert_dict_list(dictionary: dict, class_object: CustomConfigObject.__class__) -> None:
    copy: dict = dictionary.copy()
    dictionary.clear()

    for key, value in sorted(copy.items()):
        dictionary[key]: class_object = class_object.from_json(value)


T = TypeVar('T')


class TypeList(list, Generic[T]):
    """ A list object that can only accept a vale of type T """

    def __init__(self, t: T, pre_existing_list=None) -> None:
        """
        :param t: The accepted object type
        :param pre_existing_list: A list that is already existing to be converted.
        """
        if pre_existing_list is None:
            pre_existing_list = []
        super().__init__(pre_existing_list)
        self._T = t

    def append(self, __object: T) -> None:
        if type(__object) == self._T:
            super(TypeList, self).append(__object)
        else:
            raise TypeError(f"Object is not of type {self._T}")

    @property
    def t(self):
        return self._T
