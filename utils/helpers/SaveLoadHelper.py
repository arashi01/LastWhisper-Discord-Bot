import json
import os

from utils import save_as_json, CustomConfigObject


def load_configs(guild_dict: dict, config_dir: str, config_obj: CustomConfigObject.__class__, guilds: [], guild_id: int = None) -> None:
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

        if os.path.isfile(file_dir + ".disabled"):
            os.rename(file_dir + ".disabled", file_dir)

        if not os.path.isfile(file_dir):
            save_as_json(file_dir, obj)

        with open(file_dir) as f:
            obj = config_obj.from_json(json.load(f))

        guild_dict[guild_id] = obj


def save_configs(guild_dict: dict, config_dir: str, config_obj: CustomConfigObject.__class__, guild_id: int = None) -> None:
    file_dir = f"{config_dir}/{guild_id}.json"
    if not guild_id:
        for key in guild_dict:
            save_as_json(file_dir, guild_dict[key])

    else:
        if guild_id not in guild_dict:
            save_as_json(file_dir, config_obj())

        save_as_json(file_dir, guild_dict[guild_id])
