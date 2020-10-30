from discord.ext import commands, tasks
from discord import Embed, Message
from enum import Enum
from time import strptime, localtime, struct_time, mktime, strftime
from datetime import datetime

import utils
from objects.configuration import ConfigurationDictionary, Configuration
from utils.cog_class import CogClass

from objects import EventConfig, Event, EventReminderTrigger


class States(Enum):
    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    TIME = "TIME"
    NONE = None


class EventManager(CogClass, name=utils.CogNames.EventManager.value):

    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/event_manager", EventConfig)
        self.loop.start()
        self.approved_roles_dict = {
            "add_trigger": None,
            "get_event_details": None
        }

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(minutes=1)
    async def loop(self):
        await self.client.wait_until_ready()
        now: struct_time = struct_time(localtime())

        guild: EventConfig
        for guild_id, guild in self.guildDict.items():
            if not len(guild.events) >= 1:
                continue

            if not len(guild.event_reminder_triggers) >= 1:
                continue

            for event in guild.events:
                if event.datetime.tm_mday == now.tm_mday and event.datetime.tm_mon == now.tm_mon:
                    channel = self.client.get_guild(guild_id).get_channel(guild.reminder_channel_id)

                    reminder: EventReminderTrigger
                    for reminder in guild.event_reminder_triggers:
                        if (
                                event.datetime.tm_hour - reminder.hour_diff,
                                event.datetime.tm_min - reminder.minute_diff) == (
                                now.tm_hour, now.tm_min):
                            event_dict = {
                                "event_name": event.name,
                                "time_remaining": (f"{reminder.hour_diff} hour{'s' if reminder.hour_diff > 1 else ''}" if reminder.hour_diff > 1 else '') +
                                                  (" and " if reminder.hour_diff > 0 and reminder.minute_diff > 0 else "") +
                                                  (f"{reminder.minute_diff} minute{'s' if reminder.minute_diff > 1 else ''}" if reminder.minute_diff > 1 else '')
                            }

                            await channel.send(reminder.message % event_dict)

            dif = len(guild.events)
            guild.events = [x for x in guild.events if
                            not (datetime.fromtimestamp(mktime(x.datetime)) < datetime.fromtimestamp(mktime(now)))]
            if dif > len(guild.events):
                self.save_configs(guild_id)

    @commands.command()
    async def get_event_details(self, ctx: commands.Context, index: int = -1):
        guild: EventConfig = self.guildDict[ctx.guild.id]

        if index <= -1:
            embed: Embed = Embed(title="List of Upcoming Events.")
            for i in range(len(guild.events)):
                embed.add_field(name=f"Index {i}:", value=guild.events[i].name, inline=False)
            await ctx.send(embed=embed)
        else:
            if index > len(guild.events):
                await ctx.send("Index is outside the range of events.")
                return

            event: Event = guild.events[index]
            embed = Embed(title=event.name, description=f"{event.description}")

            embed.add_field(name="Date:", value=f"{strftime('%A %b %d', event.datetime)}", inline=False)
            embed.add_field(name="Time:", value=f"{strftime('%H:%M', event.datetime)}", inline=False)

            await ctx.send(embed=embed)

    @commands.command()
    async def add_trigger(self, ctx: commands.Context, hour_dif: int, minute_dif: int, message: str):
        self.guildDict[ctx.guild.id].event_reminder_triggers.append(EventReminderTrigger(hour_dif, minute_dif, message))
        self.save_configs(ctx.guild.id)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.client.user:
            return

        if not self.guildDict.__contains__(message.guild.id):
            return

        guild: EventConfig = self.guildDict[message.guild.id]
        if not guild.channel_id == message.channel.id:
            return

        event: Event = Event()

        content: [str] = message.content.split("\n")
        content = [x for x in content if x != '']
        state: States = States.NONE
        for line in content:
            if (hold := line.replace(" ", "")).startswith("[") and hold.endswith("]"):
                if (guild.name_tag.replace(" ", ""), guild.description_tag.replace(" ", ""),
                        guild.datetime_tag.replace(" ", "")).__contains__(hold[1:-1]):

                    state = {
                        guild.name_tag.replace(" ", ""): States.NAME,
                        guild.description_tag.replace(" ", ""): States.DESCRIPTION,
                        guild.datetime_tag.replace(" ", ""): States.TIME
                    }[hold[1:-1]]
                else:
                    state = States.NONE
                continue

            if state is States.NAME:
                event.name = line
                state = States.NONE
                continue

            if state is States.DESCRIPTION:
                event.description += (line + "\n")
                continue

            if state is States.TIME:
                event.datetime = strptime(line)
                state = States.NONE
                continue

        if not event.name or not event.description or not event.datetime:
            return

        guild.events.append(event)
        self.save_configs(message.guild.id)

    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("channel_id", "channel_id", set=self.set))
        config.add_configuration(Configuration("reminder_channel_id", "reminder_channel_id", set=self.set))
        config.add_configuration(Configuration("name_tag", "name_tag", set=self.set))
        config.add_configuration(Configuration("description_tag", "description_tag", set=self.set))
        config.add_configuration(Configuration("datetime_tag", "datetime_tag", set=self.set))

        return config


def setup(client: commands.bot):
    client.add_cog(EventManager(client))
