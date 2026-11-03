"""
Listen to the Kitsu events in real time with Socket.IO.
"""

from __future__ import annotations

import socketio
import logging
import os
import inspect
import signal

from typing import Any, Callable

from engineio.base_client import signal_handler
from .exception import AuthFailedException

from . import client as raw
from .client import (
    default_client,
    get_event_host,
    KitsuClient,
    make_auth_header,
)
from .helpers import normalize_model_parameter, validate_date_format

logger = logging.getLogger("gazu.events")


if os.name == "nt":
    from win32api import SetConsoleCtrlHandler

    def WindowsSignalHandler(event):
        if event == 0:
            try:
                signal_handler(signal.SIGINT, inspect.currentframe())
            except Exception:
                # SetConsoleCtrlHandler handle cannot raise exceptions
                pass

    SetConsoleCtrlHandler(WindowsSignalHandler, 1)


class EventsNamespace(socketio.ClientNamespace):
    """
    The Socket.IO namespace of the Kitsu events (``/events``).
    """

    def on_connect(self) -> None:
        pass

    def on_disconnect(self) -> None:
        pass

    def on_error(self, data: str) -> str:
        return connect_error(data)


def init(
    client: KitsuClient = default_client,
    ssl_verify: bool | None = None,
    reconnection: bool = True,
    logger: bool = False,
    **kwargs: Any,
) -> socketio.Client:
    """
    Create a SocketIO client and connect it to the event host.

    Args:
        client (KitsuClient): The client that gives the host and the tokens.
        ssl_verify (bool): If True, verify SSL certificates. If the value is
            None, use the SSL setting of ``client``.
        reconnection (bool): If True, connect again after a connection loss.
        logger (bool): If True, log the SocketIO messages.
        **kwargs: The other parameters of ``socketio.Client``.

    Returns:
        socketio.Client: The connected event client. Add listeners to it.
    """
    if ssl_verify is None:
        # Inherit the client's TLS setting instead of always verifying.
        ssl_verify = getattr(client.session, "verify", True)
    params = {
        "ssl_verify": ssl_verify,
        "reconnection": reconnection,
        "logger": logger,
    }
    params.update(kwargs)
    event_client = socketio.Client(**params)
    event_client.on("connect_error", connect_error)
    event_client.register_namespace(EventsNamespace("/events"))

    first_connect = {"done": False}

    def auth_headers() -> dict:
        # socketio invokes this on every (re)connection attempt. Refresh the
        # access token on reconnects so a long-lived listener does not retry
        # with an expired one (the first connect uses the current token).
        if (
            first_connect["done"]
            and client.refresh_token
            and client.use_refresh_token
        ):
            try:
                client.refresh_access_token()
            except Exception as exc:
                logging.getLogger("gazu.events").debug(
                    "token refresh before reconnect failed: %s", exc
                )
        first_connect["done"] = True
        return make_auth_header(client=client)

    event_client.connect(get_event_host(client), auth_headers)
    return event_client


def get_last_login_logs(
    after: str | None = None,
    before: str | None = None,
    limit: int = 100,
    cursor_login_log_id: str | None = None,
    person_ids: list[str | dict] | None = None,
    client: KitsuClient = default_client,
) -> list[dict]:
    """
    Get the last login logs.

    Only administrators can do this. The login logs contain the IP address
    of each person and include the full studio.

    Args:
        after (str): Get only the logins after the given date.
        before (str): Get only the logins before the given date.
        limit (int): The number of login logs to get (1000 at maximum).
        cursor_login_log_id (str): The ID of the last login log of the
            previous page. Use this value for cursor pagination.
        person_ids (list[str / dict]): Get only the logins of these persons.

    Returns:
        list[dict]: The login logs (person ID, date, IP address and origin)
        that match the criteria. The most recent log is first.
    """
    params = {"limit": limit}
    if after is not None:
        params["after"] = validate_date_format(after)
    if before is not None:
        params["before"] = validate_date_format(before)
    if cursor_login_log_id is not None:
        params["cursor_login_log_id"] = cursor_login_log_id
    if person_ids:
        params["person_ids"] = [
            normalize_model_parameter(person)["id"] for person in person_ids
        ]
    return raw.get("data/events/login-logs/last", params=params, client=client)


def connect_error(data: str) -> str:
    """
    Write the connection error to the log and return it.
    """
    logger.error("The connection failed! %s", data)
    return data


def add_listener(
    event_client: socketio.Client, event_name: str, event_handler: Callable
) -> socketio.Client:
    """
    Set a listener for the given event.
    """
    event_client.on(event_name, event_handler, "/events")
    return event_client


def run_client(event_client: socketio.Client) -> socketio.Client:
    """
    Run the event client. The client listens to all configured events.

    The current thread waits until the client stops.
    """
    try:
        logger.info("Listening to Kitsu events...")
        event_client.wait()
    except TypeError:
        raise AuthFailedException
    return event_client
