import unittest
from unittest import mock

import requests_mock

import gazu.client
import gazu.events
from gazu.exception import AuthFailedException

from utils import fakeid, mock_route


def make_client(verify=True):
    client = gazu.client.create_client("http://kitsu.example/api")
    client.session.verify = verify
    client.tokens = {"access_token": "acc", "refresh_token": "ref"}
    client.use_refresh_token = True
    return client


class EventsInitTestCase(unittest.TestCase):
    @mock.patch("gazu.events.socketio.Client")
    def test_init_inherits_ssl_verify_of_the_client(self, Client):
        gazu.events.init(client=make_client(verify=False))
        # call_args[1] (kwargs) works on 3.7; .kwargs is 3.8+.
        self.assertFalse(Client.call_args[1]["ssl_verify"])
        gazu.events.init(client=make_client(verify=False), ssl_verify=True)
        self.assertTrue(Client.call_args[1]["ssl_verify"])

    @mock.patch("gazu.events.socketio.Client")
    def test_init_connects_to_the_event_host(self, Client):
        client = make_client()
        client.event_host = "http://events"
        self.assertIs(gazu.events.init(client=client), Client.return_value)
        self.assertEqual(
            Client.return_value.connect.call_args[0][0], "http://events"
        )

    @mock.patch("gazu.events.socketio.Client")
    def test_init_refreshes_the_token_on_reconnect_only(self, Client):
        client = make_client()
        with mock.patch.object(client, "refresh_access_token") as refresh:
            gazu.events.init(client=client)
            _host, headers = Client.return_value.connect.call_args[0]
            # First connect: current token, no refresh.
            self.assertEqual(headers()["Authorization"], "Bearer acc")
            refresh.assert_not_called()
            headers()
            refresh.assert_called_once()

    @mock.patch("gazu.events.socketio.Client")
    def test_failed_refresh_does_not_stop_the_reconnection(self, Client):
        client = make_client()
        with mock.patch.object(
            client, "refresh_access_token", side_effect=ValueError
        ):
            gazu.events.init(client=client)
            _host, headers = Client.return_value.connect.call_args[0]
            headers()
            self.assertEqual(headers()["Authorization"], "Bearer acc")


class EventsClientTestCase(unittest.TestCase):
    def test_add_listener_uses_the_events_namespace(self):
        event_client, handler = mock.Mock(), mock.Mock()
        self.assertIs(
            gazu.events.add_listener(event_client, "task:new", handler),
            event_client,
        )
        event_client.on.assert_called_once_with("task:new", handler, "/events")

    def test_run_client_waits_for_events(self):
        event_client = mock.Mock()
        self.assertIs(gazu.events.run_client(event_client), event_client)
        event_client.wait.assert_called_once_with()

    def test_run_client_raises_when_authentication_failed(self):
        event_client = mock.Mock()
        event_client.wait.side_effect = TypeError
        with self.assertRaises(AuthFailedException):
            gazu.events.run_client(event_client)

    def test_connection_errors_are_logged_and_returned(self):
        namespace = gazu.events.EventsNamespace("/events")
        with self.assertLogs("gazu.events", "ERROR"):
            self.assertEqual(namespace.on_error("broken"), "broken")


class EventsLoginLogsTestCase(unittest.TestCase):
    def test_get_last_login_logs_sends_the_filters(self):
        logs = [{"id": fakeid("log-1")}]
        person_1, person_2 = fakeid("person-1"), fakeid("person-2")
        with requests_mock.mock() as m:
            mock_route(m, "GET", "data/events/login-logs/last", text=logs)
            self.assertEqual(
                gazu.events.get_last_login_logs(
                    after="2026-01-01",
                    before="2026-01-02T03:04:05",
                    limit=10,
                    cursor_login_log_id=fakeid("log-0"),
                    person_ids=[person_1, {"id": person_2}],
                ),
                logs,
            )
            self.assertEqual(
                m.last_request.qs,
                {
                    "limit": ["10"],
                    "after": ["2026-01-01"],
                    "before": ["2026-01-02t03:04:05"],
                    "cursor_login_log_id": [fakeid("log-0")],
                    "person_ids": [person_1, person_2],
                },
            )

    def test_get_last_login_logs_refuses_a_wrong_date(self):
        with self.assertRaises(ValueError):
            gazu.events.get_last_login_logs(after="tomorrow")


if __name__ == "__main__":
    unittest.main()
