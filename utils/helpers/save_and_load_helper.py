"""
This file mainly provides helper functions for saving and loading configurations.
"""
import json
import os
from ast import literal_eval as _literal_eval
from pathlib import Path
from typing import Union

from utils import save_as_json, CustomConfigObject, logger, save_as_string, deprecated

default_disabled_extension = ".disabled"
default_extension = ".conf"


def load_configs(guild_dict: dict, config_dir: Path, config_obj: CustomConfigObject.__class__, guilds: [],
                 guild_id: int = None, extension: str = default_extension, clear_existing: bool = True) -> bool:
    """
        Function that loads the configuration files for a extension and adds them to the list of configurations.
        This clears the guild_dict of all entries so should be used with caution.

        :param guild_dict: A dictionary collection of configurations that are added.
        :param config_dir: The directory where the configurations are stored.
        :param config_obj: A class representation of the configuration.
        :param guilds: A list of guilds that the bot is registered with used to remove configs that are no longer valid.
        :param guild_id: The Discord server id or guild id that is used to load the configurations of a specific config.
        :param extension: The file extension to be used (Default is .conf)
        :param clear_existing: flag that if set True will clear the guild_dict
    """
    if not os.path.isdir(config_dir):
        logger.warning(
            f"The config directory '{config_dir}' does not exist. Kindly create one manually or save a configuration in")
        return False

    def _get_extension(x):
        return extension + (default_disabled_extension if not x else "")

    if guild_id:
        if flag := os.path.isfile(filename := str(guild_id) + extension) or os.path.isfile(
                filename + default_disabled_extension):
            hold = _try_get_obj(config_dir, filename + (default_disabled_extension if not flag else ""), config_obj)
            if hold:
                guild_dict[int(filename[:len(_get_extension(flag)) * -1])] = hold
            return True
        else:
            logger.warning(
                f"No such config file '{str(guild_id) + extension}' or '{str(guild_id) + extension + default_disabled_extension}' in directory {config_dir}.")
            return False

    else:
        if clear_existing:
            guild_dict.clear()

        for filename in os.listdir(config_dir):
            if (flag := filename.endswith(extension)) or filename.endswith(extension + default_disabled_extension):
                guild_dict[int(filename[:len(_get_extension(flag)) * -1])] = _try_get_obj(config_dir, filename + (
                    default_disabled_extension if not flag else ""), config_obj)
            else:
                logger.warning(f"{filename} Not a valid config file. Removing!")
                os.remove(config_dir / filename)
                continue

        return True


def save_configs(guild_dict: dict, config_dir: Path, config_obj: CustomConfigObject.__class__, guild_id: int = None,
                 extension: str = default_extension) -> None:
    """
        Function used to save the configuration file of an extension.

        :param guild_dict: The full list of configurations.
        :param config_dir: The directory where the configuration is saved.
        :param config_obj: The object class of a config.
        :param guild_id: The Discord server or guild ID that is used to save the configs of a specific configuration.
        :param extension: The file extension to be used (Default is .conf)
    """
    if guild_id:
        if guild_id in guild_dict:
            save_as_string(Path(config_dir / (str(guild_id) + extension)), str(guild_dict[guild_id]))
        else:
            if os.path.isfile(config_dir / (str(guild_id) + extension + default_disabled_extension)):
                os.rename(config_dir / (str(guild_id) + extension + default_disabled_extension),
                          config_dir / (str(guild_id) + extension))
            else:
                save_as_string(Path(config_dir / (str(guild_id) + extension)), str(config_obj()))

    else:
        for key, value in guild_dict.items():
            save_as_string(Path(config_dir / (str(key) + extension)), str(value))


def _try_get_obj(config_dir: Path, filename: str, config_obj: CustomConfigObject.__class__) -> Union[
    CustomConfigObject, None]:
    """Helper function to attempt to reduce some redundant code."""
    with open(config_dir / filename) as f:
        try:
            obj = config_obj(**_literal_eval(f.read()))
        except NameError:
            logger.warning(
                f"The config file {filename} under config dir {config_dir} is either not valid or corrupted and cannot be used.\nIt will be disabled until the file is either fixed or a new file is created.")
            os.rename(config_dir / filename, filename + default_disabled_extension)
            return None
        else:
            return obj
