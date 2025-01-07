import datetime
import json
import random
import string

import unittest
import requests_mock
import gazu
from gazu.__version__ import __version__

from gazu import client as raw
from gazu.exception import (
    RouteNotFoundException,
    AuthFailedException,
    MethodNotAllowedException,
    NotAuthenticatedException,
    NotAllowedException,
    TooBigFileException,
    ServerErrorException,
)

from utils import add_verify_file_callback, mock_route


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class BaseFuncTestCase(ClientTestCase):
    def test_host_is_up(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "HEAD", raw.get_host())
            self.assertTrue(raw.host_is_up())
        self.assertFalse(raw.host_is_up())

    def test_host_is_valid(self):
        self.assertFalse(raw.host_is_valid())
        with requests_mock.mock() as mock:
            mock_route(mock, "HEAD", raw.get_host())
            mock_route(
                mock,
                "POST",
                "auth/login",
                text={},
                status_code=401,
            )
            self.assertTrue(raw.host_is_valid())

    def test_set_event_host(self):
        gazu.set_event_host("newhost")
        self.assertEqual(raw.default_client.event_host, "newhost")
        gazu.set_event_host("http://gazu.change.serverhost/api")

    def test_get_host(self):
        self.assertEqual(raw.get_host(), raw.default_client.host)

    def test_get_event_host(self):
        self.assertEqual(gazu.get_event_host(), raw.default_client.host)

    def test_set_host(self):
        raw.set_host("newhost")
        self.assertEqual(raw.get_host(), "newhost")
        raw.set_host("http://gazu-server/api")

    def test_set_tokens(self):
        pass

    def test_make_auth_header(self):
        self.assertEqual(
            raw.default_client.make_auth_header(),
            raw.make_auth_header(),
        )

    def test_url_path_join(self):
        root = raw.get_host()
        items = ["data", "persons"]
        expected_url = "{host}/data/persons".format(host=raw.get_host())

        self.assertEqual(raw.url_path_join(root, *items), expected_url)

    def test_get_full_url(self):
        test_route = "test_route"
        expected_url = raw.url_path_join(raw.get_host(), test_route)

        self.assertEqual(raw.get_full_url(test_route), expected_url)

    def test_get(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", "data/persons", text={"first_name": "John"}
            )
            self.assertEqual(raw.get("data/persons"), {"first_name": "John"})

    def test_get_two_clients(self):
        with requests_mock.mock() as mock:
            second_client = gazu.raw.create_client("http://second.host/api")
            mock_route(
                mock, "GET", "data/persons", text={"first_name": "John"}
            )
            self.assertEqual(raw.get("data/persons"), {"first_name": "John"})
            self.assertRaises(
                requests_mock.exceptions.NoMockAddress,
                raw.get,
                "data/persons",
                client=second_client,
            )
            mock_route(
                mock,
                "GET",
                raw.get_full_url("data/persons", client=second_client),
                text={"first_name": "John2"},
            )
            self.assertEqual(
                raw.get("data/persons", client=second_client),
                {"first_name": "John2"},
            )

    def test_post(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/persons",
                text={"id": "person-01", "first_name": "John"},
            )
            self.assertEqual(
                raw.post("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_post_with_a_date_field(self):
        now = datetime.datetime.now()
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/persons",
                text={"id": "person-01", "first_name": "John"},
            )
            self.assertEqual(
                raw.post("data/persons", {"birth_date": now}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_put(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/persons",
                text={"id": "person-01", "first_name": "John"},
            )
            self.assertEqual(
                raw.put("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_update(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "PUT",
                "data/persons/person-1",
                text={
                    "id": "person-1",
                    "first_name": "John",
                    "last_name": "Doe",
                },
            )
            data = {"last_name": "Doe"}
            self.assertEqual(
                raw.update("persons", "person-1", data),
                {"id": "person-1", "first_name": "John", "last_name": "Doe"},
            )

    def test_delete(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", "data/persons/person-01", text="")
            self.assertEqual(raw.delete("data/persons/person-01"), "")

    def test_fetch_all(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons",
                text=[{"first_name": "John"}],
            )
            self.assertEqual(
                raw.fetch_all("persons"), [{"first_name": "John"}]
            )

    def test_fetch_first(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons",
                text=[{"first_name": "John"}, {"first_name": "Jane"}],
            )
            self.assertEqual(
                raw.fetch_first("persons"), {"first_name": "John"}
            )

            mock_route(mock, "GET", "data/persons", text=[])
            self.assertIsNone(raw.fetch_first("persons"))

    def test_query_string(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/projects?name=Test",
                text=[{"name": "Project"}],
            )
            self.assertEqual(
                raw.fetch_first("projects", {"name": "Test"}),
                {"name": "Project"},
            )

            mock_route(mock, "GET", "data/persons", text=[])
            self.assertIsNone(raw.fetch_first("persons"))

    def test_fetch_one(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/persons/person-01",
                text={"id": "person-01", "first_name": "John"},
            )
            self.assertEqual(
                raw.fetch_one("persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_create(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "data/persons",
                text={"id": "person-01", "first_name": "John"},
            )
            self.assertEqual(
                raw.create("persons", {"first_name": "John"}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_version(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "/", text={"version": "0.2.0"})
            self.assertEqual(raw.get_api_version(), "0.2.0")

    def test_make_auth_token(self):
        tokens = {"access_token": "token_test"}

        raw.set_tokens(tokens)
        self.assertEqual(
            raw.make_auth_header(),
            {
                "Authorization": "Bearer token_test",
                "User-Agent": "CGWire Gazu %s" % __version__,
            },
        )

    def test_upload(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "data/new-file",
                    text={"id": "person-01", "first_name": "John"},
                )

                add_verify_file_callback(
                    mock, {"file": test_file.read(), "test": "True"}
                )

                raw.upload(
                    "data/new-file",
                    "./tests/fixtures/v1.png",
                    data={"test": True},
                )

            error_value = "".join(
                [
                    random.choice(
                        string.ascii_uppercase + string.ascii_lowercase
                    )
                    for _ in range(10)
                ]
            )

            with requests_mock.Mocker() as mock:
                for field in ["message", "error"]:
                    mock_route(
                        mock,
                        "POST",
                        "data/new-file",
                        text={field: error_value},
                    )

                    with self.assertRaises(
                        gazu.client.UploadFailedException
                    ) as context:
                        raw.upload(
                            "data/new-file",
                            "./tests/fixtures/v1.png",
                            data={"test": True},
                        )

                    self.assertTrue(str(context.exception) == error_value)

    def test_upload_multiple_files(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock_route(
                    mock,
                    "POST",
                    "data/new-file",
                    text={"id": "person-01", "first_name": "John"},
                )
                test_file_read = test_file.read()
                add_verify_file_callback(
                    mock,
                    {
                        "file": test_file_read,
                        "file-1": test_file_read,
                        "test": "True",
                    },
                )

                raw.upload(
                    "data/new-file",
                    "./tests/fixtures/v1.png",
                    data={
                        "test": True,
                    },
                    extra_files=["./tests/fixtures/v1.png"],
                )

    def test_check_status(self):
        class Request(object):
            def __init__(self, status_code):
                self.status_code = status_code

        class RequestText(object):
            def __init__(self, status_code):
                self.status_code = status_code
                self.text = "Error on server"

        class RequestJSON(object):
            def __init__(self, status_code):
                self.status_code = status_code
                self.text = '{"stacktrace": "stacktrace", "message": "error"}'

            def json(self):
                return json.dumps(self.text)

        self.assertRaises(
            NotAuthenticatedException, raw.check_status, Request(401), "/"
        )
        self.assertRaises(
            NotAllowedException, raw.check_status, Request(403), "/"
        )
        self.assertRaises(
            RouteNotFoundException, raw.check_status, Request(404), "/"
        )
        self.assertRaises(
            MethodNotAllowedException, raw.check_status, Request(405), "/"
        )

        self.assertRaises(
            TooBigFileException, raw.check_status, Request(413), "/"
        )

        self.assertRaises(
            ServerErrorException, raw.check_status, RequestText(500), "/"
        )

        self.assertRaises(
            ServerErrorException, raw.check_status, RequestText(502), "/"
        )

        self.assertRaises(
            ServerErrorException, raw.check_status, RequestJSON(500), "/"
        )

        self.assertRaises(
            ServerErrorException, raw.check_status, RequestJSON(502), "/"
        )

    def test_init_host(self):
        gazu.set_host("newhost")
        self.assertEqual(gazu.get_host(), "newhost")
        gazu.set_host("http://gazu-server/")
        self.assertEqual(gazu.get_host(), gazu.raw.default_client.host)

    def test_init_log_in(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "auth/login",
                text={"login": True, "tokens": {"access_token": "tokentest"}},
            )
            gazu.log_in("frank", "test")
        self.assertEqual(
            raw.default_client.tokens["tokens"]["access_token"], "tokentest"
        )

    def test_init_log_out(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "auth/logout", text={}, status_code=400)
            gazu.log_out()
            self.assertEqual(raw.default_client.tokens, {})

    def test_init_send_email_otp(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "auth/email-otp?email=test@test.com",
                text={"success": True},
            )
            success = gazu.send_email_otp("test@test.com")
            self.assertEqual(success, {"success": True})

    def test_init_refresh_token(self):
        with requests_mock.mock() as mock:
            raw.default_client.tokens["refresh_token"] = "refresh_token1"
            mock_route(
                mock,
                "GET",
                "auth/refresh-token",
                text={"access_token": "tokentest1"},
            )
            gazu.refresh_access_token()
        self.assertEqual(
            raw.default_client.tokens["access_token"], "tokentest1"
        )

    def test_init_log_in_fail(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "auth/login",
                text={"login": False},
            )
            self.assertRaises(
                AuthFailedException, gazu.log_in, "frank", "test"
            )
            self.assertRaises(AuthFailedException, gazu.log_in, "", "")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "auth/login",
                text={},
                status_code=401,
            )
            with self.assertRaises(AuthFailedException):
                gazu.log_in("", "")

    def test_get_current_user(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", "auth/authenticated", text={"user": {"id": "123"}}
            )
            current_user = raw.get_current_user()
            self.assertEqual(current_user["id"], "123")

    def test_get_file_data_from_url(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "test_url",
                text="test",
            )
            self.assertEqual(raw.get_file_data_from_url("test_url"), b"test")
