import os
from abc import abstractmethod
from typing import Union
from pathlib import Path

from discord import Guild, TextChannel, Role, Member
from discord.ext import commands

import utils
from cogs.general import General
from objects import CustomConfigObject
from utils.helpers import ConfigHelper, SaveLoadHelper
from configuration import ConfigurationDictionary
from interfaces import CogABCMeta, config, iextensionhandler


class CogClass(iextensionhandler.IExtensionHandler, config.IConfigManager, commands.Cog, metaclass=CogABCMeta):
    """
    This is an abstract class used to simplify the creation of the Extensions.
    While the class is not required it simplifies the creation and removes redundancy from the rest of the codebase.
    """
    # Static variable declaration.
    config_dir: Path
    client: commands.Bot
    config: ConfigurationDictionary
    _general_cog: General  # As there are some functions in the General Cog I cache it to reduce the number of get_cog calls that are done.
    config_object: CustomConfigObject.__class__

    def __init__(self, client: commands.bot, config_dir: Path, config_object: CustomConfigObject.__class__) -> None:
        """
        :param client: The Discord client object.
        :param config_dir: The directory where the configurations are expected to be stored.
        :param config_object: A class reference of the object to be initialized during the creation of the configs.
        """
        super().__init__()  # I am certain that this is not needed however in case there is a change in the future I am keeping this here to not break.
        self.client = client
        self.guildDict: dict = {}
        self.config_dir = config_dir if isinstance(config_dir, Path) else Path(config_dir)
        self.config = self.get_configs

        self.config_object = config_object
        if self.client.is_ready():
            self._general_cog = self.client.get_cog(utils.CogNames.General.value)
            self.load_configs()
            
    def cog_unload(self):
        from os.path import isfile
        for key, value in self.guildDict.items():
            if not isfile(self.config_dir/(str(key) + SaveLoadHelper.default_extension)):
                self.save_configs(key)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self._general_cog = self.client.get_cog(utils.CogNames.General.value)
        self.load_configs()

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not self.is_enabled(ctx):
            return False
        return await self.role_check(ctx)

    async def role_check(self, ctx: commands.Context) -> bool:
        """
        A check done to ensure the user has the correct role for a given command.

        :param ctx: The Discord Context.
        :return: If the check has failed.
        """
        # I do this to prevent redundancy in the code and allow for dynamic changing of roles while the bot is live.
        # If a better solution is discovered during the development then it will be implemented.
        approved_roles: [] = []

        try:
            approved_roles = self.guildDict[ctx.guild.id][self.get_function_roles_reference[ctx.command.name]]
        except KeyError:
            approved_roles = None
        except NotImplementedError:
            print("The get_function_roles_references method has not been implemented yet. Kindly do so.\n"
                  "Roles will default to management.")
            approved_roles = None
        finally:
            approved_roles = approved_roles if approved_roles is not None else self._general_cog.get_management_role_ids(ctx.guild.id)

        if len(approved_roles) == 0:
            return True

        member_roles = [role.id for role in ctx.author.roles]
        for role in approved_roles:
            if role in member_roles:
                return True

        if ctx.invoked_with != "help":  # Special check for the help command to prevent the sending of multiple wrong role messages.
            await ctx.send("Sorry you do not have the correct permissions to invoke this command.")

        return False

    async def cog_after_invoke(self, ctx) -> None:
        await self._general_cog.remove_message(ctx)

    # region Getters
    @property
    @abstractmethod
    def get_function_roles_reference(self) -> dict:
        """
        A function that returns a dictionary of function names and an array of allowed roles ids.

        :return: Dictionary of allowed roles for given commands.
        """
        pass
    # endregion

    # region Config
    # region Listeners
    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        # This method is used to generate the default configuration files when a server invites the bot.
        if not self.config_object:
            return

        utils.save_as_json(f"{self.config_dir}/{guild.id}.json", self.config_object())
        self.guildDict[guild.id] = self.config_object()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        # This method is used to remove the configuration files when a server invites the bot.
        if not self.config_object:
            return

        utils.remove_file(f"{self.config_dir}/{guild.id}.json")
        self.guildDict.pop(guild.id)
    # endregion

    # region IConfig
    @property
    @abstractmethod
    def get_configs(self) -> ConfigurationDictionary:
        pass

    def load_configs(self, guild_id: int = None) -> None:
        SaveLoadHelper.load_configs_json(self.guildDict, str(self.config_dir), self.config_object, self.client.guilds, guild_id)
        SaveLoadHelper.load_configs(self.guildDict, self.config_dir, self.config_object, self.client.guilds, guild_id, clear_existing=False)

    def save_configs(self, guild_id: int = None) -> None:
        SaveLoadHelper.save_configs(self.guildDict, self.config_dir, self.config_object, guild_id)

    # endregion

    # region IExtension
    async def enable(self, ctx: commands.Context) -> None:
        if self.is_enabled(ctx):
            await ctx.send("Already Enabled.")
            return

        self.load_configs(guild_id=ctx.guild.id)
        await ctx.send("Done.")

    async def disable(self, ctx: commands.Context) -> None:
        if not self.is_enabled(ctx):
            await ctx.send("Already Disabled.")
            return

        self.guildDict.pop(ctx.guild.id)
        os.rename(f"{self.config_dir}/{ctx.guild.id}.json", f"{self.config_dir}/{ctx.guild.id}.json.disabled")

        await ctx.send("Done.")

    def is_enabled(self, ctx: commands.Context) -> bool:
        return self.guildDict.__contains__(ctx.guild.id)
    # endregion

    def set(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.set(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def add(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.add(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)

    def remove(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        self.guildDict[ctx.guild.id] = ConfigHelper.remove(self.guildDict[ctx.guild.id], ctx, variable, value)
        self.save_configs(ctx.guild.id)
    # endregion
