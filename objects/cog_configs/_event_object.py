from time import struct_time

from objects import CustomConfigObject, TypeObjects


class Event(CustomConfigObject):

    def __init__(self, name: str = None, description: str = "", datetime: struct_time = None):
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
    def __init__(self, hour_diff: int = 0, minute_diff: int = 0, message: str = ""):
        self.hour_diff: int = hour_diff
        self.minute_diff: int = minute_diff
        self.message: str = message


class EventConfig(CustomConfigObject):
    def __init__(self, channel_id: TypeObjects.Channel = None, reminder_channel_id: TypeObjects.Channel = None,
                 name_tag: str = None,
                 description_tag: str = None, datetime_tag: str = None,
                 event_reminder_triggers: [EventReminderTrigger] = None,
                 events: [Event] = None):
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
        obj = cls()
        obj.__dict__ = data

        obj.events = list(map(Event.from_json, obj.events))
        obj.event_reminder_triggers = list(map(EventReminderTrigger.from_json, obj.event_reminder_triggers))

        return obj
