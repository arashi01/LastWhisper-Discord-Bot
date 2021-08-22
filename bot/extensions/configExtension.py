from typing import Union

from discord import Guild, Member, Role, Emoji, TextChannel, VoiceChannel
from discord.ext.commands import Bot, Cog, command, Context

from utils import saveLoad


class ConfigMethodHelpers:
    @staticmethod
    def set(existing_value, args: tuple, settings: dict):
        """
        Generic method to set variable.
        Its recommended to create your own if this is missing features that are not normally found.

        :param existing_value: value that is already there.
        :param args: all the arguments passed to the command.
        :param settings: settings for the variable.
        :return: new value.
        """
        return ConfigMethodHelpers.get_value_from_arg(args[0], settings)

    @staticmethod
    def add(existing_value: list, args: tuple, settings: dict):
        """
            Generic method to add variable.
            Its recommended to create your own if this is missing features that are not normally found.

            :param existing_value: value that is already there.
            :param args: all the arguments passed to the command.
            :param settings: settings for the variable.
            :return: new value.
        """
        value: Union[str, int, bool, dict] = ConfigMethodHelpers.get_value_from_arg(args[0], settings)

        if type(existing_value) is not list:
            existing_value = []

        existing_value.append(value)
        return existing_value

    @staticmethod
    def remove(existing_value: list, args: tuple, settings: dict):
        """
            Generic method to remove variable.
            Its recommended to create your own if this is missing features that are not normally found.

            :param existing_value: value that is already there.
            :param args: all the arguments passed to the command.
            :param settings: settings for the variable.
            :return: new value.
        """
        value = args[0]
        if type(value) is not int:
            raise TypeError("argument needs to be of type int.")

        if type(existing_value) is not list:
            existing_value = []

        existing_value.pop(value)
        return existing_value

    @staticmethod
    def get_value_from_arg(arg: Union[Emoji, Member, Role, TextChannel, VoiceChannel, str, int, bool, dict], settings):
        """
        Helper method to parse an argument into a more readable format and do a basic type check.
        Highly recommend writing your own if this one does not do all the functions needed.

        :param arg: Value to be parsed.
        :type arg: Emoji | Member | Role | TextChannel | VoiceChannel | str | int | bool | dict
        :param settings: Settings for the variable being set.
        :type settings: dict
        :return: what is returned.
        :rtype: str | int | bool | dict
        """
        if "value_type" in settings:
            value_type = settings["value_type"]
            if not type(arg) is value_type:
                raise TypeError(f"value {arg} does not match type {type(value_type)}")

        if isinstance(arg, (Member, Role, TextChannel, VoiceChannel)):
            return str(arg.id)

        if isinstance(arg, Emoji):
            return f"<:{arg.name}:{arg.id}>"

        return arg


class ConfigManager(Cog):
    """
    Cog with the main goal to provide configuration features to the Discord side through a CLI approach.
    Other Cogs can hook into the features of this Cog through the "config_settings" dictionary (see config command for more info)
    and utilize the methods provided to set and get configurations which will be saved automatically on Cog destruction.
    """
    Name = "ConfigManager"

    def __init__(self, bot: Bot):
        self._bot: bot = bot

        flag, obj = saveLoad.load_from_json("configs.json")
        self._configs: dict[str, dict[str, dict]] = obj if flag else {}

    def cog_unload(self):
        saveLoad.save_to_json("configs.json", self._configs)

    # commands
    @command(name="Config")
    async def config(self, ctx: Context, cog_name: str = None, action: str = None, key: str = None,
                     *args: Union[Member, Role, TextChannel, VoiceChannel, Emoji, int, bool, dict, str]) -> None:
        """
        Command for setting config based on object "hooks".
        This is primarily designed around the idea of a CLI tool.
        The way one Cog hooks into this is by having a self.config_settings as one of its attributes.
        This is a dictionary containing the information that will be used.

        The keywords "list" and "settings" are special actions that will be treated differently.
        "list" will display information.
        "settings" will not be called but will be passed to the other actions except for list.

        :param ctx: Context from api.
        :type ctx: Context
        :param cog_name: Name of Cog to configure.
        :type cog_name: str
        :param action: Name of action to be taken.
        :type action: str
        :param key: Name of key.
        :type key: str
        :param args: Tuple of additional arguments provided to callback methods.
        :type args: Member | Role | TextChannel | VoiceChannel | Emoji | int | bool | dict | str
        """
        # getting the cog config settings.
        cog: Cog = self._bot.get_cog(cog_name)
        if not cog:
            await ctx.reply(f"Sorry no cog with name {cog_name} found.", mention_author=False)
            return

        if not hasattr(cog, "config_settings"):
            return

        # check to make sure that the cog actually supports the settings idea.
        # noinspection PyUnresolvedReferences
        config_settings: dict = cog.config_settings
        if action == "settings" and action not in config_settings:
            return

        actions: dict = config_settings[action]
        if key not in actions or not callable(actions[key]):
            return

        callback = actions[key]

        # Getting settings
        settings: dict = config_settings["settings"] if "settings" in config_settings else {}

        if self.has_config(cog_name, str(ctx.guild.id)):
            config: dict = self.get_config(cog_name, str(ctx.guild.id))
        else:
            if "default_config" not in settings:
                raise NotImplementedError(f"The default_config setting has not been implemented in cog {cog_name}")

            # in case settings are missing completely a new one default one is created.
            obj = settings["default_config"]()
            config: dict = obj.to_json() if hasattr(obj, "to_json") else obj.__dict__
            self.set_config(cog_name, str(ctx.guild.id), config)

        existing_value = config[key] if key in config else None

        # List break off point
        if action == "list":
            await callback(ctx, key, config, args)
        else:
            config[key] = callback(existing_value=existing_value, args=args, settings=settings[key] if key in settings else {})

    @command(name="Reload_Configs")
    async def reload_configs(self, ctx: Context) -> None:
        """
        Command to reload configs live.
        """
        flag, obj = saveLoad.load_from_json("configs.json")

        if flag:
            self._configs: dict[str, dict[str, dict]] = obj

        await ctx.reply("Configs reloaded successfully." if flag else "There was an issue loading the configs. No changes made.", mention_author=False)

    @command(name="Save_Configs")
    async def save_configs(self, ctx: Context) -> None:
        """
        Command to save live configs.
        """
        saveLoad.save_to_json("configs.json", self._configs)
        await ctx.reply("Configs saved successfully.", mention_author=False)

    def get_config(self, cog_name: str, server_id: str) -> dict:
        """
        Returns the config dictionary for a Cog in a server.

        :param cog_name: Name of Cog used.
        :type cog_name: str
        :param server_id: server / guild ID (provided as string cause json format)
        :type server_id: str
        :return: config dictionary.
        :rtype: dict
        """
        return self._configs[server_id][cog_name] if self.has_config(cog_name, server_id) else {}

    def set_config(self, cog_name: str, server_id: str, obj: dict) -> None:
        """
        Sets the Cog config for a server.
        Additionally creates any missing dictionary entries.

        :param cog_name: Name of Cog used.
        :type cog_name: str
        :param server_id: server / guid ID (provided as string cause json format)
        :type server_id: str
        :param obj: config to be saved.
        :type obj: dict
        """
        if server_id not in self._configs:
            self._configs[server_id] = {}

        if cog_name not in self._configs[server_id]:
            self._configs[server_id][cog_name] = obj

    def has_config(self, cog_name: str, server_id: str) -> bool:
        """
        Checks if config exists for Cog in server.

        :param cog_name: Name of Cog
        :type cog_name: str
        :param server_id: Id for server/guild (given as str because of json format)
        :type server_id: str
        :return: if config exists.
        :rtype: bool
        """
        if server_id not in self._configs:
            return False

        if cog_name not in self._configs[server_id]:
            return False

        return True

    # Listeners
    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        self._configs[str(guild.id)] = {}

    @Cog.listener()
    async def on_guild_leave(self, guild: Guild):
        self._configs.pop(str(guild.id))


def setup(bot: Bot):
    bot.add_cog(ConfigManager(bot))
