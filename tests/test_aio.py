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
    def test_404_raises_route_not_found(self):
        with self.assertRaises(RouteNotFoundException):
            run(gazu.aio.check_status(FakeResponse(404), "/"))

    def test_403_raises_not_allowed(self):
        with self.assertRaises(NotAllowedException):
            run(gazu.aio.check_status(FakeResponse(403), "/"))

    def test_400_raises_parameter(self):
        with self.assertRaises(ParameterException):
            run(
                gazu.aio.check_status(
                    FakeResponse(400, {"message": "bad"}), "/"
                )
            )

    def test_400_non_json_body_does_not_crash(self):
        # Regression (BUG-4): a non-JSON 400 body must still raise
        # ParameterException, not a raw JSON decode error.
        with self.assertRaises(ParameterException):
            run(gazu.aio.check_status(FakeResponse(400, raise_json=True), "/"))

    def test_405_raises_method_not_allowed(self):
        with self.assertRaises(MethodNotAllowedException):
            run(gazu.aio.check_status(FakeResponse(405), "/"))

    def test_413_raises_too_big_file(self):
        with self.assertRaises(TooBigFileException):
            run(gazu.aio.check_status(FakeResponse(413), "/"))

    def test_422_raises_validation(self):
        with self.assertRaises(ValidationException):
            run(
                gazu.aio.check_status(
                    FakeResponse(422, {"message": "invalid"}), "/"
                )
            )

    def test_401_raises_not_authenticated(self):
        with self.assertRaises(NotAuthenticatedException):
            run(
                gazu.aio.check_status(
                    FakeResponse(401, {"message": "nope"}), "/"
                )
            )

    def test_401_non_json_body_does_not_crash(self):
        # Regression (BUG-4): a non-JSON 401 body must raise
        # NotAuthenticatedException, not a raw JSON decode error.
        with self.assertRaises(NotAuthenticatedException):
            run(gazu.aio.check_status(FakeResponse(401, raise_json=True), "/"))

    def test_500_raises_server_error(self):
        with self.assertRaises(ServerErrorException):
            run(gazu.aio.check_status(FakeResponse(500), "/"))

    def test_success_returns_status_and_no_retry(self):
        status, retry = run(gazu.aio.check_status(FakeResponse(200), "/"))
        self.assertEqual(status, 200)
        self.assertFalse(retry)


class AioClientTestCase(unittest.TestCase):
    def test_refresh_access_token_without_token_raises(self):
        # Regression (BUG-8): refreshing without a refresh token must raise
        # a typed exception instead of building a "Bearer None" header.
        client = gazu.aio.AsyncKitsuClient("http://localhost/api")
        with self.assertRaises(NotAuthenticatedException):
            run(client.refresh_access_token())

    def test_make_auth_header_includes_bearer_when_logged_in(self):
        client = gazu.aio.AsyncKitsuClient(
            "http://localhost/api", access_token="abc"
        )
        headers = client.make_auth_header()
        self.assertEqual(headers["Authorization"], "Bearer abc")

    def test_make_auth_header_without_token_has_no_authorization(self):
        client = gazu.aio.AsyncKitsuClient("http://localhost/api")
        headers = client.make_auth_header()
        self.assertNotIn("Authorization", headers)


class AioUploadTestCase(unittest.TestCase):
    def _check_upload(self, expire_token):
        async def scenario():
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

            app = web.Application()
            app.router.add_post("/pictures/preview-files/preview", upload)
            app.router.add_get("/auth/refresh-token", refresh)
            async with TestServer(app) as server:
                client = gazu.aio.AsyncKitsuClient(
                    str(server.make_url("/")),
                    access_token="old",
                    refresh_token="refresh",
                )
                try:
                    with tempfile.TemporaryDirectory() as directory:
                        paths = [
                            os.path.join(directory, n) for n in ("a", "b")
                        ]
                        for path, content in zip(paths, (b"main", b"extra")):
                            with open(path, "wb") as target:
                                target.write(content)
                        result = await gazu.aio.upload(
                            "pictures/preview-files/preview",
                            paths[0],
                            extra_files=[paths[1]],
                            data={"label": "review"},
                            client=client,
                        )
                finally:
                    await client.session.close()
            self.assertEqual(result, {"id": "preview"})
            expected = [("Bearer old", b"main", b"extra", "review")]
            if expire_token:
                expected.append(("Bearer new", b"main", b"extra", "review"))
            self.assertEqual(uploads, expected)

        run(scenario())

    def test_upload_returns_successful_response(self):
        self._check_upload(expire_token=False)

    def test_upload_reopens_all_files_after_token_refresh(self):
        self._check_upload(expire_token=True)

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


if __name__ == "__main__":
    unittest.main()
