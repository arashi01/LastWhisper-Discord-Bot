from abc import ABC, abstractmethod

from discord.ext.commands import Context, Cog

from interfaces import CogABCMeta


class IEnabler(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def enable(self, ctx: Context) -> None:
        pass


class IDisabler(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def disable(self, ctx: Context) -> None:
        pass


class IEnabled(ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    def is_enabled(self, ctx: Context) -> bool:
        pass


class IExtensionHandler(IEnabler, IDisabler, IEnabled, ABC, metaclass=CogABCMeta):
    pass
