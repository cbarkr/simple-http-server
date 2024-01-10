from enums import status, methods
from classes import request, response
from utils import DateUtils, FileUtils


def createHandler(request: request.Request) -> response.Response:
    if not request.content_type:
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    # When creating an object, you must specify Content-Length
    if not request.content_length:
        return response.Response(
            status_code=status.StatusCode.HTTP_411_LENGTH_REQUIRED,
            status_phrase=status.StatusPhrase.HTTP_411_LENGTH_REQUIRED,
        )

    # Not actually creating anything

    # Mock OK response
    return response.Response()


def readHandler(request: request.Request) -> response.Response:
    if not request.context:
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    includes_body = request.method == methods.Methods.HTTP_GET

    if request.context == "/":
        if includes_body:
            headers = {
                "Content-Type": "application/json",
            }
            return response.Response(body="hello :)")
        return response.Response()
    elif request.context == "delay":
        import time
        time.sleep(2)
        return response.Response(body="delay")

    # Only serve HTML, anything else is forbidden
    if not request.context.endswith("html"):
        return response.Response(
            status_code=status.StatusCode.HTTP_403_FORBIDDEN,
            status_phrase=status.StatusPhrase.HTTP_403_FORBIDDEN,
        )

    headers = {
        "Content-Type": "text/html",
    }
    body = None

    try:
        # Try to serve the requested context (file)
        with open(request.context, "r") as f:
            headers.update(
                {
                    "Last-Modified": FileUtils.get_file_last_modified_time_as_string(
                        f.name
                    )
                }
            )

            body = str(f.read())

    except FileNotFoundError:
        # File not found, return 404
        return response.Response(
            status_code=status.StatusCode.HTTP_404_NOT_FOUND,
            status_phrase=status.StatusPhrase.HTTP_404_NOT_FOUND,
        )
    except Exception:
        # Some other exception occurred, return 400
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )
    else:
        # If cache header unspecified, return object with OK
        if not request.if_modified_since:
            return (
                response.Response(**headers, body=body)
                if includes_body
                else response.Response(**headers)
            )

        # Otherwise, check if cached object should be used
        else:
            if DateUtils.http_date_is_greater_than(
                headers["Last-Modified"],
                request.if_modified_since,
            ):
                return (
                    response.Response(**headers, body=body)
                    if includes_body
                    else response.Response(**headers)
                )
            else:
                # Not modified, return 304
                return response.Response(
                    status_code=status.StatusCode.HTTP_304_NOT_MODIFIED,
                    status_phrase=status.StatusPhrase.HTTP_304_NOT_MODIFIED,
                )


def updateHandler(request: request.Request) -> response.Response:
    if not request.content_type or not request.context:
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    # When updating an object, you must specify Content-Length
    if not request.content_length:
        return response.Response(
            status_code=status.StatusCode.HTTP_411_LENGTH_REQUIRED,
            status_phrase=status.StatusPhrase.HTTP_411_LENGTH_REQUIRED,
        )

    # Only allow access to HTML, anything else is forbidden
    if not request.context.endswith("html"):
        return response.Response(
            status_code=status.StatusCode.HTTP_403_FORBIDDEN,
            status_phrase=status.StatusPhrase.HTTP_403_FORBIDDEN,
        )

    try:
        # Try to open the file
        with open(request.context, "r"):
            pass

    except FileNotFoundError:
        # File not found, return 404
        return response.Response(
            status_code=status.StatusCode.HTTP_404_NOT_FOUND,
            status_phrase=status.StatusPhrase.HTTP_404_NOT_FOUND,
        )
    except Exception:
        # Some other exception occurred, return 400
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    # Not actually updating anything

    # Mock OK response
    return response.Response()


def deleteHandler(request: request.Request) -> response.Response:
    if not request.context:
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    # Only allow access to HTML, anything else is forbidden
    if not request.context.endswith("html"):
        return response.Response(
            status_code=status.StatusCode.HTTP_403_FORBIDDEN,
            status_phrase=status.StatusPhrase.HTTP_403_FORBIDDEN,
        )

    try:
        # Try to open the file
        with open(request.context, "r"):
            pass

    except FileNotFoundError:
        # File not found, return 404
        return response.Response(
            status_code=status.StatusCode.HTTP_404_NOT_FOUND,
            status_phrase=status.StatusPhrase.HTTP_404_NOT_FOUND,
        )
    except Exception:
        # Some other exception occurred, return 400
        return response.Response(
            status_code=status.StatusCode.HTTP_400_BAD_REQUEST,
            status_phrase=status.StatusPhrase.HTTP_400_BAD_REQUEST,
        )

    # Not actually deleting anything

    # Mock OK response
    return response.Response()


handlers = {
    methods.Methods.HTTP_POST: createHandler,
    methods.Methods.HTTP_GET: readHandler,
    methods.Methods.HTTP_HEAD: readHandler,
    methods.Methods.HTTP_PUT: updateHandler,
    methods.Methods.HTTP_DELETE: deleteHandler,
}


def handleCRUDByMethod(request: request.Request) -> response.Response:
    return handlers[request.method](request)
