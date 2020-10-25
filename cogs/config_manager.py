from discord.ext import commands
from discord import Embed

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
    async def config(self, ctx: commands.Context):
        embed: Embed = Embed(title="Available Extensions Configs")
        for cog in self.client.cogs.values():
            if isinstance(cog, CogClass):
                embed.add_field(name=cog.qualified_name, value="___")

        await ctx.send(embed=embed)

    @config.command(name=CogNames.BuffManager.value)
    async def week_manager(self, ctx: commands.Context, variable_to_be_changed: str, sub_command: str, value: str):
        variable_to_be_changed = variable_to_be_changed.lower()
        cog: CogClass = self.client.get_cog(CogNames.BuffManager.value)

        try:
            if variable_to_be_changed in ("morning_message_channel_id", "morning_message_hour"):

                flag = variable_to_be_changed == "morning_message_hour"

                if sub_command.lower() == "set":
                    await cog.set(ctx, variable_to_be_changed, value, set_type=TypeCondition.NONE if flag else TypeCondition.CHANNEL, condition=(lambda x: 0 <= x <= 23) if flag else None, condition_message=f"Value **{value}** must be between 0 and 23 hours.")
                else:
                    raise commands.BadArgument(f"Sub command **{sub_command}** is not valid.")

            elif variable_to_be_changed in ("today_buff_approved_roles_ids", "tomorrows_buff_approved_roles_ids", "this_week_buffs_approved_roles_ids", "next_week_buffs_approved_roles_ids", "buff_list", "weeks"):

                if sub_command.lower() == "add":
                    await cog.add(ctx, variable_to_be_changed, value, set_type=TypeCondition.ROLE if not ("weeks", "buff_list").__contains__(variable_to_be_changed) else TypeCondition.NONE)

                elif sub_command.lower() == "remove":
                    await cog.remove(ctx, variable_to_be_changed, value, set_type=TypeCondition.ROLE if not ("weeks", "buff_list").__contains__(variable_to_be_changed) else TypeCondition.NONE)

                else:
                    raise commands.BadArgument(f"Sub command **{sub_command}** is not valid.")

            else:
                raise commands.BadArgument(f"No such variable with name **{variable_to_be_changed}**.")

        except commands.BadArgument as e:
            await ctx.send(str(e))
        finally:
            await ctx.send("Done.")

    @config.command(name=CogNames.MemberManager.value)
    async def member_manager(self, ctx: commands.Context, variable_to_be_changed: str, sub_command: str, value: str):
        variable_to_be_changed = variable_to_be_changed.lower()
        cog: CogClass = self.client.get_cog(CogNames.MemberManager.value)

        try:
            if variable_to_be_changed in ("member_role_id", "new_member_role_id", "welcome_channel_id", "on_member_leave_logging_channel"):

                if sub_command.lower() == "set":
                    await cog.set(ctx, variable_to_be_changed, value, TypeCondition.CHANNEL if variable_to_be_changed in ("welcome_channel_id", "on_member_leave_logging_channel") else TypeCondition.ROLE)
                else:
                    raise commands.BadArgument(f"Sub command **{sub_command}** is not valid.")

            else:
                raise commands.BadArgument(f"No such variable with name **{variable_to_be_changed}**.")

        except commands.BadArgument as e:
            await ctx.send(str(e))
        finally:
            await ctx.send("Done.")

    @config.command(name=CogNames.ManagementTools.value)
    async def management_tools(self, ctx: commands.Context, variable_to_be_changed: str, sub_command: str, value: str):
        variable_to_be_changed = variable_to_be_changed.lower()
        cog: CogClass = self.client.get_cog(CogNames.ManagementTools.value)

        try:
            if variable_to_be_changed in ("clear_allowed_role_ids", "clear_channel_id_blacklist"):

                if sub_command.lower() == "add":
                    await cog.add(ctx, variable_to_be_changed, value, set_type=TypeCondition.ROLE if variable_to_be_changed == "clear_allowed_role_ids" else TypeCondition.CHANNEL)

                elif sub_command.lower() == "remove":
                    await cog.remove(ctx, variable_to_be_changed, value, set_type=TypeCondition.ROLE if variable_to_be_changed == "clear_allowed_role_ids" else TypeCondition.CHANNEL)

                else:
                    raise commands.BadArgument(f"Sub command **{sub_command}** is not valid.")

            else:
                raise commands.BadArgument(f"No such variable with name **{variable_to_be_changed}**.")

        except commands.BadArgument as e:
            await ctx.send(str(e))
        finally:
            await ctx.send("Done.")

    @config.command(name=CogNames.General.value)
    async def general_manager(self, ctx: commands.Context, variable_to_be_changed: str, sub_command: str, value: str):
        variable_to_be_changed = variable_to_be_changed.lower()
        cog: CogClass = self.client.get_cog(CogNames.General.value)

        try:
            if variable_to_be_changed == "should_clear_command":
                if sub_command.lower() == "set":
                    if value.isnumeric() and int(value) > 1:
                        await ctx.send(f"While technically value **{value}** will give a **True** in a bool statement it would be much preferred if you just stayed to 0 and 1.")
                    await cog.set(ctx, variable_to_be_changed, value, TypeCondition.BOOL)
            elif variable_to_be_changed in ("clear_command_exception_list", "management_role_ids"):
                print([m for m in ctx.guild.members])
                if sub_command.lower() == "add":
                    await cog.add(ctx, variable_to_be_changed, value, TypeCondition.USER if variable_to_be_changed == "clear_command_exception_list" else TypeCondition.ROLE)
                elif sub_command.lower() == "remove":
                    await cog.remove(ctx, variable_to_be_changed, value, TypeCondition.USER if variable_to_be_changed == "clear_command_exception_list" else TypeCondition.ROLE)
                else:
                    raise commands.BadArgument(f"Sub command **{sub_command}** is not valid.")
            else:
                raise commands.BadArgument(f"No such variable with name **{variable_to_be_changed}**.")
        except commands.BadArgument as e:
            await ctx.send(str(e))
        finally:
            await ctx.send("Done.")

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
        roles = self.general_cog.get_management_role_ids(ctx.guild)

        if len(roles) <= 0:
            return True

        for role in ctx.author.roles:
            if roles.__contains__(role.id):
                return True

        await ctx.send("Sorry you do not have the correct permissions to invoke this command.")
        return False


def setup(client: commands.bot):
    client.add_cog(ConfigManager(client))
