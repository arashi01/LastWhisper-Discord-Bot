from discord.ext.commands import Bot, Cog, command, Context
from utils import saveLoad


class Config(Cog):
    def __init__(self, bot: Bot):
        self._bot = bot

        flag, obj = saveLoad.load_from_json("configs.json")
        self._configs: dict[str, dict] = obj if flag else {}

    def cog_unload(self):
        saveLoad.save_to_json("configs.json", self._configs)

    # todo: set config, load config, etc.


def setup(bot: Bot):
    bot.add_cog(Config(bot))
