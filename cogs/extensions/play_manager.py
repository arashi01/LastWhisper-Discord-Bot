from discord.ext import commands

import utils
from objects import PlayConfig
from utils.cog_class import CogClass


class PlayManager(CogClass, name=utils.CogNames.PlayManager.value):
    def __init__(self, client: commands.bot):
        super().__init__(client, "./config/play_manager", PlayConfig)

        self.approved_roles_dict: dict = {
            "join": None,
            "play": None,
            "stop": None,
            "leave": None
        }

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


def setup(client: commands.bot):
    pass
    client.add_cog(PlayManager(client))
