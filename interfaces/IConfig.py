from abc import ABC, ABCMeta, abstractmethod

from utils.configuration import ConfigurationDictionary


class _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing(ABC, metaclass=ABCMeta):
    def __init__(self):
        self.guildDict: dict = {}


class Load(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @abstractmethod
    def load_configs(self, guild_id: int = None) -> None:
        pass


class Save(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @abstractmethod
    def save_configs(self, guild_id: int = None) -> None:
        pass


class ConfigFileManager(Load, Save, ABC, metaclass=ABCMeta):
    pass


class GetConfig(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @property
    @abstractmethod
    def get_configs(self) -> ConfigurationDictionary:
        pass


class Config(Load, Save, GetConfig, ABC, metaclass=ABCMeta):
    pass
