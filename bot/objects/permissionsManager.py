from utils.interfaces import JsonSerializable
from typing import Union


class ServerConfig(JsonSerializable):
    def __init__(self, permissions: dict = None, *_, **__):
        self.permissions: dict = permissions if permissions else {}
