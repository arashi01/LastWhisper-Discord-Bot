from typing import Union

from discord.ext.commands import Bot, Cog, Command, Context, command
from discord import Member, Guild, Role
from utils.helpers.configManager import ConfigMethodHelpers
from objects.permissionsManager import ServerConfig


class PermissionsManager(Cog):
    """
    This cog managed permissions of commands.
    It is a purely opt in action where the cog that wishes to use it will setup a variable called permissions which
    will contain a list of commands that permissions will be set for.

    The cog will scan them and get the necessary name for the config file.
    Afterwords cogs can call has_permission in their check methods which will return a True if the user has permission or False if they do not.
    If the user is the server owner or no roles / users were set then it will default return True.

    WIP: Permission settings were the command will not work based or certain conditions.
    - User is not owner of server.
    - User is not owner of bot.
    - If empty return false.
    """
    Name: str = "PermissionsManager"

    def __init__(self, bot: Bot):
        """
        Cog that manages the permissions for commands.

        :param bot: The client.
        :type bot: Bot
        """
        self._bot = bot
        # Since it uses the config manager to add and remove permissions the config settings are added.
        self.config_settings = {
            "add": {
                "permissions": PermissionsManager.add_permission,
            },
            "remove": {
                "permissions": PermissionsManager.remove_permission,
            },
            "settings": {}
        }

        if not self._bot.is_ready():
            return

        self._setup_configs()

    @Cog.listener()
    async def on_ready(self):
        self._setup_configs()

    def _setup_configs(self):
        """
        Scans the cogs for permissions and adds them to the settings.
        """
        configs: dict = {}

        for k, v in self._bot.cogs.items():
            if k == self.qualified_name:
                continue

            if not hasattr(v, "permissions") or type(v.permissions) is not list:
                continue

            configs[k] = [c.qualified_name for c in v.permissions]

        # Due to the way the config manager is set this is how it is done.
        self.config_settings["settings"]["permission"] = configs

    def has_permission(self, cog_name: str, _command: Command, member: Member) -> bool:
        """
        Checks if the user has permission to use this command.

        :param cog_name: Name of the Cog to tell apart two commands from different Cogs.
        :type cog_name: str
        :param _command: The command being executed.
        :type _command: Command
        :param member: The member who invoked this command.
        :type member: Member
        :return: If the person has permission to use the command.
        :rtype: bool
        """
        if member.guild.owner_id == member.id:
            return True

        if not self._bot.is_ready():
            return False

        config: ServerConfig = ServerConfig.from_json(self._bot.get_cog("ConfigManager").get_config(self.qualified_name, str(member.guild.id)))

        if not hasattr(config, "permissions"):
            return True

        if cog_name not in config.permissions:
            return True

        cog_configs: dict = config.permissions[cog_name]
        if _command.qualified_name not in cog_configs:
            return True

        command_checks: dict = cog_configs[_command.qualified_name]

        # Role check
        if (roles := command_checks["roles"] if "roles" in command_checks else None) and next(
                (role for role in member.roles if str(role.id) in roles), None):
            return True

        # Individual member check.
        if "members" in command_checks and str(member.id) in command_checks["members"]:
            return True

        return False

    @command(name="Get_Command_Name")
    async def get_name(self, ctx: Context, command_name: str):
        """
        Gets the true name of the command or aliases. In order to configure the permissions.

        :param ctx: Context.
        :type ctx: Context
        :param command_name: Name of command.
        :type command_name: str
        """
        _command: Command = self._bot.get_command(command_name)
        if not _command:
            await ctx.reply(f"No command with name or aliases {command_name} could be found", mention_author=False)
            return

        await ctx.reply(_command.qualified_name, mention_author=False)

    @staticmethod
    def add_permission(existing_value, args, settings):
        cog_name, command_name, value, value_str = PermissionsManager._get_values(args)

        if cog_name not in settings or command_name not in settings[cog_name]:
            return existing_value

        if cog_name not in existing_value:
            existing_value[cog_name] = {}
        cog_configs = existing_value[cog_name]

        if command_name not in cog_configs:
            cog_configs[command_name] = {}
        command_configs = cog_configs[command_name]

        if type(value) is Role:
            if "roles" not in command_configs:
                command_configs["roles"] = []

            if value_str not in command_configs["roles"]:
                command_configs["roles"].append(value_str)

        elif type(value) is Member:
            if "members" not in command_configs:
                command_configs["members"] = []

            if value_str not in command_configs["members"]:
                command_configs["members"].append(value_str)

        return existing_value

    @staticmethod
    def remove_permission(existing_value, args, settings):
        cog_name, command_name, value, value_str = PermissionsManager._get_values(args)

        if cog_name not in settings or command_name not in settings[cog_name]:
            return existing_value

        if cog_name not in existing_value:
            return existing_value
        cog_configs = existing_value[cog_name]

        if command_name not in cog_configs:
            return existing_value
        command_configs = cog_configs[command_name]

        if type(value) is Role:
            if "roles" not in command_configs:
                command_configs["roles"] = []

            if value_str in command_configs["roles"]:
                command_configs["roles"].remove(value_str)

        elif type(value) is Member:
            if "members" not in command_configs:
                command_configs["members"] = []

            if value_str in command_configs["members"]:
                command_configs["members"].remove(value_str)

        return existing_value

    @staticmethod
    def _get_values(args) -> (str, str, Union[Role, Member], str):
        if len(args) < 3:
            raise ValueError("Not enough arguments. 3 needed.")

        if type(args[2]) is not Role or type(args[2]) is not Member:
            raise TypeError("Argument 3 is not a Role or Member.")

        cog_name: str = args[0]
        command_name: str = args[1]
        value: Union[Role, Member] = args[2]
        value_str: str = ConfigMethodHelpers.get_value_from_arg(value, {})

        return cog_name, command_name, value, value_str


def setup(bot: Bot):
    bot.add_cog(PermissionsManager(bot))
