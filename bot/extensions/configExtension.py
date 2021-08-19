from discord.ext.commands import Bot, Cog, command, Context


class Config(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @command()
    async def test(self, ctx: Context):
        await ctx.send("Whats APP")


def setup(bot: Bot):
    bot.add_cog(Config(bot))
