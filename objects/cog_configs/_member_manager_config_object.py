from objects import CustomConfigObject, TypeObjects


class MemberManagerConfig(CustomConfigObject):
    """Object representing the configs for the MemberManager extension

    This object purely holds information and does not do any form of validation.
    """
    def __init__(self, member_role_id: TypeObjects.Role = None,
                 new_member_role_id: TypeObjects.Role = None,
                 welcome_channel_id: TypeObjects.Channel = None,
                 on_member_leave_logging_channel: TypeObjects.Channel = None):
        """
        :param member_role_id: Discord role id used to mark a new user as a member.
        :type member_role_id: TypeObjects.Role
        :param new_member_role_id: Discord role id given to new members.
        :type new_member_role_id: TypeObjects.Role

        :param welcome_channel_id: Discord channel id that is checked for reactions by members.
        :type welcome_channel_id: TypeObjects.Channel

        :param on_member_leave_logging_channel: Discord channel id where a message is sent if when a member leaves the server.
        :type on_member_leave_logging_channel: TypeObjects.Channel
        """
        self.member_role_id: TypeObjects.Role = member_role_id
        self.new_member_role_id: TypeObjects.Role = new_member_role_id
        self.welcome_channel_id: TypeObjects.Channel = welcome_channel_id
        self.on_member_leave_logging_channel: TypeObjects.Channel = on_member_leave_logging_channel
