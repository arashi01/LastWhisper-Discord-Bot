from discord.ext.commands import Bot, Cog, command, group, Context, ExtensionNotFound, ExtensionNotLoaded, is_owner
from discord import Embed
from pathlib import Path
from utils import saveLoad, interfaces
import os


class Config(interfaces.JsonSerializable):
    def __init__(self, extension_dir: str = "extensions", extension_states: dict[str, bool] = {}):
        self.extension_dir: str = extension_dir
        self.extension_states: dict[str, bool] = extension_states


class ExtensionManager(Cog):
    """
    This cog handles the management of extension files for the bot.
    The extensions are loaded according to the extension_dir setting which is default extensions.
    Furthermore all extensions are loaded by default. This can be disabled by providing the extension name and False in the
    config file under extension_states.

    An extension is simply a file that can be dynamically loaded, unloaded and reloaded where code is executed.
    The entry and exit point of the file is setup(bot: Bot) and teardown(bot: Bot).
    More information can be found in:
    https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html
    """

    def __init__(self, bot: Bot, config: Config = Config()):
        """
        Creates an instance of the Extension Manager cog used to manage the loading, unloading, and reloading of extensions in the bot.

        :param bot: The bot client.
        :type bot: Bot
        :param config: Extension specific configs.
        :type config: Config
        """
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
                # I honestly wished that / would work instead of . and that you can have the .py at the end. would make it easier then this mess.
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
    @is_owner()
    @group(name="Extensions", invoke_without_command=True)
    async def list_extensions(self, ctx: Context, extension_name: str = None):
        """
        Command group to list state of all extensions found in the extension directory set.
        Or the sate of one extension.

        :param ctx: Context.
        :type ctx: Context
        :param extension_name: Name of the extension file. (should not include .py, Directory might be chainable if you add a .)
        :type extension_name: str
        """
        embed: Embed = Embed()

        if extension_name:
            embed.title = "Loaded Extension"
            file_path = self._config.extension_dir + "." + extension_name
            path = Path(self._config.extension_dir, extension_name + ".py")
            if not path.is_file():
                await ctx.send(f"{extension_name} is not a valid extension name")
                return

            embed.add_field(name=extension_name,
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
    async def load_extension(self, ctx: Context, extension_name: str):
        """
        Loads the extension if it exists.

        :param ctx: Context.
        :type ctx: Context
        :param extension_name: Name of extension file.
        :type extension_name: str
        """
        try:
            self._bot.load_extension(self._config.extension_dir + "." + extension_name)
            await ctx.reply("Extension Loaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {extension_name}.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {extension_name} could not be loaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {extension_name} please contact bot admin.",
                            mention_author=False)

    @list_extensions.command()
    async def unload_extension(self, ctx: Context, extension_name: str):
        """
        Unloads the extension if it exists and is loaded.

        :param ctx: Context.
        :type ctx: Context
        :param extension_name: Name of extension file.
        :type extension_name: str
        """
        try:
            self._bot.unload_extension(self._config.extension_dir + "." + extension_name)
            await ctx.reply("Extension Unloaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {extension_name} loaded.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {extension_name} could not be unloaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {extension_name} please contact bot admin.",
                            mention_author=False)

    @list_extensions.command()
    async def reload_extension(self, ctx: Context, extension_name: str):
        """
        Reloads the extension if it exists and is loaded.

        :param ctx: Context.
        :type ctx: Context
        :param extension_name: Name of extension file.
        :type extension_name: str
        """
        try:
            self._bot.reload_extension(self._config.extension_dir + "." + extension_name)
            await ctx.reply(f"Extension {extension_name} reloaded.", mention_author=False)
        except ExtensionNotFound as e:
            await ctx.reply(f"There is no extension with the name {extension_name}.", mention_author=False)
        except ExtensionNotLoaded as e:
            await ctx.reply(f"The extension {extension_name} could not be loaded. There may be errors within.",
                            mention_author=False)
        except Exception as e:
            print(e)
            await ctx.reply(f"Critical error unloading extension {extension_name} please contact bot admin.",
                            mention_author=False)

    # endregion

    # region ExtensionConfigs
    _configs: dict[str, dict] = {}

    @classmethod
    def load_configs(cls):
        """
        Loads the config file for extensions.
        """
        flag: bool
        configs: dict[str, dict]
        flag, configs = saveLoad.load_from_json("extensionConfigs.json")

        if flag:
            cls._configs = configs
        else:
            print("No extension config file found. settings will be left as default.")

    @classmethod
    def merge_configs(cls, key: str, obj: interfaces.JsonSerializable):
        """
        Merges the loaded configs with the object.
        This is different then the Config Manager method as Cog configs should have defaults to ensure they work.
        Furthermore, not all settings should be overwritten. Also it results in a cleaner config file.

        :param key: Config key. Does not have to be name of Cog.
        :type key: str
        :param obj: Object which settings will be merged.
        :type obj: interfaces.JsonSerializable
        """
        if key in cls._configs:
            for k, v in cls._configs[key].items():
                obj.__dict__[k] = v

    @classmethod
    def set_config(cls, key: str, obj: interfaces.JsonSerializable):
        """
        Sets config object based on key and object provided.

        :param key: Config key. Does not have to be name of Cog.
        :type key: str
        :param obj: Object.
        :type obj: interfaces.JsonSerializable
        """
        cls._configs[key] = obj.to_json

    # endregion


def setup(bot: Bot):
    ExtensionManager.load_configs()
    bot.add_cog(ExtensionManager(bot))
