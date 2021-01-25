from abc import ABCMeta, ABC

from discord.ext.commands import CogMeta


class CogABCMeta(CogMeta, ABCMeta):
    pass


class _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing(ABC, metaclass=CogABCMeta):
    def __init__(self):
        self.guildDict: dict = {}
