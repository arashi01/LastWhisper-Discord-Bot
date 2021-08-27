from typing import Union, Any

from discord import Guild, Member, Role, Emoji, TextChannel, VoiceChannel, Message
from discord.ext.commands import Bot, Cog, command, Context, when_mentioned

from extensions.permissionsExtension import PermissionsManager
from utils import saveLoad


class ConfigManager(Cog):
    """
    Cog with the main goal to provide configuration features to the Discord side through a CLI approach.
    Other Cogs can hook into the features of this Cog through the "config_settings" dictionary (see config command for more info)
    and utilize the methods provided to set and get configurations which will be saved automatically on Cog destruction.
    """
    Name = "ConfigManager"

    def __init__(self, bot: Bot):
        self._permission_manager: PermissionsManager
        self._bot: bot = bot
        self.permissions = [self.config, self.reload_configs, self.save_configs, self.set_prefixes]

        flag, obj = saveLoad.load_from_json("configs.json")
        self._configs: dict[str, Any] = obj if flag else {}

        if self._bot.is_ready():
            self._permission_manager = self._bot.get_cog(PermissionsManager.Name)

    @Cog.listener()
    async def on_ready(self):
        self._permission_manager = self._bot.get_cog(PermissionsManager.Name)

    def cog_unload(self):
        saveLoad.save_to_json("configs.json", self._configs)

    # commands
    @command("SetPrefixes")
    async def set_prefixes(self, ctx: Context, *args):
        if str(ctx.guild.id) not in self._configs:
            self._configs[str(ctx.guild.id)] = {"prefixes": list(args)}
        else:
            self._configs[str(ctx.guild.id)]["prefixes"] = list(args)

        await ctx.reply(f"Prefixes set to " + " ".join(["'" + x + "'" for x in list(args)]) + ".", mention_author=False)

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
            config: dict = obj.to_json if hasattr(obj, "to_json") else obj.__dict__
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
        Tries to return the default config if none was found. Else just returns an empty dict.

        :param cog_name: Name of Cog used.
        :type cog_name: str
        :param server_id: server / guild ID (provided as string cause json format)
        :type server_id: str
        :return: config dictionary.
        :rtype: dict
        """
        if self.has_config(cog_name, server_id):
            return self._configs[server_id][cog_name]

        cog: Cog = self._bot.get_cog(cog_name)
        if cog and hasattr(cog, "config_settings"):
            if "settings" in cog.config_settings and "default_config" in cog.config_settings["settings"]:
                obj = cog.config_settings["settings"]["default_config"]()
                return obj.to_json if hasattr(obj, "to_json") else obj.__dict__

        return {}

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
            self._configs[server_id] = {"prefix": "|"}

        if cog_name not in self._configs[server_id]:
            self._configs[server_id][cog_name] = obj

    def get_cog_configs(self, cog_name: str) -> dict[str, dict]:
        """
        Returns all the configs for a cog.

        :param cog_name: Name of Cog to get configs for.
        :type cog_name: str
        :return: dictionary of configs with server / guild ID.
        :rtype: dict[str, dict]
        """
        result: dict = {}

        for k, v in self._configs.items():
            if cog_name in v:
                result[k] = v[cog_name]

        return result

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
    async def on_guild_leave(self, guild: Guild):
        self._configs.pop(str(guild.id))

    # region Checks

    def cog_check(self, ctx: Context) -> bool:
        if not self._permission_manager:
            return True

        return self._permission_manager.has_permission(self.qualified_name, ctx.command, ctx.author)

    # endregion

    # region Prefixes

    @staticmethod
    def get_prefix(*prefixes):
        def inner(bot: Bot, message: Message):
            config_manager: ConfigManager = bot.get_cog(ConfigManager.Name)
            if not config_manager:
                return list(prefixes)

            _prefixes: list = list(config_manager.get_config("prefixes", str(message.guild.id)))
            return when_mentioned(bot, message) + _prefixes

        return inner

    # endregion


def setup(bot: Bot):
    bot.add_cog(ConfigManager(bot))
