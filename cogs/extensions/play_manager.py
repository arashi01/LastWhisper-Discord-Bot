from pathlib import Path

from objects import ConfigurationDictionary
from discord.ext import commands

import utils
from objects import PlayConfig
from objects.role_object import RoleObject
from utils.cog_class import CogClass


class PlayManager(CogClass, name=utils.CogNames.PlayManager.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, Path("./config/play_manager"), PlayConfig)

        self.player: dict = {}

    @commands.command()
    async def join(self, ctx: commands.Context):
        if ctx.voice_client is None:
            return await ctx.author.voice.channel.connect()
        else:
            if ctx.voice_client.is_playing() is False and not self.player[ctx.guild.id]['queue']:
                return await ctx.author.voice.channel.connect()

    @commands.command()
    async def play(self, ctx: commands.Context, url: str):
        pass

    @commands.command()
    async def stop(self, ctx: commands.Context):
        pass

    @commands.command()
    async def leave(self, ctx: commands.Context):
        return await ctx.voice_client.disconnect()

    @property
    def get_configs(self) -> ConfigurationDictionary:
        return ConfigurationDictionary()

    @property
    def role_list(self) -> dict:
        return {
            self.join.name: RoleObject("", "", True),
            self.play.name: RoleObject("", "", True),
            self.stop.name: RoleObject("", "", True),
            self.leave.name: RoleObject("", "", True)
        }


def setup(client: commands.bot):
    pass
    # client.add_cog(PlayManager(client))
