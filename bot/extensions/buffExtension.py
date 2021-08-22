import datetime

from discord.ext.commands import Bot, Cog, command, Context
from discord import TextChannel
from extensions.configExtension import ConfigManager, ConfigMethodHelpers
from utils.helpers.buffManager import buff_embed, week_buff_embed
from objects.buffManager import ServerConfig, Week, Day
from datetime import datetime, timedelta
import json


class BuffManager(Cog):
    def __init__(self, bot: Bot):
        self._bot: Bot = bot
        self.config_settings = {
            "set": {
                "message_channel_id": ConfigMethodHelpers.set
            },
            "add": {
                "days": BuffManager.add_day,
                "weeks": BuffManager.add_week
            },
            "remove": {
                "days": BuffManager.remove_day,
                "weeks": BuffManager.remove_week
            },
            "list": {
                "day_template": BuffManager.list_templates,
                "week_template": BuffManager.list_templates,
                "days": BuffManager.list_obj,
                "weeks": BuffManager.list_obj
            },
            "settings": {
                "message_channel_id": {
                    "value_type": TextChannel
                },
                "default_config": ServerConfig
            }
        }
        self.config_obj = ServerConfig

    # region Commands

    @command(name="todays_buff", aliases=["tdb"])
    async def today_buff(self, ctx: Context):
        today: datetime = datetime.today()
        day: Day = self._get_day(today, self._get_configs(ctx))

        await ctx.reply(embed=buff_embed(day, today), mention_author=False)

    @command(name="tomorrows_buff", aliases=["tmb"])
    async def tomorrow_buff(self, ctx: Context):
        tomorrow: datetime = datetime.today() + timedelta(days=1)
        day: Day = self._get_day(tomorrow, self._get_configs(ctx))

        await ctx.reply(embed=buff_embed(day, tomorrow), mention_author=False)

    @command(name="weeks_buffs", aliases=["twb"])
    async def week_buff(self, ctx: Context):
        config: ServerConfig = self._get_configs(ctx)

        this_week: datetime = datetime.today()
        week: Week = self._get_week(this_week, config)

        await ctx.reply(embed=week_buff_embed(week, config.days, this_week), mention_author=False)

    @command(name="next_weeks_buffs", aliases=["nwb"])
    async def next_week_buff(self, ctx: Context):
        config: ServerConfig = self._get_configs(ctx)

        next_week: datetime = datetime.today() + timedelta(weeks=1)
        week: Week = self._get_week(next_week, config)

        await ctx.reply(embed=week_buff_embed(week, config.days, next_week), mention_author=False)

    # endregion

    # region Config helper methods
    @staticmethod
    def add_day(existing_value: list, args, settings):
        if type(existing_value) is not list:
            existing_value = []

        try:
            day = Day(**json.loads(args[0]))
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
        config: ServerConfig = ServerConfig.from_dict(config)
        value = args[0] if len(args) > 0 else None

        if type(value) is int:
            await ctx.reply(embed=buff_embed(config.days[value % len(config.days)], datetime.min) if key == "days" else
                            week_buff_embed(config.weeks[value % len(config.weeks)], config.days, datetime.min),
                            mention_author=False)
            return

        if key == "days":
            for day in config.days:
                await ctx.reply(embed=buff_embed(day, datetime.min), mention_author=False)
        else:
            for week in config.weeks:
                await ctx.reply(embed=week_buff_embed(week, config.days, datetime.min), mention_author=False)

    # endregion

    # region helper methods
    def _get_configs(self, ctx: Context) -> ServerConfig:
        config_cog: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        return ServerConfig.from_dict(config_cog.get_config(self.qualified_name, str(ctx.guild.id)))

    @staticmethod
    def _get_day(date: datetime, config: ServerConfig) -> Day:
        if len(config.days) <= 0:
            return Day("No data set")

        week: Week = BuffManager._get_week(date, config)
        day: Day = next((x for x in config.days if x.uuid == week.days[date.isoweekday() - 1]), Day("Missing data"))

        return day

    @staticmethod
    def _get_week(date: datetime, config: ServerConfig) -> Week:
        if len(config.weeks) <= 0:
            return Week()

        return config.weeks[date.isocalendar().week % len(config.weeks)]
    # endregion


def setup(bot: Bot):
    bot.add_cog(BuffManager(bot))
