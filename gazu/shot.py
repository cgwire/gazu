from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_previews_for_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Previews from database for given shot.
    """
    shot = normalize_model_parameter(shot)
    return raw.fetch_all("shots/%s/preview-files" % shot["id"], client=client)


@cache
def all_shots_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Shots from database or for given project.
    """
    project = normalize_model_parameter(project)
    shots = raw.fetch_all("projects/%s/shots" % project["id"], client=client)

    return sort_by_name(shots)


@cache
def all_shots_for_episode(episode, client=default):
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: Shots which are children of given episode.
    """
    episode = normalize_model_parameter(episode)
    return sort_by_name(
        raw.fetch_all("episodes/%s/shots" % episode["id"], client=client)
    )


@cache
def all_shots_for_sequence(sequence, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Shots which are children of given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return sort_by_name(
        raw.fetch_all("sequences/%s/shots" % sequence["id"], client=client)
    )


@cache
def all_sequences_for_project(project, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Sequences from database for given project.
    """
    project = normalize_model_parameter(project)
    path = "projects/%s/sequences" % project["id"]
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_sequences_for_episode(episode, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Sequences which are children of given episode.
    """
    episode = normalize_model_parameter(episode)
    path = "episodes/%s/sequences" % episode["id"]
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_episodes_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Episodes from database for given project.
    """
    project = normalize_model_parameter(project)
    path = "projects/%s/episodes" % project["id"]
    episodes = raw.fetch_all(path, client=client)
    return sort_by_name(episodes)


@cache
def get_episode(episode_id, client=default):
    """
    Args:
        episode_id (str): Id of claimed episode.

    Returns:
        dict: Episode corresponding to given episode ID.
    """
    return raw.fetch_one("episodes", episode_id, client=client)


@cache
def get_episode_by_name(project, episode_name, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        episode_name (str): Name of claimed episode.

    Returns:
        dict: Episode corresponding to given name and project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "episodes",
        {"project_id": project["id"], "name": episode_name},
        client=client
    )


@cache
def get_episode_from_sequence(sequence, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        dict: Episode which is parent of given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return get_episode(sequence["parent_id"], client=client)


@cache
def get_sequence(sequence_id, client=default):
    """
    Args:
        sequence_id (str): ID of claimed sequence.

    Returns:
        dict: Sequence corresponding to given sequence ID.
    """
    return raw.fetch_one("sequences", sequence_id, client=client)


@cache
def get_sequence_by_name(project, sequence_name, episode=None, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        sequence_name (str): Name of claimed sequence.
        episode (str / dict): The episode dict or the episode ID (optional).

    Returns:
        dict: Seqence corresponding to given name and project (and episode in
        case of TV Show).
    """
    project = normalize_model_parameter(project)
    if episode is None:
        params = {"project_id": project["id"], "name": sequence_name}
    else:
        episode = normalize_model_parameter(episode)
        params = {"episode_id": episode["id"], "name": sequence_name}
    return raw.fetch_first("sequences", params, client=client)


@cache
def get_sequence_from_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        dict: Sequence which is parent of given shot.
    """
    shot = normalize_model_parameter(shot)
    return get_sequence(shot["parent_id"], client=client)


@cache
def get_shot(shot_id, client=default):
    """
    Args:
        shot_id (str): Id of claimed shot.

    Returns:
        dict: Shot corresponding to given shot ID.
    """
    return raw.fetch_one("shots", shot_id, client=client)


@cache
def get_shot_by_name(sequence, shot_name, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        shot_name (str): Name of claimed shot.

    Returns:
        dict: Shot corresponding to given name and sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return raw.fetch_first(
        "shots/all",
        {"sequence_id": sequence["id"], "name": shot_name},
        client=client
    )


@cache
def get_episode_url(episode, client=default):
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        url (str): Web url associated to the given episode
    """
    episode = normalize_model_parameter(episode)
    episode = get_episode(episode["id"])
    path = "{host}/productions/{project_id}/episodes/{episode_id}/shots"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        project_id=episode["project_id"],
        episode_id=episode["id"],
    )


@cache
def get_shot_url(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        url (str): Web url associated to the given shot
    """
    shot = normalize_model_parameter(shot)
    shot = get_shot(shot["id"])
    path = "{host}/productions/{project_id}/"
    if shot["episode_id"] is None:
        path += "shots/{shot_id}/"
    else:
        path += "episodes/{episode_id}/shots/{shot_id}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        project_id=shot["project_id"],
        shot_id=shot["id"],
        episode_id=shot["episode_id"],
    )

def new_sequence(project, name, episode=None, client=default):
    """
    Create a sequence for given project and episode.

    Args:
        project (str / dict): The project dict or the project ID.
        episode (str / dict): The episode dict or the episode ID.
        name (str): The name of the sequence to create.

    Returns:
        Created sequence.
    """
    project = normalize_model_parameter(project)
    data = {"name": name}

    if episode is not None:
        episode = normalize_model_parameter(episode)
        data["episode_id"] = episode["id"]

    sequence = \
        get_sequence_by_name(project, name, episode=episode, client=client)
    if sequence is None:
        path = "data/projects/%s/sequences" % project["id"]
        return raw.post(path, data, client=client)
    else:
        return sequence


def new_shot(
    project,
    sequence,
    name,
    nb_frames=None,
    frame_in=None,
    frame_out=None,
    data={},
    client=default
):
    """
    Create a shot for given sequence and project. Add frame in and frame out
    parameters to shot extra data. Allow to set metadata too.

    Args:
        project (str / dict): The project dict or the project ID.
        sequence (str / dict): The sequence dict or the sequence ID.
        name (str): The name of the shot to create.
        frame_in (int):
        frame_out (int):
        data (dict): Free field to set metadata of any kind.

    Returns:
        Created shot.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)

    if frame_in is not None:
        data["frame_in"] = frame_in
    if frame_out is not None:
        data["frame_out"] = frame_out

    data = {"name": name, "data": data, "sequence_id": sequence["id"]}
    if nb_frames is not None:
        data["nb_frames"] = nb_frames

    shot = get_shot_by_name(sequence, name, client=client)
    if shot is None:
        path = "data/projects/%s/shots" % project["id"]
        return raw.post(path, data, client=client)
    else:
        return shot


def update_shot(shot, client=default):
    """
    Save given shot data into the API. Metadata are fully replaced by the ones
    set on given shot.

    Args:
        shot (dict): The shot dict to update.

    Returns:
        dict: Updated shot.
    """
    return raw.put("data/entities/%s" % shot["id"], shot, client=client)


def update_sequence(sequence, client=default):
    """
    Save given sequence data into the API. Metadata are fully replaced by the
    ones set on given sequence.

    Args:
        sequence (dict): The sequence dict to update.

    Returns:
        dict: Updated sequence.
    """
    return raw.put("data/entities/%s" % sequence["id"], sequence, client=client)


@cache
def get_asset_instances_for_shot(shot, client=default):
    """
    Return the list of asset instances linked to given shot.
    """
    return raw.get("data/shots/%s/asset-instances" % shot["id"], client=client)


def update_shot_data(shot, data={}, client=default):
    """
    Update the metadata for the provided shot. Keys that are not provided are
    not changed.

    Args:
        shot (dict / ID): The shot dict or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated shot.
    """
    shot = normalize_model_parameter(shot)
    current_shot = get_shot(shot["id"], client=client)
    updated_shot = {"id": current_shot["id"], "data": current_shot["data"]}
    updated_shot["data"].update(data)
    update_shot(updated_shot, client=client)


def update_sequence_data(sequence, data={}, client=default):
    """
    Update the metadata for the provided sequence. Keys that are not provided
    are not changed.

    Args:
        sequence (dict / ID): The sequence dicto or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated sequence.
    """
    sequence = normalize_model_parameter(sequence)
    current_sequence = get_sequence(sequence["id"], client=client)

    if not current_sequence.get('data'):
        current_sequence["data"] = {}

    updated_sequence = {
        "id": current_sequence["id"],
        "data": current_sequence["data"]
    }
    updated_sequence["data"].update(data)
    return update_sequence(updated_sequence, client)


def remove_shot(shot, force=False, client=default):
    """
    Remove given shot from database.

    Args:
        shot (dict / str): Shot to remove.
    """
    shot = normalize_model_parameter(shot)
    path = "data/shots/%s" % shot["id"]
    params = {}
    if force:
        params = {"force": "true"}
    return raw.delete(path, params, client=client)


def restore_shot(shot, client=default):
    """
    Restore given shot into database (uncancel it).

    Args:
        shot (dict / str): Shot to restore.
    """
    shot = normalize_model_parameter(shot)
    path = "data/shots/%s" % shot["id"]
    data = {"canceled": False}
    return raw.put(path, data, client=client)


def new_episode(project, name, client=default):
    """
    Create an episode for given project.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the episode to create.

    Returns:
        dict: Created episode.
    """
    project = normalize_model_parameter(project)
    data = {"name": name}
    episode = get_episode_by_name(project, name, client=client)
    if episode is None:
        return raw.post(
            "data/projects/%s/episodes" % project["id"],
            data,
            client=client
        )
    else:
        return episode


def update_episode(episode, client=default):
    """
    Save given episode data into the API. Metadata are fully replaced by the
    ones set on given episode.

    Args:
        episode (dict): The episode dict to update.

    Returns:
        dict: Updated episode.
    """
    return raw.put("data/entities/%s" % episode["id"], episode, client=client)


def update_episode_data(episode, data={}, client=default):
    """
    Update the metadata for the provided episode. Keys that are not provided
    are not changed.

    Args:
        episode (dict / ID): The episode dict or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated episode.
    """
    episode = normalize_model_parameter(episode)
    current_episode = get_sequence(episode["id"], client=client)
    updated_episode = {
        "id": current_episode["id"],
        "data": current_episode["data"]
    }
    updated_episode["data"].update(data)
    return update_episode(updated_episode, client=client)


def remove_episode(episode, force=False, client=default):
    """
    Remove given episode and related from database.

    Args:
        episode (dict / str): Episode to remove.
    """
    episode = normalize_model_parameter(episode)
    path = "data/episodes/%s" % episode["id"]
    params = {}
    if force:
        params = {"force": "true"}
    return raw.delete(path, params=params, client=client)


def remove_sequence(sequence, force=False, client=default):
    """
    Remove given sequence and related from database.

    Args:
        sequence (dict / str): Sequence to remove.
    """
    sequence = normalize_model_parameter(sequence)
    path = "data/sequences/%s" % sequence["id"]
    params = {}
    if force:
        params = {"force": "true"}
    return raw.delete(path, params=params, client=client)


@cache
def all_asset_instances_for_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Asset instances linked to given shot.
    """
    shot = normalize_model_parameter(shot)
    return raw.get("data/shots/%s/asset-instances" % shot["id"], client=client)


def add_asset_instance_to_shot(shot, asset_instance, client=default):
    """
    Link a new asset instance to given shot.

    Args:
        shot (str / dict): The shot dict or the shot ID.
        asset_instance (str / dict): The asset instance dict or ID.

    Returns:
        dict: Related shot.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    data = {"asset_instance_id": asset_instance["id"]}
    path = "data/shots/%s/asset-instances" % shot["id"]
    return raw.post(path, data, client=client)


def remove_asset_instance_from_shot(shot, asset_instance, client=default):
    """
    Remove link between an asset instance and given shot.

    Args:
        shot (str / dict): The shot dict or the shot ID.
        asset_instance (str / dict): The asset instance dict or ID.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    path = "data/shots/%s/asset-instances/%s" % (
        shot["id"],
        asset_instance["id"],
    )
    return raw.delete(path, client=client)
