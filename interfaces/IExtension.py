from abc import ABC, ABCMeta, abstractmethod

from discord.ext.commands import Context, Cog
from interfaces import CogABCMeta


class Enabled(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def enable(self, ctx: Context) -> None:
        pass


class Disable(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def disable(self, ctx: Context) -> None:
        pass


class IsEnabled(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    def is_enabled(self, ctx: Context) -> bool:
        pass


class Extension(Enabled, Disable, IsEnabled, ABC, metaclass=CogABCMeta):
    pass
