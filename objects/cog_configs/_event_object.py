from datetime import datetime as _datetime

from objects import CustomConfigObject, TypeObjects


class Event(CustomConfigObject):
    """
    Object representing a Event.
    This object purely holds information and does not do any form of validation.
    """

    def __init__(self, name: str = "", description: str = "", datetime: _datetime = None):
        """
        :param name: The name of the event.
        :param description: The description of the event.
        :param datetime: The date and time when the event happens.
        """

        self.name: str = name
        self.description: str = description
        self.datetime: _datetime = datetime

    def __repr__(self):
        return str(self.__dict__)


class EventReminderTrigger(CustomConfigObject):
    """
    Object representing a Trigger that is fired to remind people of an event.
    This object purely holds information and does not do any form of validation.
    """

    def __init__(self, hour_diff=0, minute_diff=0, message=""):
        """
        :param hour_diff: The number of hours different from when the event is meant to take place.
        :param minute_diff: The number of minutes different from when the event is meant to take place.
        :param message: The message that is to be sent when the reminder is is given.
        """

        self.hour_diff: int = hour_diff
        self.minute_diff: int = minute_diff
        self.message: str = message


class EventConfig(CustomConfigObject):
    """
    The config object for the EventManager used by Discord servers with the extension enabled.
    This object purely holds information and does not do any form of validation.
    """

    def __init__(self,
                 channel_id: TypeObjects.Channel = None, reminder_channel_id: TypeObjects.Channel = None,
                 name_tag: str = None, description_tag: str = None, datetime_tag: str = None,
                 event_ids: list = None, event_edit_ids: list = None, event_cancel_ids: list = None,
                 trigger_ids: list = None, trigger_edit_ids: list = None, trigger_remove_ids: list = None,
                 event_reminder_triggers: [EventReminderTrigger] = None, events: [Event] = None):
        """
        :param channel_id: The Discord channel id that is checked for event posts.
        :param reminder_channel_id: The Discord channel id where the reminders are posted.

        :param name_tag: The tag used to represent a name for an event.
        :param description_tag: The tag used to represent a description for an event.
        :param datetime_tag: The tag used to represent a date and time for an event.

        :param event_reminder_triggers: A collection of triggers that are used to remind of events.
        :param events: A key, value collection of the events for a Discord Server.
        """

        self.channel_id: int = channel_id
        self.reminder_channel_id: int = reminder_channel_id

        self.name_tag: str = name_tag
        self.description_tag: str = description_tag
        self.datetime_tag: str = datetime_tag

        self.event_ids: list = event_ids or []
        self.event_edit_ids: list = event_edit_ids or []
        self.event_cancel_ids: list = event_cancel_ids or []

        self.trigger_ids: list = trigger_ids or []
        self.trigger_edit_ids: list = trigger_edit_ids or []
        self.trigger_remove_ids: list = trigger_remove_ids or []

        self.event_reminder_triggers: [EventReminderTrigger] = list(map(lambda a: EventReminderTrigger(**a), event_reminder_triggers or []))
        self.events: [Event] = list(map(lambda a: Event(**a), events or []))

    @classmethod
    def from_json(cls, data):
        obj = super().from_json(data)

        obj.events = list(map(Event.from_json, obj.events))
        obj.event_reminder_triggers = list(map(EventReminderTrigger.from_json, obj.event_reminder_triggers))

        return obj
