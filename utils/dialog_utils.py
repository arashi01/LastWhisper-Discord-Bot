import asyncio
from enum import Enum

from discord import Embed, Member, Reaction, Message
from discord.ext.commands import Context

_yes = "\N{White Heavy Check Mark}"
_no = "\N{Negative Squared Cross Mark}"
_cancel = "\N{Prohibited Sign}"


class DialogReturn(Enum):
    YES = 1
    NO = 0
    CANCEL = -1
    FAILED = None
    ERROR = None


async def setup_embed(ctx: Context, title: str, description: str, fields: list = None, timeout: float = 0.0) -> Message:
    embed: Embed = Embed(title=title, description=description)

    if fields:
        for field in fields:
            if len(field) == 2:
                embed.add_field(name=field[0], value=field[1])

    embed.set_footer(text=f"You have {timeout} seconds to respond.")

    return await ctx.send(embed=embed)


async def yes_no(ctx: Context, title: str, description: str, fields: [] = None, timeout: float = 10.0) -> DialogReturn:
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


async def yes_no_cancel() -> DialogReturn:
    pass
