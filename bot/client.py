from discord.ext.commands import Bot
from discord.ext import commands
from discord import Intents
from extensions.configExtension import ConfigManager
import os
import logging

# container check.
if os.getenv("IS_RUNNING_IN_DOCKER"):
    token_file_path: str = str(os.environ.get("DISCORD_BOT_TOKEN"))
    with open(token_file_path, "r") as token_file:
        TOKEN = token_file.read()
else:
    with open("../secrets/token") as token_file:
        TOKEN = token_file.read()

# logging
logging.basicConfig(level=logging.INFO)

# client creation
_client = Bot(command_prefix=ConfigManager.get_prefix("|"), intents=Intents.all())


@_client.event
async def on_ready():
    logging.info("Im ready.")


def main():
    _client.load_extension("extensions.extensionExtension")
    logging.info("Bot starting up")
    _client.run(TOKEN)


if __name__ == "__main__":
    main()
