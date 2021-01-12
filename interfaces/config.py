from abc import ABC, ABCMeta, abstractmethod

from configuration import ConfigurationDictionary


class _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing(ABC, metaclass=ABCMeta):
    def __init__(self):
        self._guildDict: dict = {}


class ILoader(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @abstractmethod
    def load_configs(self, guild_id: int = None) -> None:
        pass


class ISaver(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @abstractmethod
    def save_configs(self, guild_id: int = None) -> None:
        pass


class IConfigFileManager(ILoader, ISaver, ABC, metaclass=ABCMeta):
    pass


class IConfigDeliverer(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, metaclass=ABCMeta):
    @property
    @abstractmethod
    def get_configs(self) -> ConfigurationDictionary:
        pass


class IConfigManager(ILoader, ISaver, IConfigDeliverer, ABC, metaclass=ABCMeta):
    pass
