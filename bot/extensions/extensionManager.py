from discord.ext.commands import Bot, Cog, command, Context
from discord import Embed
from pathlib import Path
import os


class Config:
    def __init__(self, extension_dir: str = "extensions", extension_states: dict[str, bool] = {}):
        self.extension_dir: str = extension_dir
        self.extension_states: dict[str, bool] = extension_states


class ExtensionManager(Cog):
    _config: Config = Config()

    def __init__(self, bot: Bot, config: Config = Config()):
        self.bot = bot
        self._config = config

        # Ensures that this is only ran when the bot first stats up
        if bot.is_ready():
            return
        # load existing extensions
        for p in os.listdir(self._config.extension_dir):
            path: Path = Path(self._config.extension_dir, p)
            if str(path.absolute()) == __file__:
                continue

            if path.is_file():
                file_path: str = str(path).replace("/", ".")
                file_path = file_path[:file_path.rindex(".")]
                file_name = file_path.split(".")[-1]
                if file_name in self._config.extension_states and not self._config.extension_states[file_name]:
                    continue

                try:
                    bot.load_extension(file_path)
                except Exception as e:
                    print(e)

    @command()
    async def load_extension(self, ctx: Context, name: str):
        _Path: Path = Path(self._config.extension_dir, name + ".py")
        if not _Path.is_file():
            await ctx.send("Not a valid File.")
            return

        file_path: str = str(_Path).replace("/", ".")
        try:
            self.bot.load_extension(file_path[:file_path.rindex(".")])
        except Exception as e:
            print(e)
            await ctx.send(str(e))

    @command()
    async def unload_extension(self, ctx: Context, name: str):
        if self._config.extension_dir + "." + name not in self.bot.extensions.keys():
            await ctx.send(f"There is no extension with the name {name}")
            return

        try:
            self.bot.unload_extension(self._config.extension_dir + "." + name)
        except Exception as e:
            print(e)
            await ctx.send(str(e))

    @command()
    async def reload_extension(self, ctx: Context, name: str):
        if self._config.extension_dir + "." + name not in self.bot.extensions.keys():
            await ctx.send(f"There is no extension with the name {name}")
            return

        try:
            self.bot.reload_extension(self._config.extension_dir + "." + name)
        except Exception as e:
            print(e)
            await ctx.send(str(e))

    @command()
    async def list_extensions(self, ctx: Context, name: str = None):
        embed: Embed = Embed()

        if name:
            embed.title = "Loaded Extension"
            file_path = self._config.extension_dir + "." + name
            path = Path(self._config.extension_dir, name + ".py")
            if not path.is_file():
                await ctx.send(f"{name} is not a valid extension name")
                return

            embed.add_field(name=name, value=":green_circle:" if file_path in self.bot.extensions.keys() else ":red_circle:")
        else:
            loaded_extensions = self.bot.extensions.keys()
            for f in os.listdir(self._config.extension_dir):
                path = Path(self._config.extension_dir, f)
                if path.is_file():
                    file_path: str = self._config.extension_dir + "." + f[:f.rindex(".")]
                    embed.add_field(name=f[:f.rindex(".")], value=":green_circle:" if file_path in loaded_extensions else ":red_circle:")

        await ctx.reply(embed=embed, mention_author=False)


def setup(bot: Bot):
    bot.add_cog(ExtensionManager(bot))
