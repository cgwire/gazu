from .exception import AuthFailedException
from .client import default_client


def init(client=default_client, ssl_verify=True):
    """
    Init configuration for SocketIO client.

    Returns:
        Event client that will be able to set listeners.
    """
    from socketIO_client import SocketIO, BaseNamespace
    from . import get_event_host
    from gazu.client import make_auth_header

    path = get_event_host(client)
    event_client = SocketIO(
        path,
        None,
        headers=make_auth_header(),
        verify=ssl_verify
    )
    main_namespace = event_client.define(BaseNamespace, "/events")
    event_client.main_namespace = main_namespace
    event_client.on('error', connect_error)
    return event_client


def connect_error(data):
    print("The connection failed!")
    return data


def add_listener(event_client, event_name, event_handler):
    """
    Set a listener that reacts to a given event.
    """
    event_client.main_namespace.on(event_name, event_handler)
    return event_client


def run_client(event_client):
    """
    Run event client (it blocks current thread). It listens to all events
    configured.
    """
    try:
        print("Listening to Kitsu events...")
        event_client.wait()
    except TypeError:
        raise AuthFailedException
    return event_client
