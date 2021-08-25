import datetime
from discord.ext.commands import Bot, Cog, command, Context
from discord.ext import tasks
from discord import TextChannel, Guild
from extensions.configExtension import ConfigManager
from extensions.permissionsExtension import PermissionsManager
from utils.helpers.buffManager import buff_embed, week_buff_embed
from utils.helpers.configManager import ConfigMethodHelpers
from objects.buffManager import ServerConfig, Week, Buff
from datetime import datetime, timedelta
import json


class BuffManager(Cog):
    def __init__(self, bot: Bot):
        self._permission_manager: PermissionsManager
        self._bot: Bot = bot
        self._configs: dict = {}
        self.config_settings = {
            "set": {
                "message": ConfigMethodHelpers.set,
                "message_channel_id": ConfigMethodHelpers.set,
                "message_sent_hour": BuffManager.set_time,
                "message_weekday": ConfigMethodHelpers.set,
            },
            "add": {
                "days": BuffManager.add_day,
                "weeks": BuffManager.add_week,
            },
            "remove": {
                "days": BuffManager.remove_day,
                "weeks": BuffManager.remove_week,
            },
            "list": {
                "days": BuffManager.list_obj,
                "day_template": BuffManager.list_templates,
                "weeks": BuffManager.list_obj,
                "week_template": BuffManager.list_templates,
            },
            "settings": {
                "default_config": ServerConfig,
                "message_channel_id": {
                    "value_type": TextChannel,
                },
                "message_weekday": {
                    "value_type": int,
                    "range": {
                        "min_inclusive": 1,
                        "max_inclusive": 7
                    },
                },
            },
        }
        self.permissions = [self.today_buff, self.tomorrow_buff, self.week_buff, self.next_week_buff]

        # self.loop.add_exception_type(asyncpg.PostgresConnectionError)
        self.loop.start()

        if not self._bot.is_ready():
            return

        self._permission_manager = self._bot.get_cog(PermissionsManager.Name)

        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        self._configs = config_manager.get_cog_configs(self.qualified_name)

    def cog_unload(self):
        self.loop.stop()

    # region Commands

    @command(name="todays_buff", aliases=["tdb"])
    async def today_buff(self, ctx: Context):
        today: datetime = datetime.today()
        day: Buff = self._get_day(today, self._get_configs(ctx))

        await ctx.reply(embed=buff_embed(day, today), mention_author=False)

    @command(name="tomorrows_buff", aliases=["tmb"])
    async def tomorrow_buff(self, ctx: Context):
        tomorrow: datetime = datetime.today() + timedelta(days=1)
        day: Buff = self._get_day(tomorrow, self._get_configs(ctx))

        await ctx.reply(embed=buff_embed(day, tomorrow), mention_author=False)

    @command(name="weeks_buffs", aliases=["twb"])
    async def week_buff(self, ctx: Context):
        config: ServerConfig = self._get_configs(ctx)

        this_week: datetime = datetime.today()
        week: Week = self._get_week(this_week, config)

        await ctx.reply(embed=week_buff_embed(week, config.buffs, this_week), mention_author=False)

    @command(name="next_weeks_buffs", aliases=["nwb"])
    async def next_week_buff(self, ctx: Context):
        config: ServerConfig = self._get_configs(ctx)

        next_week: datetime = datetime.today() + timedelta(weeks=1)
        week: Week = self._get_week(next_week, config)

        await ctx.reply(embed=week_buff_embed(week, config.buffs, next_week), mention_author=False)

    # endregion

    # region Config helper methods
    @staticmethod
    def set_time(existing_value: str, args, settings):
        arg = args[0]

        if not type(arg) is str:
            raise TypeError(f"value {arg} does not match type {type(str)}")

        try:
            # if a value error is thrown it means the format was wrong.
            datetime.strptime(arg, "%H:%M")
            return arg
        except ValueError:
            raise ValueError(f"value {arg} is not in the correct format Hour:Minutes eg. 18:07 or 07:56")

    @staticmethod
    def add_day(existing_value: list, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        try:
            day = Buff(**json.loads(args[0]))
            existing_value.append(day)
        except ValueError:
            pass

        return existing_value

    @staticmethod
    def remove_day(existing_value: list, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        value = args[0]
        if type(value) is not int:
            raise ValueError("argument passes is not a valid int")

        existing_value.pop(value)

        return existing_value

    @staticmethod
    def add_week(existing_value: list, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        try:
            week = Week(**json.loads(args[0]))
            existing_value.append(week)
        except ValueError:
            pass

        return existing_value

    @staticmethod
    def remove_week(existing_value: list, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        value = args[0]
        if type(value) is not int:
            raise ValueError("argument passes is not a valid int")

        existing_value.pop(value)

        return existing_value

    @staticmethod
    async def list_templates(ctx: Context, key: str, _, __):
        await ctx.reply(
            "\"{\\\\\"buff\\\\\": \\\\\"[buff text here]\\\\\", \\\\\"image_url\\\\\": \\\\\"[image url here]\\\\\"}\""
            if key == "day_template" else
            "\"{\\\\\"days\\\\\": [\\\\\"[Monday]\\\\\",\\\\\"[Tuesday]\\\\\",\\\\\"[Wednesday]\\\\\",\\\\\"[Thursday]\\\\\",\\\\\"[Friday]\\\\\",\\\\\"[Saturday]\\\\\",\\\\\"[Sunday]\\\\\"]}\"",
            mention_author=False)

    @staticmethod
    async def list_obj(ctx: Context, key: str, config, args):
        config: ServerConfig = ServerConfig.from_json(config)
        value = args[0] if len(args) > 0 else None

        if type(value) is int:
            await ctx.reply(
                embed=buff_embed(config.buffs[value % len(config.buffs)], datetime.min) if key == "days" else
                week_buff_embed(config.weeks[value % len(config.weeks)], config.buffs, datetime.min),
                mention_author=False)
            return

        if key == "days":
            for day in config.buffs:
                await ctx.reply(embed=buff_embed(day, datetime.min), mention_author=False)
        else:
            for week in config.weeks:
                await ctx.reply(embed=week_buff_embed(week, config.buffs, datetime.min), mention_author=False)

    # endregion

    # region helper methods
    def _get_configs(self, ctx: Context) -> ServerConfig:
        config_cog: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        return ServerConfig.from_json(config_cog.get_config(self.qualified_name, str(ctx.guild.id)))

    @staticmethod
    def _get_day(date: datetime, config: ServerConfig) -> Buff:
        if len(config.buffs) <= 0:
            return Buff("No data set")

        week: Week = BuffManager._get_week(date, config)
        day: Buff = next((x for x in config.buffs if x.uuid == week.days[date.isoweekday() - 1]), Buff("Missing data"))

        return day

    @staticmethod
    def _get_week(date: datetime, config: ServerConfig) -> Week:
        if len(config.weeks) <= 0:
            return Week()

        return config.weeks[date.isocalendar().week % len(config.weeks)]

    # endregion

    # region Listeners

    @Cog.listener()
    async def on_ready(self):
        self._permission_manager = self._bot.get_cog(PermissionsManager.Name)

        cog: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        self._configs = cog.get_cog_configs(self.qualified_name)

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        cog: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        cog.set_config(self.qualified_name, str(guild.id), ServerConfig().to_json)
        self._configs = cog.get_cog_configs(self.qualified_name)

    # endregion

    # region Timers

    @tasks.loop(minutes=1)
    async def loop(self):
        now: datetime = datetime.now()

        for k, v in self._configs.items():
            config: ServerConfig = ServerConfig.from_json(v)
            # check if message channel was set.
            if not config.message_channel_id:
                continue
            channel: TextChannel = self._bot.get_channel(int(config.message_channel_id))
            if not channel:
                print("Channel not found.")
                continue

            # check if the hour was set.
            if config.message_sent_hour:
                if now.time().strftime("%H:%M") == config.message_sent_hour:
                    await channel.send(config.message if config.message else "Today's buffs shall be.",
                                       embed=buff_embed(self._get_day(now, config), now))

                    # check if the weekday was set.
                    if config.message_weekday:
                        if now.isoweekday() == config.message_weekday:
                            await channel.send(embed=week_buff_embed(self._get_week(now, config), config.buffs, now))

    @loop.before_loop
    async def before_loop(self):
        # If i understood the logic here this will wait first before the loop is began that way the first minute is not lost.
        await self._bot.wait_until_ready()

    # endregion

    # region Checks

    def cog_check(self, ctx: Context) -> bool:
        if not self._permission_manager:
            return True

        return self._permission_manager.has_permission(self.qualified_name, ctx.command, ctx.author)

    # endregion


def setup(bot: Bot):
    bot.add_cog(BuffManager(bot))
