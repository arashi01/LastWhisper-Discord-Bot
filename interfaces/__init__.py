from abc import ABCMeta, ABC

from discord.ext.commands import CogMeta


class CogABCMeta(CogMeta, ABCMeta):
    pass


class _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing(ABC, metaclass=CogABCMeta):
    guildDict: dict = {}
