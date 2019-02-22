
# imports
from . import client
from .helpers import normalize_model_parameter
from .sorting import sort_by_name


def get_all_playlists():
    """
    Retrieve all playlists for all projects

    Returns:
        dict: Playlists found
    """

    return sort_by_name(client.fetch_all("playlist"))


def get_all_shots_on_playlist(playlist):
    """
    Retrieve all shots assigned to the given playlist

    Args:
        playlist (str / dict): The playlist id value

    Returns:
        list: Playlists found on project
    """

    playlist = normalize_model_parameter(playlist)
    return sort_by_name(playlist["shots"])


def get_playlists_for_project(project):
    """
    Retrieve all playlists for the given project

    Args:
        project (str / dict): The project id value

    Returns:
        dict: Playlists found on project
    """

    project = normalize_model_parameter(project)

    if project is None:
        return sort_by_name(client.fetch_all("playlist"))

    else:
        return sort_by_name(
            client.fetch_all("projects/%s/playlist" % project["id"])
        )

