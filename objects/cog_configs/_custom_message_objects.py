from datetime import datetime

from objects import CustomConfigObject, convert_dict_list_json, TypeObjects


class Message(CustomConfigObject):
    """
    Object representing a message.
    This object purely holds information and does not do any form of validation.
    """

    def __init__(self, message="", channel_id: TypeObjects.Channel = -1,
                 date: datetime = None, should_repeat: bool = False):
        """
        :param message: The message that will be posted.
        :param channel_id: The Discord Channel id where the message will be posted.
        :param date: The date and time when the message will be posted.
        :param should_repeat: Bool if the message should be repeated or destroyed once posted.
        """

        self.message: str = message
        self.channel_id: TypeObjects.Channel = channel_id
        self.date: datetime = date if date else datetime.now()
        self.should_repeat: bool = should_repeat

    @staticmethod
    def converter(obj):
        obj.date = obj.date.__str__()
        return obj.__dict__

    @classmethod
    def from_json(cls, data):
        obj = cls()
        obj.__dict__ = data

        obj.date = datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")

        return obj


class CustomMessagesConfig(CustomConfigObject):
    """
    The config object for a Discord server with the CustomMessages extension Enabled.
    This object purely holds data and does not do any form of validation.
    """

    def __init__(self, messages: {} = None):
        """
        :param messages: A key,value collection of Message objects.
        """
        self.messages: {} = {} if messages is None else messages

    @classmethod
    def from_json(cls, data):
        obj = cls()
        obj.__dict__ = data

        convert_dict_list_json(obj.messages, Message)

        return obj
