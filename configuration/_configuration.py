from types import CoroutineType


class Configuration(object):
    # noinspection PyShadowingBuiltins
    def __init__(self, name: str, config_name: str, set=None, add=None, remove=None) -> None:
        self.name: str = name
        self.config_name: str = config_name

        self._set_function: CoroutineType = set
        self._add_function: CoroutineType = add
        self._remove_function: CoroutineType = remove

        # self.preview_embed: Embed = None

    @property
    def get_set_function(self):
        return self._set_function

    @property
    def get_add_function(self):
        return self._add_function

    @property
    def get_remove_function(self):
        return self._remove_function
