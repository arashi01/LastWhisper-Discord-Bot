from abc import ABCMeta

from discord.ext.commands import CogMeta


class CogABCMeta(CogMeta, ABCMeta):
    pass
