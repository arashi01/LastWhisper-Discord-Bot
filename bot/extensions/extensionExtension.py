from discord.ext.commands import Bot, Cog, command, group, Context, ExtensionNotFound, ExtensionNotLoaded
from discord import Embed
from pathlib import Path
from utils import saveLoad, interfaces
import os


class Config(interfaces.JsonSerializable):
    def __init__(self, extension_dir: str = "extensions", extension_states: dict[str, bool] = {}):
        self.extension_dir: str = extension_dir
        self.extension_states: dict[str, bool] = extension_states


class ExtensionManager(Cog):
    def __init__(self, bot: Bot, config: Config = Config()):
        self._bot = bot
        self._config: Config = config
        self.merge_configs(self.qualified_name, config)

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

    # region Extension Management
    @group(name="Extensions", invoke_without_command=True)
    async def list_extensions(self, ctx: Context, name: str = None):
        embed: Embed = Embed()

        if name:
            embed.title = "Loaded Extension"
            file_path = self._config.extension_dir + "." + name
            path = Path(self._config.extension_dir, name + ".py")
            if not path.is_file():
                await ctx.send(f"{name} is not a valid extension name")
                return

            embed.add_field(name=name,
                            value=":green_circle:" if file_path in self._bot.extensions.keys() else ":red_circle:")
        else:
            embed.title = "Loaded Extensions"
            embed.description = "Extensions found and state."
            loaded_extensions = self._bot.extensions.keys()
            for f in os.listdir(self._config.extension_dir):
                path = Path(self._config.extension_dir, f)
                if path.is_file():
                    file_path: str = self._config.extension_dir + "." + f[:f.rindex(".")]
                    embed.add_field(name=f[:f.rindex(".")],
                                    value=":green_circle:" if file_path in loaded_extensions else ":red_circle:")

        await ctx.reply(embed=embed, mention_author=False)

    @list_extensions.command()
    async def load_extension(self, ctx: Context, name: str):
        try:
            self._bot.load_extension(self._config.extension_dir + "." + name)
            await ctx.reply("Extension Loaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {name}.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {name} could not be loaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {name} please contact bot admin.",
                            mention_author=False)

    @list_extensions.command()
    async def unload_extension(self, ctx: Context, name: str):
        try:
            self._bot.unload_extension(self._config.extension_dir + "." + name)
            await ctx.reply("Extension Unloaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {name} loaded.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {name} could not be unloaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {name} please contact bot admin.",
                            mention_author=False)

    @list_extensions.command()
    async def reload_extension(self, ctx: Context, name: str):
        try:
            self._bot.reload_extension(self._config.extension_dir + "." + name)
            await ctx.reply(f"Extension {name} reloaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {name}.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {name} could not be loaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {name} please contact bot admin.",
                            mention_author=False)

    # endregion

    # region ExtensionConfigs
    _configs: dict[str, dict] = {}

    @classmethod
    def load_configs(cls):
        flag: bool
        configs: dict[str, dict]
        flag, configs = saveLoad.load_from_json("extensionConfigs.json")

        if flag:
            cls._configs = configs

    @classmethod
    def merge_configs(cls, key: str, obj: interfaces.JsonSerializable):
        if key in cls._configs:
            for k, v in cls._configs[key].items():
                obj.__dict__[k] = v

    @classmethod
    def set_config(cls, key: str, obj: interfaces.JsonSerializable):
        cls._configs[key] = obj.to_json

    # endregion


def setup(bot: Bot):
    ExtensionManager.load_configs()
    bot.add_cog(ExtensionManager(bot))
