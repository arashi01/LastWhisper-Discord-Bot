from enum import Enum


class CogNames(Enum):
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

# Deprecated Will be removed
class TypeCondition(Enum):
    NONE = 0
    CHANNEL = 1
    USER = 2
    ROLE = 3
    BOOL = 4
