from discord.ext import commands
from discord import Embed, TextChannel, Role, Member

import typing

from cogs.general import General
from utils import TypeCondition, CogNames
from utils.cog_class import CogClass


class ConfigManager(commands.Cog, name=CogNames.ConfigManager.value):
    def __init__(self, client: commands.bot):
        self.client: commands.bot = client
        self.general_cog: General = client.cogs[CogNames.General.value]

    async def cog_before_invoke(self, ctx: commands.Context):
        pass

    @commands.group(invoke_without_command=True)
    async def config(self, ctx: commands.Context, extension: str = None, variable: str = "", action: str = "", value: typing.Union[TextChannel, Role, Member, str, int] = None):
        embed: Embed = Embed(title="Available Extensions Configs")
        if not extension:
            for cog in self.client.cogs.values():
                if isinstance(cog, CogClass):
                    embed.add_field(name=cog.qualified_name, value="___")

            await ctx.send(embed=embed)
        else:
            if extension in self.client.cogs.keys():
                if isinstance(cog := self.client.cogs[extension], CogClass):
                    if isinstance(variable_result := cog.config[variable], dict):
                        if callable(action_result := variable_result[action]):
                            await action_result(ctx, variable, value)
                        else:
                            await ctx.send(action_result)
                    else:
                        await ctx.send(variable_result)

    @config.command()
    async def reload(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            cog = self.client.cogs[extension]
            if isinstance(cog, CogClass):
                if not cog.is_enabled(ctx):
                    await ctx.send(f"Extension **{extension}** is **Not** enabled on your server. Nothing to do.")
                    return

                cog.load_configs(ctx.guild.id)
            else:
                await ctx.send(f"**{extension}** is not a valid extension.")

        else:
            await ctx.send(f"**{extension}** is not a valid extension.")
        await ctx.send("Done.")

    @commands.group(invoke_without_command=True)
    async def extension(self, ctx: commands.Context):
        embed: Embed = Embed(title="Extensions Status")
        for cog in self.client.cogs.values():
            if isinstance(cog, CogClass):
                embed.add_field(name=cog.qualified_name, value=":white_check_mark:" if cog.is_enabled(ctx) else ":x:")

        await ctx.send(embed=embed)

    @extension.command()
    async def is_enabled(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            cog = self.client.cogs[extension]
            if isinstance(cog, CogClass):
                embed = Embed(title=cog.qualified_name,
                              description=':white_check_mark:' if cog.is_enabled(ctx) else ':x:')
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Extension **{extension}** does not exist.")
        else:
            await ctx.send(f"Extension **{extension}** does not exist.")

    @extension.command()
    async def enable(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            cog = self.client.cogs[extension]
            if isinstance(cog, CogClass):
                await cog.enable(ctx)
            else:
                await ctx.send(f"Extension **{extension}** does not exist.")
        else:
            await ctx.send(f"Extension **{extension}** does not exist.")

    @extension.command()
    async def disable(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            cog = self.client.cogs[extension]
            if isinstance(cog, CogClass):
                await cog.disable(ctx)
            else:
                await ctx.send(f"Extension **{extension}** does not exist.")
        else:
            await ctx.send(f"Extension **{extension}** does not exist.")

    async def cog_check(self, ctx: commands.Context):
        return await self.role_check(ctx)

    async def role_check(self, ctx: commands.Context) -> bool:
        roles = self.general_cog.get_management_role_ids(ctx.guild.id)

        if len(roles) <= 0:
            return True

        for role in ctx.author.roles:
            if roles.__contains__(role.id):
                return True

        await ctx.send("Sorry you do not have the correct permissions to invoke this command.")
        return False


def setup(client: commands.bot):
    client.add_cog(ConfigManager(client))
