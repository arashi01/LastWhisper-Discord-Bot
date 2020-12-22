import asyncio
from enum import Enum

from discord import Embed, Member, Reaction, Message
from discord.ext.commands import Context

# Some internal default used for the dialog box.
_yes = "\N{White Heavy Check Mark}"
_no = "\N{Negative Squared Cross Mark}"


class DialogReturn(Enum):
    """ A collection of possible responses. """
    YES = 1
    NO = 0
    CANCEL = -1
    FAILED = None
    ERROR = None


async def setup_embed(ctx: Context, title: str, description: str, fields: list = None, timeout: float = 0.0) -> Message:
    """
    This sets up the embed with the necessary information before the embed is posted.

    :param ctx: The Discord Context.
    :param title: The title of the embed.
    :param description: The description of the embed.
    :param fields: A list of tuples that are used to represent any additional information.
    :param timeout: This is used to show how much time is left on the embed in the footer.
    :return: Returns the message where the embed was posted.
    """
    embed: Embed = Embed(title=title, description=description)

    if fields:
        for field in fields:
            if len(field) == 2:
                embed.add_field(name=field[0], value=field[1])

    embed.set_footer(text=f"You have {timeout} seconds to respond.")

    return await ctx.send(embed=embed)


async def yes_no(ctx: Context, title: str, description: str, fields: [] = None, timeout: float = 10.0) -> DialogReturn:
    """
    An automated dialog response embed message handler that will return a result of a dialog. This one is for yes or no.

    :param ctx: The Discord Context.
    :param title: The title of the dialog.
    :param description: The description for the dialog.
    :param fields: A list of tuples that are used to represent any additional information.
    :param timeout: The amount of time before the message deletes and returns FAILED.
    :return: The result of the Dialog.
    """
    message = await setup_embed(ctx, title, description, fields, timeout)

    await message.add_reaction(_yes)
    await message.add_reaction(_no)
    await asyncio.sleep(1)

    def check(_reaction: Reaction, _member: Member):
        return _reaction.message == message and _member == ctx.author and _reaction.emoji in (_yes, _no)

    try:
        reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=check)
    except asyncio.TimeoutError:
        await message.delete()
        return DialogReturn.FAILED
    else:
        if reaction.emoji == _yes:
            await message.delete()
            return DialogReturn.YES
        elif reaction.emoji == _no:
            await message.delete()
            return DialogReturn.NO
        else:
            return DialogReturn.ERROR


async def get_author_written_response(ctx, title, description, fields: [] = None, timeout: float = 30.0, delete_response: bool = False) -> str:
    """
    A automatic dialog for getting a users next written response.

    :param ctx: The Discord Context.
    :param title: The title of the dialog.
    :param description: The description for the dialog.
    :param fields: A list of tuples that are used to represent any additional information.
    :param timeout: The amount of time before the message deletes and returns "".
    :param delete_response: Should the response be deleted after.
    :return: The result of the Dialog.
    """
    message = await setup_embed(ctx, title, description, fields, timeout)

    def check(_message: Message):
        return _message.author == ctx.author

    try:
        response: Message = await ctx.bot.wait_for("message", timeout=timeout, check=check)
        content = response.content
        if delete_response:
            await response.delete()

    except asyncio.TimeoutError:
        await message.delete()
        return ""
    else:
        await message.delete()
        return content
