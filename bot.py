import discord
from discord.ext import commands

from cogs import general
from cogs.debug import get_cog_list
import utils
from utils import logger
import shutil

intents = discord.Intents.default()
intents.members = True
intents.messages = True

client = commands.Bot(command_prefix=general.General.get_prefix, intents=intents)


@client.event
async def on_ready():
    logger.info("Ready")


if __name__ == "__main__":
    for extension in get_cog_list("./cogs"):
        client.load_extension(extension)

    client.run(utils.load_as_string("./token"))
    shutil.rmtree("./.temp")
    print("Good Bye!")

