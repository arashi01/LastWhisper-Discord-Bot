import discord
from discord.ext import commands

from pathlib import Path

import utils
from cogs import general
from cogs.debug import get_cog_list
from utils import logger

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.reactions = True

client = commands.Bot(command_prefix=general.General.get_prefix, intents=intents, help_command=None)


@client.event
async def on_ready():
    logger.info("Ready")


if __name__ == "__main__":
    for extension in get_cog_list("./cogs"):
        client.load_extension(extension)
    try:
        client.run(utils.load_as_string(Path("./token")))
    except FileNotFoundError:
        print("Missing token file.")
    print("Good Bye!")

