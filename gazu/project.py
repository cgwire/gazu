from . import client

from .sorting import sort_by_name


def all():
    """
    Returns all the projects stored in the database.
    """
    return sort_by_name(client.fetch_all('projects'))


def fetch_project(project_id):
    """
    Returns project corresponding to given id
    """
    return client.fetch_one('projects', project_id)


def open_projects():
    """
    Returns all the open projects stored in the database.
    """
    return sort_by_name(client.fetch_all('projects/open'))
