from typing import Any


class HTTPMessage:
    """
    Represents a HTTP message
    NOTE: HTTPMessage attributes are common to requests and responses
    """

    def __init__(self, *args, **kwargs) -> None:
        # Start/status line
        self.version: str = kwargs.get("version", "HTTP/1.1")

        # Headers
        self.connection: str = kwargs.get("Connection", "")

        # Body
        self.body: Any = kwargs.get("body", None)

    def __str__(self) -> str:
        return self.serializer()

    def __iter__(self):
        for k in self.__dict__:
            yield k, getattr(self, k)

    def serializer(self) -> str:
        raise NotImplementedError

    @staticmethod
    def deserializer():
        raise NotImplementedError
