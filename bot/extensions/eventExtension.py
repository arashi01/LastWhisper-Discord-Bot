import json

from discord.ext.commands import Bot, Cog, command, Context
from discord.ext import tasks
from discord import Message, TextChannel, RawMessageDeleteEvent, RawMessageUpdateEvent, Embed
from enum import Enum
from extensions.configExtension import ConfigManager
from extensions.permissionsExtension import PermissionsManager
from utils.helpers.configManager import ConfigMethodHelpers
from objects.eventManager import ServerConfig, Event, ReminderTrigger
import re

from datetime import datetime, timedelta


class _States(Enum):
    NONE = None,
    NAME = 1,
    DESCRIPTION = 2,
    TIME = 3,
    ADDITIONAL = 4,


class EventManager(Cog):
    save_time_format: str = "%H:%M %m/%d/%Y"
    _dt: datetime = datetime(1970, 1, 1)

    def __init__(self, bot: Bot):
        self._bot: Bot = bot
        self._permission_manager: PermissionsManager
        self.config_settings = {
            "set": {
                "delimiter_pattern": ConfigMethodHelpers.set,
                "announcement_tag": EventManager.set_tag,
                "description_tag": EventManager.set_tag,
                "datetime_tag": EventManager.set_tag,
                "datetime_format": ConfigMethodHelpers.set,
                "listener_channel_id": ConfigMethodHelpers.set,
            },
            "add": {
                "tag_exclusion_list": ConfigMethodHelpers.add,
                "reminders": EventManager.add_reminder,
            },
            "remove": {
                "tag_exclusion_list": ConfigMethodHelpers.remove,
                "reminders": EventManager.remove_reminder,
            },
            "list": {
                "reminders": EventManager.list_reminders,
                "reminder_template": EventManager.reminder_template,
            },
            "settings": {
                "delimiter_pattern": {
                    "value_type": str
                },
                "default_config": ServerConfig,
                "datetime_format": {
                    "value_type": str
                },
                "listener_channel_id": {
                    "value_type": TextChannel
                },
                "tag_exclusion_list": {
                    "value_type": str
                },
            }
        }
        self.permissions = [self.print_event]

        self.loop.start()

        if not self._bot.is_ready():
            return

        self._permission_manager = self._bot.get_cog(PermissionsManager.Name)

        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        self._configs = config_manager.get_cog_configs(self.qualified_name)

    # region Loops

    @tasks.loop(minutes=1)
    async def loop(self):
        now: datetime = datetime.now()
        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        configs: dict = config_manager.get_cog_configs(self.qualified_name)

        for guild_id, v in configs.items():
            try:
                config: ServerConfig = ServerConfig.from_json(v)

                if len(config.events) <= 0 or len(config.reminders) <= 0:
                    continue

                if not config.posting_channel_id:
                    continue

                posting_channel: TextChannel = self._bot.get_channel(int(config.posting_channel_id))
                if not posting_channel:
                    continue

                for reminder in config.reminders:
                    reminder_time: datetime = datetime.strptime(reminder.time_delta, "%H:%M")
                    reminder_time_delta: timedelta = timedelta(hours=reminder_time.hour, minutes=reminder_time.minute)
                    for event in config.events:
                        event_time: datetime = datetime.strptime(event.datetime, self.save_time_format)

                        if now.date() != event_time.date():
                            continue

                        if reminder_time_delta <= (event_time - now) < (reminder_time_delta + timedelta(minutes=1)):
                            message_values: dict = {
                                "event_name": event.name,
                                "hours_diff": str(reminder_time.hour),
                                "minutes_diff": str(reminder_time.minute)
                            }

                            await posting_channel.send(reminder.message.format_map(message_values))

                config.events = [event for event in config.events if (datetime.strptime(event.datetime, self.save_time_format) - now).total_seconds() > 0]
            except Exception as e:
                print(e)

    @loop.before_loop
    async def before_loop(self):
        await self._bot.wait_until_ready()

    # endregion

    # region Commands

    @command(name="Event")
    async def print_event(self, ctx: Context, index: int = None):
        config: ServerConfig = self._get_config(str(ctx.guild.id))
        embed: Embed = Embed()
        if index is not None:
            event: Event = config.events[index % len(config.events)]

            embed.title = event.name
            embed.description = event.description

            for k, v in event.additions.items():
                embed.add_field(name=k, value=v, inline=False)

            time: timedelta = abs(self._dt - datetime.strptime(event.datetime, self.save_time_format))
            embed.add_field(name="Time remaining:", value=f"<t:{int(time.total_seconds())}:R>", inline=False)
            embed.add_field(name="Set For:", value=f"<t:{int(time.total_seconds())}:f>", inline=False)
        else:
            embed.title = "Upcoming Events."

            if len(config.events) > 0:
                for i, event in enumerate(config.events):
                    time: timedelta = abs(self._dt - datetime.strptime(event.datetime, self.save_time_format))
                    embed.add_field(name=f"Event {i}", value=f"{event.name}\n**Begins: <t:{int(time.total_seconds())}:R>**", inline=False)
            else:
                embed.add_field(name="Notice", value="There are no upcoming events.")

            embed.set_footer(text="Do Event [index] for a more detailed view.")

        await ctx.reply(embed=embed, mention_author=False)

    # endregion

    # region Listeners

    @Cog.listener()
    async def on_message(self, message: Message):
        config: ServerConfig = self._get_config(str(message.guild.id))
        if not config.listener_channel_id or str(message.channel.id) != config.listener_channel_id:
            return

        event: Event = self._parse_event(str(message.id), message.content, config)
        if event.validate():
            config.events.append(event)

    @Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        config: ServerConfig = self._get_config(str(payload.guild_id))
        if not config.listener_channel_id or str(payload.channel_id) != config.listener_channel_id:
            return

        event_ids = [x.message_id for x in config.events]
        if (index := event_ids.index(str(payload.message_id)) if str(payload.message_id) in event_ids else None) is None:
            return

        event: Event = self._parse_event(str(payload.message_id), payload.data["content"], config)
        if event.validate():
            config.events[index] = event

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        config: ServerConfig = self._get_config(str(payload.guild_id))
        if not config.listener_channel_id or str(payload.channel_id) != config.listener_channel_id:
            return

        event_ids = [x.message_id for x in config.events]
        if (index := event_ids.index(str(payload.message_id)) if str(payload.message_id) in event_ids else None) is not None:
            config.events.pop(index)

    # endregion

    # region Helper Methods

    def _get_config(self, guild_id: str) -> ServerConfig:
        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        return ServerConfig.from_json(config_manager.get_config(self.qualified_name, guild_id))

    @classmethod
    def _parse_event(cls, message_id: str, content: str, config: ServerConfig) -> Event:
        state: _States = _States.NONE
        event: Event = Event(message_id=str(message_id))

        _pattern_split: list = [line.strip() for line in re.split(config.delimiter_pattern, content) if line]
        _content: dict = {item[0]: item[1] for item in cls._div_chunks(_pattern_split, 2) if len(item) == 2}

        for k, v in _content.items():
            if k == config.announcement_tag:
                event.name = v
                continue

            if k == config.description_tag:
                event.description = v
                continue

            if k == config.datetime_tag:
                event.datetime = datetime.strptime(v, config.datetime_format).strftime(cls.save_time_format)
                continue

            if k not in config.tag_exclusion_list:
                event.additions[k] = v
                continue

        return event

    @staticmethod
    def _div_chunks(lis: list, n: int) -> list[list]:
        for i in range(0, len(lis), n):
            yield lis[i:i + n]

    # endregion

    # region Config Setters.

    @staticmethod
    def set_tag(existing_value, args, settings):
        value: str = args[0]
        if type(value) != str:
            raise TypeError(f"Value {value} is not a string.")

        return value.strip()

    # todo: reminder formatter.
    @staticmethod
    def add_reminder(existing_value, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        try:
            day = ReminderTrigger(**json.loads(args[0]))
            existing_value.append(day)
        except ValueError:
            pass

        return existing_value

    @staticmethod
    def remove_reminder(existing_value, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        value = args[0]
        if type(value) is not int:
            raise ValueError("argument passes is not a valid int")

        existing_value.pop(value)

        return existing_value

    @staticmethod
    async def list_reminders(ctx: Context, key: str, config, args):
        config: ServerConfig = ServerConfig.from_json(config)
        value = args[0] if len(args) > 0 else None
        embed: Embed = Embed(title="Reminder Triggers")

        if type(value) is int:
            reminder: ReminderTrigger = config.reminders[value % len(config.reminders)]
            embed.description = reminder.message
            embed.add_field(name="Time Delta", value=reminder.time_delta)
        else:
            for i, reminder in enumerate(config.reminders):
                embed.add_field(name=f"Index {i}:", value=f"Message: {reminder.message}\nTime Delta: {reminder.time_delta}", inline=False)

        await ctx.reply(embed=embed, mention_author=False)

    @staticmethod
    async def reminder_template(ctx: Context, key, config, args):
        await ctx.reply("\"{\\\\\"message\\\\\": \\\\\"[message here]\\\\\", \\\\\"time_delta\\\\\": \\\\\"[Time delta here in format (HH:MM) (24-hours)]\\\\\"}\"", mention_author=False)

    # endregion

    # region Checks

    def cog_check(self, ctx: Context) -> bool:
        if not self._permission_manager:
            return True

        return self._permission_manager.has_permission(self.qualified_name, ctx.command, ctx.author)

    # endregion


def setup(bot: Bot):
    bot.add_cog(EventManager(bot))
