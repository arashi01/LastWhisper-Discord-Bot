"""
This file mainly provides helper functions for saving and loading configurations.
"""
import json
import os

from pathlib import Path

from utils import save_as_json, CustomConfigObject


def load_configs(guild_dict: dict, config_dir: Path, config_obj: CustomConfigObject.__class__, guilds: [], guild_id: int = None, extension: str = ".pydict") -> None:
    if guild_id:
        pass
    else:
        guild_dict.clear()
        for filename in os.listdir(config_dir):
            if filename.endswith(extension):
                if filename[:len(extension) * -1] not in [str(guild.id) for guild in guilds]:
                    os.remove(config_dir + filename)


def load_configs_json(guild_dict: dict, config_dir: str, config_obj: CustomConfigObject.__class__, guilds: [], guild_id: int = None) -> None:
    """
    Function that loads the configuration files for a extension and adds them to the list of configurations.
    This clears the guild_dict of all entries so should be used with caution.

    :param guild_dict: A dictionary collection of configurations that are added.
    :param config_dir: The directory where the configurations are stored.
    :param config_obj: A class representation of the configuration.
    :param guilds: A list of guilds that the bot is registered with used to remove configs that are no longer valid.
    :param guild_id: The Discord server id or guild id that is used to load the configurations of a specific config.
    """
    if not guild_id:
        guild_dict.clear()
        for filename in os.listdir(config_dir):
            if filename.endswith(".json"):
                if filename[:-5] not in [str(guild.id) for guild in guilds]:
                    os.remove(f"{config_dir}/{filename}")
                    continue

                with open(f"{config_dir}/{filename}") as f:
                    json_obj = json.load(f)

                guild_dict[int(filename[:-5])] = config_obj.from_json(json_obj)

    else:
        file_dir = f"{config_dir}/{guild_id}.json"
        obj = config_obj()

        if os.path.isfile(file_dir + ".disabled"):  # Checks if there is an existing configuration that is disabled by default.
            os.rename(file_dir + ".disabled", file_dir)

        if not os.path.isfile(file_dir):
            save_as_json(file_dir, obj)

        with open(file_dir) as f:
            obj = config_obj.from_json(json.load(f))

        guild_dict[guild_id] = obj


def save_configs(guild_dict: dict, config_dir: str, config_obj: CustomConfigObject.__class__, guild_id: int = None) -> None:
    """
    Function used to save the configuration file of an extension.

    :param guild_dict: The full list of configurations.
    :param config_dir: The directory where the configuration is saved.
    :param config_obj: The object class of a config.
    :param guild_id: The Discord server or guild ID that is used to save the configs of a specific configuration.
    """

    file_dir = f"{config_dir}/{guild_id}.json"
    if not guild_id:
        for key in guild_dict:
            save_as_json(file_dir, guild_dict[key])

    else:
        if guild_id not in guild_dict:
            save_as_json(file_dir, config_obj())

        save_as_json(file_dir, guild_dict[guild_id])
