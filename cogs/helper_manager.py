from discord.ext import commands
import os
import json


class HelperManager(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        if not os.path.isdir("./help_docs"):
            os.mkdir("./help_docs")

    @commands.Cog.listener()
    async def on_ready(self):
        self._load_help_docs()

    @commands.Command
    async def reload_help_docs(self, _):
        self._load_help_docs()

    def _load_help_docs(self):
        cog: commands.Cog
        for _, cog in self.client.cogs.items():
            if not os.path.isfile(f"./help_docs/{cog.qualified_name}.json"):
                continue

            try:
                with open(f"./help_docs/{cog.qualified_name}.json") as f:
                    help_doc = json.load(f)

                for command in cog.get_commands():
                    if command.name in help_doc:
                        if "help" in (doc := help_doc[command.name]):
                            command.help = doc["help"]
                        if "brief" in (doc := help_doc[command.name]):
                            command.brief = doc["brief"]

            except json.JSONDecodeError:
                print(f"There is an issue with helper doc {cog.qualified_name}. Please Fix.")


def setup(client: commands.Bot):
    client.add_cog(HelperManager(client))
