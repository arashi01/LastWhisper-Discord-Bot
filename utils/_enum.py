from enum import Enum


class CogNames(Enum):
    """
    This is an enum of the names of the Cogs.
    This is used to help keep the naming consistent throughout the project.
    """
    ConfigManager = "ConfigManager"
    Debug = "Debug"
    General = "General"
    Logger = "Logger"

    CustomMessages = "CustomMessages"
    EventManager = "EventManager"
    ManagementTools = "ManagementTools"
    PlayManager = "PlayManager"
    MemberManager = "MemberManager"
    BuffManager = "BuffManager"
