from enum import Enum


class Methods(Enum):
    HTTP_GET = "GET"
    HTTP_HEAD = "HEAD"
    HTTP_POST = "POST"
    HTTP_PUT = "PUT"
    HTTP_DELETE = "DELETE"


allowed_methods = [m for m in Methods]
