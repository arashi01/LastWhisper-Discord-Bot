from discord.ext import commands
import os
import json


class HelperManager(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        if not os.path.isdir("./help_docs"):
            os.mkdir("./help_docs")

    def cog_check(self, ctx):
        return self.client.is_owner(ctx.author)

    @commands.Cog.listener()
    async def on_ready(self):
        self._load_help_docs()

    @commands.Command
    async def reload_help_docs(self, ctx):
        self._load_help_docs()
        await ctx.send("done.")

    def _load_help_docs(self):
        cog: commands.Cog
        for _, cog in self.client.cogs.items():
            if not os.path.isfile(f"./help_docs/{cog.qualified_name}.json"):
                continue

            try:
                with open(f"./help_docs/{cog.qualified_name}.json") as f:
                    help_doc = json.load(f)

                def set_commands_help(_command, _docs: {}):
                    if _command.name not in _docs:
                        return

                    set_help(_command, _docs[_command.name])
                    if isinstance(_command, commands.Group) and "commands" in _docs[_command.name]:
                        for _sub_command in _command.commands:
                            set_commands_help(_sub_command, _docs[_command.name]["commands"])

                def set_help(_command: commands.Command, _doc: dict):
                    if "help" in _doc:
                        _command.help = _doc["help"]
                    if "brief" in _doc:
                        _command.brief = _doc["brief"]

                for command in cog.get_commands():
                    set_commands_help(command, help_doc)

            except json.JSONDecodeError:
                print(f"There is an issue with helper doc {cog.qualified_name}. Please Fix.")


def setup(client: commands.Bot):
    client.add_cog(HelperManager(client))
