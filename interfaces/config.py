from abc import ABC, abstractmethod

from configuration import ConfigurationDictionary
from discord.ext.commands import Cog

from interfaces import CogABCMeta, _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing


class ILoader(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    def load_configs(self, guild_id: int = None) -> None:
        pass


class ISaver(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    def save_configs(self, guild_id: int = None) -> None:
        pass


class IConfigFileManager(ILoader, ISaver, _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC,
                         metaclass=CogABCMeta):
    pass


class IConfigDeliverer(ABC, Cog, metaclass=CogABCMeta):
    @property
    @abstractmethod
    def get_configs(self) -> ConfigurationDictionary:
        pass


class IConfigManager(IConfigFileManager, IConfigDeliverer, ABC, metaclass=CogABCMeta):
    pass
