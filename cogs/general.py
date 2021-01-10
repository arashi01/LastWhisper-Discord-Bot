from typing import Union
from pathlib import Path as _Path

from discord import TextChannel, Role, Member
from discord.ext import commands
from discord.ext.commands import Context

import utils
from objects import GeneralConfig
from configuration import ConfigurationDictionary, Configuration
from utils.helpers import ConfigHelper, SaveLoadHelper
from interfaces import CogABCMeta
from interfaces import IConfig, IExtension


class General(IExtension.IsEnabled, IConfig.Config, commands.Cog, name=utils.CogNames.General.value, metaclass=CogABCMeta):
    def __init__(self, client: commands.bot):
        super().__init__()
        self.client = client
        self.config_dir:_Path = _Path("./config/general")
        self.config_object = GeneralConfig.__class__
        self.general_cog: General = self
        self.guildDict: dict = {}

        if client.is_ready():
            self.on_ready()

    def on_ready(self) -> None:
        self.load_configs()

        for guild in [guild.id for guild in self.client.guilds if guild.id not in self.guildDict]:
            self.save_configs(guild)
            
    @commands.Cog.listener("on_ready")
    async def _on_ready(self) -> None:
        self.on_ready()

    @staticmethod
    def get_prefix(client: commands.bot, message):
        try:
            return client.get_cog(utils.CogNames.General.value).guildDict[message.guild.id].prefix
        except KeyError:
            return "|"

    @commands.command(name="changePrefix")
    async def change_prefix(self, ctx: commands.Context, prefix: str = "|"):
        guild: GeneralConfig = self.guildDict[ctx.guild.id]
        guild.prefix = prefix
        self.save_configs(ctx.guild.id)
        await ctx.send(f"Prefix changed to {prefix}")

    async def remove_message(self, ctx: commands.Context):
        guild: GeneralConfig = self.guildDict[ctx.guild.id]
        if guild.should_clear_command:
            await ctx.message.delete()
        elif guild.clear_command_exception_list.__contains__(ctx.author.id):
            await ctx.message.delete()

    def get_management_role_ids(self, guild_id: int):
        return self.guildDict[guild_id].management_role_ids

    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("should_clear_commands", "should_clear_command", set=self.set))
        config.add_configuration(Configuration("clear_command_exception_list", "clear_command_exception_list", add=self.add, remove=self.remove))
        config.add_configuration(Configuration("management_role_ids", "management_role_ids", add=self.add, remove=self.remove))

        return config

    @property
    def get_function_roles_reference(self) -> dict:
        return {
            self.change_prefix.name: None,
        }

    def is_enabled(self, ctx: Context) -> bool:
        return True

    def load_configs(self, guild_id: int = None) -> None:
        SaveLoadHelper.load_configs(self.guildDict, self.config_dir, GeneralConfig, self.client.guilds)

    def save_configs(self, guild_id: int = None) -> None:
        SaveLoadHelper.save_configs(self.guildDict, self.config_dir, GeneralConfig, guild_id)

    def set(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.set(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def add(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.add(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def remove(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.remove(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)


def setup(client: commands.bot):
    client.add_cog(General(client))
