from socketserver import BaseRequestHandler, ThreadingTCPServer

from classes.request import Request
from classes.response import Response
from enums.status import StatusCode, StatusPhrase
from enums.methods import allowed_methods
from crud import handleCRUDByMethod


class ServerDetails:
    host = "localhost"
    port = 9999


class ThreadedTCPRequestHandler(BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024).strip(), "ascii")

        if not data:
            res = Response(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                status_phrase=StatusPhrase.HTTP_400_BAD_REQUEST,
            )
            self.request.sendall(bytes(str(res), "ascii"))
            return

        self.deserialized_request = Request.deserializer(data)
        self.fulfillRequest()

        try:
            self.request.sendall(bytes(str(self.serialized_response), "ascii"))
        except Exception:
            res = Response(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                status_phrase=StatusPhrase.HTTP_400_BAD_REQUEST,
            )
            self.request.sendall(bytes(str(res), "ascii"))

    def fulfillRequest(self):
        # Only handle specified methods
        if (
            not self.deserialized_request.method
            or self.deserialized_request.method not in allowed_methods
        ):
            self.serialized_response = Response(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                status_phrase=StatusPhrase.HTTP_400_BAD_REQUEST,
            )
            return

        try:
            self.serialized_response = handleCRUDByMethod(self.deserialized_request)
        except Exception:
            self.serialized_response = Response(
                status_code=StatusCode.HTTP_400_BAD_REQUEST,
                status_phrase=StatusPhrase.HTTP_400_BAD_REQUEST,
            )
        return


class ThreadedTCPServer(ThreadingTCPServer):
    def __init__(self, server_address, handler, meta=None, *args, **kwargs):
        super().__init__(server_address, handler)
        self.allow_reuse_address = True
        self.meta = meta


if __name__ == "__main__":
    with ThreadedTCPServer(
        (ServerDetails.host, ServerDetails.port), ThreadedTCPRequestHandler
    ) as server:
        host, port = server.server_address

        print(f"Serving on {host}:{port}")
        server.serve_forever()
