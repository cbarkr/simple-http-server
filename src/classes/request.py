from enums.methods import Methods, allowed_methods
from classes.message import HTTPMessage


class Request(HTTPMessage):
    """
    Represents a HTTP request
    By default, the request is 'GET / HTTP/1.1'
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(**kwargs)

        # Start line
        self.method: Methods = kwargs.get("method", Methods.HTTP_GET)
        self.context: str = kwargs.get("context", "/")

        # Headers
        self.host: str = kwargs.get("Host", "")
        self.user_agent: str = kwargs.get("User-Agent", "")
        self.accept: str = kwargs.get("Accept", "")
        self.accept_language: str = kwargs.get("Accept-Language", "")
        self.accept_encoding: str = kwargs.get("Accept-Encoding", "")
        self.referer: str = kwargs.get("Referer", "")
        self.upgrade_insecure_requests: int = kwargs.get("Upgrade-Insecure-Requests", 0)
        self.if_modified_since: str = kwargs.get("If-Modified-Since", "")
        self.if_none_match: str = kwargs.get("If-None-Match", "")
        self.cache_control: str = kwargs.get("Cache-Control", "")
        self.content_type: str = kwargs.get("Content-Type", "")
        self.content_length: str = kwargs.get("Content-Length", 0)

    def serializer(self) -> str:
        # First line must be in the form <method> <context> <version>
        if self.method not in allowed_methods:
            request_str = f"{self.method} {self.context} {self.version}\r\n"
        else:
            request_str = f"{self.method.value} {self.context} {self.version}\r\n"

        # Subsequent lines must be headers in the form <header-name>: <header-value>
        for k, v in self:
            if v and k not in ("method", "context", "version", "body"):
                k_formatted = "-".join(
                    [k_entry.capitalize() for k_entry in k.split("_")]
                )
                request_str += f"{k_formatted}: {v}\r\n"

        # Lastly, append the body (without the header name)
        if self.body:
            request_str += f"\r\n{self.body}\r\n"

        return request_str

    @staticmethod
    def deserializer(req) -> "Request":
        tokens = req.splitlines()
        method, context, version = tokens.pop(0).split()
        headers = {}
        body = ""

        try:
            method = Methods(method)
        except Exception:
            pass

        # Remove leading slash when accessed from browser
        if len(context) > 1 and context[0] == "/":
            # Remove leading slash
            context = context[1::]

        if tokens:
            try:
                # Body is indicated by a newline, which will be the first empty string here
                body_start = tokens.index("")
            except ValueError:
                # No body, everything must be headers
                headers = dict([h.split(": ") for h in tokens])
            else:
                # Request contains a body, parse headers and body accordingly
                headers = dict([h.split(": ") for h in tokens[:body_start:]])
                body = "\r\n".join(tokens[body_start + 1 : :])

        return Request(
            method=method, context=context, version=version, body=body, **headers
        )
