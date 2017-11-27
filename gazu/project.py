from . import client

from .sorting import sort_by_name

from cachetools import cached

from .cache import cache


def clear_cache():
    cache.clear()



def all():
    """
    Returns all the projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects"))


@cached(cache)
def all_open_projects():
    """
    Returns all the open projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects/open"))


def get_project(project_id):
    """
    Returns project corresponding to given id.
    """
    return client.fetch_one("projects", project_id)


def get_project_by_name(project_name):
    """
    Returns project corresponding to given name.
    """
    result = client.fetch_all("projects?name=%s" % project_name)
    return next(iter(result or []), None)
