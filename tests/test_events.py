import unittest
from unittest import mock

import requests_mock

import gazu.client
import gazu.events

from utils import fakeid, mock_route


class EventsInitTestCase(unittest.TestCase):
    def _make_client(self, verify, refresh_token):
        client = gazu.client.create_client("http://kitsu.example/api")
        client.session.verify = verify
        client.tokens = {
            "access_token": "acc",
            "refresh_token": refresh_token,
        }
        client.use_refresh_token = True
        return client

    @mock.patch("gazu.events.socketio.Client")
    def test_init_inherits_ssl_verify(self, Client):
        client = self._make_client(verify=False, refresh_token="ref")
        gazu.events.init(client=client)
        # ssl_verify is inherited from the client (False), not forced to True.
        # call_args[1] (kwargs) works on 3.7; .kwargs is 3.8+.
        self.assertFalse(Client.call_args[1]["ssl_verify"])

    @mock.patch("gazu.events.socketio.Client")
    def test_init_refreshes_token_on_reconnect_only(self, Client):
        event_client = Client.return_value
        client = self._make_client(verify=True, refresh_token="ref")
        with mock.patch.object(client, "refresh_access_token") as refresh:
            gazu.events.init(client=client)
            # connect receives a callable for the headers.
            _host, headers_cb = event_client.connect.call_args[0]
            self.assertTrue(callable(headers_cb))
            # First (initial) connect: current token, no refresh.
            self.assertEqual(headers_cb()["Authorization"], "Bearer acc")
            refresh.assert_not_called()
            # Subsequent (reconnect) attempts refresh the token.
            headers_cb()
            refresh.assert_called_once()


class EventsLoginLogsTestCase(unittest.TestCase):
    def test_get_last_login_logs(self):
        with requests_mock.mock() as mock:
            mock_route(
                mock,
                "GET",
                "data/events/login-logs/last",
                text=[
                    {"id": fakeid("log-1"), "person_id": fakeid("person-1")}
                ],
            )
            result = gazu.events.get_last_login_logs(
                after="2026-01-01",
                limit=10,
                person_ids=[fakeid("person-1"), {"id": fakeid("person-2")}],
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["id"], fakeid("log-1"))
            qs = mock.last_request.qs
            self.assertEqual(qs["limit"], ["10"])
            self.assertEqual(qs["after"], ["2026-01-01"])
            # person_ids must be repeated params, one per person, with dicts
            # and raw ids both accepted.
            self.assertEqual(
                qs["person_ids"],
                [fakeid("person-1"), fakeid("person-2")],
            )


if __name__ == "__main__":
    unittest.main()
