from discord.ext.commands import Bot
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
_client = Bot(command_prefix="|")


def main():
    _client.load_extension("extensions.extensionManager")
    logging.log(logging.INFO, "Bot starting up")
    _client.run(TOKEN)


if __name__ == "__main__":
    main()
