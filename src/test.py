from pathlib import Path
from unittest import TestCase, main
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR

from classes.request import Request
from classes.response import Response
from enums.status import StatusCode, StatusPhrase
from enums.methods import Methods
from utils import DateUtilsBase, FileUtilsBase


class TestServer(TestCase):
    """
    Test HTTP socket server
    setUp and tearDown used to open new sockets for each test case
    """

    @classmethod
    def setUpClass(cls):
        cls.server_host = "localhost"
        cls.server_port = 9999
        cls.test_file = "test.html"

    def setUp(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.server_host, self.server_port))

    def tearDown(self):
        self.sock.shutdown(SHUT_RDWR)
        self.sock.close()

    def send(self, message):
        if not self.sock:
            return
        self.sock.sendall(bytes(message, "ascii"))

    def receive(self):
        if not self.sock:
            return
        return str(self.sock.recv(1024), "ascii")

    ##########
    #  GET   #
    ##########

    def test_get_authorized(self):
        req = Request()
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "hello :)")

    def test_get_unauthorized(self):
        req = Request(context="server.py")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_403_FORBIDDEN)
        self.assertEqual(response.body, "")

    def test_get_not_exists(self):
        req = Request(context="t.html")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_404_NOT_FOUND)
        self.assertEqual(response.body, "")

    def test_get_authorized_and_file_exists(self):
        req = Request(context=self.test_file)
        self.send(str(req))

        with open(self.test_file, "r") as f:
            file_body = str(f.read())
            expected_response_body = "\r\n".join(
                file_body.splitlines()
            )  # Split and rejoin to match line endings

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, expected_response_body)

    def test_get_authorized_and_file_exists_and_is_cached(self):
        # Should always be unmodified
        modified_timestamp = (
            FileUtilsBase.get_file_last_modified_time_in_s(Path(self.test_file)) + 10
        )
        modified_http_date = DateUtilsBase.get_http_date(modified_timestamp)

        headers = {"If-Modified-Since": modified_http_date}

        req = Request(context=self.test_file, **headers)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_304_NOT_MODIFIED)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_304_NOT_MODIFIED)
        self.assertEqual(response.body, "")

    ##########
    #  HEAD  #
    ##########

    def test_head_authorized(self):
        req = Request(method=Methods.HTTP_HEAD)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "")

    def test_head_unauthorized(self):
        req = Request(method=Methods.HTTP_HEAD, context="server.py")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_403_FORBIDDEN)
        self.assertEqual(response.body, "")

    def test_head_not_exists(self):
        req = Request(method=Methods.HTTP_HEAD, context="t.html")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_404_NOT_FOUND)
        self.assertEqual(response.body, "")

    def test_head_authorized_and_file_exists(self):
        req = Request(method=Methods.HTTP_HEAD, context=self.test_file)
        self.send(str(req))

        # TODO: Assert headers equal?

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "")

    def test_head_authorized_and_file_exists_and_is_cached(self):
        # Should always be unmodified
        modified_timestamp = (
            FileUtilsBase.get_file_last_modified_time_in_s(Path(self.test_file)) + 11
        )
        modified_http_date = DateUtilsBase.get_http_date(modified_timestamp)

        headers = {"If-Modified-Since": modified_http_date}

        req = Request(method=Methods.HTTP_HEAD, context=self.test_file, **headers)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_304_NOT_MODIFIED)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_304_NOT_MODIFIED)
        self.assertEqual(response.body, "")

    ##########
    #  POST  #
    ##########

    def test_post_with_content_length(self):
        content = "Test data"
        content_length = len(content)

        headers = {"Content-Type": "text/plain", "Content-Length": content_length}

        req = Request(method=Methods.HTTP_POST, body=content, **headers)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "")

    def test_post_without_content_length(self):
        headers = {
            "Content-Type": "text/plain",
        }

        req = Request(method=Methods.HTTP_POST, body="Test data", **headers)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_411_LENGTH_REQUIRED)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_411_LENGTH_REQUIRED)
        self.assertEqual(response.body, "")

    ##########
    #  PUT   #
    ##########

    def test_put_with_content_length(self):
        content = "Updated test data"
        content_length = len(content)

        headers = {"Content-Type": "text/plain", "Content-Length": content_length}

        req = Request(
            method=Methods.HTTP_PUT,
            context=self.test_file,
            body=content,
            **headers,
        )
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "")

    def test_put_without_content_length(self):
        headers = {
            "Content-Type": "text/plain",
        }

        req = Request(
            method=Methods.HTTP_PUT,
            context=self.test_file,
            body="Updated test data",
            **headers,
        )
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_411_LENGTH_REQUIRED)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_411_LENGTH_REQUIRED)
        self.assertEqual(response.body, "")

    def test_put_unauthorized(self):
        content = "Updated test data"
        content_length = len(content)

        headers = {"Content-Type": "text/plain", "Content-Length": content_length}

        req = Request(
            method=Methods.HTTP_PUT, context="server.py", body=content, **headers
        )
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_403_FORBIDDEN)
        self.assertEqual(response.body, "")

    def test_put_not_exists(self):
        content = "Updated test data"
        content_length = len(content)

        headers = {"Content-Type": "text/plain", "Content-Length": content_length}

        req = Request(
            method=Methods.HTTP_PUT, context="t.html", body=content, **headers
        )
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_404_NOT_FOUND)
        self.assertEqual(response.body, "")

    ##########
    # DELETE #
    ##########

    def test_delete_ok(self):
        req = Request(method=Methods.HTTP_DELETE, context=self.test_file)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_200_OK)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_200_OK)
        self.assertEqual(response.body, "")

    def test_delete_unauthorized(self):
        req = Request(method=Methods.HTTP_DELETE, context="server.py")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_403_FORBIDDEN)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_403_FORBIDDEN)
        self.assertEqual(response.body, "")

    def test_delete_not_exists(self):
        req = Request(method=Methods.HTTP_DELETE, context="t.html")
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_404_NOT_FOUND)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_404_NOT_FOUND)
        self.assertEqual(response.body, "")

    ##########
    #  Other #
    ##########

    def test_unsupported_method_not_ok(self):
        req = Request(method="UNSUPPORTED", context=self.test_file)
        self.send(str(req))

        response = Response.deserializer(self.receive())
        self.assertEqual(response.status_code, StatusCode.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_phrase, StatusPhrase.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.body, "")


if __name__ == "__main__":
    main()
