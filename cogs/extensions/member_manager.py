import discord
from discord.ext import commands
from discord.utils import get

from json import loads

import utils
from objects import MemberManagerConfig
from objects.configuration import ConfigurationDictionary, Configuration
from utils.cog_class import CogClass


class MemberManager(CogClass, name=utils.CogNames.MemberManager.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/member_manager", MemberManagerConfig)

        self.welcome_channel_message_ids = {}
        try:
            hold = utils.load_as_string("./.temp/member_manager")
            hold = loads(hold)
            for key, value in hold.items():
                self.welcome_channel_message_ids[int(key)] = value
            utils.os.remove("./.temp/member_manager")
        except FileNotFoundError:
            self.welcome_channel_message_ids = {}

    def cog_unload(self):
        utils.save_as_json("./.temp/member_manager", self.welcome_channel_message_ids)

    @commands.Cog.listener()
    async def on_ready(self):
        await super().on_ready()
        for guild_id, guild_config in self.guildDict.items():
            messages: [discord.message] = await self.client.get_channel(guild_config.welcome_channel_id).history(limit=None).flatten()
            message_ids: [int] = [message.id for message in messages]

            self.welcome_channel_message_ids[guild_id] = message_ids

            guild: discord.Guild = self.client.get_guild(guild_id)

            new_member_role: discord.Role = guild.get_role(guild_config.new_member_role_id)
            member_role: discord.Role = guild.get_role(guild_config.member_role_id)

            for message in messages:
                for users in [await reaction.users().flatten() for reaction in message.reactions]:
                    for user_id in [user.id for user in users]:
                        member: discord.Member = guild.get_member(user_id)
                        if new_member_role in member.roles:
                            await member.remove_roles(new_member_role)
                            await member.add_roles(member_role)

                await message.clear_reactions()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild_id = payload.guild_id
        guild_config: MemberManagerConfig = self.guildDict[guild_id]

        if not payload.channel_id == guild_config.welcome_channel_id:
            return

        if payload.message_id not in self.welcome_channel_message_ids[guild_id]:
            return

        member: discord.Member = payload.member

        guild: discord.Guild = self.client.get_guild(guild_id)

        new_member_role = guild.get_role(guild_config.new_member_role_id)
        member_role = guild.get_role(guild_config.member_role_id)

        if new_member_role in member.roles:
            await member.add_roles(member_role)
            await member.remove_roles(new_member_role)

        await (await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)).clear_reactions()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild: MemberManagerConfig = self.guildDict[member.guild.id]

        role: discord.Role = get(member.guild.roles, id=guild.new_member_role_id)
        await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild = self.guildDict[member.guild.id]
        embed = discord.Embed(title="User left.", description=f"User **{member.name}** has left this discord server.")
        embed.add_field(name="Joined On:", value=str(member.joined_at)[:-7])
        embed.add_field(name="Nickname was:", value=member.nick)
        embed.set_thumbnail(url=member.avatar_url)
        await get(member.guild.channels, id=guild.on_member_leave_logging_channel).send(embed=embed)

    @property
    def get_configs(self) -> ConfigurationDictionary:
        config: ConfigurationDictionary = ConfigurationDictionary()

        config.add_configuration(Configuration("member_role_id", "member_role_id", set=self.set))
        config.add_configuration(Configuration("new_member_role_id", "new_member_role_id", set=self.set))
        config.add_configuration(Configuration("welcome_channel_id", "welcome_channel_id", set=self.set))
        config.add_configuration(Configuration("on_member_leave_logging_channel", "on_member_leave_logging_channel", set=self.set))

        return config

    @property
    def get_function_roles_reference(self) -> dict:
        return {}


def setup(client: commands.bot):
    client.add_cog(MemberManager(client))
