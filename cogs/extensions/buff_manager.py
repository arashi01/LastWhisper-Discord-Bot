import datetime
from typing import Union

from discord import TextChannel, Embed
from discord.ext import commands, tasks

import utils
from objects import Week, BuffManagerConfig, Buff
from objects.configuration import Configuration, ConfigurationDictionary
from utils.cog_class import CogClass


class BuffManager(CogClass, name=utils.CogNames.BuffManager.value):
    def __init__(self, client: commands.bot) -> None:
        super().__init__(client, "./config/buff_manager", BuffManagerConfig)
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
                # but index will leave it here unless it starts giving issues. Trying to save memory.

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
            elif action == "view":
                def get_embed() -> Embed:
                    result: Embed = Embed(title=f"Indexes of object **{obj_type}**", description="These are the indexes and the names of the objects registered.")

                    # noinspection PyShadowingNames
                    for index, value in self.guildDict[ctx.guild.id]["buff_list" if obj_type == "buff" else "weeks"].items():
                        result.add_field(name=f"Index {index}", value=f"```\n{value.name}\n```", inline=False)

                    return result

                if len(args) == 0:
                    await ctx.send(embed=get_embed())
                    return

                if len(args) > 1:
                    raise commands.TooManyArguments()

                try:
                    obj: Union[Week, Buff] = self.guildDict[ctx.guild.id]["buff_list" if obj_type == "buff" else "weeks"][str(args[0])]
                except KeyError:
                    await ctx.send(f"Sorry the index {args[0]} is not valid. Please give a correct index.", embed=get_embed())
                    return

                embed = Embed(title=f"**{obj_type}** in Index {args[0]}", description=f"Name of object {obj_type}\n```\n{obj.name}\n```")
                if isinstance(obj, Week):
                    for i in range(0, 6):
                        embed.add_field(name=f"Buff index for {utils.days[i]}", value=obj.get_value(i))
                else:
                    try:
                        embed.set_thumbnail(url=obj.image_url)
                    except Exception:
                        embed.add_field(name="Image error", value="Sorry the url is not a valid image.")

                await ctx.send(embed=embed)
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

    @property
    def get_function_roles_reference(self) -> dict:
        return {
            self.today_buff.qualified_name: "tdb_ids",
            self.tomorrow_buff.qualified_name: "tmb_ids",
            self.week_buffs.qualified_name: "twb_ids",
            self.next_week_buffs.qualified_name: "nwb_ids"
        }
    # endregion


def setup(client: commands.bot):
    client.add_cog(BuffManager(client))
