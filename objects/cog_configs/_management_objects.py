from objects import CustomConfigObject, TypeList, TypeObjects


class ManagementToolsConfig(CustomConfigObject):
    """
    Object representing the configs for the ManagementTools extension.
    This object holds information only and does not do any form of validation.
    """

    def __init__(self, clear_allowed_role_ids: TypeList = None, clear_channel_id_blacklist: TypeList = None):
        """
        :param clear_allowed_role_ids: Collection of Discord role ids that are allowed to execute the clear command.
        :param clear_channel_id_blacklist: Collection of Discord channel ids where the clear command is not allowed to be executed.
        """
        self.clear_allowed_role_ids: TypeList = TypeList(
            TypeObjects.Role) if not clear_allowed_role_ids else clear_allowed_role_ids
        self.clear_channel_id_blacklist: TypeList = TypeList(
            TypeObjects.Channel) if not clear_channel_id_blacklist else clear_channel_id_blacklist
