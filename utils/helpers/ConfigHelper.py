"""
This file mainly provides some helper functions for the configuration.
"""
from typing import Union

from discord import TextChannel, Role, Member
from discord.ext.commands import Context, BadArgument

from objects import TypeObjects, CustomConfigObject

# A collection of lambda functions to check if a id is in a guild.
_TypeConditionCheck = {
    TypeObjects.Channel: lambda ctx, x: x in ctx.guild.channels,
    TypeObjects.Member: lambda ctx, x: x in ctx.guild.members,
    TypeObjects.Role: lambda ctx, x: x in ctx.guild.roles,
    bool: lambda _, _v: True,
    int: lambda _, _v: True
}


def set(config: CustomConfigObject, ctx: Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> CustomConfigObject:
    """
    Function used to set the value of a configuration.

    :param config: The configuration object.
    :param ctx: The Discord Context.
    :param variable: The variable that is gonna be changed.
    :param value: The value the variable will be changed to.
    :return: A potentially modified configuration object.
    """
    variable_type = config[variable].__class__

    if isinstance(variable_type, str):
        config[variable] = value
    else:
        if not _TypeConditionCheck[variable_type](ctx, value):
            raise BadArgument(f"value {value} is not a valid **{variable_type.__name__}** that is in your server.")

        config[variable] = value.id if isinstance(value, (TextChannel, Role, Member)) else value

    return config


def add(config: CustomConfigObject, ctx: Context, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> CustomConfigObject:
    """
    Function used to add a value to a configuration.

    :param config: The configuration object.
    :param ctx: The Discord Context.
    :param variable: The variable that is gonna be changed.
    :param value: The value the variable will be changed to.
    :return: A potentially modified configuration object.
    """
    variable_type = config[variable].t

    if isinstance(variable_type, str):
        config[variable].append(value)
    else:
        if not _TypeConditionCheck[variable_type](ctx, value):
            raise BadArgument(f"value {value} is not a valid **{variable_type.__name__}** that is in your server.")

        if (variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value) in config[variable]:
            raise BadArgument(f"value {value} is already in the list {variable}.")

        config[ctx.guild.id][variable].append(
            variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value)

    return config


def remove(config: CustomConfigObject, _, variable: str, value: Union[TextChannel, Role, Member, str, int, bool]) -> CustomConfigObject:
    """
    Function used to remove a value to a configuration.

    :param config: The configuration object.
    :param variable: The variable that is gonna be changed.
    :param value: The value the variable will be changed to.
    :return: A potentially modified configuration object.
    """
    variable_type = config[variable].t
    actual_variable: list = config[variable]

    if not len(actual_variable) > 0:
        raise BadArgument(f"List **{variable}** is empty.")

    value = variable_type(value.id) if isinstance(value, (TextChannel, Role, Member)) else value

    if value not in actual_variable:
        raise BadArgument(f"value {value} is not in the list.")

    actual_variable.remove(value)

    return config
