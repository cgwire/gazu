__version__ = '0.2.0'

from . import client
from . import project
from . import person
from . import task
from . import shot
from . import asset
from . import files


def set_host(url):
    client.set_host(url)


def log_in(email, password):
    client.post("auth/login", {
        "email": email,
        "password": password
    })
