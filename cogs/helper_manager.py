import asyncio
import itertools
import json
import os
from math import ceil
from typing import Union

from discord import Embed, Message, Reaction, Member
from discord.ext import commands

from utils import CogClass


class HelperManager(commands.Cog):
    """
    A cog that deals with the Help command and the help messages of commands/groups/Cogs.
    """

    def __init__(self, client: commands.Bot):
        """
        :param client: A Discord bot client.
        """
        self.client = client
        if not os.path.isdir("./help_docs"):
            os.mkdir("./help_docs")

        self.client.help_command = self.HelpCommand()

    def cog_unload(self):
        self.client.help_command = None

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
        """
        Loads the help for all the commands and sets them.
        If no help documentation was it nothing is done so the standard way of providing help can be used instead.
        """

        cog: commands.Cog
        for _, cog in self.client.cogs.items():
            if not os.path.isfile(f"./help_docs/{cog.qualified_name}.json"):
                continue

            try:
                with open(f"./help_docs/{cog.qualified_name}.json") as f:
                    help_doc = json.load(f)

                if "description" in help_doc:
                    cog.__cog_cleaned_doc__ = help_doc["description"]

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

    class HelpCommand(commands.HelpCommand):
        """
        A custom written help command that uses embeds to show help information and provide some user control for long lists of commands.
        """

        def __init__(self, **options):
            super().__init__(**options)
            self.sort_commands = options.pop("sort_commands", True)
            self.no_category: str = options.pop("no_category", "No Category")
            self.commands_heading: str = options.pop("commands_heading", "Commands:")
            self.page_size = options.pop("page_size",
                                         3)  # The size of the help page. (i.e. the number of categories allow to be shown at once.)
            self.left_reaction = options.pop("left_reaction", "⬅")
            self.stop_reaction = options.pop("stop_reaction", "⏹️")
            self.right_reaction = options.pop("right_reaction", "➡️")
            self._help_page_number = 0
            self._max_pages = 0

            self.paginator = self.EmbedPaginator()

        async def prepare_help_command(self, ctx, command=None) -> None:
            """
            Method used to prepare the help command before it is sent.

            :param ctx: The Discord Context.
            :param command: The 'command'.
            """
            self.paginator.clear()
            self.paginator.set_author(ctx.author)

            return await super().prepare_help_command(ctx, command)

        async def send_command_help(self, command: commands.Command) -> None:
            """
            Sends the help embed for a command.

            :param command: The command that the help is being asked about.
            """
            self.paginator.title(f"Command *{command.name}*")
            self.paginator.description(command.help)

            self.paginator.add_usage(self.get_command_signature(command))

            self.paginator.close(self.context, command)
            await self.get_destination().send(embed=self.paginator.embed)

        async def send_group_help(self, group: commands.Group) -> None:
            """
            Sends the help embed for a group of commands.

            :param group: The command group that help is being asked about.
            """
            self.paginator.title(f"Command *{group.name}*")
            self.paginator.description(group.help)

            if group.commands:
                self.paginator.add_sub_commands(await self.filter_commands(group.commands, sort=self.sort_commands))

            self.paginator.add_usage(self.get_command_signature(group))
            self.paginator.close(self.context, group, self.get_ending_note())

            await self.get_destination().send(embed=self.paginator.embed)

        async def send_cog_help(self, cog: commands.Cog) -> None:
            """
            Sends the help embed for a Cog.

            :param cog: The Cog that help is being asked about.
            """
            self.paginator.title(f"Category: {cog.qualified_name}")
            self.paginator.description(cog.description)

            if filtered_commands := await self.filter_commands(cog.get_commands(), sort=self.sort_commands):
                self.paginator.add_sub_commands(filtered_commands)

            self.paginator.close(self.context, cog, self.get_ending_note())

            await self.get_destination().send(embed=self.paginator.embed)

        async def display_help_page(self, number: int) -> None:
            """
            Method used to create the help pages for the embed.

            :param number: The page number.
            """

            def get_category(command):
                return command.cog.qualified_name if command.cog else self.no_category

            filtered_commands = await self.filter_commands(self.context.bot.commands, sort=True, key=get_category)

            self._help_page_number = number

            self.paginator.clear_fields()

            categories: dict = {k: list(v) for k, v in itertools.groupby(filtered_commands, key=get_category)}
            self._max_pages = ceil(len(categories.keys()) / self.page_size)

            index = self._help_page_number * self.page_size
            for category, _commands in list(categories.items())[index: index + self.page_size]:
                self.paginator.add_sub_commands(_commands, category=category)

            self.paginator.title(f"Help [{self._help_page_number + 1}/{self._max_pages}]")

        async def send_bot_help(self, mapping) -> None:
            """
            Sends the help embed.

            :param mapping: A mapping of the commands for the bot.
            """
            await self.display_help_page(0)

            self.paginator.close(self.context, note=self.get_ending_note())

            message: Message = await self.get_destination().send(embed=self.paginator.embed)
            await message.add_reaction(self.left_reaction)
            await message.add_reaction(self.stop_reaction)
            await message.add_reaction(self.right_reaction)
            await asyncio.sleep(1.0)

            reaction: Reaction
            user: Member

            while True:
                try:
                    reaction, member = await self.context.bot.wait_for("reaction_add", timeout=10.0, check=lambda x,
                                                                                                                  _member: _member == self.context.author)
                except asyncio.TimeoutError:
                    break
                else:
                    if reaction.emoji == self.left_reaction:
                        if self._help_page_number - 1 >= 0:
                            await self.display_help_page(number=self._help_page_number - 1)
                            await message.edit(embed=self.paginator.embed)
                        await message.remove_reaction(reaction, member)

                    elif reaction.emoji == self.right_reaction:
                        if self._help_page_number + 1 < self._max_pages:
                            await self.display_help_page(number=self._help_page_number + 1)
                            await message.edit(embed=self.paginator.embed)
                        await message.remove_reaction(reaction, member)

                    elif reaction.emoji == self.stop_reaction:
                        break

            await message.clear_reactions()

        def get_ending_note(self) -> str:
            """
            Returns the ending notes for the help command.
            """
            return f"Type {self.clean_prefix}{self.invoked_with} command for more info on a command.\n" \
                   f"You can also type {self.clean_prefix}{self.invoked_with} category for more info on a category."

        class EmbedPaginator:
            """A paginator based on the paginator of provided help methods."""

            def __init__(self) -> None:
                self._embed: Embed = Embed()

            def title(self, text) -> None:
                self._embed.title = text

            def description(self, description) -> None:
                self._embed.description = description

            def from_dict(self, value: dict) -> None:
                self._embed = Embed.from_dict(value)

            def set_author(self, author: Member):
                self._embed.set_author(name=author.display_name, icon_url=author.avatar_url)

            def clear(self) -> None:
                self._embed = Embed()

            def clear_fields(self) -> None:
                self._embed.clear_fields()

            @property
            def embed(self) -> Embed:
                return self._embed

            def add_usage(self, command: str) -> None:
                self._embed.add_field(name="Usage:", value=f'``{command}``', inline=False)

            # noinspection PyShadowingNames
            def add_sub_commands(self, commands: [commands.Command], category: str = "Commands:") -> None:
                self._embed.add_field(name=f"Category *{category}:*" if category != "Commands:" else category,
                                      value="> " + "\n> ".join(
                                          [f"***{command.name}:*** {command.short_doc}" for command in commands]),
                                      inline=False)

            def close(self, context: commands.Context,
                      obj: Union[commands.Group, commands.Cog, commands.Command] = None,
                      note=None) -> None:

                if obj:
                    if isinstance(cog := obj if isinstance(obj, commands.Cog) else obj.cog, CogClass):
                        self.embed.add_field(name="Extension is:", value=':white_check_mark: Enabled' if cog.is_enabled(
                            context) else ':x: Disabled', inline=False)

                if note:
                    self.embed.set_footer(text=note)


def setup(client: commands.Bot):
    client.add_cog(HelperManager(client))
