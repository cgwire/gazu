import base64
import hashlib
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from unittest.mock import patch as mock_patch

import requests_mock

import gazu
from gazu import client as raw
from gazu.exception import AuthFailedException

from utils import mock_route

# Placeholder replaced by the state gazu generates.
STATE = object()


class AuthTestCase(unittest.TestCase):
    def test_host_wrappers(self):
        gazu.set_host("http://a/api")
        self.assertEqual(gazu.get_host(), "http://a/api")
        gazu.set_event_host("http://events")
        self.assertEqual(gazu.get_event_host(), "http://events")

    def test_log_in_stores_the_tokens(self):
        tokens = {"login": True, "access_token": "abc"}
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "auth/login", text=tokens)
            self.assertEqual(gazu.log_in("a@b.c", "pwd", totp="123"), tokens)
            self.assertEqual(mock.last_request.json()["totp"], "123")
        self.assertEqual(raw.default_client.access_token, "abc")

    def test_log_in_refused_raises(self):
        for kwargs in (
            {"text": {"login": False}},
            {"text": {}, "status_code": 401},
            {"text": {}},
        ):
            with self.subTest(kwargs), requests_mock.mock() as mock:
                mock_route(mock, "POST", "auth/login", **kwargs)
                with self.assertRaises(AuthFailedException):
                    gazu.log_in("a@b.c", "pwd")

    def test_log_in_keeps_the_message_of_the_server(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "POST",
                "auth/login",
                text={"message": "Wrong 2FA code"},
                status_code=400,
            )
            with self.assertRaises(AuthFailedException) as context:
                gazu.log_in("a@b.c", "pwd")
        self.assertIn("Wrong 2FA code", str(context.exception))

    def test_log_out_removes_the_tokens_when_the_server_refuses(self):
        for status_code in (200, 400, 401):
            with self.subTest(status_code), requests_mock.mock() as mock:
                raw.set_tokens({"access_token": "abc"})
                mock_route(
                    mock,
                    "GET",
                    "auth/logout",
                    text={},
                    status_code=status_code,
                )
                self.assertEqual(gazu.log_out(), {})
                self.assertEqual(raw.default_client.tokens, {})

    def test_send_email_otp(self):
        with requests_mock.mock() as mock:
            mock_route(mock, "GET", "auth/email-otp", text={"success": True})
            self.assertEqual(gazu.send_email_otp("a@b.c"), {"success": True})
            self.assertEqual(mock.last_request.qs, {"email": ["a@b.c"]})

    def test_refresh_access_token(self):
        raw.set_tokens({"refresh_token": "refresh"})
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "auth/refresh-token",
                text={"access_token": "new"},
            )
            gazu.refresh_access_token()
            self.assertEqual(
                mock.last_request.headers["Authorization"], "Bearer refresh"
            )
        self.assertEqual(raw.default_client.access_token, "new")

    def test_set_token_accepts_a_dict_or_an_access_token(self):
        for token, expected in (
            ({"access_token": "a", "refresh_token": "b"}, None),
            ("a", {"access_token": "a"}),
        ):
            gazu.set_token(token)
            self.assertEqual(raw.default_client.tokens, expected or token)

    def test_create_session_returns_a_logged_in_client(self):
        tokens = {"login": True, "access_token": "abc"}
        with requests_mock.mock() as mock:
            mock_route(mock, "POST", "http://a/api/auth/login", text=tokens)
            mock_route(mock, "GET", "http://a/api/auth/logout", text={})
            with gazu.create_session("http://a/api", "a@b.c", "pwd") as client:
                self.assertEqual(client.access_token, "abc")
                self.assertIsNot(client, raw.default_client)
            self.assertEqual(mock.call_count, 2)
        self.assertIsNone(client.access_token)

    def test_create_session_closes_the_session_when_login_fails(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock, "POST", "http://a/api/auth/login", text={"login": False}
            )
            with mock_patch("requests.Session.close") as close:
                with self.assertRaises(AuthFailedException):
                    gazu.create_session("http://a/api", "a@b.c", "pwd")
        self.assertTrue(close.called)


class BrowserLoginTestCase(unittest.TestCase):
    def fake_browser(self, *queries):
        """
        Return a webbrowser.open replacement that sends each query to the
        loopback listener, the way the Kitsu page would.
        """
        self.opened = []

        def visit(port, query):
            opener = urllib.request.build_opener(
                urllib.request.ProxyHandler({})
            )
            for params in query:
                try:
                    opener.open(
                        "http://127.0.0.1:%s/?%s"
                        % (port, urllib.parse.urlencode(params)),
                        timeout=5,
                    )
                except urllib.error.HTTPError:
                    pass

        def open_browser(url):
            parsed = urllib.parse.urlparse(url)
            params = dict(urllib.parse.parse_qsl(parsed.query))
            self.opened.append((parsed, params))
            query = [
                {
                    key: (params["state"] if value is STATE else value)
                    for key, value in item.items()
                }
                for item in queries
            ]
            threading.Thread(
                target=visit, args=(params["port"], query)
            ).start()
            return True

        return open_browser

    def mock_server(self, mock, **exchange):
        mock_route(mock, "POST", "auth/app-login/token", **exchange)

    def test_log_in_with_browser(self):
        tokens = {
            "login": True,
            "access_token": "access",
            "refresh_token": "refresh",
        }
        browser = self.fake_browser({"code": "code1", "state": STATE})
        with requests_mock.mock() as mock:
            self.mock_server(mock, text=tokens)
            with mock_patch("webbrowser.open", browser):
                result = gazu.log_in_with_browser(app_name="Prism")
            body = mock.request_history[-1].json()

        self.assertEqual(result, tokens)
        self.assertEqual(raw.default_client.tokens, tokens)
        parsed, params = self.opened[0]
        self.assertEqual(parsed.path, "/app-login")
        self.assertEqual(params["app_name"], "Prism")
        self.assertEqual(body["code"], "code1")
        challenge = (
            base64.urlsafe_b64encode(
                hashlib.sha256(body["code_verifier"].encode()).digest()
            )
            .decode()
            .rstrip("=")
        )
        self.assertEqual(params["code_challenge"], challenge)

    def test_log_in_with_browser_refused(self):
        browser = self.fake_browser({"error": "access_denied", "state": STATE})
        with requests_mock.mock() as mock:
            self.mock_server(mock, text={})
            with mock_patch("webbrowser.open", browser):
                with self.assertRaises(AuthFailedException) as context:
                    gazu.log_in_with_browser()
            self.assertIn("access_denied", str(context.exception))
            self.assertFalse(
                any(r.method == "POST" for r in mock.request_history)
            )

    def test_log_in_with_browser_ignores_wrong_state(self):
        tokens = {"access_token": "access", "refresh_token": "refresh"}
        browser = self.fake_browser(
            {"code": "forged", "state": "wrong"},
            {},
            {"code": "code1", "state": STATE},
        )
        with requests_mock.mock() as mock:
            self.mock_server(mock, text=tokens)
            with mock_patch("webbrowser.open", browser):
                gazu.log_in_with_browser()
            body = mock.request_history[-1].json()
        self.assertEqual(body["code"], "code1")

    def test_log_in_with_browser_wrong_state_then_timeout(self):
        browser = self.fake_browser({"code": "forged", "state": "wrong"})
        with requests_mock.mock() as mock:
            self.mock_server(mock, text={})
            with mock_patch("webbrowser.open", browser):
                with self.assertRaises(AuthFailedException) as context:
                    gazu.log_in_with_browser(timeout=0.5)
        self.assertIn("timed out", str(context.exception))

    def test_log_in_with_browser_timeout(self):
        with requests_mock.mock() as mock:
            self.mock_server(mock, text={})
            with mock_patch("webbrowser.open", lambda url: True):
                with self.assertRaises(AuthFailedException) as context:
                    gazu.log_in_with_browser(timeout=0.2)
        self.assertIn("timed out", str(context.exception))

    def test_log_in_with_browser_logs_url_without_browser(self):
        with requests_mock.mock() as mock:
            self.mock_server(mock, text={})
            with mock_patch("webbrowser.open", lambda url: False):
                with self.assertLogs("gazu", "INFO") as logs:
                    with self.assertRaises(AuthFailedException):
                        gazu.log_in_with_browser(timeout=0.2)
        self.assertIn("/app-login?", logs.output[0])

    def test_log_in_with_browser_exchange_rejected(self):
        browser = self.fake_browser({"code": "code1", "state": STATE})
        with requests_mock.mock() as mock:
            self.mock_server(
                mock, text={"message": "Invalid code"}, status_code=400
            )
            with mock_patch("webbrowser.open", browser):
                with self.assertRaises(AuthFailedException) as context:
                    gazu.log_in_with_browser()
        self.assertIn("rejected", str(context.exception))
