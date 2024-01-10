from enums.status import StatusCode, StatusPhrase
from classes.message import HTTPMessage
from utils import DateUtils


class Response(HTTPMessage):
    """
    Represents a HTTP response
    By default, the response is 'HTTP/1.1 200 OK'
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(**kwargs)

        # Status line
        self.status_code: StatusCode = kwargs.get("status_code", StatusCode.HTTP_200_OK)
        self.status_phrase: StatusPhrase = kwargs.get(
            "status_phrase", StatusPhrase.HTTP_200_OK
        )

        # Headers
        self.access_control_allow_origin: str = kwargs.get(
            "Access-Control-Allow-Origin", ""
        )
        self.content_encoding: str = kwargs.get("Content-Encoding", "")
        self.content_type: str = kwargs.get("Content-Type", "text/plain")
        self.date: str = kwargs.get("Date", DateUtils.get_http_date())
        self.etag: str = kwargs.get("ETag", "")
        self.expires: str = kwargs.get("Expires", "")
        self.keep_alive: str = kwargs.get("Keep-Alive", "")
        self.last_modified: str = kwargs.get("Last-Modified", "")
        self.server: str = kwargs.get("Server", "MP Web Server")
        self.set_cookie: str = kwargs.get("Set-Cookie", "")
        self.transfer_encoding: str = kwargs.get("Transfer-Encoding", "")
        self.vary: str = kwargs.get("Vary", "")

    def serializer(self) -> str:
        # First line must be the status line in the form <version> <status-code> <status-phrase>
        response_str = (
            f"{self.version} {self.status_code.value} {self.status_phrase.value}\r\n"
        )

        # Subsequent lines must be headers in the form <header-name>: <header-value>
        for k, v in self:
            if v and (k not in ("version", "status_code", "status_phrase", "body")):
                k_formatted = "-".join(
                    [k_entry.capitalize() for k_entry in k.split("_")]
                )
                response_str += f"{k_formatted}: {v}\r\n"

        # Lastly, append the body (without the header name)
        if self.body:
            response_str += f"\r\n{self.body}\r\n"

        return response_str

    @staticmethod
    def deserializer(res) -> "Response":
        tokens = res.splitlines()
        start_line = tokens.pop(0).split()
        version = start_line[0]
        code = start_line[1]
        phrase = " ".join(start_line[2::])
        headers = {}
        body = ""

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

        return Response(
            version=version,
            status_code=StatusCode(int(code)),
            status_phrase=StatusPhrase(phrase),
            body=body,
            **headers,
        )
