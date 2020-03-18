from . import client
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
from . import task
from . import user
from . import playlist

from .exception import AuthFailedException, ParameterException
from .__version__ import __version__


def get_host():
    return client.get_host()


def set_host(url):
    client.set_host(url)


def log_in(email, password):
    tokens = {}
    try:
        tokens = client.post(
            "auth/login", {"email": email, "password": password}
        )
    except ParameterException:
        pass

    if "login" in tokens and tokens.get("login", False) == False:
        raise AuthFailedException
    else:
        client.set_tokens(tokens)
    return tokens


def get_event_host():
    return client.get_event_host()


def set_event_host(url):
    client.set_event_host(url)
