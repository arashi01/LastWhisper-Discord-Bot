from objects import CustomConfigObject, TypeObjects


class MemberManagerConfig(CustomConfigObject):
    def __init__(self, member_role_id: TypeObjects.Role = None, new_member_role_id: TypeObjects.Role = None, welcome_channel_id: TypeObjects.Channel = None, on_member_leave_logging_channel: TypeObjects.Channel = None):
        self.member_role_id: TypeObjects.Role = member_role_id
        self.new_member_role_id: TypeObjects.Role = new_member_role_id
        self.welcome_channel_id: TypeObjects.Channel = welcome_channel_id
        self.on_member_leave_logging_channel: TypeObjects.Channel = on_member_leave_logging_channel
