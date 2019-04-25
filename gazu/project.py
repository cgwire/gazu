from . import client

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter


@cache
def all_projects():
    """
    Returns:
        list: Projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects"))


@cache
def all_open_projects():
    """
    Returns:
        Open projects stored in the database.
    """
    return sort_by_name(client.fetch_all("projects/open"))


@cache
def get_project(project_id):
    """
    Args:
        project_id (str): ID of claimed project.

    Returns:
        dict: Project corresponding to given id.
    """
    return client.fetch_one("projects", project_id)


@cache
def get_project_by_name(project_name):
    """
    Args:
        project_name (str): Name of claimed project.

    Returns:
        dict: Project corresponding to given name.
    """
    return client.fetch_first("projects?name=%s" % project_name)


def new_project(name, production_type="short"):
    """
    Creates a new project.

    Args:
        name (str): Name of the project to create.
        production_type (str): short, featurefilm, tvshow

    Returns:
        dict: Created project.
    """
    data = {
        "name": name,
        "production_type": production_type
    }
    project = get_project_by_name(name)
    if project is None:
        project = client.create("projects", data)
    return project


def remove_project(project):
    """
    Remove given project from database. (Prior to do that, make sure, there
    is no asset or shot left).

    Args:
        project (dict / str): Project to remove.
    """
    project = normalize_model_parameter(project)
    path = "data/projects/%s" % project["id"]
    return client.delete(path)


def update_project(project):
    """
    Save given project data into the API. Metadata are fully replaced by the
    ones set on given project.

    Args:
        project (dict): The project to update.

    Returns:
        dict: Updated project.
    """
    return client.put("data/projects/%s" % project["id"], project)


def update_project_data(project, data={}):
    """
    Update the metadata for the provided project. Keys that are not provided
    are not changed.

    Args:
        project (dict / ID): The project dict or id to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated project.
    """
    project = normalize_model_parameter(project)
    project = get_project(project["id"])
    if "data" not in project or project["data"] is None:
        project["data"] = {}
    project["data"].update(data)
    update_project(project)
