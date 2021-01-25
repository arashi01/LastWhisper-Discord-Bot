from abc import ABC, abstractmethod

from discord.ext.commands import Cog

from interfaces import CogABCMeta, _HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing


class IRoleProvider(_HiddenGuildDictObjToEnsureThatSelfGuildDictIsAThing, ABC, Cog, metaclass=CogABCMeta):
    @property
    @abstractmethod
    def role_list(self) -> dict:
        """
                A function that returns a dictionary of function names and an array of allowed roles ids.

                :return: Dictionary of allowed roles for given commands.
        """
        pass
