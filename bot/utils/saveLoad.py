# File containing a collection of methods for managing files.
import json
from pathlib import Path


class ComplexEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, "to_json"):
            return o.to_json
        else:
            return json.JSONEncoder.default(self, o)


def save_to_json(file_path: str, obj):
    path: Path = Path(file_path)
    with open(path, "w") as file:
        json.dump(obj, file, indent=4, sort_keys=True, cls=ComplexEncoder)


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
