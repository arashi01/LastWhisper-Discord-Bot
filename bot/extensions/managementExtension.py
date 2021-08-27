import asyncio
from typing import Union

from discord.ext.commands import Bot, Cog, Context, command, BadArgument
from discord import TextChannel, Role, Reaction, RawReactionActionEvent, Message, Member, Guild, NotFound, User
from discord.iterators import ReactionIterator
from discord.ext import tasks

from extensions.configExtension import ConfigManager
from extensions.permissionsExtension import PermissionsManager
from objects.managementTools import ServerConfigs
from utils.helpers.configManager import ConfigMethodHelpers


class ManagementTools(Cog):
    def __init__(self, bot: Bot):
        # Ignored since a name error would occur latter on and not worth it to do a try catch.
        # noinspection PyTypeChecker
        self._permission_manager: PermissionsManager = None
        self._bot = bot
        self.config_settings = {
            "set": {
                "user_info_channel_id": ConfigMethodHelpers.set,
                "new_user_role_id": ConfigMethodHelpers.set,
                "member_role_id": ConfigMethodHelpers.set,
                "reaction_check_channel": ConfigMethodHelpers.set,
            },
            "add": {
                "clear_channel_id_blacklist": ConfigMethodHelpers.add,
                "reaction_message_ids": ConfigMethodHelpers.add,
            },
            "remove": {
                "clear_channel_id_blacklist": ConfigMethodHelpers.add,
                "reaction_message_ids": ConfigMethodHelpers.add,
            },
            "settings": {
                "default_config": ServerConfigs,
                "reaction_message_ids": {
                    "convert_to": str
                },
                "user_info_channel_id": {
                    "value_type": TextChannel
                },
                "new_user_role_id": {
                    "value_type": Role
                },
                "member_role_id": {
                    "value_type": Role
                },
                "reaction_check_channel": {
                    "value_type": TextChannel
                },
            }
        }

        if self._bot.is_ready():
            self._permission_manager = self._bot.get_cog(PermissionsManager.Name)
            self._task.start()

    @Cog.listener()
    async def on_ready(self):
        self._permission_manager = self._bot.get_cog(PermissionsManager.Name)
        # await self._convert_existing_reactions()

    def cog_check(self, ctx: Context) -> bool:
        if not self._permission_manager:
            return False

        return self._permission_manager.has_permission(self.qualified_name, ctx.command, ctx.author)

    # region Commands

    @command()
    async def clear(self, ctx: Context, amount: Union[int, str]):
        config: ServerConfigs = self._get_config(ctx.guild.id)

        if str(ctx.guild.id) in config.clear_channel_id_blacklist:
            return

        if not amount:
            raise BadArgument("Argument amount must be an positive integer or 'all'")

        if type(amount) == int:
            if amount < 0:
                raise BadArgument("Argument amount must be an positive integer or 'all'")

            await ctx.channel.purge(limit=amount + 1)
            await ctx.send("Done.", delete_after=5)
        else:
            if amount != "all":
                raise BadArgument("Argument amount must be an positive integer or 'all'")

            await ctx.channel.purge(limit=None)
            await ctx.send("Cleared Everything.", delete_after=5)

    # endregion

    # region Listeners

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        config: ServerConfigs = self._get_config(payload.guild_id)

        if not config.member_role_id:
            return

        if str(payload.message_id) not in config.reaction_message_ids:
            return

        guild: Guild = self._bot.get_guild(payload.guild_id)
        member_role: Role = guild.get_role(int(config.member_role_id))
        member: Member = payload.member
        if member_role and member_role not in member.roles:
            await member.add_roles(member_role, reason=f"Reacted to message in accordance to the {self.qualified_name} Cog for the bot.")

        if config.new_user_role_id:
            new_member_role: Role = guild.get_role(int(config.new_user_role_id))
            if new_member_role in member.roles:
                await member.remove_roles(new_member_role, reason=f"Reacted to message in accordance to the {self.qualified_name} Cog for the bot. And had new member role.")

        channel: TextChannel = self._bot.get_channel(payload.channel_id)
        message: Message = channel.get_partial_message(payload.message_id)
        await message.remove_reaction(payload.emoji, payload.member)

    @Cog.listener()
    async def on_member_join(self, member: Member):
        config: ServerConfigs = self._get_config(member.guild.id)

        if not config.new_user_role_id:
            return

        guild: Guild = self._bot.get_guild(member.guild.id)
        new_member_role: Role = guild.get_role(int(config.new_user_role_id))

        if new_member_role:
            await member.add_roles(new_member_role, reason=f"Joined. {self.qualified_name} Cog operation.")

    # endregion

    # region Helpers

    @tasks.loop(count=1)
    async def _task(self):
        # Weird hack but works save enough... I hope.
        await self._convert_existing_reactions()

    async def _convert_existing_reactions(self):
        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        configs: dict = config_manager.get_cog_configs(self.qualified_name) if config_manager else {}

        for guild_id, v in configs.items():
            guild: Guild = self._bot.get_guild(int(guild_id))
            config: ServerConfigs = ServerConfigs.from_json(v)

            if not guild:
                continue

            channel: TextChannel = self._bot.get_channel(int(config.reaction_check_channel))
            if not channel:
                continue

            member_role: Role = guild.get_role(int(config.member_role_id))
            if not member_role:
                continue

            new_member_role: Role = guild.get_role(int(config.new_user_role_id))

            for message_id in config.reaction_message_ids:
                try:
                    message: Message = await channel.fetch_message(int(message_id))
                except NotFound:
                    continue

                for reaction in message.reactions:
                    async for user in reaction.users():
                        member: Member = guild.get_member(user.id)
                        if not member:
                            continue

                        if member_role not in member.roles:
                            await member.add_roles(member_role, reason=f"Reacted to message in accordance to the {self.qualified_name} Cog for the bot.")
                        if new_member_role in member.roles:
                            await member.remove_roles(new_member_role, reason=f"Reacted to message in accordance to the {self.qualified_name} Cog for the bot. And had new member role.")

                await message.clear_reactions()

    def _get_config(self, guild_id: int) -> ServerConfigs:
        config_manager: ConfigManager = self._bot.get_cog(ConfigManager.Name)
        return ServerConfigs.from_json(config_manager.get_config(self.qualified_name, str(guild_id))) if config_manager else ServerConfigs()

    # endregion


def setup(bot: Bot):
    bot.add_cog(ManagementTools(bot))
