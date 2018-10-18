from . import client
from . import cache
from . import helpers

from . import asset
from . import context
from . import entity
from . import files
from . import project
from . import person
from . import shot
from . import task
from . import user

from .exception import AuthFailedException

__version__ = '0.6.2'


def get_host():
    return client.get_host()


def set_host(url):
    client.set_host(url)


def log_in(email, password):
    tokens = client.post("auth/login", {
        "email": email,
        "password": password
    })
    if "login" in tokens and tokens["login"] == False:
        raise AuthFailedException
    else:
        client.set_tokens(tokens)
    return tokens
