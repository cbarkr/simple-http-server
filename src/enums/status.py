from enum import Enum


class StatusCode(Enum):
    HTTP_200_OK = 200
    HTTP_304_NOT_MODIFIED = 304
    HTTP_400_BAD_REQUEST = 400
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_411_LENGTH_REQUIRED = 411
    HTTP_500_INTERNAL_SERVER_ERROR = 500


class StatusPhrase(Enum):
    HTTP_200_OK = "OK"
    HTTP_304_NOT_MODIFIED = "Not Modified"
    HTTP_400_BAD_REQUEST = "Bad Request"
    HTTP_403_FORBIDDEN = "Forbidden"
    HTTP_404_NOT_FOUND = "Not Found"
    HTTP_411_LENGTH_REQUIRED = "Length Required"
    HTTP_500_INTERNAL_SERVER_ERROR = "Internal Server Error"
