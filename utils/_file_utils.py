import os
from ast import literal_eval as _literal_eval
from json import dump
from pathlib import Path

from objects import CustomConfigObject

# Sets the working directory to be the directory of the bot.py file. This is done due to an error occurring when you run the bot outside the expected directory.
os.chdir(Path(__file__).parent.parent)


def load_as_string(path: Path) -> str:
    """
    Loads a document and returns the content as a string.

    :param path: Path to document.
    :return: Content as String.
    """
    result: str

    with open(path, "r") as f:
        result = f.read()

    return result


def load_as_dict(path: Path) -> dict:
    result: dict

    with open(path, "r") as f:
        result = _literal_eval(f.read())

    return result


def save_as_string(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        f.write(str(data))


def save_as_json(path: str, obj: object) -> None:
    """
    Saves the object as a json file.
    Note: does not end the file with the extension .json

    :param path: Path where object is saved to.
    :param obj: The object being saved.
    """
    try:
        Path(path[:path.rindex('/')]).mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            if isinstance(obj, CustomConfigObject):
                dump(obj.__dict__, f, indent=4, default=obj.converter)
            else:
                dump(obj, f, indent=4, default=lambda o: o.__dict__)
    except Exception as e:
        print(e)


def remove_file(path: str) -> None:
    """
    Removes a file in a given directory.

    :param path: The location of the file.
    """
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(e)
