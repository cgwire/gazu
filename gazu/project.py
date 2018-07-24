from deprecated import deprecated

from . import client

from .sorting import sort_by_name
from .cache import cache


@cache
def all_projects():
    """
    Returns all the projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects"))


@cache
def all_open_projects():
    """
    Returns all the open projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects/open"))


@cache
def get_project(project_id):
    """
    Returns project corresponding to given id.
    """
    return client.fetch_one("projects", project_id)


@cache
def get_project_by_name(project_name):
    """
    Returns project corresponding to given name.
    """
    return client.fetch_first("projects?name=%s" % project_name)


def new_project(name):
    data = {
        "name": name
    }
    project = get_project_by_name(name)
    if project is None:
        project = client.create("projects", data)
    return project


@deprecated
def all():
    return all_projects()
