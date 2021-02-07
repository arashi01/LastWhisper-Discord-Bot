import typing

from discord import Embed, TextChannel, Role, Member
from discord.ext import commands

from cogs.general import General
from interfaces import config, extension, roles
from objects.role_object import RoleObject
from utils import CogNames
from utils.cog_class import CogClass
from utils.helpers import role_helper


class ConfigManager(roles.IRoleProvider, commands.Cog, name=CogNames.ConfigManager.value):
    def __init__(self, client: commands.bot):
        super().__init__()
        self._client: commands.bot = client
        if self._client.is_ready:
            self._general_cog: General = self._client.get_cog(CogNames.General.value)

    @commands.Cog.listener()
    async def on_ready(self):
        self._general_cog: General = self._client.get_cog(CogNames.General.value)

    @commands.group(invoke_without_command=True)
    async def config(self, ctx: commands.Context, extension_name: str = None, variable: str = "", action: str = "",
                     value: typing.Union[TextChannel, Role, Member, str, int, bool] = None):
        if not extension_name:
            embed: Embed = Embed(title="Available Extensions Configs")
            for cog in self._client.cogs.values():
                if isinstance(cog, CogClass):
                    if isinstance(cog, extension.IEnabled) and not cog.is_enabled(ctx):
                        continue

                    embed.add_field(name=cog.qualified_name, value="___")

            await ctx.reply(embed=embed, mention_author=False)

        else:
            if extension_name in self._client.cogs.keys():
                if isinstance(cog := self._client.cogs[extension_name], config.IConfigDeliverer):
                    if isinstance(variable_result := cog.get_configs.get_configurations_dict[variable], dict):
                        if action in ("set", "add", "remove"):
                            variable_result[action](ctx, variable_result["config_name"], value)
                        elif action == "":
                            embed: Embed = variable_result["long preview"](Embed(), ctx, variable_result["config_name"])
                            await ctx.reply(embed=embed, mention_author=False)
                        else:
                            raise commands.BadArgument(f"Action **{action}** is not valid.")
                    else:
                        raise commands.BadArgument(
                            f"**{variable}** is not valid configuration name for Extension **{extension_name}**.")
                else:
                    raise commands.BadArgument(f"**{extension_name}** is not Extension.")
            else:
                raise commands.BadArgument(f"**{extension_name}** does not exist.")

            await ctx.reply("Done.", mention_author=False)

    @config.command()
    async def reload(self, ctx: commands.Context, extension_name: str):
        if extension_name in self._client.cogs:
            cog = self._client.cogs[extension_name]
            if isinstance(cog, extension.IEnabled):
                if not cog.is_enabled(ctx):
                    await ctx.reply(f"Extension **{extension_name}** is **Not** enabled on your server. Nothing to do.",
                                    mention_author=False)
                    return
                if isinstance(cog, config.ILoader):
                    cog.load_configs(ctx.guild.id)
                else:
                    raise AttributeError(f"Cog {cog.__name__} does not implement interface interface.config.ILoader")
            else:
                await ctx.reply(f"**{extension_name}** is not a valid extension.", mention_author=False)

        else:
            await ctx.reply(f"**{extension_name}** is not a valid extension.", mention_author=False)
        await ctx.reply("Done.", mention_author=False)

    @staticmethod
    def _is_enabled(cog: extension.IEnabled, ctx: commands.Context) -> str:
        return ':white_check_mark: Enabled' if cog.is_enabled(ctx) else ':x: Disabled'

    @commands.group(invoke_without_command=True)
    async def extension(self, ctx: commands.Context):
        embed: Embed = Embed(title="Extensions Status")
        for cog in self._client.cogs.values():
            if isinstance(cog, extension.IEnabled):
                embed.add_field(name=cog.qualified_name, value=self._is_enabled(cog, ctx))

        await ctx.reply(embed=embed, mention_author=False)

    @extension.command()
    async def is_enabled(self, ctx: commands.Context, extension_name: str):
        if extension_name in self._client.cogs:
            if isinstance(cog := self._client.cogs[extension_name], extension.IEnabled):
                await ctx.reply(embed=Embed(title=cog.qualified_name, description=self._is_enabled(cog, ctx)),
                                mention_author=False)
            else:
                await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)
        else:
            await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)

    @extension.command()
    async def enable(self, ctx: commands.Context, extension_name: str):
        if extension_name in self._client.cogs:
            if isinstance(cog := self._client.cogs[extension_name], extension.IEnabler):
                await cog.enable(ctx)
            else:
                await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)
        else:
            await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)

    @extension.command()
    async def disable(self, ctx: commands.Context, extension_name: str):
        if extension_name in self._client.cogs:
            if isinstance(cog := self._client.cogs[extension_name], extension.IDisabler):
                await cog.disable(ctx)
            else:
                await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)
        else:
            await ctx.reply(f"Extension **{extension_name}** does not exist.", mention_author=False)

    @role_helper.cog_check_replacement
    async def cog_check(self, ctx: commands.Context):
        pass

    @property
    def role_list(self) -> dict:
        return {
            self.config.name: RoleObject("", "", True),
            self.reload.name: RoleObject("", "", True),

            self.extension.name: RoleObject("", "", True),
            self.is_enabled.name: RoleObject("", "", True),
            self.enable.name: RoleObject("", "", True),
            self.disable: RoleObject("", "", True)
        }


def setup(client: commands.bot):
    client.add_cog(ConfigManager(client))
