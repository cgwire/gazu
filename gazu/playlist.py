from __future__ import annotations

import requests

from typing_extensions import Literal

from . import client as raw

from .helpers import normalize_model_parameter
from .sorting import sort_by_name

from .cache import cache
from .client import KitsuClient

default = raw.default_client


@cache
def all_playlists(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: All playlists for all projects.
    """
    return sort_by_name(raw.fetch_all("playlists", client=client))


@cache
def all_shots_for_playlist(
    playlist: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        list: All shots linked to the given playlist
    """
    playlist = normalize_model_parameter(playlist)
    playlist = raw.fetch_one("playlists", playlist["id"], client=client)
    return sort_by_name(playlist["shots"])


@cache
def all_playlists_for_project(
    project: str | dict, client: KitsuClient = default, page: int = 1
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        page (int): Page number for pagination

    Returns:
        list: All playlists for the given project
    """
    project = normalize_model_parameter(project)
    return sort_by_name(
        raw.fetch_all(
            "projects/%s/playlists" % project["id"],
            params={"page": page},
            client=client,
        )
    )


@cache
def all_playlists_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: All playlists for the given episode.
    """
    project = normalize_model_parameter(episode["project_id"])
    return sort_by_name(
        raw.fetch_all(
            "projects/%s/episodes/%s/playlists"
            % (
                project["id"],
                episode["id"],
            ),
            client=client,
        )
    )


@cache
def get_playlist(playlist: str | dict, client: KitsuClient = default) -> dict:
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        dict: playlist object for given id.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.fetch_one("playlists", playlist["id"], client=client)


@cache
def get_playlist_by_name(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The playlist name

    Returns:
        dict: Playlist matching given name for given project.
    """
    project = normalize_model_parameter(project)
    params = {"project_id": project["id"], "name": name}
    return raw.fetch_first("playlists", params=params, client=client)


def new_playlist(
    project: str | dict,
    name: str,
    episode: str | dict | None = None,
    for_entity: Literal["shot", "asset", "sequence"] = "shot",
    for_client: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create a new playlist in the database for given project.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): Playlist name.
        for_entity (str): The type of entity to include in the playlist, can
            be one of "asset", "sequence" or "shot".
        for_client (bool): Whether the playlist should be shared with clients.

    Returns:
        dict: Created playlist.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "project_id": project["id"],
        "for_entity": for_entity,
        "for_client": for_client,
    }
    if episode is not None:
        episode = normalize_model_parameter(episode)
        data["episode_id"] = episode["id"]
    playlist = get_playlist_by_name(project, name, client=client)
    if playlist is None:
        playlist = raw.post("data/playlists/", data, client=client)
    return playlist


def update_playlist(playlist: dict, client: KitsuClient = default) -> dict:
    """
    Save given playlist data into the API. Metadata are fully replaced by
    the ones set on given playlist.

    Args:
        playlist (dict): The playlist dict to update.

    Returns:
        dict: Updated playlist.
    """
    return raw.put(
        "data/playlists/%s" % playlist["id"], playlist, client=client
    )


def get_entity_preview_files(
    entity: str | dict, client: KitsuClient = default
) -> dict[str, list[dict]]:
    """
    Get all preview files grouped by task type for a given entity.

    Args:
        entity (str / dict): The entity to retrieve files from or its ID.

    Returns:
        dict: A dict where keys are task type IDs and value array of revisions.
    """
    entity = normalize_model_parameter(entity)
    return raw.get(
        "data/playlists/entities/%s/preview-files" % entity["id"],
        client=client,
    )


def add_entity_to_playlist(
    playlist: dict,
    entity: str | dict,
    preview_file: str | dict | None = None,
    persist: bool = True,
    client: KitsuClient = default,
) -> dict:
    """
    Add an entity to the playlist, use the last uploaded preview as revision
    to review.

    Args:
        playlist (dict): Playlist object to modify.
        entity (str / dict): The entity to add or its ID.
        preview_file (str / dict): Set it to force a give revision to review.
        persist (bool): Set it to True to save the result to the API.

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)

    if preview_file is None:
        preview_files = get_entity_preview_files(entity)
        for task_type_id in preview_files.keys():
            task_type_files = preview_files[task_type_id]
            first_file = task_type_files[0]
            if (
                preview_file is None
                or preview_file["created_at"] < first_file["created_at"]
            ):
                preview_file = first_file

    preview_file = normalize_model_parameter(preview_file)
    playlist["shots"].append(
        {"entity_id": entity["id"], "preview_file_id": preview_file["id"]}
    )
    if persist:
        update_playlist(playlist, client=client)
    return playlist


def remove_entity_from_playlist(
    playlist: dict,
    entity: str | dict,
    persist: bool = True,
    client: KitsuClient = default,
) -> dict:
    """
    Remove all occurences of a given entity from a playlist.

    Args:
        playlist (dict): Playlist object to modify
        entity (str / dict): the entity to remove or its ID
        persist (bool): Set it to True to save the result to the API.

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)
    playlist["shots"] = [
        entry
        for entry in playlist["shots"]
        if entry["entity_id"] != entity["id"]
    ]
    if persist:
        update_playlist(playlist, client=client)
    return playlist


def update_entity_preview(
    playlist: dict,
    entity: str | dict,
    preview_file: str | dict,
    persist: bool = True,
    client: KitsuClient = default,
) -> dict:
    """
    Update the preview file linked to a given entity in a playlist.

    Args:
        playlist (dict): Playlist object to modify.
        entity (str / dict): The entity to update the preview file for.
        preview_file (str / dict): The new preview file to set for the entity.
        persist (bool): Set it to True to save the result to the API.

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)
    preview_file = normalize_model_parameter(preview_file)
    for entry in playlist["shots"]:
        if entry["entity_id"] == entity["id"]:
            entry["preview_file_id"] = preview_file["id"]
    if persist:
        update_playlist(playlist, client=client)
    return playlist


@cache
def delete_playlist(
    playlist: str | dict, client: KitsuClient = default
) -> str:
    """
    Delete a playlist.

    Args:
        playlist (str / dict): The playlist dict or id.

    Returns:
        Response: Request response object.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.delete("data/playlists/%s" % playlist["id"], client=client)


@cache
def get_entity_previews(
    playlist: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get entity previews for a playlist.

    Args:
        playlist (str / dict): The playlist dict or id.

    Returns:
        list: Entity previews for the playlist.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.fetch_all(
        "playlists/%s/entity-previews" % playlist["id"], client=client
    )


@cache
def get_build_job(
    build_job: str | dict, client: KitsuClient = default
) -> dict:
    """
    Get a build job.

    Args:
        build_job (str / dict): The build job dict or id.

    Returns:
        dict: Build job information.
    """
    build_job = normalize_model_parameter(build_job)
    return raw.fetch_one(
        "playlists/build-jobs", build_job["id"], client=client
    )


def remove_build_job(
    build_job: str | dict, client: KitsuClient = default
) -> str:
    """
    Delete a build job.

    Args:
        build_job (str / dict): The build job dict or id.
    """
    build_job = normalize_model_parameter(build_job)
    return raw.delete(
        "data/playlists/build-jobs/%s" % build_job["id"], client=client
    )


@cache
def all_build_jobs_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all build jobs for a project.

    Args:
        project (str / dict): The project dict or id.

    Returns:
        list: All build jobs for the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/build-jobs" % project["id"], client=client
    )


def build_playlist_movie(
    playlist: str | dict, client: KitsuClient = default
) -> dict:
    """
    Build a movie for a playlist.

    Args:
        playlist (str / dict): The playlist dict or id.

    Returns:
        dict: Build job information.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.post(
        "data/playlists/%s/build-movie" % playlist["id"], {}, client=client
    )


def download_playlist_build(
    playlist: str | dict,
    build_job: str | dict,
    file_path: str,
    client: KitsuClient = default,
) -> requests.Response:
    """
    Download a playlist build.

    Args:
        playlist (str / dict): The playlist dict or id.
        build_job (str / dict): The build job dict or id.
        file_path (str): The location to store the file on the hard drive.

    Returns:
        Response: Request response object.
    """
    playlist = normalize_model_parameter(playlist)
    build_job = normalize_model_parameter(build_job)
    path = "data/playlists/%s/build-jobs/%s/download" % (
        playlist["id"],
        build_job["id"],
    )
    return raw.download(path, file_path, client=client)


def download_playlist_zip(
    playlist: str | dict, file_path: str, client: KitsuClient = default
) -> requests.Response:
    """
    Download a playlist as a zip file.

    Args:
        playlist (str / dict): The playlist dict or id.
        file_path (str): The location to store the file on the hard drive.

    Returns:
        Response: Request response object.
    """
    playlist = normalize_model_parameter(playlist)
    path = "data/playlists/%s/download/zip" % playlist["id"]
    return raw.download(path, file_path, client=client)


def generate_temp_playlist(
    project: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Generate a temporary playlist.

    Args:
        project (str / dict): The project dict or id.
        data (dict): Playlist generation data.

    Returns:
        dict: Generated temporary playlist.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        "data/projects/%s/playlists/temp" % project["id"], data, client=client
    )


def notify_clients_playlist_ready(
    playlist: str | dict, client: KitsuClient = default
) -> dict:
    """
    Notify clients that a playlist is ready.

    Args:
        playlist (str / dict): The playlist dict or id.

    Returns:
        dict: Notification response.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.post(
        "data/playlists/%s/notify-clients" % playlist["id"], {}, client=client
    )
