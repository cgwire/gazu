from . import client
from .sorting import sort_by_name


def all():
    return sort_by_name(client.fetch_all('persons'))
