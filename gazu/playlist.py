from __future__ import annotations

import requests

from typing_extensions import Literal

from . import client as raw

from .helpers import normalize_model_parameter
from .sorting import sort_by_name

from .cache import cache
from .client import KitsuClient

default = raw.default_client


def _fetch_playlist_pages(
    path: str, page: int | None, client: KitsuClient
) -> list[dict]:
    """
    Return the playlists of the given page, or of all pages if page is None.

    Args:
        path (str): The path of the playlists.
        page (int): The page number, or None for all pages.
        client (KitsuClient): The client to use for the request.

    Returns:
        list: The playlists.
    """
    if page is not None:
        return raw.fetch_all(path, params={"page": page}, client=client)
    playlists = {}
    page = 1
    while True:
        entries = raw.fetch_all(path, params={"page": page}, client=client)
        # Stop on a page with no new playlist: older Zou versions may ignore
        # the page parameter and then always return the same list.
        new_entries = [e for e in entries if e["id"] not in playlists]
        if not new_entries:
            return list(playlists.values())
        playlists.update((entry["id"], entry) for entry in new_entries)
        page += 1


@cache
def all_playlists(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The playlists of all projects.
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
        list: The shots of the given playlist.
    """
    playlist = normalize_model_parameter(playlist)
    playlist = raw.fetch_one("playlists", playlist["id"], client=client)
    return sort_by_name(playlist["shots"])


@cache
def all_playlists_for_project(
    project: str | dict,
    client: KitsuClient = default,
    page: int | None = None,
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        page (int): The page number. If the value is None, return the playlists
            of all pages.

    Returns:
        list: The playlists of the given project.
    """
    project = normalize_model_parameter(project)
    return sort_by_name(
        _fetch_playlist_pages(
            f"projects/{project['id']}/playlists", page, client
        )
    )


@cache
def all_playlists_for_episode(
    episode: str | dict,
    client: KitsuClient = default,
    page: int | None = None,
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.
        page (int): The page number. If the value is None, return the playlists
            of all pages.

    Returns:
        list: The playlists of the given episode.
    """
    episode = normalize_model_parameter(episode)
    # Fetch the episode when only an ID was given, to get its project_id.
    if "project_id" not in episode:
        episode = raw.fetch_one("episodes", episode["id"], client=client)
    project = normalize_model_parameter(episode["project_id"])
    return sort_by_name(
        _fetch_playlist_pages(
            f"projects/{project['id']}/episodes/{episode['id']}/playlists",
            page,
            client,
        )
    )


@cache
def get_playlist(playlist: str | dict, client: KitsuClient = default) -> dict:
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        dict: The playlist with the given ID.
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
        name (str): The playlist name.

    Returns:
        dict: The playlist with the given name in the given project, or None
        if no playlist matches.
    """
    project = normalize_model_parameter(project)
    params = {"project_id": project["id"], "name": name}
    return raw.fetch_first("playlists", params=params, client=client)


def new_playlist(
    project: str | dict,
    name: str,
    episode: str | dict | None = None,
    for_entity: Literal[
        "shot", "asset", "sequence", "edit", "episode"
    ] = "shot",
    for_client: bool = False,
    is_for_all: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Create a playlist in the database for the given project.

    If a playlist with this name exists in the project, return this playlist.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The playlist name.
        episode (str / dict / None): The optional episode dict or ID. If the
            value is None, the playlist is at the project level. Set
            is_for_all to True to put it in "All Assets" in the web UI.
        for_entity (str): The type of entity in the playlist: "asset", "edit",
            "episode", "sequence" or "shot".
        for_client (bool): If True, share the playlist with clients.
        is_for_all (bool): If True and episode is None, the API creates the
            playlist in "All Assets" and not in "Main Pack" in the web UI.

    Returns:
        dict: The created or existing playlist.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "project_id": project["id"],
        "for_entity": for_entity,
        "for_client": for_client,
        "is_for_all": is_for_all,
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
    Save the given playlist data to the API.

    The given fields replace the current values. For example, the given
    ``shots`` list replaces the current list.

    Args:
        playlist (dict): The playlist dict to update.

    Returns:
        dict: The updated playlist.
    """
    return raw.put(f"data/playlists/{playlist['id']}", playlist, client=client)


def get_entity_preview_files(
    entity: str | dict, client: KitsuClient = default
) -> dict[str, list[dict]]:
    """
    Get all preview files of the given entity, by task type.

    Args:
        entity (str / dict): The entity or its ID.

    Returns:
        dict: The keys are task type IDs. The values are lists of revisions.
    """
    entity = normalize_model_parameter(entity)
    return raw.get(
        f"data/playlists/entities/{entity['id']}/preview-files",
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
    Add an entity to the playlist.

    By default, the revision to review is the last uploaded preview.

    Args:
        playlist (dict): The playlist. This function does not change this
            dict. Use the returned playlist.
        entity (str / dict): The entity to add or its ID.
        preview_file (str / dict): The revision to review. Use this value to
            select a different revision.
        persist (bool): If True, save the result to the API.

    Returns:
        dict: The updated playlist.
    """
    entity = normalize_model_parameter(entity)

    if preview_file is None:
        preview_files = get_entity_preview_files(entity, client=client)
        for task_type_id in preview_files.keys():
            task_type_files = preview_files[task_type_id]
            if not task_type_files:
                continue
            first_file = task_type_files[0]
            if (
                preview_file is None
                or preview_file["created_at"] < first_file["created_at"]
            ):
                preview_file = first_file

    entry = {"entity_id": entity["id"]}
    if preview_file is not None:
        preview_file = normalize_model_parameter(preview_file)
        entry["preview_file_id"] = preview_file["id"]

    if persist:
        return raw.post(
            f"actions/playlists/{playlist['id']}/add-entity",
            entry,
            client=client,
        )

    updated = dict(playlist)
    updated["shots"] = list(updated.get("shots") or [])
    updated["shots"].append(entry)
    return updated


def remove_entity_from_playlist(
    playlist: dict,
    entity: str | dict,
    persist: bool = True,
    client: KitsuClient = default,
) -> dict:
    """
    Remove all occurrences of the given entity from a playlist.

    Args:
        playlist (dict): The playlist. This function changes this dict.
        entity (str / dict): The entity to remove or its ID.
        persist (bool): If True, save the result to the API.

    Returns:
        dict: The updated playlist.
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
    Update the preview file of the given entity in a playlist.

    Args:
        playlist (dict): The playlist. This function changes this dict.
        entity (str / dict): The entity of the preview file.
        preview_file (str / dict): The new preview file of the entity.
        persist (bool): If True, save the result to the API.

    Returns:
        dict: The updated playlist.
    """
    entity = normalize_model_parameter(entity)
    preview_file = normalize_model_parameter(preview_file)
    for entry in playlist["shots"]:
        if entry["entity_id"] == entity["id"]:
            entry["preview_file_id"] = preview_file["id"]
    if persist:
        update_playlist(playlist, client=client)
    return playlist


def delete_playlist(
    playlist: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a playlist.

    Args:
        playlist (str / dict): The playlist dict or ID.

    Returns:
        str: The response text of the API.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.delete(f"data/playlists/{playlist['id']}", client=client)


@cache
def get_build_job(
    playlist: str | dict,
    build_job: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Get a build job.

    Args:
        playlist (str / dict): The playlist of the build job.
        build_job (str / dict): The build job dict or ID.

    Returns:
        dict: The build job data.
    """
    playlist = normalize_model_parameter(playlist)
    build_job = normalize_model_parameter(build_job)
    return raw.get(
        f"data/playlists/{playlist['id']}/jobs/{build_job['id']}",
        client=client,
    )


def remove_build_job(
    playlist: str | dict,
    build_job: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a build job.

    Args:
        playlist (str / dict): The playlist of the build job.
        build_job (str / dict): The build job dict or ID.

    Returns:
        str: The response text of the API.
    """
    playlist = normalize_model_parameter(playlist)
    build_job = normalize_model_parameter(build_job)
    return raw.delete(
        f"data/playlists/{playlist['id']}/jobs/{build_job['id']}",
        client=client,
    )


@cache
def all_build_jobs_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all build jobs of a project.

    Args:
        project (str / dict): The project dict or ID.

    Returns:
        list: The build jobs of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/build-jobs", client=client)


def build_playlist_movie(
    playlist: str | dict, client: KitsuClient = default
) -> dict:
    """
    Start the build of a movie for a playlist.

    Only a manager of the project can do this.

    Args:
        playlist (str / dict): The playlist dict or ID.

    Returns:
        dict: The build job data.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.get(f"data/playlists/{playlist['id']}/build/mp4", client=client)


def download_playlist_build(
    playlist: str | dict,
    build_job: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download a playlist build.

    Args:
        playlist (str / dict): The playlist dict or ID.
        build_job (str / dict): The build job dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the request.
    """
    playlist = normalize_model_parameter(playlist)
    build_job = normalize_model_parameter(build_job)
    path = f"data/playlists/{playlist['id']}/jobs/{build_job['id']}/build/mp4"
    return raw.download(
        path, file_path, client=client, progress_callback=progress_callback
    )


def download_playlist_zip(
    playlist: str | dict,
    file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> requests.Response:
    """
    Download a playlist as a ZIP file.

    Args:
        playlist (str / dict): The playlist dict or ID.
        file_path (str): The location of the file on the hard drive.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the download.

    Returns:
        requests.Response: The response object of the request.
    """
    playlist = normalize_model_parameter(playlist)
    path = f"data/playlists/{playlist['id']}/download/zip"
    return raw.download(
        path, file_path, client=client, progress_callback=progress_callback
    )


def generate_temp_playlist(
    project: str | dict, data: dict, client: KitsuClient = default
) -> dict:
    """
    Make a temporary playlist.

    Args:
        project (str / dict): The project dict or ID.
        data (dict): The body of the request, with the ``task_ids`` key, the
            ``entity_ids`` key or both.

    Returns:
        list: The entries of the temporary playlist.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/playlists/temp", data, client=client
    )


def notify_clients_playlist_ready(
    playlist: str | dict, client: KitsuClient = default
) -> dict:
    """
    Tell the clients that a playlist is ready.

    Only a manager of the project can do this.

    Args:
        playlist (str / dict): The playlist dict or ID.

    Returns:
        dict: A dict with the 'status' key.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.post(
        f"data/playlists/{playlist['id']}/notify-clients", {}, client=client
    )


def new_share_link(
    playlist: str | dict,
    expiration_date: str | None = None,
    can_comment: bool = True,
    password: str | None = None,
    can_download: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Make a share link for a playlist.

    Only a manager of the project can do this.

    Args:
        playlist (str / dict): The playlist dict or ID.
        expiration_date (str): The optional ISO expiration date of the link.
        can_comment (bool): If True, guests can comment (True by default).
        password (str): The optional password of the link.
        can_download (bool): If True, guests can download the playlist as a
            ZIP file (False by default).

    Returns:
        dict: The created share link with its token.
    """
    playlist = normalize_model_parameter(playlist)
    data = {"can_comment": can_comment}
    if can_download:
        data["can_download"] = True
    if expiration_date:
        data["expiration_date"] = expiration_date
    if password:
        data["password"] = password
    return raw.post(
        f"data/playlists/{playlist['id']}/share", data, client=client
    )


def all_share_links_for_playlist(
    playlist: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    List all active share links of a playlist.

    Only a manager of the project can do this.

    Args:
        playlist (str / dict): The playlist dict or ID.

    Returns:
        list: The active share links.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.fetch_all(f"playlists/{playlist['id']}/share", client=client)


def remove_share_link(
    playlist: str | dict,
    token: str,
    client: KitsuClient = default,
) -> str:
    """
    Disable a share link.

    Only a manager of the project can do this.

    Args:
        playlist (str / dict): The playlist dict or ID.
        token (str): The token of the share link.

    Returns:
        str: The response of the API.
    """
    playlist = normalize_model_parameter(playlist)
    return raw.delete(
        f"data/playlists/{playlist['id']}/share/{token}", client=client
    )
