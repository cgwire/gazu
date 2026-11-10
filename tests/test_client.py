import datetime
import json
import os
import tempfile
import time
import unittest
from unittest.mock import patch

import requests
import requests_mock

import gazu
from gazu import client as raw
from gazu.__version__ import __version__
from gazu.exception import (
    MethodNotAllowedException,
    NotAllowedException,
    NotAuthenticatedException,
    ParameterException,
    PreviewFileProcessingException,
    RouteNotFoundException,
    ServerErrorException,
    TooBigFileException,
    UploadFailedException,
    ValidationException,
)

from utils import add_verify_file_callback, fakeid, mock_route

EXPIRED = {"status_code": 401, "json": {"message": "Signature has expired"}}
FIXTURE = "./tests/fixtures/v1.png"


class FakeResponse:
    """Expose only what check_status and the message functions read."""

    text = "Error on server"

    def __init__(self, status_code=200, body=None):
        self.status_code = status_code
        self.body = body

    def json(self):
        if self.body is None:
            raise ValueError("no json")
        return self.body


def refreshing_client(**kwargs):
    client = raw.create_client(
        "http://second.host/api", use_refresh_token=True, **kwargs
    )
    client.tokens = {"access_token": "old", "refresh_token": "refresh"}
    return client


class HostTestCase(unittest.TestCase):
    def test_host_is_up(self):
        for kwargs, expected in (
            ({}, True),
            ({"status_code": 500}, False),
            ({"exc": requests.exceptions.ConnectTimeout}, False),
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "HEAD", raw.get_host(), **kwargs)
                self.assertEqual(raw.host_is_up(), expected)

    def test_host_is_valid(self):
        for status_code, expected in (
            (200, True),
            (400, True),
            (401, True),
            (500, False),
        ):
            with self.subTest(status_code), requests_mock.mock() as mock:
                mock_route(mock, "HEAD", raw.get_host())
                mock_route(
                    mock,
                    "POST",
                    "auth/login",
                    text={},
                    status_code=status_code,
                )
                self.assertEqual(raw.host_is_valid(), expected)

    def test_host_is_not_valid_when_it_is_down(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "HEAD", raw.get_host(), status_code=500)
            self.assertFalse(raw.host_is_valid())

    def test_set_host(self):
        self.assertEqual(raw.set_host("http://a/api"), "http://a/api")
        self.assertEqual(raw.get_host(), "http://a/api")

    def test_event_host_falls_back_to_the_host(self):
        raw.set_host("http://a/api")
        raw.default_client.event_host = None
        self.assertEqual(raw.get_event_host(), "http://a/api")
        raw.set_event_host("http://events")
        self.assertEqual(raw.get_event_host(), "http://events")

    def test_get_api_url_from_host_removes_the_suffix(self):
        for host, expected in (
            ("http://a/api", "http://a"),
            ("http://a", "http://a"),
        ):
            raw.set_host(host)
            self.assertEqual(raw.get_api_url_from_host(), expected)

    def test_url_path_join_removes_extra_slashes(self):
        self.assertEqual(raw.url_path_join("a/", "/b/", "c"), "a/b/c")

    def test_get_full_url(self):
        raw.set_host("http://a/api")
        self.assertEqual(raw.get_full_url("/data/"), "http://a/api/data")

    def test_build_path_with_params(self):
        for path, params, expected in (
            ("a", None, "a"),
            ("a", {}, "a"),
            ("a", {"b": 1}, "a?b=1"),
            ("a?b=1", {"c": 2}, "a?b=1&c=2"),
            # Zou reads a list as a repeated parameter.
            ("a", {"b": ["x", "y"]}, "a?b=x&b=y"),
        ):
            with self.subTest(params=params):
                self.assertEqual(
                    raw.build_path_with_params(path, params), expected
                )

    def test_make_auth_header_sends_the_token_only_when_there_is_one(self):
        agent = f"CGWire Gazu {__version__}"
        raw.set_tokens({})
        self.assertEqual(raw.make_auth_header(), {"User-Agent": agent})
        self.assertEqual(
            raw.set_tokens({"access_token": "abc"}), {"access_token": "abc"}
        )
        self.assertEqual(
            raw.make_auth_header(),
            {"Authorization": "Bearer abc", "User-Agent": agent},
        )

    def test_clients_are_independent(self):
        second = raw.create_client("http://second.host/api", access_token="b")
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/new-file", text={"from": "default"})
            mock_route(
                mock,
                "GET",
                raw.get_full_url("data/new-file", client=second),
                text={"from": "second"},
            )
            self.assertEqual(raw.get("data/new-file"), {"from": "default"})
            self.assertEqual(
                raw.get("data/new-file", client=second), {"from": "second"}
            )
            self.assertEqual(
                mock.last_request.headers["Authorization"], "Bearer b"
            )

    def test_client_logs_out_at_the_end_of_the_block(self):
        second = raw.create_client("http://second.host/api", access_token="b")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/logout", client=second),
                text={},
            )
            with second as client:
                self.assertIs(client, second)
            self.assertEqual(mock.call_count, 1)
        self.assertIsNone(second.access_token)

    def test_client_end_of_block_ignores_a_failed_logout(self):
        second = raw.create_client("http://second.host/api", access_token="b")
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/logout", client=second),
                exc=requests.exceptions.ConnectTimeout,
            )
            with second:
                pass
        self.assertIsNone(second.access_token)


class RequestsTestCase(unittest.TestCase):
    def test_get(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "data/new-file", text={"b": 1})
            self.assertEqual(
                raw.get("data/new-file", params={"c": 2}), {"b": 1}
            )
            self.assertEqual(mock.last_request.qs, {"c": ["2"]})
            self.assertEqual(
                raw.get("data/new-file", json_response=False), '{"b": 1}'
            )

    def test_post_encodes_dates_in_iso_format(self):
        date = datetime.datetime(2026, 1, 2, 3, 4, 5)
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/new-file", text={"id": "b"})
            self.assertEqual(
                raw.post("data/new-file", {"date": date}), {"id": "b"}
            )
            self.assertEqual(
                mock.last_request.json(), {"date": "2026-01-02T03:04:05"}
            )
            self.assertEqual(
                mock.last_request.headers["Content-Type"], "application/json"
            )

    def test_post_raises_when_the_response_is_not_json(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "data/new-file", text="<html>")
            with self.assertRaises(json.JSONDecodeError):
                raw.post("data/new-file", {})

    def test_put(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "PUT", "data/new-file", text={"id": "b"})
            self.assertEqual(raw.put("data/new-file", {"c": 1}), {"id": "b"})
            self.assertEqual(mock.last_request.json(), {"c": 1})

    def test_delete(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "DELETE", "data/new-file", text="")
            self.assertEqual(raw.delete("data/new-file", {"force": True}), "")
            self.assertEqual(mock.last_request.qs, {"force": ["true"]})

    def test_request_body_with_a_secret_is_not_logged(self):
        for data, logged in (
            ({"name": "a"}, True),
            ({"password": "a"}, False),
            ({"refresh_token": "a"}, False),
            (1, True),
        ):
            with self.subTest(data=data):
                with patch.object(raw.logger, "debug") as debug:
                    raw._log_request_body(data)
                self.assertEqual(debug.called, logged)

    def test_requests_retry_with_a_refreshed_token(self):
        client = refreshing_client()
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/refresh-token", client=client),
                text={"access_token": "new"},
            )
            mock.get(
                raw.get_full_url("data/new-file", client=client),
                [EXPIRED, {"json": {"b": 1}}],
            )
            self.assertEqual(raw.get("data/new-file", client=client), {"b": 1})
            self.assertEqual(
                mock.last_request.headers["Authorization"], "Bearer new"
            )
        # The server gave no new refresh token: the client keeps its own.
        self.assertEqual(client.refresh_token, "refresh")

    def test_requests_stop_after_too_many_refused_tokens(self):
        client = refreshing_client()
        for name, call in (
            ("GET", lambda: raw.get("data/new-file", client=client)),
            ("POST", lambda: raw.post("data/new-file", {}, client=client)),
            ("PUT", lambda: raw.put("data/new-file", {}, client=client)),
            ("DELETE", lambda: raw.delete("data/new-file", client=client)),
            (
                "GET",
                lambda: raw.get_file_data_from_url(
                    "data/new-file", client=client
                ),
            ),
            (
                "POST",
                lambda: raw.upload("data/new-file", FIXTURE, client=client),
            ),
            (
                "GET",
                lambda: raw.download("data/new-file", None, client=client),
            ),
        ):
            with self.subTest(name), requests_mock.mock() as mock:
                mock_route(
                    mock,
                    "GET",
                    raw.get_full_url("auth/refresh-token", client=client),
                    text={"access_token": "new"},
                )
                mock_route(
                    mock,
                    name,
                    raw.get_full_url("data/new-file", client=client),
                    **EXPIRED,
                )
                with self.assertRaises(NotAuthenticatedException):
                    call()

    def test_refresh_without_refresh_token_raises(self):
        client = raw.create_client("http://second.host/api")
        with self.assertRaises(NotAuthenticatedException):
            client.refresh_access_token()

    def test_callback_can_authorize_a_retry(self):
        client = raw.create_client(
            "http://second.host/api",
            callback_not_authenticated=lambda client, path: True,
        )
        status_code, retry = raw.check_status(
            FakeResponse(401, {}), "/", client=client
        )
        self.assertEqual((status_code, retry), (401, True))

    def test_fetch_all_sends_the_fields(self):
        for fields in (["a", "b"], "a,b"):
            with self.subTest(fields=fields), requests_mock.mock() as mock:
                mock_route(mock, "GET", "data/persons", text=[{"a": 1}])
                self.assertEqual(
                    raw.fetch_all("persons", fields=fields), [{"a": 1}]
                )
                self.assertEqual(mock.last_request.qs, {"fields": ["a,b"]})

    def test_fetch_all_reads_all_pages(self):
        def page(request, context):
            number = int(request.qs["page"][0])
            return json.dumps(
                {"nb_pages": 3, "page": number, "data": [{"id": number}]}
            )

        with requests_mock.mock() as mock:
            mock.get(raw.get_full_url("data/tasks"), text=page)
            self.assertEqual(
                raw.fetch_all("tasks", paginated=True, limit=1),
                [{"id": 1}, {"id": 2}, {"id": 3}],
            )
            self.assertEqual(mock.call_count, 3)
            self.assertEqual(mock.last_request.qs["limit"], ["1"])

    def test_fetch_all_walks_by_cursor(self):
        rows = [{"id": number} for number in range(1, 6)]

        def page(request, context):
            cursor = int(request.qs.get("cursor_id", ["0"])[0])
            limit = int(request.qs["limit"][0])
            return json.dumps(
                [row for row in rows if row["id"] > cursor][:limit]
            )

        params = {"project_id": "a"}
        for limit, call_count in ((2, 3), (5, 2), (10, 1)):
            with self.subTest(limit=limit), requests_mock.mock() as mock:
                mock.get(raw.get_full_url("data/tasks"), text=page)
                self.assertEqual(
                    raw.fetch_all(
                        "tasks", params, by_cursor=True, limit=limit
                    ),
                    rows,
                )
                self.assertEqual(mock.call_count, call_count)
                self.assertEqual(mock.last_request.qs["project_id"], ["a"])
        self.assertEqual(params, {"project_id": "a"})

    def test_fetch_all_by_cursor_reads_a_route_without_cursor_once(self):
        # An old API answers the whole list whatever the parameters, even
        # when it is as long as the limit.
        for nb_rows, call_count in ((1, 1), (2, 2), (3, 1)):
            rows = [{"id": number} for number in range(nb_rows)]
            with self.subTest(nb_rows=nb_rows), requests_mock.mock() as mock:
                mock_route(mock, "GET", "data/tasks", text=rows)
                self.assertEqual(
                    raw.fetch_all("tasks", by_cursor=True, limit=2), rows
                )
                self.assertEqual(mock.call_count, call_count)

    def test_fetch_first(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "GET", "data/new-file", text=[{"id": 1}, {"id": 2}]
            )
            self.assertEqual(
                raw.fetch_first("new-file", {"b": "c"}), {"id": 1}
            )
            self.assertEqual(mock.last_request.qs, {"b": ["c"]})
            mock_route(mock, "GET", "data/new-file", text=[])
            self.assertIsNone(raw.fetch_first("new-file"))

    def test_model_helpers_use_the_data_routes(self):
        for call, method, path, body in (
            (
                lambda: raw.fetch_one("persons", "b"),
                "GET",
                "data/persons/b",
                None,
            ),
            (
                lambda: raw.create("persons", {"c": 1}),
                "POST",
                "data/persons",
                {"c": 1},
            ),
            (
                lambda: raw.update("persons", "b", {"c": 1}),
                "PUT",
                "data/persons/b",
                {"c": 1},
            ),
            (
                lambda: raw.import_data("entities", {"c": 1}),
                "POST",
                "import/kitsu/entities",
                {"c": 1},
            ),
        ):
            with self.subTest(path), requests_mock.mock() as mock:
                mock_route(mock, method, path, text={"id": "result"})
                self.assertEqual(call(), {"id": "result"})
                if body is not None:
                    self.assertEqual(mock.last_request.json(), body)

    def test_get_api_version_and_current_user(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "/", text={"version": "0.2.0"})
            mock_route(
                mock, "GET", "auth/authenticated", text={"user": {"id": "a"}}
            )
            self.assertEqual(raw.get_api_version(), "0.2.0")
            self.assertEqual(raw.get_current_user(), {"id": "a"})

    def test_get_file_data_from_url(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "test_url", text="relative")
            mock_route(mock, "GET", "http://other/a", text="full")
            self.assertEqual(
                raw.get_file_data_from_url("test_url"), b"relative"
            )
            self.assertEqual(
                raw.get_file_data_from_url("http://other/a", full=True),
                b"full",
            )


class StatusTestCase(unittest.TestCase):
    def test_error_status_raises_the_matching_exception(self):
        for status_code, body, exception in (
            (400, {"message": "bad"}, ParameterException),
            (401, None, NotAuthenticatedException),
            (403, None, NotAllowedException),
            (404, None, RouteNotFoundException),
            (405, None, MethodNotAllowedException),
            (413, None, TooBigFileException),
            (422, {"message": "bad"}, ValidationException),
            (422, None, ValidationException),
            (500, None, ServerErrorException),
            (502, None, ServerErrorException),
            (500, {"stacktrace": "s", "message": "m"}, ServerErrorException),
            (
                422,
                {"message": "Signature has expired"},
                NotAuthenticatedException,
            ),
        ):
            with self.subTest(status_code=status_code, body=body):
                with self.assertRaises(exception):
                    raw.check_status(FakeResponse(status_code, body), "/")

    def test_success_returns_the_status_and_no_retry(self):
        self.assertEqual(
            raw.check_status(FakeResponse(200), "/"), (200, False)
        )

    def test_422_with_an_expired_signature_refreshes_the_token(self):
        client = refreshing_client()
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/refresh-token", client=client),
                text={"access_token": "new", "refresh_token": "new-refresh"},
            )
            result = raw.check_status(
                FakeResponse(422, {"message": "Signature has expired"}),
                "/",
                client=client,
            )
        self.assertEqual(result, (422, True))
        self.assertEqual(client.access_token, "new")
        self.assertEqual(client.refresh_token, "new-refresh")

    def test_get_message_from_response(self):
        for body, expected in (
            (None, "No additional information"),
            ([], "No additional information"),
            ({"error": "Broken"}, "Broken"),
            # Zou sends a boolean "error" flag next to the real message.
            ({"error": True, "message": "Bad"}, "Bad"),
            (
                {
                    "message": "Bad",
                    "data": {"errors": [{"field": "a", "message": "b"}]},
                },
                "Bad (a: b)",
            ),
        ):
            with self.subTest(body=body):
                self.assertEqual(
                    raw.get_message_from_response(FakeResponse(body=body)),
                    expected,
                )


class UploadTestCase(unittest.TestCase):
    def test_upload_sends_the_files_and_the_data(self):
        with open(FIXTURE, "rb") as test_file:
            content = test_file.read()
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", "data/new-file", text={"id": "b"})
            add_verify_file_callback(
                mock, {"file": content, "file-1": content, "test": "True"}
            )
            self.assertEqual(
                raw.upload(
                    "data/new-file",
                    FIXTURE,
                    data={"test": True},
                    extra_files=[FIXTURE],
                ),
                {"id": "b"},
            )

    def test_upload_raises_when_the_response_has_a_message(self):
        for field in ("message", "error"):
            with self.subTest(field), requests_mock.Mocker() as mock:
                mock_route(
                    mock, "POST", "data/new-file", text={field: "Broken"}
                )
                with self.assertRaises(UploadFailedException) as context:
                    raw.upload("data/new-file", FIXTURE)
                self.assertEqual(str(context.exception), "Broken")

    def test_upload_raises_when_the_response_is_not_json(self):
        with requests_mock.Mocker() as mock:
            mock_route(mock, "POST", "data/new-file", text="<html>")
            with self.assertRaises(json.JSONDecodeError):
                raw.upload("data/new-file", FIXTURE)

    def test_upload_sends_the_files_again_after_a_token_refresh(self):
        client = refreshing_client()
        bodies = []

        def answer(request, context):
            bodies.append(request.body)
            if len(bodies) == 1:
                context.status_code = 401
                return json.dumps({"message": "Signature has expired"})
            return "{}"

        with requests_mock.Mocker() as mock:
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/refresh-token", client=client),
                text={"access_token": "new"},
            )
            mock.post(
                raw.get_full_url("data/new-file", client=client), text=answer
            )
            raw.upload("data/new-file", FIXTURE, client=client)
        with open(FIXTURE, "rb") as test_file:
            content = test_file.read()
        self.assertEqual(len(bodies), 2)
        self.assertIn(content, bodies[1])

    def test_progress_ignores_the_parts_that_are_not_files(self):
        # A JSON tuple, as batch comments make, has no file descriptor.
        progress = []
        with open(FIXTURE, "rb") as test_file:
            size = os.fstat(test_file.fileno()).st_size
            files = {
                "file": test_file,
                "comments": (None, "[]", "application/json"),
            }
            with requests_mock.Mocker() as mock:
                mock_route(mock, "POST", "data/new-file", text={})
                raw.upload(
                    "data/new-file",
                    files=files,
                    progress_callback=lambda *args: progress.append(args),
                )
        self.assertEqual(progress[-1], (size, size))

    def test_open_files_are_closed_when_an_extra_file_is_missing(self):
        real_open = open
        opened = []

        def track_open(*args, **kwargs):
            stream = real_open(*args, **kwargs)
            opened.append(stream)
            return stream

        with patch("gazu.client.open", side_effect=track_open, create=True):
            with self.assertRaises(FileNotFoundError):
                raw.upload("data/new-file", FIXTURE, extra_files=["./missing"])
        self.assertTrue(opened[0].closed)


class DownloadTestCase(unittest.TestCase):
    path = f"pictures/thumbnails/preview-files/{fakeid('preview-1')}.png"
    processing = {
        "status_code": 202,
        "json": {"status": "processing"},
        "headers": {"Retry-After": "0"},
    }

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.target = os.path.join(directory.name, "out.png")

    def read_target(self):
        with open(self.target, "rb") as downloaded:
            return downloaded.read()

    def test_download_writes_the_file_and_asks_for_json(self):
        # The JSON answer lets the server say that the file is not ready.
        with requests_mock.mock() as mock:
            mock.get(raw.get_full_url(self.path), content=b"PNG")
            raw.download(self.path, self.target, params={"a": "b"})
            self.assertEqual(
                mock.last_request.headers["Accept"],
                raw.DOWNLOAD_ACCEPT_HEADER,
            )
            self.assertEqual(mock.last_request.qs, {"a": ["b"]})
        self.assertEqual(self.read_target(), b"PNG")

    def test_download_reports_progress(self):
        calls = []
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url(self.path),
                content=b"PNG",
                headers={"content-length": "3"},
            )
            raw.download(
                self.path,
                self.target,
                progress_callback=lambda *args: calls.append(args),
            )
        self.assertEqual(calls, [(3, 3)])

    def test_download_retries_while_the_preview_is_processing(self):
        for target in (self.target, None):
            with self.subTest(target=target), requests_mock.mock() as mock:
                mock.get(
                    raw.get_full_url(self.path),
                    [self.processing, {"content": b"PNG"}],
                )
                response = raw.download(self.path, target)
                self.assertEqual(mock.call_count, 2)
                if target is None:
                    self.assertEqual(response.content, b"PNG")
                else:
                    self.assertEqual(self.read_target(), b"PNG")

    def test_download_gives_up_after_the_processing_timeout(self):
        with requests_mock.mock() as mock:
            mock.get(raw.get_full_url(self.path), **self.processing)
            with self.assertRaises(PreviewFileProcessingException):
                raw.download(self.path, self.target, processing_timeout=0)
        self.assertFalse(os.path.exists(self.target))

    def test_download_does_not_retry_or_write_a_missing_file(self):
        with requests_mock.mock() as mock:
            mock.get(raw.get_full_url(self.path), status_code=404, text="{}")
            with self.assertRaises(RouteNotFoundException):
                raw.download(self.path, self.target)
            self.assertEqual(mock.call_count, 1)
        self.assertFalse(os.path.exists(self.target))

    def test_download_retries_with_the_refreshed_token(self):
        client = refreshing_client()
        with requests_mock.mock() as mock:
            mock.get(
                raw.get_full_url(self.path, client=client),
                [EXPIRED, {"content": b"PNG"}],
            )
            mock_route(
                mock,
                "GET",
                raw.get_full_url("auth/refresh-token", client=client),
                text={"access_token": "new"},
            )
            response = raw.download(self.path, None, client=client)
            self.assertEqual(
                mock.last_request.headers["Authorization"], "Bearer new"
            )
        self.assertEqual(response.content, b"PNG")


class RetryAfterTestCase(unittest.TestCase):
    class Response:
        def __init__(self, headers):
            self.headers = headers

    def test_invalid_header_gives_the_default_delay(self):
        deadline = time.monotonic() + 100
        for headers in ({}, {"Retry-After": "soon"}):
            self.assertEqual(
                raw._retry_after(self.Response(headers), deadline),
                raw.DEFAULT_RETRY_AFTER,
            )

    def test_delay_stays_before_the_deadline(self):
        # An hour of Retry-After must not make the caller sleep that long:
        # the code checks the deadline only after the delay.
        delay = raw._retry_after(
            self.Response({"Retry-After": "3600"}), time.monotonic() + 0.05
        )
        self.assertLessEqual(delay, 0.1)

    def test_delay_is_never_negative(self):
        self.assertEqual(
            raw._retry_after(
                self.Response({"Retry-After": "5"}), time.monotonic() - 10
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
