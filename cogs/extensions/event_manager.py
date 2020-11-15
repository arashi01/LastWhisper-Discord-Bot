import asyncio
import copy
from datetime import datetime, timedelta
from enum import Enum
from time import strptime, mktime, strftime, asctime

from discord import Embed, Message, HTTPException
from discord.ext import commands, tasks

import utils
from objects import EventConfig, Event, EventReminderTrigger
from objects.configuration import ConfigurationDictionary, Configuration
from utils.cog_class import CogClass
from utils.dialog_utils import yes_no, get_author_written_response, DialogReturn, setup_embed


class States(Enum):
    NAME = "NAME"
    DESCRIPTION = "DESCRIPTION"
    TIME = "TIME"
    NONE = None


class EventManager(CogClass, name=utils.CogNames.EventManager.value):

    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/event_manager", EventConfig)
        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(minutes=1)
    async def loop(self):
        await self.client.wait_until_ready()
        now = datetime.now()

        for guild_id, config in self.guildDict.items():
            if not (len(config.events) and len(config.event_reminder_triggers)):
                continue

            for event in config.events:
                event_datetime = datetime.fromtimestamp(mktime(event.datetime))

                if event_datetime.date() == now.date():
                    if not (channel := self.client.get_guild(guild_id).get_channel(config.reminder_channel_id)):
                        continue

                    for reminder in config.event_reminder_triggers:
                        if (now + timedelta(hours=reminder.hour_diff, minutes=reminder.minute_diff)).time().replace(
                                second=0, microsecond=0) == event_datetime.time():
                            def _add_s(number: int) -> str:
                                return "s" if number > 1 else ""

                            event_dict = {
                                "everyone": "@everyone",
                                "here": "@here",
                                "event_name": event.name,
                                "hours_remaining": f"{reminder.hour_diff} hour{_add_s(reminder.hour_diff)} remaining" if reminder.hour_diff > 0 else "",
                                "minutes_remaining": f"{reminder.minute_diff} minute{_add_s(reminder.minute_diff)} remaining" if reminder.minute_diff > 0 else "",
                                "and": " and " if (reminder.hour_diff * 60) + reminder.minute_diff > 60 else ""
                            }

                            try:
                                await channel.send(reminder.message % event_dict)
                            except HTTPException as e:
                                print(e)

            dif = len(config.events)
            config.events = [_event for _event in config.events if
                             datetime.fromtimestamp(mktime(_event.datetime)) > now]
            if dif > len(config.events):
                self.save_configs(guild_id)

    # region Events
    @commands.group(name="Event", invoke_without_command=True)
    async def event(self, ctx: commands.Context, index: int = None):
        config: EventConfig = self.guildDict[ctx.guild.id]

        if not index:
            embed: Embed = Embed(title="List of Upcoming Events.")
            for i in range(len(config.events)):
                embed.add_field(name=f"Index {i + 1}:", value=config.events[i].name, inline=False)
            await ctx.send(embed=embed)
        else:
            if index - 1 >= len(config.events):
                raise commands.BadArgument(f"Index {index} out of range.")

            event: Event = config.events[index - 1]
            embed = Embed(title=event.name, description=f"{event.description}")

            embed.add_field(name="Date:", value=f"{strftime('%A %b %d', event.datetime)}", inline=False)
            embed.add_field(name="Time:", value=f"{strftime('%H:%M', event.datetime)}", inline=False)

            await ctx.send(embed=embed)

    @commands.Cog.listener(name="on_message")
    async def create_event(self, message: Message):
        if message.author == self.client.user:
            return

        # noinspection PyTypeChecker
        if not self.is_enabled(message):  # This works due to the context have the same setup for getting the guild id.
            return

        config: EventConfig = self.guildDict[message.guild.id]
        if not config.channel_id:
            return

        if not config.channel_id == message.channel.id:
            return

        event: Event = Event()

        content: [str] = [x for x in message.content.split("\n") if x != '']
        state: States = States.NONE
        for line in content:
            if (hold := line.replace(" ", "")).startswith("[") and hold.endswith("]"):
                if hold[1:-1] in (_name_tag := config.name_tag.replace(" ", ""),
                                  _description_tag := config.description_tag.replace(" ", ""),
                                  _datetime_tag := config.datetime_tag.replace(" ", "")):
                    state = {
                        _name_tag: States.NAME,
                        _description_tag: States.DESCRIPTION,
                        _datetime_tag: States.TIME
                    }[hold[1:-1]]
                else:
                    state = States.NONE
                continue

            if state is States.NAME:
                event.name = line
                state = States.NONE
                continue

            if state is States.DESCRIPTION:
                event.description += line + "\n"
                continue

            if state is States.TIME:
                event.datetime = strptime(line)
                state = States.NONE
                continue

        if not event.name or not event.description or not event.datetime:
            return

        guild.events.append(event)
        self.save_configs(message.guild.id)

    @event.command(name="cancel")
    async def cancel_event(self, ctx: commands.Context, index: int = None, confirm: bool = False):
        config: EventConfig = self.guildDict[ctx.guild.id]
        if index - 1 >= len(config.events) or index <= 0:
            raise commands.BadArgument(f"Index {index} out of range.")

        if confirm:
            config.events.pop(index - 1)
            self.save_configs(ctx.guild.id)
        else:
            result: DialogReturn = await yes_no(ctx, "Are you sure?",
                                                f"Are you sure you want to cancel the event {config.events[index - 1].name}?",
                                                timeout=20.0)
            if result == DialogReturn.YES:
                config.events.pop(index - 1)
                self.save_configs(ctx.guild.id)

        await ctx.send("Done.")

    @event.command(name="edit")
    async def edit_event(self, ctx: commands.Context, index: int, name: str = "", time: str = "", *,
                         description: str = ""):
        config: EventConfig = self.guildDict[ctx.guild.id]
        if 0 >= index - 1 >= len(config.events):
            raise commands.BadArgument(f"Index {index} out of range.")

        old_event: Event = copy.deepcopy(new_event := config.events[index - 1])

        if name or time or description:
            if name:
                new_event.name = name
            if description:
                new_event.description = description
            if time:
                try:
                    new_event.datetime = strptime(time)
                except ValueError:
                    raise commands.BadArgument(f"Argument '**{time}**' is not in the correct time format.")
        else:
            _one = "1\N{COMBINING ENCLOSING KEYCAP}"
            _two = "2\N{COMBINING ENCLOSING KEYCAP}"
            _three = "3\N{COMBINING ENCLOSING KEYCAP}"
            _cancel = "\N{Black Square For Stop}"

            def _wizard_check(_reaction, _member):
                return _member == ctx.author and _reaction.emoji in (_one, _two, _three, _cancel)

            wizard_message: Message = await setup_embed(ctx, "Edit Event Wizard.",
                                                        "Hello this is an automatic wizard to allow for simple edit of an event.\n" +
                                                        "Please prepare your changes in advance to save time.\n" +
                                                        "You will have 60 seconds to commit your change.\n" +
                                                        "React with what you want to change. Use the key provided for assistance.",
                                                        [(
                                                            "Key:",
                                                            "> %s: Name\n> %s: Time & Date\n> %s: Description\n> %s: Cancel" %
                                                            (_one, _two, _three, _cancel)
                                                          )],
                                                        60.0)

            while True:
                await wizard_message.add_reaction(_one)
                await wizard_message.add_reaction(_two)
                await wizard_message.add_reaction(_three)
                await wizard_message.add_reaction(_cancel)
                await asyncio.sleep(1)

                try:
                    reaction, member = await self.client.wait_for("reaction_add", timeout=60, check=_wizard_check)
                except asyncio.TimeoutError:
                    await wizard_message.clear_reactions()
                    return
                else:
                    await wizard_message.clear_reactions()
                    if reaction.emoji == _one:
                        text = await get_author_written_response(ctx,
                                                                 "Edit Event Name",
                                                                 "Your next message will be the new name for the event.",
                                                                 timeout=60)
                        if text:
                            new_event.name = text
                            break
                    elif reaction.emoji == _two:
                        text = await get_author_written_response(ctx,
                                                                 "Edit Event Time & Date",
                                                                 "Your next message will be the new time and date for the event.",
                                                                 timeout=60)
                        if text:
                            try:
                                new_event.datetime = strptime(text)
                                break
                            except ValueError:
                                await ctx.send("Invalid time format.", delete_after=3)
                    elif reaction.emoji == _three:
                        text = await get_author_written_response(ctx,
                                                                 "Edit Event Description",
                                                                 "Your next message will be the new description for the event.",
                                                                 timeout=60)

                        if text:
                            new_event.description = text
                            break

                    elif reaction.emoji == _cancel:
                        await wizard_message.delete()
                        return
            await wizard_message.delete()

        title = "Change Event Details?"
        description = "Are you sure you want to change the **Old** event details into the **New** ones?"

        result: DialogReturn = await yes_no(ctx, title, description, [
            ("Old:",
             f"**Name:**\n> {old_event.name}\n**Description:**\n```\n{old_event.description}\n```\n**Time:**\n> {asctime(old_event.datetime)}"),
            ("New:",
             f"**Name:**\n> {new_event.name}\n**Description:**\n```\n{new_event.description}\n```\n**Time:**\n> {asctime(new_event.datetime)}")
        ], timeout=60.0)

        if result in (DialogReturn.NO, DialogReturn.FAILED, DialogReturn.ERROR):
            config.events[index - 1] = old_event

        self.save_configs(ctx.guild.id)

    # endregion

    # region Triggers
    @commands.group(name="Trigger", invoke_without_command=True)
    async def trigger(self, ctx: commands.Context, index: int = None):
        config: EventConfig = self.guildDict[ctx.guild.id]
        embed: Embed = Embed()
        if index:
            if index - 1 >= len(config.event_reminder_triggers):
                raise commands.BadArgument(f"Index {index} out of range.")

            trigger: EventReminderTrigger = config.event_reminder_triggers[index - 1]

            embed.title = f"Index *{index}*"
            embed.add_field(name="Hours Difference", value=f"> {trigger.hour_diff}")
            embed.add_field(name="Minutes Difference", value=f"> {trigger.minute_diff}")
            embed.add_field(name="Message", value=f"```\n{trigger.message}\n```", inline=False)
        else:
            embed.title = "List of Triggers."
            for trigger in config.event_reminder_triggers:
                embed.add_field(name=f"Index {config.event_reminder_triggers.index(trigger) + 1}",
                                value=f"> **Hours Diff:** {trigger.hour_diff}, **Minutes Diff:** {trigger.minute_diff}",
                                inline=False)

        await ctx.send(embed=embed)

    @trigger.command(name="add")
    async def add_trigger(self, ctx: commands.Context, hour_dif: int, minute_dif: int, *, message: str):
        self.guildDict[ctx.guild.id].event_reminder_triggers.append(EventReminderTrigger(hour_dif, minute_dif, message))
        self.save_configs(ctx.guild.id)

    @trigger.command(name="edit")
    async def edit_trigger(self, ctx: commands.Context, index: int, hour_diff: int, minute_diff: int, *, message: str):
        config: EventConfig = self.guildDict[ctx.guild.id]

        if index - 1 >= len(config.event_reminder_triggers) or index <= 0:
            raise commands.BadArgument(f"Index {index} is not a valid index.")

        old_trigger: EventReminderTrigger = copy.deepcopy(new_trigger := config.event_reminder_triggers[index - 1])

        new_trigger.hour_diff = hour_diff
        new_trigger.minute_diff = minute_diff
        new_trigger.message = message

        values = [
            ("Old:",
             f"```\n {old_trigger.message} \n```\n> **Hours Diff**: {old_trigger.hour_diff}, **Minutes Diff**: {old_trigger.minute_diff}"),
            ("New:",
             f"```\n {new_trigger.message} \n```\n> **Hours Diff**: {new_trigger.hour_diff}, **Minutes Diff**: {new_trigger.minute_diff}")
        ]

        result: DialogReturn = await yes_no(ctx, "Are you sure?",
                                            "Are you sure you want to change the trigger from **Old** to **New**?",
                                            values)

        if result in (DialogReturn.NO, DialogReturn.FAILED, DialogReturn.ERROR):
            config.event_reminder_triggers[index - 1] = old_trigger

        self.save_configs(ctx.guild.id)

    @trigger.command(name="remove")
    async def remove_trigger(self, ctx: commands.Context, index: int, confirm: bool = False):
        config: EventConfig = self.guildDict[ctx.guild.id]

        if index - 1 >= len(config.event_reminder_triggers) or index < 0:
            raise commands.BadArgument(f"Index {index} is not a valid index.")

        if confirm:
            config.event_reminder_triggers.pop(index - 1)
            self.save_configs(ctx.guild.id)

        else:
            result: DialogReturn = await yes_no(ctx, "Are you sure?",
                                                f"Are you sure you want to remove the Trigger {index}?", timeout=20.0)
            if result == DialogReturn.YES:
                config.event_reminder_triggers.pop(index - 1)
                self.save_configs(ctx.guild.id)

        await ctx.send("Done.")

    # endregion

    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("channel_id", "channel_id", set=self.set))
        config.add_configuration(Configuration("reminder_channel_id", "reminder_channel_id", set=self.set))
        config.add_configuration(Configuration("name_tag", "name_tag", set=self.set))
        config.add_configuration(Configuration("description_tag", "description_tag", set=self.set))
        config.add_configuration(Configuration("datetime_tag", "datetime_tag", set=self.set))

        config.add_configuration(Configuration("event_ids", "event_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("event_edit_ids", "event_edit_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("event_cancel_ids", "event_cancel_ids", add=self.add, remove=self.remove))

        config.add_configuration(Configuration("trigger_ids", "trigger_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("trigger_edit_ids", "trigger_edit_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("trigger_remove_ids", "trigger_remove_ids", add=self.add, remove=self.remove))

        return config

    @property
    def get_function_roles_reference(self) -> dict:
        return {
            self.event.name: "event_ids",
            self.edit_event.name: "event_edit_ids",
            self.cancel_event.name: "event_cancel_ids",

            self.add_trigger.name: "trigger_ids",
            self.edit_trigger.name: "trigger_edit_ids",
            self.remove_trigger.name: "trigger_remove_ids"
        }


def setup(client: commands.bot):
    client.add_cog(EventManager(client))
