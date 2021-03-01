from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_project_status(client=default):
    """
    Returns:
        list: Project status listed in database.
    """
    return sort_by_name(raw.fetch_all("project-status", client=client))


@cache
def get_project_status_by_name(project_status_name, client=default):
    """
    Args:
        project_status_name (str): Name of claimed project status.

    Returns:
        dict: Project status corresponding to given name.
    """
    return raw.fetch_first(
        "project-status", {"name": project_status_name}, client=client
    )


@cache
def all_projects(client=default):
    """
    Returns:
        list: Projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects", client=client))


@cache
def all_open_projects(client=default):
    """
    Returns:
        Open projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects/open", client=client))


@cache
def get_project(project_id, client=default):
    """
    Args:
        project_id (str): ID of claimed project.

    Returns:
        dict: Project corresponding to given id.
    """
    return raw.fetch_one("projects", project_id, client=client)


@cache
def get_project_url(project, section="assets", client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        section (str): The section we want to open in the browser.

    Returns:
        url (str): Web url associated to the given project
    """
    project = normalize_model_parameter(project)
    path = "{host}/productions/{project_id}/{section}/"
    return path.format(
        host=raw.get_api_url_from_host(),
        project_id=project["id"],
        section=section
    )


@cache
def get_project_by_name(project_name, client=default):
    """
    Args:
        project_name (str): Name of claimed project.

    Returns:
        dict: Project corresponding to given name.
    """
    return raw.fetch_first("projects", {"name": project_name}, client=client)


def new_project(name, production_type="short", client=default):
    """
    Creates a new project.

    Args:
        name (str): Name of the project to create.
        production_type (str): short, featurefilm, tvshow

    Returns:
        dict: Created project.
    """
    data = {"name": name, "production_type": production_type}
    project = get_project_by_name(name, client=client)
    if project is None:
        project = raw.create("projects", data, client=client)
    return project


def remove_project(project, force=False, client=default):
    """
    Remove given project from database. (Prior to do that, make sure, there
    is no asset or shot left).

    Args:
        project (dict / str): Project to remove.
    """
    project = normalize_model_parameter(project)
    path = "data/projects/%s" % project["id"]
    if force:
        path += "?force=true"
    return raw.delete(path, client=client)


def update_project(project, client=default):
    """
    Save given project data into the API. Metadata are fully replaced by the
    ones set on given project.

    Args:
        project (dict): The project to update.

    Returns:
        dict: Updated project.
    """
    return raw.put(
        "data/projects/%s" % project["id"], project, client=client
    )


def update_project_data(project, data={}, client=default):
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
    project = get_project(project["id"], client=client)
    if "data" not in project or project["data"] is None:
        project["data"] = {}
    project["data"].update(data)
    update_project(project, client=client)


def close_project(project, client=default):
    """
    Closes the provided project.

    Args:
        project (dict / ID): The project dict or id to save in database.

    Returns:
        dict: Updated project.
    """
    closed_status_id = None
    for status in all_project_status(client=client):
        if status["name"].lower() == "closed":
            closed_status_id = status["id"]

    project["project_status_id"] = closed_status_id
    update_project(project, client=client)
    return project
