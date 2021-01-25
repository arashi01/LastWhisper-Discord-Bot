from abc import ABC, abstractmethod

from discord.ext.commands import Context, Cog

from interfaces import CogABCMeta, _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing


class IEnabler(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def enable(self, ctx: Context) -> None:
        pass


class IDisabler(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    async def disable(self, ctx: Context) -> None:
        pass


class IEnabled(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @abstractmethod
    def is_enabled(self, ctx: Context) -> bool:
        pass


class IExtensionHandler(IEnabler, IDisabler, IEnabled, ABC, metaclass=CogABCMeta):
    pass
