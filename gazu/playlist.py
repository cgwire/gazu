from . import client
from .helpers import normalize_model_parameter
from .sorting import sort_by_name

from .cache import cache


@cache
def all_playlists():
    """
    Returns:
        list: All playlists for all projects.
    """

    return sort_by_name(client.fetch_all("playlists"))


@cache
def all_shots_for_playlist(playlist):
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        list: All shots linked to the given playlist
    """

    playlist = normalize_model_parameter(playlist)
    playlist = client.fetch_one("playlists", playlist["id"])
    return sort_by_name(playlist["shots"])


@cache
def all_playlists_for_project(project):
    """

    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: All playlists for the given project
    """

    project = normalize_model_parameter(project)
    return sort_by_name(
        client.fetch_all("projects/%s/playlists" % project["id"])
    )


@cache
def get_playlist(playlist):
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        dict: playlist object for given id.
    """

    playlist = normalize_model_parameter(playlist)
    return client.fetch_one("playlists", playlist["id"])


@cache
def get_playlist_by_name(project, name):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The playlist name

    Returns:
        dict: Playlist matching given name for given project.
    """
    project = normalize_model_parameter(project)
    playlists = all_playlists_for_project(project)
    for playlist in playlists:
        if playlist["name"] == name:
            return playlist
    return None


def new_playlist(project, name):
    """
    Create a new playlist in the database for given project.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): Playlist name.

    Returns:
        dict: Created playlist.
    """
    project = normalize_model_parameter(project)
    data = {"name": name, "project_id": project["id"]}
    playlist = get_playlist_by_name(project, name)
    if playlist is None:
        playlist = client.post("data/playlists/", data)
    return playlist


def update_playlist(playlist):
    """
    Save given playlist data into the API. Metadata are fully replaced by
    the ones set on given playlist.

    Args:
        playlist (dict): The playlist dict to update.

    Returns:
        dict: Updated playlist.
    """
    return client.put("data/playlists/%s" % playlist["id"], playlist)
