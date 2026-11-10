import asyncio
import os
import tempfile
import unittest
from unittest.mock import patch

import pytest

pytest.importorskip("aiohttp")  # async extra is optional; skip if absent

import gazu.aio
from aiohttp import web
from aiohttp.test_utils import TestServer
from gazu.exception import (
    AuthFailedException,
    RouteNotFoundException,
    NotAllowedException,
    ParameterException,
    MethodNotAllowedException,
    TooBigFileException,
    ValidationException,
    NotAuthenticatedException,
    ServerErrorException,
)


def run(coro):
    return asyncio.run(coro)


def serve(routes, scenario, **client_args):
    """
    Run scenario(client) against a real server with the given
    (method, path, handler) routes.
    """

    async def main():
        app = web.Application()
        for method, path, handler in routes:
            app.router.add_route(method, path, handler)
        async with TestServer(app) as server:
            client = gazu.aio.AsyncKitsuClient(
                str(server.make_url("/")), **client_args
            )
            try:
                return await scenario(client)
            finally:
                await client.session.close()

    return run(main())


def answer(payload, status=200):
    async def handler(request):
        return web.json_response(payload, status=status)

    return handler


class FakeResponse:
    """Minimal stand-in for an aiohttp response in check_status tests."""

    def __init__(self, status, body=None, raise_json=False):
        self.status = status
        self._body = body if body is not None else {}
        self._raise_json = raise_json

    async def json(self):
        if self._raise_json:
            raise ValueError("not json")
        return self._body

    async def text(self):
        return str(self._body)


class AioCheckStatusTestCase(unittest.TestCase):
    def test_error_status_raises_the_matching_exception(self):
        for response, exception in (
            (FakeResponse(404), RouteNotFoundException),
            (FakeResponse(403), NotAllowedException),
            (FakeResponse(400, {"message": "bad"}), ParameterException),
            # A non-JSON body must not surface as a raw decode error.
            (FakeResponse(400, raise_json=True), ParameterException),
            (FakeResponse(405), MethodNotAllowedException),
            (FakeResponse(413), TooBigFileException),
            (FakeResponse(422, {"message": "invalid"}), ValidationException),
            (FakeResponse(422, raise_json=True), ValidationException),
            (FakeResponse(401, {"message": "no"}), NotAuthenticatedException),
            (FakeResponse(401, raise_json=True), NotAuthenticatedException),
            (FakeResponse(500), ServerErrorException),
            (FakeResponse(502, raise_json=True), ServerErrorException),
        ):
            with self.subTest(status=response.status):
                with self.assertRaises(exception):
                    run(gazu.aio.check_status(response, "/"))

    def test_success_returns_status_and_no_retry(self):
        status, retry = run(gazu.aio.check_status(FakeResponse(200), "/"))
        self.assertEqual(status, 200)
        self.assertFalse(retry)

    def test_callback_can_authorize_a_retry(self):
        client = gazu.aio.AsyncKitsuClient(
            "http://localhost/api",
            callback_not_authenticated=lambda client, path: True,
        )
        status, retry = run(
            gazu.aio.check_status(FakeResponse(401), "/", client=client)
        )
        self.assertEqual((status, retry), (401, True))


class AioClientTestCase(unittest.TestCase):
    def test_refresh_access_token_without_token_raises(self):
        # Refreshing must not build a "Bearer None" header.
        client = gazu.aio.AsyncKitsuClient("http://localhost/api")
        with self.assertRaises(NotAuthenticatedException):
            run(client.refresh_access_token())

    def test_make_auth_header_sends_the_token_only_when_there_is_one(self):
        client = gazu.aio.AsyncKitsuClient("http://localhost/api")
        self.assertNotIn("Authorization", client.make_auth_header())
        client.access_token = "abc"
        self.assertEqual(
            client.make_auth_header()["Authorization"], "Bearer abc"
        )

    def test_get_retries_with_a_refreshed_token(self):
        seen = []

        async def data(request):
            seen.append(request.headers["Authorization"])
            if len(seen) == 1:
                return web.json_response(
                    {"message": "Signature has expired"}, status=401
                )
            return web.json_response({"ok": True})

        routes = [
            ("GET", "/data", data),
            ("GET", "/auth/refresh-token", answer({"access_token": "new"})),
        ]
        result = serve(
            routes,
            lambda client: gazu.aio.get("data", client=client),
            access_token="old",
            refresh_token="refresh",
        )
        self.assertEqual(result, {"ok": True})
        self.assertEqual(seen, ["Bearer old", "Bearer new"])

    def test_client_logs_out_at_the_end_of_the_block(self):
        calls = []

        async def logout(request):
            calls.append(request.headers["Authorization"])
            return web.json_response({})

        async def scenario(client):
            async with client:
                pass
            return client.tokens

        tokens = serve(
            [("GET", "/auth/logout", logout)], scenario, access_token="abc"
        )
        self.assertEqual(calls, ["Bearer abc"])
        self.assertIsNone(tokens["access_token"])


class AioRequestsTestCase(unittest.TestCase):
    def test_verbs_send_their_data_and_return_the_response(self):
        async def echo(request):
            return web.json_response(
                {
                    "method": request.method,
                    "query": dict(request.query),
                    "body": (
                        await request.json() if request.can_read_body else None
                    ),
                }
            )

        async def deleted(request):
            return web.Response(text=request.query_string)

        routes = [
            ("GET", "/path", echo),
            ("POST", "/path", echo),
            ("PUT", "/path", echo),
            ("DELETE", "/path", deleted),
        ]

        async def scenario(client):
            return (
                await gazu.aio.get("path", params={"a": "1"}, client=client),
                await gazu.aio.post("path", {"b": 2}, client=client),
                await gazu.aio.put("path", {"c": 3}, client=client),
                await gazu.aio.delete(
                    "path", params={"force": "true"}, client=client
                ),
            )

        got, posted, updated, removed = serve(routes, scenario)
        self.assertEqual(got["query"], {"a": "1"})
        self.assertEqual(posted["body"], {"b": 2})
        self.assertEqual(updated["body"], {"c": 3})
        self.assertEqual(removed, "force=true")

    def test_get_can_return_text(self):
        async def text(request):
            return web.Response(text="a,b")

        result = serve(
            [("GET", "/csv", text)],
            lambda client: gazu.aio.get(
                "csv", json_response=False, client=client
            ),
        )
        self.assertEqual(result, "a,b")

    def test_requests_raise_after_too_many_refused_tokens(self):
        routes = [
            ("*", "/path", answer({"message": "Signature has expired"}, 401)),
            ("GET", "/auth/refresh-token", answer({"access_token": "new"})),
        ]
        for request in (
            lambda client: gazu.aio.get("path", client=client),
            lambda client: gazu.aio.post("path", {}, client=client),
            lambda client: gazu.aio.put("path", {}, client=client),
            lambda client: gazu.aio.delete("path", client=client),
        ):
            with self.assertRaises(NotAuthenticatedException):
                serve(routes, request, refresh_token="refresh")

    def test_fetch_all_reads_all_pages_with_fields(self):
        queries = []

        async def tasks(request):
            queries.append(dict(request.query))
            page = int(request.query["page"])
            return web.json_response(
                {"nb_pages": 2, "page": page, "data": [{"id": page}]}
            )

        result = serve(
            [("GET", "/data/tasks", tasks)],
            lambda client: gazu.aio.fetch_all(
                "tasks",
                client=client,
                paginated=True,
                limit=1,
                fields=["id", "name"],
            ),
        )
        self.assertEqual(result, [{"id": 1}, {"id": 2}])
        self.assertEqual(
            queries,
            [
                {"page": "1", "limit": "1", "fields": "id,name"},
                {"page": "2", "limit": "1", "fields": "id,name"},
            ],
        )

    def test_fetch_all_walks_by_cursor(self):
        rows = [{"id": number} for number in range(1, 6)]
        queries = []

        async def tasks(request):
            queries.append(dict(request.query))
            cursor = int(request.query.get("cursor_id", 0))
            limit = int(request.query["limit"])
            return web.json_response(
                [row for row in rows if row["id"] > cursor][:limit]
            )

        result = serve(
            [("GET", "/data/tasks", tasks)],
            lambda client: gazu.aio.fetch_all("tasks", client=client, limit=2),
        )
        self.assertEqual(result, rows)
        self.assertEqual(
            queries,
            [
                {"limit": "2"},
                {"limit": "2", "cursor_id": "2"},
                {"limit": "2", "cursor_id": "4"},
            ],
        )

    def test_fetch_all_without_pagination_returns_the_response(self):
        result = serve(
            [("GET", "/data/tasks", answer([{"id": 1}]))],
            lambda client: gazu.aio.fetch_all("tasks", client=client),
        )
        self.assertEqual(result, [{"id": 1}])

    def test_fetch_first_returns_the_first_entry_or_none(self):
        routes = [
            ("GET", "/data/full", answer([{"id": 1}, {"id": 2}])),
            ("GET", "/data/empty", answer([])),
        ]

        async def scenario(client):
            return (
                await gazu.aio.fetch_first("full", client=client),
                await gazu.aio.fetch_first("empty", client=client),
            )

        self.assertEqual(serve(routes, scenario), ({"id": 1}, None))

    def test_model_helpers_use_the_data_routes(self):
        async def echo(request):
            return web.json_response(await request.json())

        routes = [
            ("GET", "/data/tasks/id", answer({"id": "id"})),
            ("POST", "/data/tasks", echo),
            ("PUT", "/data/tasks/id", echo),
        ]

        async def scenario(client):
            return (
                await gazu.aio.fetch_one("tasks", "id", client=client),
                await gazu.aio.create("tasks", {"a": 1}, client=client),
                await gazu.aio.update("tasks", "id", {"b": 2}, client=client),
            )

        self.assertEqual(
            serve(routes, scenario), ({"id": "id"}, {"a": 1}, {"b": 2})
        )

    def test_check_server_status(self):
        async def scenario(client):
            return await gazu.aio.check_server_status(client)

        self.assertTrue(serve([("HEAD", "/", answer({}))], scenario))
        client = gazu.aio.AsyncKitsuClient("http://127.0.0.1:1/api")

        async def down():
            try:
                return await gazu.aio.check_server_status(client)
            finally:
                await client.session.close()

        self.assertFalse(run(down()))


class AioAuthTestCase(unittest.TestCase):
    def test_log_in_stores_the_tokens(self):
        tokens = {"login": True, "access_token": "abc"}

        async def scenario(client):
            await gazu.aio.log_in("a@b.c", "pwd", client=client)
            return client.access_token

        result = serve([("POST", "/auth/login", answer(tokens))], scenario)
        self.assertEqual(result, "abc")

    def test_log_in_raises_when_the_api_refuses(self):
        for response in (answer({"login": False}), answer({}, status=401)):
            with self.assertRaises(AuthFailedException):
                serve(
                    [("POST", "/auth/login", response)],
                    lambda client: gazu.aio.log_in(
                        "a@b.c", "pwd", client=client
                    ),
                )

    def test_log_out_removes_the_tokens(self):
        async def scenario(client):
            return await gazu.aio.log_out(client)

        tokens = serve(
            [("GET", "/auth/logout", answer({}))],
            scenario,
            access_token="abc",
        )
        self.assertIsNone(tokens["access_token"])

    def test_create_session_returns_a_logged_in_client(self):
        async def main():
            app = web.Application()
            app.router.add_post(
                "/auth/login",
                answer({"login": True, "access_token": "abc"}),
            )
            async with TestServer(app) as server:
                client = await gazu.aio.create_session(
                    str(server.make_url("/")), "a@b.c", "pwd"
                )
                await client.session.close()
                return client.access_token

        self.assertEqual(run(main()), "abc")


class AioUploadTestCase(unittest.TestCase):
    def _check_upload(self, expire_token):
        uploads = []

        async def upload(request):
            form = await request.post()
            uploads.append(
                (
                    request.headers["Authorization"],
                    form["file"].file.read(),
                    form["file-1"].file.read(),
                    form["label"],
                )
            )
            if expire_token and len(uploads) == 1:
                return web.json_response(
                    {"message": "Signature has expired"}, status=401
                )
            return web.json_response({"id": "preview"})

        async def refresh(request):
            self.assertEqual(
                request.headers["Authorization"], "Bearer refresh"
            )
            return web.json_response({"access_token": "new"})

        with tempfile.TemporaryDirectory() as directory:
            paths = [os.path.join(directory, n) for n in ("a", "b")]
            for path, content in zip(paths, (b"main", b"extra")):
                with open(path, "wb") as target:
                    target.write(content)
            result = serve(
                [
                    ("POST", "/pictures/preview-files/preview", upload),
                    ("GET", "/auth/refresh-token", refresh),
                ],
                lambda client: gazu.aio.upload(
                    "pictures/preview-files/preview",
                    paths[0],
                    extra_files=[paths[1]],
                    data={"label": "review"},
                    client=client,
                ),
                access_token="old",
                refresh_token="refresh",
            )
        self.assertEqual(result, {"id": "preview"})
        expected = [("Bearer old", b"main", b"extra", "review")]
        if expire_token:
            expected.append(("Bearer new", b"main", b"extra", "review"))
        self.assertEqual(uploads, expected)

    def test_upload_returns_successful_response(self):
        self._check_upload(expire_token=False)

    def test_upload_reopens_all_files_after_token_refresh(self):
        self._check_upload(expire_token=True)

    def test_upload_reports_progress_over_all_files(self):
        calls = []

        async def upload(request):
            await request.post()
            return web.json_response({})

        with tempfile.TemporaryDirectory() as directory:
            paths = [os.path.join(directory, n) for n in ("a", "b")]
            for path, size in zip(paths, (100000, 50000)):
                with open(path, "wb") as target:
                    target.write(b"x" * size)
            serve(
                [("POST", "/upload", upload)],
                lambda client: gazu.aio.upload(
                    "upload",
                    paths[0],
                    extra_files=[paths[1]],
                    client=client,
                    progress_callback=lambda *args: calls.append(args),
                ),
            )
        self.assertEqual(calls[-1], (150000, 150000))

    def test_upload_raises_when_the_response_has_a_message(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "a")
            with open(path, "wb") as target:
                target.write(b"a")
            with self.assertRaises(gazu.aio.UploadFailedException):
                serve(
                    [("POST", "/upload", answer({"message": "broken"}))],
                    lambda client: gazu.aio.upload(
                        "upload", path, client=client
                    ),
                )

    def test_upload_closes_main_file_when_extra_file_is_missing(self):
        opened = []
        real_open = open

        def track_open(*args, **kwargs):
            stream = real_open(*args, **kwargs)
            opened.append(stream)
            return stream

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "preview")
            with open(path, "wb") as target:
                target.write(b"preview")
            client = gazu.aio.AsyncKitsuClient("http://localhost/api")
            with patch("gazu.aio.open", side_effect=track_open, create=True):
                with self.assertRaises(FileNotFoundError):
                    run(
                        gazu.aio.upload(
                            "pictures/preview-files/preview",
                            path,
                            extra_files=[os.path.join(directory, "missing")],
                            client=client,
                        )
                    )
            self.assertEqual(len(opened), 1)
            self.assertTrue(opened[0].closed)


class AioDownloadTestCase(unittest.TestCase):
    def test_download_writes_the_file_and_reports_progress(self):
        calls = []

        async def movie(request):
            self.assertEqual(request.query["lowdef"], "true")
            return web.Response(body=b"content")

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "a")
            serve(
                [("GET", "/movie", movie)],
                lambda client: gazu.aio.download(
                    "movie",
                    path,
                    params={"lowdef": "true"},
                    client=client,
                    progress_callback=lambda *args: calls.append(args),
                ),
            )
            with open(path, "rb") as target:
                self.assertEqual(target.read(), b"content")
        self.assertEqual(calls[-1], (7, 7))

    def test_download_does_not_write_an_error_body(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "a")
            with self.assertRaises(RouteNotFoundException):
                serve(
                    [("GET", "/movie", answer({}, status=404))],
                    lambda client: gazu.aio.download(
                        "movie", path, client=client
                    ),
                )
            self.assertFalse(os.path.exists(path))

    def test_download_retries_with_a_refreshed_token(self):
        seen = []

        async def movie(request):
            seen.append(request.headers["Authorization"])
            if len(seen) == 1:
                return web.json_response(
                    {"message": "Signature has expired"}, status=401
                )
            return web.Response(body=b"content")

        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "a")
            serve(
                [
                    ("GET", "/movie", movie),
                    (
                        "GET",
                        "/auth/refresh-token",
                        answer({"access_token": "new"}),
                    ),
                ],
                lambda client: gazu.aio.download("movie", path, client=client),
                access_token="old",
                refresh_token="refresh",
            )
        self.assertEqual(seen, ["Bearer old", "Bearer new"])


if __name__ == "__main__":
    unittest.main()
