import cgi
import datetime
import json
import io
import sys

import unittest
import requests_mock
import gazu
from gazu.__version__ import __version__

from gazu import client as raw, set_event_host
from gazu.exception import (
    RouteNotFoundException,
    AuthFailedException,
    MethodNotAllowedException,
    NotAuthenticatedException,
    NotAllowedException,
    TooBigFileException,
    ServerErrorException,
)


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


class BaseFuncTestCase(ClientTestCase):
    def test_host_is_up(self):
        with requests_mock.mock() as mock:
            mock.head(raw.get_host())
            self.assertTrue(raw.host_is_up())
        self.assertFalse(raw.host_is_up())

    def test_host_is_valid(self):
        self.assertFalse(raw.host_is_valid())
        with requests_mock.mock() as mock:
            mock.head(raw.get_host())
            mock.post(
                raw.get_full_url("auth/login"), text=json.dumps({}), status_code=400
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
        pass

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
            mock.get(
                raw.get_full_url("data/persons"),
                text=json.dumps({"first_name": "John"}),
            )
            self.assertEqual(raw.get("data/persons"), {"first_name": "John"})

    def test_get_two_clients(self):
        with requests_mock.mock() as mock:
            second_client = gazu.raw.create_client("http://second.host/api")
            mock.get(
                raw.get_full_url("data/persons"),
                text=json.dumps({"first_name": "John"}),
            )
            self.assertEqual(raw.get("data/persons"), {"first_name": "John"})
            self.assertRaises(
                requests_mock.exceptions.NoMockAddress,
                raw.get,
                "data/persons",
                client=second_client,
            )
            mock.get(
                raw.get_full_url("data/persons", client=second_client),
                text=json.dumps({"first_name": "John2"}),
            )
            self.assertEqual(
                raw.get("data/persons", client=second_client),
                {"first_name": "John2"},
            )

    def test_post(self):
        with requests_mock.mock() as mock:
            mock.post(
                raw.get_full_url("data/persons"),
                text=json.dumps({"id": "person-01", "first_name": "John"}),
            )
            self.assertEqual(
                raw.post("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_post_with_a_date_field(self):
        now = datetime.datetime.now()
        with requests_mock.mock() as mock:
            mock.post(
                raw.get_full_url("data/persons"),
                text=json.dumps({"id": "person-01", "first_name": "John"}),
            )
            self.assertEqual(
                raw.post("data/persons", {"birth_date": now}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_put(self):
        with requests_mock.mock() as mock:
            mock.put(
                raw.get_full_url("data/persons"),
                text=json.dumps({"id": "person-01", "first_name": "John"}),
            )
            self.assertEqual(
                raw.put("data/persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_update(self):
        with requests_mock.mock() as mock:
            mock.put(
                raw.get_full_url("data/persons/person-1"),
                text=json.dumps(
                    {"id": "person-1", "first_name": "John", "last_name": "Doe"}
                ),
            )
            data = {"last_name": "Doe"}
            self.assertEqual(
                raw.update("persons", "person-1", data),
                {"id": "person-1", "first_name": "John", "last_name": "Doe"},
            )

    def test_delete(self):
        with requests_mock.mock() as mock:
            mock.delete(raw.get_full_url("data/persons/person-01"), text="")
            self.assertEqual(raw.delete("data/persons/person-01"), "")

    def test_fetch_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("data/persons"),
                text=json.dumps([{"first_name": "John"}]),
            )
            self.assertEqual(raw.fetch_all("persons"), [{"first_name": "John"}])

    def test_fetch_first(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("data/persons"),
                text=json.dumps([{"first_name": "John"}, {"first_name": "Jane"}]),
            )
            self.assertEqual(raw.fetch_first("persons"), {"first_name": "John"})

            mock.get(raw.get_full_url("data/persons"), text=json.dumps([]))
            self.assertIsNone(raw.fetch_first("persons"))

    def test_query_string(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("data/projects?name=Test"),
                text=json.dumps([{"name": "Project"}]),
            )
            self.assertEqual(
                raw.fetch_first("projects", {"name": "Test"}),
                {"name": "Project"},
            )

            mock.get(raw.get_full_url("data/persons"), text=json.dumps([]))
            self.assertIsNone(raw.fetch_first("persons"))

    def test_fetch_one(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("data/persons/person-01"),
                text=json.dumps({"id": "person-01", "first_name": "John"}),
            )
            self.assertEqual(
                raw.fetch_one("persons", "person-01"),
                {"id": "person-01", "first_name": "John"},
            )

    def test_create(self):
        with requests_mock.mock() as mock:
            mock.post(
                raw.get_full_url("data/persons"),
                text=json.dumps({"id": "person-01", "first_name": "John"}),
            )
            self.assertEqual(
                raw.create("persons", {"first_name": "John"}),
                {"id": "person-01", "first_name": "John"},
            )

    def test_version(self):
        with requests_mock.mock() as mock:
            mock.get(raw.get_host() + "/", text=json.dumps({"version": "0.2.0"}))
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
                mock.post(
                    raw.get_full_url("data/new-file"),
                    text=json.dumps({"id": "person-01", "first_name": "John"}),
                )

                def verify_file_callback(request):
                    body_file = io.BytesIO(request.body)
                    _, pdict = cgi.parse_header(request.headers["Content-Type"])
                    if sys.version_info[0] == 3:
                        pdict["boundary"] = bytes(pdict["boundary"], "UTF-8")
                    else:
                        pdict["boundary"] = bytes(pdict["boundary"])
                    parsed = cgi.parse_multipart(fp=body_file, pdict=pdict)
                    assert "file" in parsed
                    assert "test" in parsed and parsed["test"]
                    assert test_file.read() == parsed["file"][0]
                    return None

                mock.post("data/new-file", json={})
                mock.add_matcher(verify_file_callback)
                raw.upload(
                    "data/new-file", "./tests/fixtures/v1.png", data={"test": True}
                )
            with requests_mock.Mocker() as mock:
                mock.post(
                    raw.get_full_url("data/new-file"),
                    text=json.dumps({"message": "Error"}),
                )
                mock.post("data/new-file", json={})
                with self.assertRaises(gazu.client.UploadFailedException):
                    raw.upload(
                        "data/new-file", "./tests/fixtures/v1.png", data={"test": True}
                    )

    def test_upload_multiple_files(self):
        with open("./tests/fixtures/v1.png", "rb") as test_file:
            with requests_mock.Mocker() as mock:
                mock.post(
                    raw.get_full_url("data/new-file"),
                    text=json.dumps({"id": "person-01", "first_name": "John"}),
                )

                def verify_file_callback(request):
                    body_file = io.BytesIO(request.body)
                    _, pdict = cgi.parse_header(request.headers["Content-Type"])
                    if sys.version_info[0] == 3:
                        pdict["boundary"] = bytes(pdict["boundary"], "UTF-8")
                    else:
                        pdict["boundary"] = bytes(pdict["boundary"])
                    parsed = cgi.parse_multipart(fp=body_file, pdict=pdict)
                    assert "file" in parsed
                    assert "test" in parsed and parsed["test"]
                    file_data = test_file.read()
                    assert file_data == parsed["file"][0]
                    assert file_data == parsed["file-2"][0]
                    return None

                mock.post("data/new-file", json={})
                mock.add_matcher(verify_file_callback)
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
        self.assertRaises(NotAllowedException, raw.check_status, Request(403), "/")
        self.assertRaises(RouteNotFoundException, raw.check_status, Request(404), "/")
        self.assertRaises(
            MethodNotAllowedException, raw.check_status, Request(405), "/"
        )

        self.assertRaises(TooBigFileException, raw.check_status, Request(413), "/")

        self.assertRaises(ServerErrorException, raw.check_status, RequestText(500), "/")

        self.assertRaises(ServerErrorException, raw.check_status, RequestText(502), "/")

        self.assertRaises(ServerErrorException, raw.check_status, RequestJSON(500), "/")

        self.assertRaises(ServerErrorException, raw.check_status, RequestJSON(502), "/")

    def test_init_host(self):
        gazu.set_host("newhost")
        self.assertEqual(gazu.get_host(), "newhost")
        gazu.set_host("http://gazu-server/")
        self.assertEqual(gazu.get_host(), gazu.raw.default_client.host)

    def test_init_log_in(self):
        with requests_mock.mock() as mock:
            mock.post(
                raw.get_full_url("auth/login"),
                text=json.dumps(
                    {"login": True, "tokens": {"access_token": "tokentest"}}
                ),
            )
            gazu.log_in("frank", "test")
        self.assertEqual(
            raw.default_client.tokens["tokens"]["access_token"], "tokentest"
        )

    def test_init_log_out(self):
        with requests_mock.mock() as mock:
            mock.head(raw.get_host())
            mock.get(
                raw.get_full_url("auth/logout"), text=json.dumps({}), status_code=400
            )
            gazu.log_out()
            self.assertEqual(raw.default_client.tokens, {})

    def test_init_log_in_fail(self):
        with requests_mock.mock() as mock:
            mock.post(
                raw.get_full_url("auth/login"),
                text=json.dumps({"login": False}),
            )
            self.assertRaises(AuthFailedException, gazu.log_in, "frank", "test")
            self.assertRaises(AuthFailedException, gazu.log_in, "", "")
        with requests_mock.mock() as mock:
            mock.head(raw.get_host())
            mock.post(
                raw.get_full_url("auth/login"), text=json.dumps({}), status_code=400
            )
            with self.assertRaises(AuthFailedException):
                gazu.log_in("", "")

    def test_get_current_user(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("auth/authenticated"),
                text=json.dumps({"user": {"id": "123"}}),
            )
            current_user = raw.get_current_user()
            self.assertEqual(current_user["id"], "123")

    def test_get_file_data_from_url(self):
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url("test_url"),
                text="test",
            )
            self.assertEqual(raw.get_file_data_from_url("test_url"), b"test")
