from typing import Union

from discord import Emoji, Member, Role, TextChannel, VoiceChannel


class ConfigMethodHelpers:
    @staticmethod
    def set(existing_value, args: tuple, settings: dict):
        """
        Generic method to set variable.
        Its recommended to create your own if this is missing features that are not normally found.

        :param existing_value: value that is already there.
        :param args: all the arguments passed to the command.
        :param settings: settings for the variable.
        :return: new value.
        """
        return ConfigMethodHelpers.get_value_from_arg(args[0], settings)

    @staticmethod
    def add(existing_value: list, args: tuple, settings: dict):
        """
            Generic method to add variable.
            Its recommended to create your own if this is missing features that are not normally found.

            :param existing_value: value that is already there.
            :param args: all the arguments passed to the command.
            :param settings: settings for the variable.
            :return: new value.
        """
        value: Union[str, int, bool, dict] = ConfigMethodHelpers.get_value_from_arg(args[0], settings)

        if type(existing_value) is not list:
            existing_value = []

        existing_value.append(value)
        return existing_value

    @staticmethod
    def remove(existing_value: list, args: tuple, settings: dict):
        """
            Generic method to remove variable.
            Its recommended to create your own if this is missing features that are not normally found.

            :param existing_value: value that is already there.
            :param args: all the arguments passed to the command.
            :param settings: settings for the variable.
            :return: new value.
        """
        value = args[0]
        if type(value) is not int:
            raise TypeError("argument needs to be of type int.")

        if type(existing_value) is not list:
            existing_value = []

        existing_value.pop(value)
        return existing_value

    @staticmethod
    def get_value_from_arg(arg: Union[Emoji, Member, Role, TextChannel, VoiceChannel, str, int, bool, dict], settings):
        """
        Helper method to parse an argument into a more readable format and do a basic type check.
        Highly recommend writing your own if this one does not do all the functions needed.

        :param arg: Value to be parsed.
        :type arg: Emoji | Member | Role | TextChannel | VoiceChannel | str | int | bool | dict
        :param settings: Settings for the variable being set.
        :type settings: dict
        :return: what is returned.
        :rtype: str | int | bool | dict
        """
        if "value_type" in settings:
            value_type = settings["value_type"]
            if not type(arg) is value_type:
                raise TypeError(f"value {arg} does not match type {type(value_type)}")

        if "range" in settings and type(arg) == int:
            _range: dict = settings["range"]
            if (min_inclusive := _range.get("min_inclusive", None)) and not arg >= min_inclusive:
                raise TypeError(f"value {arg} is outsize of min range {min_inclusive}")
            if (max_inclusive := _range.get("max_inclusive", None)) and not arg <= max_inclusive:
                raise TypeError(f"value {arg} is outsize of max range {max_inclusive}")
            if (min_exclusive := _range.get("min_exclusive", None)) and not arg > min_exclusive:
                raise TypeError(f"value {arg} is not in min range {min_exclusive}")
            if (max_exclusive := _range.get("max_exclusive", None)) and not arg < max_exclusive:
                raise TypeError(f"value {arg} is not in max range {max_exclusive}")

        if isinstance(arg, (Member, Role, TextChannel, VoiceChannel)):
            return str(arg.id)

        if isinstance(arg, Emoji):
            return f"<:{arg.name}:{arg.id}>"

        return arg

