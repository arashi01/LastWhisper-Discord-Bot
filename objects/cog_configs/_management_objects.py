from objects import CustomConfigObject, TypeList, TypeObjects


class ManagementToolsConfig(CustomConfigObject):
    def __init__(self, clear_allowed_role_ids: TypeList = None, clear_channel_id_blacklist: TypeList = None):
        self.clear_allowed_role_ids: TypeList = TypeList(TypeObjects.Role) if not clear_allowed_role_ids else clear_allowed_role_ids
        self.clear_channel_id_blacklist: TypeList = TypeList(TypeObjects.Channel) if not clear_channel_id_blacklist else clear_channel_id_blacklist
