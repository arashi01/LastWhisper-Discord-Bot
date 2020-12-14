from time import struct_time

from objects import CustomConfigObject, TypeObjects, TypeList


class Event(CustomConfigObject):
    """ Object representing a Event.

    This object purely holds information and does not do any form of validation.
    """

    def __init__(self, name: str = "", description: str = "", datetime: struct_time = None):
        """
        :param name: The name of the event.
        :type name: str
        :param description: The description of the event.
        :type description: str
        :param datetime: The date and time when the event happens.
        :type datetime: struct_time
        """

        self.name: str = name
        self.description: str = description
        self.datetime: struct_time = datetime

    @classmethod
    def from_json(cls, data):
        obj = cls()
        obj.__dict__ = data

        obj.datetime = struct_time(obj.datetime)

        return obj


class EventReminderTrigger(CustomConfigObject):
    """ Object representing a Trigger that is fired to remind people of an event.

    This object purely holds information and does not do any form of validation.
    """

    def __init__(self, hour_diff=0, minute_diff=0, message=""):
        """
        :param hour_diff: The number of hours different from when the event is meant to take place.
        :type hour_diff: int
        :param minute_diff: The number of minutes different from when the event is meant to take place.
        :type minute_diff: int
        :param message: The message that is to be sent when the reminder is is given.
        :type message: str
        """

        self.hour_diff: int = hour_diff
        self.minute_diff: int = minute_diff
        self.message: str = message


class EventConfig(CustomConfigObject):
    """ The config object for the EventManager used by Discord servers with the extension enabled.

    This object purely holds information and does not do any form of validation.
    """

    def __init__(self,
                 channel_id: TypeObjects.Channel = None, reminder_channel_id: TypeObjects.Channel = None,
                 name_tag: str = None, description_tag: str = None, datetime_tag: str = None,
                 event_reminder_triggers: [EventReminderTrigger] = None, events: [Event] = None):
        """
        :param channel_id: The Discord channel id that is checked for event posts.
        :type channel_id: TypeObjects.Channel
        :param reminder_channel_id: The Discord channel id where the reminders are posted.
        :type reminder_channel_id: TypeObjects.Channel

        :param name_tag: The tag used to represent a name for an event.
        :type name_tag: str
        :param description_tag: The tag used to represent a description for an event.
        :type description_tag: str
        :param datetime_tag: The tag used to represent a date and time for an event.
        :type datetime_tag: str

        :param event_reminder_triggers: A collection of triggers that are used to remind of events.
        :type event_reminder_triggers: list
        :param events: A key, value collection of the events for a Discord Server.
        :type events: dict
        """

        self.channel_id: int = channel_id
        self.reminder_channel_id: int = reminder_channel_id

        self.name_tag: str = name_tag
        self.description_tag: str = description_tag
        self.datetime_tag: str = datetime_tag

        self.event_ids: TypeList = TypeList(TypeObjects.Role)
        self.event_edit_ids: TypeList = TypeList(TypeObjects.Role)
        self.event_cancel_ids: TypeList = TypeList(TypeObjects.Role)

        self.trigger_ids: TypeList = TypeList(TypeObjects.Role)
        self.trigger_edit_ids: TypeList = TypeList(TypeObjects.Role)
        self.trigger_remove_ids: TypeList = TypeList(TypeObjects.Role)

        self.event_reminder_triggers: [
            EventReminderTrigger] = event_reminder_triggers if event_reminder_triggers else []
        self.events: [Event] = [] if not events else events

    @classmethod
    def from_json(cls, data):
        obj = super().from_json(data)

        obj.events = list(map(Event.from_json, obj.events))
        obj.event_reminder_triggers = list(map(EventReminderTrigger.from_json, obj.event_reminder_triggers))

        return obj
