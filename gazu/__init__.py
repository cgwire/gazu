from . import client as raw
from . import cache
from . import helpers
from . import events

from . import asset
from . import casting
from . import context
from . import entity
from . import files
from . import project
from . import person
from . import shot
from . import sync
from . import task
from . import user
from . import playlist

from .exception import AuthFailedException, ParameterException
from .__version__ import __version__


def get_host(client=raw.default_client):
    return raw.get_host(client=client)


def set_host(url, client=raw.default_client):
    raw.set_host(url, client=client)


def log_in(email, password, client=raw.default_client):
    tokens = {}
    try:
        tokens = raw.post(
            "auth/login", {"email": email, "password": password}, client=client
        )
    except ParameterException:
        pass

    if not tokens or (
        "login" in tokens and tokens.get("login", False) == False
    ):
        raise AuthFailedException
    else:
        raw.set_tokens(tokens, client=client)
    return tokens


def log_out(client=raw.default_client):
    tokens = {}
    try:
        raw.get(
            "auth/logout", client=client
        )
    except ParameterException:
        pass
    raw.set_tokens(tokens, client=client)
    return tokens


def get_event_host(client=raw.default_client):
    return raw.get_event_host(client=client)


def set_event_host(url, client=raw.default_client):
    raw.set_event_host(url, client=client)
