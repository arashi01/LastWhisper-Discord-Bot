import json
import os
from abc import abstractmethod
from typing import Union

from discord import TextChannel, Member, Role, Guild
from discord.ext import commands

import utils
from objects import CustomConfigObject, TypeObjects
from objects.configuration import ConfigurationDictionary


class CogClass(commands.Cog):
    def __init__(self, client: commands.bot, config_dir: str, config_object: CustomConfigObject.__class__) -> None:
        self.client: commands.bot = client
        self.guildDict: dict = {}
        self.config_dir: str = config_dir
        self.config: ConfigurationDictionary = self.get_configs
        self._general_cog = self.client.get_cog(utils.CogNames.General.value)

        self.config_object: CustomConfigObject.__class__ = config_object
        if self.client.is_ready():
            self.load_configs()

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_configs()
        self._general_cog = self.client.get_cog(utils.CogNames.General.value)

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not self.is_enabled(ctx):
            return False
        return await self.role_check(ctx)

    async def role_check(self, ctx: commands.Context) -> bool:
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

        if ctx.invoked_with != "help":
            await ctx.send("Sorry you do not have the correct permissions to invoke this command.")

        return False

    async def cog_after_invoke(self, ctx) -> None:
        await self._general_cog.remove_message(ctx)

    # region Getters
    @property
    @abstractmethod
    def get_configs(self) -> ConfigurationDictionary:
        pass

    @property
    @abstractmethod
    def get_function_roles_reference(self) -> dict:
        pass
    # endregion

    # region Join and Leave Listeners
    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:
        if not self.config_object:
            return

        utils.save_as_json(f"{self.config_dir}/{guild.id}.json", self.config_object())
        self.guildDict[guild.id] = self.config_object()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:
        if not self.config_object:
            return

        utils.remove_file(f"{self.config_dir}/{guild.id}.json")
        self.guildDict.pop(guild.id)
    # endregion

    # region Config
    def load_configs(self, guild_id: int = None) -> None:
        if not guild_id:
            self.guildDict.clear()
            for filename in os.listdir(self.config_dir):
                if filename.endswith(".json"):
                    with open(f"{self.config_dir}/{filename}") as f:
                        json_obj = json.load(f)
                    self.guildDict[int(filename[:-5])] = self.config_object.from_json(json_obj)

        else:
            file_dir = f"{self.config_dir}/{guild_id}.json"
            obj = self.config_object()

            if os.path.isfile(file_dir + ".disabled"):
                os.rename(file_dir + ".disabled", file_dir)

            if not os.path.isfile(file_dir):
                utils.save_as_json(file_dir, obj)

            with open(file_dir) as f:
                obj = self.config_object.from_json(json.load(f))

            self.guildDict[guild_id] = obj

    def save_configs(self, guild_id: int = None) -> None:
        if not self.config_object:
            return

        file_dir = f"{self.config_dir}/{guild_id}.json"
        if not guild_id:
            for key in self.guildDict:
                utils.save_as_json(file_dir, self.guildDict[key])

        else:
            if not self.guildDict.__contains__(guild_id):
                utils.save_as_json(file_dir, self.config_object())

            utils.save_as_json(file_dir, self.guildDict[guild_id])

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

    _TypeConditionCheck = {
        TypeObjects.Channel: lambda ctx, x: x in ctx.guild.channels,
        TypeObjects.Member: lambda ctx, x: x in ctx.guild.members,
        TypeObjects.Role: lambda ctx, x: x in ctx.guild.roles,
        bool: lambda _, _v: True,
        int: lambda _, _v: True
    }

    def set(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        guild = self.guildDict[ctx.guild.id]
        variable_type = guild[variable].__class__

        if isinstance(variable_type, str):
            guild[variable] = value
        else:
            if not self._TypeConditionCheck[variable_type](ctx, value):
                raise commands.BadArgument(f"value {value} is not a valid **{variable_type.__name__}** that is in your server.")

            guild[variable] = value.id if isinstance(value, (TextChannel, Role, Member)) else value

        self.save_configs(ctx.guild.id)

    def add(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        guild = self.guildDict[ctx.guild.id]
        variable_type = guild[variable].t

        if isinstance(variable_type, str):
            guild[variable].append(value)
        else:
            if not self._TypeConditionCheck[variable_type](ctx, value):
                raise commands.BadArgument(f"value {value} is not a valid **{variable_type.__name__}** that is in your server.")

            if (variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value) in guild[variable]:
                raise commands.BadArgument(f"value {value} is already in the list {variable}.")

            self.guildDict[ctx.guild.id][variable].append(variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value)
        self.save_configs(ctx.guild.id)

    def remove(self, ctx: commands.Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> None:
        guild = self.guildDict[ctx.guild.id]
        variable_type = guild[variable].t
        actual_variable: list = guild[variable]

        if not len(actual_variable) > 0:
            raise commands.BadArgument(f"List **{variable}** is empty.")

        value = variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value

        if value not in actual_variable:
            raise commands.BadArgument(f"value {value} is not in the list.")

        actual_variable.remove(value)
        self.save_configs(ctx.guild.id)
    # endregion
