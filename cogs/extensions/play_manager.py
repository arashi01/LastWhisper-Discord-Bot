from discord.ext import commands

import utils
from objects import PlayConfig
from configuration import ConfigurationDictionary
from utils.cog_class import CogClass


class PlayManager(CogClass, name=utils.CogNames.PlayManager.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/play_manager", PlayConfig)

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
    def get_function_roles_reference(self) -> dict:
        return {
            self.join.name: None,
            self.play.name: None,
            self.stop.name: None,
            self.leave.name: None
        }


def setup(client: commands.bot):
    pass
    client.add_cog(PlayManager(client))
