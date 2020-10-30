from objects import CustomConfigObject, TypeList, TypeObjects


class GeneralConfig(CustomConfigObject):
    def __init__(self, should_clear_command: bool = False, clear_command_exception_list: TypeList = None,
                 management_role_ids: TypeList = None, prefix: str = "|"):
        self.should_clear_command: bool = should_clear_command
        self.clear_command_exception_list: TypeList = TypeList(TypeObjects.Member) if not clear_command_exception_list else clear_command_exception_list
        self.management_role_ids: TypeList = TypeList(TypeObjects.Role) if not management_role_ids else management_role_ids
        self.prefix: str = prefix
