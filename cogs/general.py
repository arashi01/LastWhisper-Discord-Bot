from typing import Union
from pathlib import Path as _Path

from discord import TextChannel, Role, Member, Guild
from discord.ext import commands
from discord.ext.commands import Context

import utils
from objects import GeneralConfig
from configuration import ConfigurationDictionary, Configuration
from utils.helpers import config_helper, save_and_load_helper, role_helper
from interfaces import CogABCMeta, roles
from interfaces import config, extension
from objects.role_object import RoleObject


class General(extension.IEnabled, config.IConfigManager, roles.IRoleProvider, commands.Cog,
              name=utils.CogNames.General.value, metaclass=CogABCMeta):

    _config_dir: _Path
    _config_object = GeneralConfig.__class__

    def __init__(self, client: commands.bot):
        super().__init__()
        self._client = client
        self._config_dir: _Path = _Path("./config/general")
        self._general_cog: General = self
        self.guildDict: dict = {}

        if client.is_ready():
            self.on_ready()

    def on_ready(self) -> None:
        self.load_configs()

        for guild in [guild.id for guild in self._client.guilds if guild.id not in self.guildDict]:
            self.save_configs(guild)

    @commands.Cog.listener("on_ready")
    async def _on_ready(self) -> None:
        self.on_ready()

    def get_guild_prefix(self, guild_id: int):
        try:
            return self.guildDict[guild_id].prefix
        except KeyError:
            return "/"

    @staticmethod
    def get_prefix(client: commands.bot, message):
        return client.get_cog(utils.CogNames.General.value).get_guild_prefix(message.guild.id)

    @commands.command(name="LastWhisper_ChangePrefix")
    async def change_prefix(self, ctx: commands.Context, prefix: str = "/"):
        guild: GeneralConfig = self.guildDict[ctx.guild.id]
        guild.prefix = prefix
        self.save_configs(ctx.guild.id)
        await ctx.reply(f"Prefix changed to {prefix}", mention_author=False)

    async def remove_message(self, ctx: commands.Context):
        guild: GeneralConfig = self.guildDict[ctx.guild.id]
        if guild.should_clear_command:
            await ctx.message.delete()
        elif guild.clear_command_exception_list.__contains__(ctx.author.id):
            await ctx.message.delete()

    def get_management_role_ids(self, guild_id: int):
        try:
            return self.guildDict[guild_id].management_role_ids
        except KeyError:
            return []

    @property
    def get_configs(self) -> ConfigurationDictionary:
        _config: ConfigurationDictionary = ConfigurationDictionary()

        _config.add_configuration(Configuration("should_clear_commands", "should_clear_command", set=self.set))
        _config.add_configuration(
            Configuration("clear_command_exception_list", "clear_command_exception_list", add=self.add,
                          remove=self.remove))
        _config.add_configuration(
            Configuration("management_role_ids", "management_role_ids", add=self.add, remove=self.remove))

        return _config

    @role_helper.cog_check_replacement
    async def cog_check(self, ctx: commands.Context) -> bool:
        pass

    @property
    def role_list(self) -> dict:
        return {
            self.change_prefix.name: RoleObject(self.change_prefix.name, "change_prefix", True)
        }

    # region Configs
    def is_enabled(self, ctx: Context) -> bool:
        return ctx.guild.id in self.guildDict

    def load_configs(self, guild_id: int = None) -> None:
        save_and_load_helper.load_configs(self.guildDict, self._config_dir, GeneralConfig, self._client.guilds)

    def save_configs(self, guild_id: int = None) -> None:
        save_and_load_helper.save_configs(self.guildDict, self._config_dir, GeneralConfig, guild_id)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        self.save_configs(guild.id)
        self.load_configs(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        if guild.id not in self.guildDict:
            return

        utils.remove_file(f"{self._config_dir}/{str(guild.id) + save_and_load_helper.default_extension}")
        utils.remove_file(
            f"{self._config_dir}/{str(guild.id) + save_and_load_helper.default_extension + save_and_load_helper.default_disabled_extension}")
        self.guildDict.pop(guild.id)

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


def setup(client: commands.bot):
    client.add_cog(General(client))
