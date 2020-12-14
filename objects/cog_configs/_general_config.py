from objects import CustomConfigObject, TypeList, TypeObjects


class GeneralConfig(CustomConfigObject):
    """Object representing the general configs for a Discord server"""

    def __init__(self, should_clear_command: bool = False,
                 clear_command_exception_list: TypeList = None,
                 management_role_ids: TypeList = None,
                 prefix: str = "|"):
        """
        :param should_clear_command: Bool check if any command executed should be deleted.
        :type should_clear_command: bool
        :param clear_command_exception_list: A list of Discord member ids that acts as a override to the should_clear_command.
        :type clear_command_exception_list: TypeList
        :param management_role_ids: A collection of Discord role ids that represent the management roles.
        :type management_role_ids: TypeList
        :param prefix: The prefix for server commands. Default is '|' to prevent unexpected issues.
        :type prefix: str
        """

        self.should_clear_command: bool = should_clear_command
        self.clear_command_exception_list: TypeList = TypeList(TypeObjects.Member) if not clear_command_exception_list else clear_command_exception_list
        self.management_role_ids: TypeList = TypeList(TypeObjects.Role) if not management_role_ids else management_role_ids
        self.prefix: str = prefix
