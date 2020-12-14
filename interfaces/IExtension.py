from abc import ABC, ABCMeta, abstractmethod

from discord.ext.commands import Context


class Enabled(ABC, metaclass=ABCMeta):
    @abstractmethod
    async def enable(self, ctx: Context) -> None:
        pass


class Disable(ABC, metaclass=ABCMeta):
    @abstractmethod
    async def disable(self, ctx: Context) -> None:
        pass


class IsEnabled(ABC, metaclass=ABCMeta):
    @abstractmethod
    def is_enabled(self, ctx: Context) -> bool:
        pass


class Extension(Enabled, Disable, IsEnabled, ABC, metaclass=ABCMeta):
    pass
