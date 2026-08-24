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
    Init configuration for SocketIO client.

    Returns:
        Event client that will be able to set listeners.
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
    Get last login logs. Requires admin permissions (login logs carry the IP
    address of every person and cover the whole studio).

    Args:
        after (str): Get only logins occuring after given date.
        before (str): Get only logins occuring before given date.
        limit (int): Number of login logs to retrieve (server caps at 1000).
        cursor_login_log_id (str): ID of the last login log from previous
            page, for cursor-based pagination.
        person_ids (list[str / dict]): Get only logins of given persons.

    Returns:
        list[dict]: Last login logs (person id, date, IP address and origin)
        matching criterions, most recent first.
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
    logger.error("The connection failed! %s", data)
    return data


def add_listener(
    event_client: socketio.Client, event_name: str, event_handler: Callable
) -> socketio.Client:
    """
    Set a listener that reacts to a given event.
    """
    event_client.on(event_name, event_handler, "/events")
    return event_client


def run_client(event_client: socketio.Client) -> socketio.Client:
    """
    Run event client (it blocks current thread). It listens to all events
    configured.
    """
    try:
        logger.info("Listening to Kitsu events...")
        event_client.wait()
    except TypeError:
        raise AuthFailedException
    return event_client
