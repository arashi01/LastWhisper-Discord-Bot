class RoleObject(object):
    def __init__(self, command_name: str, config_dict_name: str, is_management: bool = False):
        self.command_name: str = command_name
        self.config_dict_name: str = config_dict_name
        self.is_management: bool = is_management or False
