from functools import wraps as _wraps
from inspect import iscoroutinefunction

from discord.ext.commands import Cog, Context

from interfaces.extension import IEnabled
from interfaces.roles import IRoleProvider
from objects.role_object import RoleObject


def cog_check_replacement(func):
    @_wraps(func)
    async def wrapper(cog: Cog, *args, **kwargs):
        flag: bool = True

        if isinstance(ctx := args[0], Context):
            if isinstance(cog, IEnabled):
                if not cog.is_enabled(ctx):
                    flag &= False

            flag &= await role_check(ctx)

        if iscoroutinefunction(func):
            flag &= await func(cog, *args, **kwargs) or True
        else:
            flag &= func(cog, *args, **kwargs) or True

        return flag

    return wrapper


async def role_check(ctx: Context) -> bool:
    """
            A check done to ensure the user has the correct role for a given command.

            :param ctx: The Discord Context.
            :return: If the check has failed.
    """
    # I do this to prevent redundancy in the code and allow for dynamic changing of roles while the bot is live.
    # If a better solution is discovered during the development then it will be implemented.

    if not isinstance((cog := ctx.cog), IRoleProvider):
        return True

    try:
        if ctx.author == ctx.guild.owner:
            return True

        role_key: RoleObject = cog.role_list[ctx.command.name]
        approved_roles: list = cog.guildDict[ctx.guild.id][role_key.config_dict_name] or []
        if role_key.is_management and not approved_roles:
            approved_roles.extend(cog.get_management_role_ids(ctx.guild.id))

        for role in approved_roles:
            if role in ctx.author.roles:
                return True

        if ctx.invoked_with != "help":
            await ctx.send("Sorry you do not have the correct permissions to invoke this command.")

        return False
    except KeyError:
        return False
