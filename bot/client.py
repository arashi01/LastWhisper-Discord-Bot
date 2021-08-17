# noinspection PyPackageRequirements
import discord
import os
import logging

# dev mode check.
DEV_MODE: bool = bool(os.environ.get("RUNNING_DOCKER_COMPOSE", False))

if DEV_MODE:
    token_file_path: str = str(os.environ.get("DISCORD_BOT_TOKEN"))
    with open(token_file_path, "r") as token_file:
        TOKEN = token_file.read()
else:
    TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

# logging
logging.basicConfig(level=logging.INFO)

# client creation
_client = discord.Client()


@_client.event
async def on_ready():
    print("Ready")


@_client.event
async def on_message(message):
    if message.author == _client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello")


def main():
    logging.log(logging.INFO, "Bot starting up")
    _client.run(TOKEN)


if __name__ == "__main__":
    main()
