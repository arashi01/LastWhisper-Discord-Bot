import datetime
import json

from discord import TextChannel, Member, Role
from discord.ext import commands, tasks
from discord.utils import get
from typing import Union

import utils
from utils.cog_class import CogClass
from objects import Week, BuffManagerConfig, Buff
from objects.configuration import Configuration, ConfigurationDictionary


class BuffManager(CogClass, name=utils.CogNames.BuffManager.value):
    def __init__(self, client: commands.bot) -> None:
        super().__init__(client, "./config/buff_manager", BuffManagerConfig)
        self.approved_roles_dict = {
            "today_buff": "today_buff_approved_roles_ids",
            "tomorrow_buff": "tomorrows_buff_approved_roles_ids",
            "week_buffs": "this_week_buffs_approved_roles_ids",
            "next_week_buffs": "next_week_buffs_approved_roles_ids"
        }
        self.today = datetime.datetime.now()

        self.loop.start()

    def cog_unload(self) -> None:
        self.loop.cancel()

    @tasks.loop(minutes=1)
    async def loop(self) -> None:
        await self.client.wait_until_ready()
        self.today = datetime.datetime.now()

        for key, guild in self.guildDict.items():

            if self.today.hour == guild.mm_hour and self.today.minute == 0:
                week, buff = self.get_week_buff(guild, self.today)
                morning_message_channel: TextChannel = self.client.get_channel(guild.mm_channel_id)

                # Posts the daily buff message.
                await morning_message_channel.send("Good morning Everyone!",
                                                   embed=utils.get_date_buff_embed(
                                                       "Today's buff shall be:",
                                                       self.today,
                                                       buff
                                                   ))

                # Posts the weeks buffs message.
                if self.today.weekday() == 0:
                    await morning_message_channel.send(
                        embed=utils.get_weeks_buff_embed(
                            week,
                            guild.buff_list
                        ))

    @commands.command(aliases=["today'sBuff", "tdb"])
    async def today_buff(self, ctx: commands.Context) -> None:
        guild: BuffManagerConfig = self.guildDict[ctx.guild.id]

        _, buff = self.get_week_buff(guild, self.today)

        await ctx.send(embed=utils.get_date_buff_embed(
            "Today's buff shall be:",
            self.today,
            buff
        ))

    @commands.command(aliases=["tomorrow'sBuff", "trb", "tmb"])
    async def tomorrow_buff(self, ctx: commands.Context) -> None:
        guild: BuffManagerConfig = self.guildDict[ctx.guild.id]

        tomorrow = self.today + datetime.timedelta(days=1)
        _, buff = self.get_week_buff(guild, tomorrow)

        await ctx.send(embed=utils.get_date_buff_embed(
            "Tomorrow's buff shall be:",
            tomorrow,
            buff,
        ))

    @commands.command(aliases=["thisWeek'sBuffs", "wbs", "twb"])
    async def week_buffs(self, ctx: commands.Context) -> None:
        guild: BuffManagerConfig = self.guildDict[ctx.guild.id]

        week, _ = self.get_week_buff(guild, self.today)

        await ctx.send(embed=utils.get_weeks_buff_embed(
            week,
            guild.buff_list
        ))

    @commands.command(aliases=["nextWeek'sBuffs", "nwb"])
    async def next_week_buffs(self, ctx: commands.Context) -> None:
        guild: BuffManagerConfig = self.guildDict[ctx.guild.id]

        week, _ = self.get_week_buff(guild, self.today + datetime.timedelta(days=7))

        await ctx.send(embed=utils.get_weeks_buff_embed(
            week,
            guild.buff_list
        ))

    @staticmethod
    def get_week_buff(config: BuffManagerConfig, date: datetime) -> (int, int):
        (row, col) = utils.get_index(date, len(config.weeks))
        week: Week = config.weeks[list(config.weeks.keys())[row]]
        buff: Buff = config.buff_list[list(config.buff_list.keys())[week.get_value(col)]]
        return week, buff

    @commands.command(name="BuffManager")
    async def buff_manager(self, ctx: commands.Context, obj_type: str, action: str = None, *args) -> None:
        if obj_type in ("week", "buff"):
            if action == "add":
                if len(args) != (len_hold := (8 if obj_type == "week" else 2)):
                    raise commands.BadArgument(f"Must be {len_hold} arguments.")
                del len_hold
                # I cannot tell if this is a good idea in any way, shape or form,
                # but i will leave it here unless it starts giving issues. Trying to save memory.

                obj: Union[Week, Buff] = Week(*args) if obj_type == "week" else Buff(*args)
                config: BuffManagerConfig = self.guildDict[ctx.guild.id]

                index: int = 0
                for key in sorted(config["buff_list" if obj_type == "buff" else "weeks"].keys()):
                    if int(key) > index:
                        break
                    else:
                        index += 1

                config["buff_list" if obj_type == "buff" else "weeks"][str(index)] = obj
                self.save_configs(guild_id=ctx.guild.id)
            elif action == "remove":
                try:
                    if len(args) != 1:
                        raise commands.BadArgument("Arguments must be 1.")

                    self.guildDict[ctx.guild.id]["buff_list" if obj_type == "buff" else "weeks"].pop(*args)
                    self.save_configs(ctx.guild.id)
                except KeyError:
                    await ctx.send("Sorry the index is not valid!")
            elif action == "":
                await ctx.send(f"This is an example preview cause the dev got lazy.")
            else:
                await ctx.send(f"There is no action with the name {action}.")
        else:
            await ctx.send(f"Sorry I do not know about object {obj_type}.")

    # region Config
    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("mm_channel_id", "mm_channel_id", set=self.set))
        config.add_configuration(Configuration("mm_hour", "mm_hour", set=self.set))

        config.add_configuration(Configuration("tdb_ids", "tdb_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("tmb_ids", "tmb_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("twb_ids", "twb_ids", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("nwb_ids", "nwb_ids", add=self.add, remove=self.remove))
        return config
    # endregion


def setup(client: commands.bot):
    client.add_cog(BuffManager(client))
