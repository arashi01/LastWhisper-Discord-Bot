from discord.ext import commands
from discord import Embed, TextChannel, Role, Member

import typing

from cogs.general import General
from utils import CogNames
from utils.cog_class import CogClass
from interfaces import config, iextensionhandler


class ConfigManager(commands.Cog, name=CogNames.ConfigManager.value):

    def __init__(self, client: commands.bot):
        self.client: commands.bot = client
        self.general_cog: General = self.client.get_cog(CogNames.General.value)

    @commands.Cog.listener()
    async def on_ready(self):
        self.general_cog: General = self.client.get_cog(CogNames.General.value)

    async def cog_before_invoke(self, ctx: commands.Context):
        pass

    @commands.group(invoke_without_command=True)
    async def config(self, ctx: commands.Context, extension: str = None, variable: str = "", action: str = "", value: typing.Union[TextChannel, Role, Member, str, int, bool] = None):
        if not extension:
            embed: Embed = Embed(title="Available Extensions Configs")
            for cog in self.client.cogs.values():
                if isinstance(cog, CogClass):
                    embed.add_field(name=cog.qualified_name, value="___")

            await ctx.send(embed=embed)

        else:
            if extension in self.client.cogs.keys():
                if isinstance(cog := self.client.cogs[extension], config.IConfigDeliverer):
                    if isinstance(variable_result := cog.config.get_configurations_dict[variable], dict):
                        if action in ("set", "add", "remove"):
                            variable_result[action](ctx, variable_result["config_name"], value)
                        elif action == "":
                            embed: Embed = variable_result["long preview"](Embed(), ctx, variable_result["config_name"])
                            await ctx.send(embed=embed)
                        else:
                            raise commands.BadArgument(f"Action **{action}** is not valid.")
                    else:
                        raise commands.BadArgument(f"**{variable}** is not valid configuration name for Extension **{extension}**.")
                else:
                    raise commands.BadArgument(f"**{extension}** is not Extension.")
            else:
                raise commands.BadArgument(f"**{extension}** does not exist.")

        await ctx.send("Done.")

    @config.command()
    async def reload(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            cog = self.client.cogs[extension]
            if isinstance(cog, extension.IsEnabled) and isinstance(cog, config.ILoader):
                if not cog.is_enabled(ctx):
                    await ctx.send(f"Extension **{extension}** is **Not** enabled on your server. Nothing to do.")
                    return

                cog.load_configs(ctx.guild.id)
            else:
                await ctx.send(f"**{extension}** is not a valid extension.")

        else:
            await ctx.send(f"**{extension}** is not a valid extension.")
        await ctx.send("Done.")

    @staticmethod
    def _is_enabled(cog: iextensionhandler.IEnabled, ctx: commands.Context) -> str:
        return ':white_check_mark: Enabled' if cog.is_enabled(ctx) else ':x: Disabled'

    @commands.group(invoke_without_command=True)
    async def extension(self, ctx: commands.Context):
        embed: Embed = Embed(title="Extensions Status")
        for cog in self.client.cogs.values():
            if isinstance(cog, iextensionhandler.IEnabled):
                embed.add_field(name=cog.qualified_name, value=self._is_enabled(cog, ctx))

        await ctx.send(embed=embed)

    @extension.command()
    async def is_enabled(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            if isinstance(cog := self.client.cogs[extension], extension.IsEnabled):
                await ctx.send(embed=Embed(title=cog.qualified_name, description=self._is_enabled(cog, ctx)))
            else:
                await ctx.send(f"Extension **{extension}** does not exist.")
        else:
            await ctx.send(f"Extension **{extension}** does not exist.")

    @extension.command()
    async def enable(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            if isinstance(cog := self.client.cogs[extension], extension.Enabled):
                await cog.enable(ctx)
            else:
                await ctx.send(f"Extension **{extension}** does not exist.")
        else:
            await ctx.send(f"Extension **{extension}** does not exist.")

    @extension.command()
    async def disable(self, ctx: commands.Context, extension: str):
        if extension in self.client.cogs:
            if isinstance(cog := self.client.cogs[extension], extension.Disable):
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
        if ctx.invoked_with != "help":
            await ctx.send("Sorry you do not have the correct permissions to invoke this command.")

        return False


def setup(client: commands.bot):
    client.add_cog(ConfigManager(client))
