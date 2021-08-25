from utils.interfaces import JsonSerializable


class ReminderTrigger(JsonSerializable):
    def __init__(self, message: str = None, time_delta: str = None, *_, **__):
        self.message: str = message
        self.time_delta: str = time_delta


class Event(JsonSerializable):
    def __init__(self, message_id: str = None, name: str = None, description: str = None, datetime: str = None, additions: dict[str, str] = None, *_, **__):
        self.message_id: str = message_id
        self.name: str = name
        self.description: str = description
        self.datetime: str = datetime
        self.additions: dict[str, str] = additions if additions else {}

    def validate(self) -> bool:
        """
        Ensures that the object is a valid event.
        :rtype: bool
        """
        return self.name is not None and self.description and self.datetime


class ServerConfig(JsonSerializable):
    def __init__(self, delimiter_pattern: str = "\\[(.*?)\\]", announcement_tag: str = None, description_tag: str = None,
                 datetime_tag: str = None, datetime_format: str = None, tag_exclusion_list: list[str] = None,
                 posting_channel_id: str = None, listener_channel_id: str = None, events: list[Event] = None,
                 reminders: list[ReminderTrigger] = None, *_, **__):

        # Listener and parser configs
        self.listener_channel_id: str = listener_channel_id
        self.delimiter_pattern: str = delimiter_pattern
        self.announcement_tag: str = announcement_tag
        self.description_tag: str = description_tag
        self.datetime_tag: str = datetime_tag
        self.datetime_format: str = datetime_format
        self.tag_exclusion_list: list[str] = tag_exclusion_list if tag_exclusion_list else []

        # Reminder poster configs
        self.posting_channel_id: str = posting_channel_id

        # actual objects
        self.events: list[Event] = events if events else []
        self.reminders: list[ReminderTrigger] = reminders if reminders else []

    @classmethod
    def from_json(cls, data: dict):
        obj: cls = super().from_json(data)

        events: list[Event] = []
        for event in obj.events:
            events.append(Event(**event) if type(event) == dict else event)
        obj.events = events

        reminders: list[ReminderTrigger] = []
        for reminder in obj.reminders:
            reminders.append(ReminderTrigger(**reminder) if type(reminder) is dict else reminder)
        obj.reminders = reminders

        return obj
