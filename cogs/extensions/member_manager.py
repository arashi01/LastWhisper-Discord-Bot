from discord import Message, RawReactionActionEvent, Member, Guild, Embed, TextChannel
from discord.ext import commands

import utils
from objects import MemberManagerConfig
from objects.configuration import ConfigurationDictionary, Configuration
from utils.cog_class import CogClass


class MemberManager(CogClass, name=utils.CogNames.MemberManager.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/member_manager", MemberManagerConfig)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        guild_id = payload.guild_id
        config: MemberManagerConfig = self.guildDict[guild_id]

        if not ((channel := self.client.get_channel(config.welcome_channel_id)) and payload.channel_id == channel.id):
            return

        member: Member = payload.member

        guild: Guild = self.client.get_guild(guild_id)

        new_member_role = guild.get_role(config.new_member_role_id)
        member_role = guild.get_role(config.member_role_id)

        if new_member_role in member.roles:
            await member.add_roles(member_role)
            await member.remove_roles(new_member_role)

        await (await channel.fetch_message(payload.message_id)).clear_reactions()

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        # noinspection PyTypeChecker
        if not self.is_enabled(member):  # Done like this due to guild id being called the same.
            return

        guild: MemberManagerConfig = self.guildDict[member.guild.id]

        if role := member.guild.get_role(guild.new_member_role_id):
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member: Member):
        # noinspection PyTypeChecker
        if not self.is_enabled(member):  # Done like this due to guild id being called the same.
            return

        guild = self.guildDict[member.guild.id]
        embed = Embed(title="User left.", description=f"User **{member.name}** has left this discord server.")
        embed.add_field(name="Joined On:", value=str(member.joined_at)[:-7])
        embed.add_field(name="Nickname was:", value=member.nick)
        embed.set_thumbnail(url=member.avatar_url)
        await self.client.get_channel(guild.on_member_leave_logging_channel).send(embed=embed)

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
