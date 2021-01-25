import os
from abc import ABC
from pathlib import Path
from typing import Union

from discord import Guild, TextChannel, Role, Member
from discord.ext import commands

import utils
from cogs.general import General
from interfaces import CogABCMeta, config, extension
from objects import CustomConfigObject
from utils.helpers import config_helper, save_and_load_helper, role_helper


class CogClass(extension.IExtensionHandler, config.IConfigManager, ABC, commands.Cog, metaclass=CogABCMeta):
    """
    This is an abstract class used to simplify the creation of the Extensions.
    While the class is not required it simplifies the creation and removes redundancy from the rest of the codebase.
    """
    # Static variable declaration.
    _config_dir: Path
    _client: commands.Bot
    _general_cog: General  # As there are some functions in the General Cog I cache it to reduce the number of get_cog calls that are done.
    _config_object: CustomConfigObject.__class__

    def __init__(self, client: commands.bot, config_dir: Path, config_object: CustomConfigObject.__class__) -> None:
        """
        :param client: The Discord client object.
        :param config_dir: The directory where the configurations are expected to be stored.
        :param config_object: A class reference of the object to be initialized during the creation of the configs.
        """
        super().__init__()  # I am certain that this is not needed however in case there is a change in the future I am keeping this here to not break.
        self._client = client
        self._config_dir = config_dir if isinstance(config_dir, Path) else Path(config_dir)

        self._config_object = config_object
        if self._client.is_ready():
            self._general_cog = self._client.get_cog(utils.CogNames.General.value)
            self.load_configs()

    def cog_unload(self):
        from os.path import isfile
        for key, value in self.guildDict.items():
            if not isfile(self._config_dir / (str(key) + save_and_load_helper.default_extension)):
                self.save_configs(key)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self._general_cog = self._client.get_cog(utils.CogNames.General.value)
        self.load_configs()

    @role_helper.cog_check_replacement
    async def cog_check(self, ctx: commands.Context) -> bool:
        pass

    async def cog_after_invoke(self, ctx) -> None:
        await self._general_cog.remove_message(ctx)

    # region Config
    # region Listeners
    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        # This method is used to generate the default configuration files when a server invites the bot.
        if not self._config_object:
            return

        self.save_configs(guild.id)
        self.load_configs(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        # This method is used to remove the configuration files when a server invites the bot.
        if not self._config_object:
            return

        if guild.id not in self.guildDict:
            return

        utils.remove_file(f"{self._config_dir}/{str(guild.id) + save_and_load_helper.default_extension}")
        utils.remove_file(
            f"{self._config_dir}/{str(guild.id) + save_and_load_helper.default_extension + save_and_load_helper.default_disabled_extension}")
        self.guildDict.pop(guild.id)

    # endregion

    # region config interfaces
    def load_configs(self, guild_id: int = None) -> None:
        save_and_load_helper.load_configs_json(self.guildDict, str(self._config_dir), self._config_object,
                                               self._client.guilds, guild_id)
        save_and_load_helper.load_configs(self.guildDict, self._config_dir, self._config_object, self._client.guilds,
                                          guild_id, clear_existing=False)

    def save_configs(self, guild_id: int = None) -> None:
        save_and_load_helper.save_configs(self.guildDict, self._config_dir, self._config_object, guild_id)

    # endregion

    # region extension interfaces
    async def enable(self, ctx: commands.Context) -> None:
        if self.is_enabled(ctx):
            await ctx.reply("Already Enabled.", mention_author=False)
            return

        self.load_configs(guild_id=ctx.guild.id)
        await ctx.reply("Done.", mention_author=False)

    async def disable(self, ctx: commands.Context) -> None:
        if not self.is_enabled(ctx):
            await ctx.reply("Already Disabled.", mention_author=False)
            return

        self.guildDict.pop(ctx.guild.id)
        os.rename(f"{self._config_dir}/{ctx.guild.id}.json", f"{self._config_dir}/{ctx.guild.id}.json.disabled")

        await ctx.reply("Done.", mention_author=False)

    def is_enabled(self, ctx: commands.Context) -> bool:
        return ctx.guild.id in self.guildDict

    # endregion

    def set(self, ctx: commands.Context, variable: str,
            value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = config_helper.set(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def add(self, ctx: commands.Context, variable: str,
            value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = config_helper.add(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def remove(self, ctx: commands.Context, variable: str,
               value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = config_helper.remove(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)
    # endregion
