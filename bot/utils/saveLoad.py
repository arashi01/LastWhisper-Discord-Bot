# File containing a collection of methods for managing files.
import json
from pathlib import Path


def save_to_json(file_path: str, obj: dict):
    path: Path = Path(file_path)
    with open(path, "w") as file:
        json.dump(obj, file, indent=2)


def load_from_json(file_path: str) -> (bool, dict):
    path: Path = Path(file_path)
    obj: dict = {}
    try:
        with open(path, "r+") as file:
            obj = json.load(file)
    except Exception as e:
        print(e)
        return False, obj

    return True, obj
