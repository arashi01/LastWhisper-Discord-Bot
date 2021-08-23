class JsonSerializable:
    @property
    def to_json(self) -> dict:
        return self.__dict__

    @classmethod
    def from_json(cls, data: dict):
        obj: cls = cls()
        obj.__dict__ = data
        return obj
