from utils.interfaces import JsonSerializable


class ServerConfigs(JsonSerializable):
    def __init__(self, user_info_channel_id: str = None, clear_channel_id_blacklist: list[str] = None, new_user_role_id: str = None, member_role_id: str = None, reaction_message_ids: list[str] = None, reaction_check_channel: str = None, *_, **__):
        self.user_info_channel_id: str = user_info_channel_id
        self.clear_channel_id_blacklist: list[str] = clear_channel_id_blacklist if clear_channel_id_blacklist else []
        self.new_user_role_id: str = new_user_role_id
        self.member_role_id = member_role_id
        self.reaction_message_ids: list[str] = reaction_message_ids if reaction_message_ids else []
        self.reaction_check_channel: str = reaction_check_channel
