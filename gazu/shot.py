from __future__ import annotations

from typing_extensions import Literal

import requests

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_previews_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The previews of the given shot.
    """
    shot = normalize_model_parameter(shot)
    return raw.fetch_all(f"shots/{shot['id']}/preview-files", client=client)


@cache
def all_shots_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The shots of the given project.
    """
    project = normalize_model_parameter(project)
    shots = raw.fetch_all(
        f"projects/{project['id']}/shots", by_cursor=True, client=client
    )
    return sort_by_name(shots)


@cache
def all_shots_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: The shots of the given episode.
    """
    episode = normalize_model_parameter(episode)
    return sort_by_name(
        raw.fetch_all(f"episodes/{episode['id']}/shots", client=client)
    )


@cache
def all_shots_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The shots of the given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return sort_by_name(
        raw.fetch_all(f"sequences/{sequence['id']}/shots", client=client)
    )


@cache
def all_sequences_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The sequences of the given project.
    """
    project = normalize_model_parameter(project)
    path = f"projects/{project['id']}/sequences"
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_sequences_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: The sequences of the given episode.
    """
    episode = normalize_model_parameter(episode)
    path = f"episodes/{episode['id']}/sequences"
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_episodes_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The episodes of the given project.
    """
    project = normalize_model_parameter(project)
    path = f"projects/{project['id']}/episodes"
    episodes = raw.fetch_all(path, client=client)
    return sort_by_name(episodes)


@cache
def get_episode(episode_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        episode_id (str): The ID of the episode.

    Returns:
        dict: The episode with the given ID.
    """
    return raw.fetch_one("episodes", episode_id, client=client)


@cache
def get_episode_by_name(
    project: str | dict, episode_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        episode_name (str): The name of the episode.

    Returns:
        dict: The episode with the given name in the given project, or None if
        no episode matches.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "episodes",
        {"project_id": project["id"], "name": episode_name},
        client=client,
    )


@cache
def get_episode_from_sequence(
    sequence: dict, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        sequence (dict): The sequence dict.

    Returns:
        dict: The parent episode of the given sequence, or None if the sequence
        has no parent.
    """
    if sequence["parent_id"] is None:
        return None
    else:
        return get_episode(sequence["parent_id"], client=client)


@cache
def get_sequence(sequence_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        sequence_id (str): The ID of the sequence.

    Returns:
        dict: The sequence with the given ID.
    """
    return raw.fetch_one("sequences", sequence_id, client=client)


@cache
def get_sequence_by_name(
    project: str | dict,
    sequence_name: str,
    episode: str | dict | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        sequence_name (str): The name of the sequence.
        episode (str / dict): The episode dict or the episode ID (optional).

    Returns:
        dict: The sequence with the given name in the given project, or in the
        given episode for a TV show. None if no sequence matches.
    """
    project = normalize_model_parameter(project)
    if episode is None:
        params = {"project_id": project["id"], "name": sequence_name}
    else:
        episode = normalize_model_parameter(episode)
        params = {"episode_id": episode["id"], "name": sequence_name}
    return raw.fetch_first("sequences", params, client=client)


@cache
def get_sequence_from_shot(shot: dict, client: KitsuClient = default) -> dict:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: The parent sequence of the given shot.
    """
    shot = normalize_model_parameter(shot)
    if "parent_id" not in shot:
        # Only an ID was given: fetch the full shot to read its parent.
        shot = get_shot(shot["id"], client=client)
    return get_sequence(shot["parent_id"], client=client)


@cache
def get_shot(shot_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        shot_id (str): The ID of the shot.

    Returns:
        dict: The shot with the given ID.
    """
    return raw.fetch_one("shots", shot_id, client=client)


@cache
def get_shot_by_name(
    sequence: str | dict, shot_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        shot_name (str): The name of the shot.

    Returns:
        dict: The shot with the given name in the given sequence, or None if no
        shot matches.
    """
    sequence = normalize_model_parameter(sequence)
    return raw.fetch_first(
        "shots/all",
        {"sequence_id": sequence["id"], "name": shot_name},
        client=client,
    )


@cache
def get_episode_url(episode: str | dict, client: KitsuClient = default) -> str:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        url (str): The web URL of the given episode.
    """
    episode = normalize_model_parameter(episode)
    episode = get_episode(episode["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = episode["project_id"]
    episode_id = episode["id"]
    return f"{host}/productions/{project_id}/episodes/{episode_id}/shots"


@cache
def get_shot_url(shot: str | dict, client: KitsuClient = default) -> str:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        url (str): The web URL of the given shot.
    """
    shot = normalize_model_parameter(shot)
    shot = get_shot(shot["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = shot["project_id"]
    shot_id = shot["id"]
    if shot["episode_id"] is None:
        return f"{host}/productions/{project_id}/shots/{shot_id}/"
    else:
        episode_id = shot["episode_id"]
        return f"{host}/productions/{project_id}/episodes/{episode_id}/shots/{shot_id}/"


@cache
def get_all_episodes_url(
    project: str | dict, client: KitsuClient = default
) -> str:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        url (str): The web URL of the episodes list page of the given project.
        Use this function only for TV shows. For other production types, the
        page exists in the user interface but it is empty.
    """
    project = normalize_model_parameter(project)
    host = raw.get_api_url_from_host(client=client)
    return f"{host}/productions/{project['id']}/episodes/"


@cache
def get_all_sequences_url(
    project: str | dict, client: KitsuClient = default
) -> str:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        url (str): The web URL of the sequences list page of the given project.
    """
    project = normalize_model_parameter(project)
    host = raw.get_api_url_from_host(client=client)
    return f"{host}/productions/{project['id']}/sequences/"


@cache
def get_sequence_url(
    sequence: str | dict, client: KitsuClient = default
) -> str:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        url (str): The web URL of the given sequence. The URL is different if
        the sequence is in an episode (TV show) or at the project root.
    """
    sequence = normalize_model_parameter(sequence)
    sequence = get_sequence(sequence["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    project_id = sequence["project_id"]
    sequence_id = sequence["id"]
    if sequence.get("parent_id") is None:
        return f"{host}/productions/{project_id}/sequences/{sequence_id}/"
    else:
        episode_id = sequence["parent_id"]
        return (
            f"{host}/productions/{project_id}/episodes/{episode_id}"
            f"/sequences/{sequence_id}/"
        )


def new_sequence(
    project: str | dict,
    name: str,
    episode: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a sequence for the given project and episode.

    If this sequence exists, return it.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the sequence to create.
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        dict: The created or existing sequence.
    """
    project = normalize_model_parameter(project)
    data = {"name": name}

    if episode is not None:
        episode = normalize_model_parameter(episode)
        data["episode_id"] = episode["id"]

    sequence = get_sequence_by_name(
        project, name, episode=episode, client=client
    )
    if sequence is None:
        path = f"data/projects/{project['id']}/sequences"
        return raw.post(path, data, client=client)
    else:
        return sequence


def new_shot(
    project: str | dict,
    sequence: str | dict,
    name: str,
    nb_frames: int | None = None,
    frame_in: int | None = None,
    frame_out: int | None = None,
    description: str | None = None,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a shot for the given sequence and project.

    This function adds the frame in and frame out values to the extra data of
    the shot. You can also set metadata. If a shot with this name exists in
    the sequence, return this shot.

    Args:
        project (str / dict): The project dict or the project ID.
        sequence (str / dict): The sequence dict or the sequence ID.
        name (str): The name of the shot to create.
        nb_frames (int): The number of frames of the shot.
        frame_in (int): The frame in value of the shot.
        frame_out (int): The frame out value of the shot.
        description (str): The description of the shot.
        data (dict): A free field for metadata of all types.

    Returns:
        dict: The created or existing shot.
    """
    # Copy to avoid mutating the dict provided by the caller.
    data = dict(data) if data else {}
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)

    if frame_in is not None:
        data["frame_in"] = frame_in
    if frame_out is not None:
        data["frame_out"] = frame_out

    data = {"name": name, "data": data, "sequence_id": sequence["id"]}
    if nb_frames is not None:
        data["nb_frames"] = nb_frames

    if description is not None:
        data["description"] = description

    shot = get_shot_by_name(sequence, name, client=client)
    if shot is None:
        path = f"data/projects/{project['id']}/shots"
        return raw.post(path, data, client=client)
    else:
        return shot


def update_shot(shot: dict, client: KitsuClient = default) -> dict:
    """
    Save the given shot data to the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        shot (dict): The shot dict to update.

    Returns:
        dict: The updated shot.
    """
    return raw.put(f"data/entities/{shot['id']}", shot, client=client)


def update_sequence(sequence: dict, client: KitsuClient = default) -> dict:
    """
    Save the given sequence data to the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        sequence (dict): The sequence dict to update.

    Returns:
        dict: The updated sequence.
    """
    return raw.put(f"data/entities/{sequence['id']}", sequence, client=client)


@cache
def get_asset_instances_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> dict:
    """
    Return the asset instances of the given shot.

    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: The keys are asset IDs. The values are lists of asset instances.
    """
    shot = normalize_model_parameter(shot)
    return raw.get(f"data/shots/{shot['id']}/asset-instances", client=client)


def update_shot_data(
    shot: str | dict,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the metadata of the given shot.

    This function does not change the keys that are not in ``data``.

    Args:
        shot (str / dict): The shot dict or the shot ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated shot.
    """
    if data is None:
        data = {}
    shot = normalize_model_parameter(shot)
    # Invalidate the cache so the base read (and later reads) reflect the
    # server state; merging onto a stale cached copy reverts concurrent edits.
    get_shot.clear_cache()
    current_shot = get_shot(shot["id"], client=client)
    current_data = current_shot["data"] or {}
    updated_shot = {
        "id": current_shot["id"],
        "data": {**current_data, **data},
    }
    result = update_shot(updated_shot, client=client)
    get_shot.clear_cache()
    return result


def update_sequence_data(
    sequence: str | dict,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the metadata of the given sequence.

    This function does not change the keys that are not in ``data``.

    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated sequence.
    """
    if data is None:
        data = {}
    sequence = normalize_model_parameter(sequence)
    current_sequence = get_sequence(sequence["id"], client=client)
    updated_sequence = {
        "id": current_sequence["id"],
        "data": {**(current_sequence.get("data") or {}), **data},
    }
    return update_sequence(updated_sequence, client=client)


def remove_shot(
    shot: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given shot from the database.

    If tasks are linked to the shot, the API sets the shot to canceled and
    does not remove it. To remove the shot and its tasks, set ``force`` to
    True.

    Args:
        shot (str / dict): The shot to remove.
        force (bool): If True, remove the shot and its tasks.

    Returns:
        str: The response of the API.
    """
    shot = normalize_model_parameter(shot)
    path = f"data/shots/{shot['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def restore_shot(shot: str | dict, client: KitsuClient = default) -> dict:
    """
    Restore the given shot. The shot is not canceled after this operation.

    Args:
        shot (str / dict): The shot to restore.

    Returns:
        dict: The updated shot.
    """
    shot = normalize_model_parameter(shot)
    path = f"data/shots/{shot['id']}"
    data = {"canceled": False}
    return raw.put(path, data, client=client)


def new_episode(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict:
    """
    Create an episode for the given project.

    If an episode with this name exists in the project, return this episode.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the episode to create.

    Returns:
        dict: The created or existing episode.
    """
    project = normalize_model_parameter(project)
    data = {"name": name}
    episode = get_episode_by_name(project, name, client=client)
    if episode is None:
        return raw.post(
            f"data/projects/{project['id']}/episodes", data, client=client
        )
    else:
        return episode


def update_episode(episode: dict, client: KitsuClient = default) -> dict:
    """
    Save the given episode data to the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        episode (dict): The episode dict to update.

    Returns:
        dict: The updated episode.
    """
    return raw.put(f"data/entities/{episode['id']}", episode, client=client)


def update_episode_data(
    episode: str | dict,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the metadata of the given episode.

    This function does not change the keys that are not in ``data``.

    Args:
        episode (str / dict): The episode dict or the episode ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated episode.
    """
    if data is None:
        data = {}
    episode = normalize_model_parameter(episode)
    current_episode = get_episode(episode["id"], client=client)
    updated_episode = {
        "id": current_episode["id"],
        "data": {**(current_episode["data"] or {}), **data},
    }
    return update_episode(updated_episode, client=client)


def remove_episode(
    episode: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given episode from the database.

    If ``force`` is True, the API also removes all records linked to the
    episode: sequences, shots, assets, playlists and tasks.

    If ``force`` is False, the API removes only the episode. If records are
    linked to the episode, the operation fails.

    Args:
        episode (str / dict): The episode to remove.
        force (bool): If True, also remove all data linked to the episode.

    Returns:
        str: The response of the API.

    Raises:
        ParameterException:
            If entities are linked to the episode and ``force`` is False.
    """
    episode = normalize_model_parameter(episode)
    path = f"data/episodes/{episode['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params=params, client=client)


def remove_sequence(
    sequence: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given sequence from the database.

    If ``force`` is True, the API also removes all records linked to the
    sequence: shots, scenes and tasks.

    If ``force`` is False, the API removes only the sequence. If records are
    linked to the sequence, the operation fails.

    Args:
        sequence (str / dict): The sequence to remove.
        force (bool): If True, also remove all data linked to the sequence.

    Returns:
        str: The response of the API.

    Raises:
        ParameterException:
            If entities are linked to the sequence and ``force`` is False.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"data/sequences/{sequence['id']}"
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params=params, client=client)


def all_asset_instances_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> dict:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: The keys are asset IDs. The values are lists of asset instances.
    """
    # Kept as an alias of get_asset_instances_for_shot for backward compat.
    # No @cache here: the delegate already caches.
    return get_asset_instances_for_shot(shot, client=client)


def add_asset_instance_to_shot(
    shot: str | dict, asset_instance: str | dict, client: KitsuClient = default
) -> dict:
    """
    Link a new asset instance to the given shot.

    Args:
        shot (str / dict): The shot dict or the shot ID.
        asset_instance (str / dict): The asset instance dict or ID.

    Returns:
        dict: The related shot.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"asset_instance_id": asset_instance["id"]}
    path = f"data/shots/{shot['id']}/asset-instances"
    return raw.post(path, data, client=client)


def remove_asset_instance_from_shot(
    shot: str | dict, asset_instance: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the link between an asset instance and the given shot.

    Args:
        shot (str / dict): The shot dict or the shot ID.
        asset_instance (str / dict): The asset instance dict or ID.

    Returns:
        str: The response of the API.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    path = f"data/shots/{shot['id']}/asset-instances/{asset_instance['id']}"
    return raw.delete(path, client=client)


def import_shots_with_csv(
    project: str | dict,
    csv_file_path: str,
    client: KitsuClient = default,
    progress_callback=None,
) -> list[dict]:
    """
    Import the shots from an exported CSV file into the given project.

    Args:
        project (str / dict): The ID or dict of the target project.
        csv_file_path (str): The path of the CSV file on the disk.
        progress_callback (Callable): The function ``(bytes_read, total)``
            that this function calls during the upload.

    Returns:
        list[dict]: The shots that the import created.
    """
    project = normalize_model_parameter(project)
    return raw.upload(
        f"import/csv/projects/{project['id']}/shots",
        csv_file_path,
        client=client,
        progress_callback=progress_callback,
    )


def import_otio(
    project: str | dict,
    otio_file_path: str,
    episode: str | dict | None = None,
    naming_convention: str | None = None,
    match_case: bool = True,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict[Literal["created_shots", "updated_shots"], list[dict]]:
    """
    Import shots from an OpenTimelineIO file.

    This function also works with the formats of all OTIO adapters.

    Args:
        project (str / dict): The project dict or the project ID.
        otio_file_path (str): The OTIO file path.
        episode (str / dict): The episode dict or the episode ID.
        naming_convention (str): The template that finds the shot names in the
            file. If the value is None, this function uses a default template.
        match_case (bool): If True, the letter case of the shot names must
            match.
        progress_callback (Callable): The function ``(bytes_read, total)``
            that this function calls during the upload.

    Returns:
        dict: A dict with the "created_shots" and "updated_shots" keys. Each
            value is the list of the records that the import changed.
    """
    if naming_convention is None:
        if episode is not None:
            naming_convention = (
                "${project_name}_${episode_name}-${sequence_name}-${shot_name}"
            )
        else:
            naming_convention = "${project_name}_${sequence_name}-${shot_name}"
    project = normalize_model_parameter(project)
    path = f"/import/otio/projects/{project['id']}"
    if episode is not None:
        episode = normalize_model_parameter(episode)
        path += f"/episodes/{episode['id']}"
    return raw.upload(
        path,
        otio_file_path,
        data={
            "naming_convention": naming_convention,
            "match_case": match_case,
        },
        client=client,
        progress_callback=progress_callback,
    )


def export_shots_with_csv(
    project: str | dict,
    csv_file_path: str,
    episode: str | dict | None = None,
    assigned_to_me: bool = False,
    client: KitsuClient = default,
    progress_callback=None,
    assigned_to: str | dict | bool | None = None,
) -> requests.Response:
    """
    Export the shot data of a project to a CSV file on the disk.

    Args:
        project (str / dict):
            The ID or dict of the project to export.
        csv_file_path (str):
            The path of the CSV file on the disk. If the file exists, this
            function replaces it.
        episode (str | dict | None):
            The ID or dict of an episode. This function exports only the
            shots of this episode. If the value is None, this function exports
            all shots.
        assigned_to_me (bool):
            If True, export only the shots with one or more tasks assigned to
            the current user. Zou cannot filter on a different person.
        progress_callback (Callable):
            The function ``(bytes_read, total)`` that this function calls
            during the download. The value of ``total`` is 0 if it is unknown.
        assigned_to:
            Do not use this parameter. Use ``assigned_to_me``. A true value
            sets the filter on the current user. Zou ignores the given person.

    Returns:
        requests.Response: The response of the API server.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    params = {}
    if episode:
        params["episode_id"] = episode["id"]
    if assigned_to_me or assigned_to:
        params["assigned_to"] = "true"
    return raw.download(
        f"export/csv/projects/{project['id']}/shots.csv",
        csv_file_path,
        params=params,
        client=client,
        progress_callback=progress_callback,
    )
