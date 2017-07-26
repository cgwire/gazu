from . import client
from . import project
from . import person
from . import task
from . import shot
from . import asset
from . import files

from .exception import AuthFailedException

__version__ = '0.3.0'


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
