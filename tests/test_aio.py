import asyncio
import unittest
import unittest.mock

import pytest

pytest.importorskip("aiohttp")  # async extra is optional; skip if absent

import gazu.aio
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


if __name__ == "__main__":
    unittest.main()


class AioFetchAllPaginatedTestCase(unittest.TestCase):
    def test_fetch_all_paginated(self):
        pages = {
            1: {"data": [{"id": "a"}], "nb_pages": 2, "page": 1},
            2: {"data": [{"id": "b"}], "nb_pages": 2, "page": 2},
        }
        calls = []

        async def fake_get(path, params=None, client=None):
            calls.append(dict(params))
            return pages[params["page"]]

        params = {"project_id": "p"}
        with unittest.mock.patch.object(gazu.aio, "get", fake_get):
            result = asyncio.run(
                gazu.aio.fetch_all("tasks", params, paginated=True)
            )
        self.assertEqual(result, [{"id": "a"}, {"id": "b"}])
        self.assertEqual(params, {"project_id": "p"})
        self.assertEqual(calls[0]["limit"], gazu.client.PAGE_SIZE)

    def test_fetch_all_paginated_on_unpaginated_route(self):
        async def fake_get(path, params=None, client=None):
            return [{"id": "a"}]

        with unittest.mock.patch.object(gazu.aio, "get", fake_get):
            result = asyncio.run(gazu.aio.fetch_all("tasks", paginated=True))
        self.assertEqual(result, [{"id": "a"}])
