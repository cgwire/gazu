from deprecated import deprecated

from . import client

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter


@cache
def all_shots_for_project(project):
    """
    Retrieve all shots from database or for given project.
    """
    project = normalize_model_parameter(project)
    shots = client.fetch_all("projects/%s/shots" % project["id"])

    return sort_by_name(shots)


@cache
def all_shots_for_sequence(sequence):
    """
    Retrieve all shots which are children from given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return sort_by_name(client.fetch_all("sequences/%s/shots" % sequence["id"]))


@cache
def all_sequences(project=None):
    """
    Retrieve all sequences from database or for given project.
    """
    if project is not None:
        project = normalize_model_parameter(project)
        sequences = client.fetch_all("projects/%s/sequences" % project["id"])
    else:
        sequences = client.fetch_all("sequences")

    return sort_by_name(sequences)


@cache
def all_sequences_for_episode(episode):
    """
    Retrieve all sequences which are children of given episode.
    """
    episode = normalize_model_parameter(episode)
    sequences = client.fetch_all("episodes/%s/sequences" % episode["id"])
    return sort_by_name(sequences)


@cache
def all_episodes_for_project(project):
    """
    Retrieve all episodes from database or for given project.
    """
    project = normalize_model_parameter(project)
    episodes = client.fetch_all("projects/%s/episodes" % project["id"])
    return sort_by_name(episodes)


@cache
def get_episode(episode_id):
    """
    Return episode corresponding to given episode ID.
    """
    return client.fetch_one('episodes', episode_id)


@cache
def get_episode_by_name(project, episode_name):
    """
    Returns episode corresponding to given name and project.
    """
    project = normalize_model_parameter(project)
    return client.fetch_first("episodes?project_id=%s&name=%s" % (
        project["id"],
        episode_name
    ))


@cache
def get_episode_from_sequence(sequence):
    """
    Return episode which is parent of given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return get_episode(sequence["parent_id"])


@cache
def get_sequence(sequence_id):
    """
    Return sequence corresponding to given sequence ID.
    """
    return client.fetch_one('sequences', sequence_id)


@cache
def get_sequence_by_name(project, sequence_name, episode=None):
    """
    Returns sequence corresponding to given name and project.
    """
    project = normalize_model_parameter(project)
    if episode is None:
        path = "sequences?project_id=%s&name=%s" % (
            project["id"],
            sequence_name
        )
    else:
        episode = normalize_model_parameter(episode)
        path = "sequences?parent_id=%s&name=%s" % (episode["id"], sequence_name)
    return client.fetch_first(path)


@cache
def get_sequence_from_shot(shot):
    """
    Return sequence which is parent of given shot.
    """
    shot = normalize_model_parameter(shot)
    return get_sequence(shot["parent_id"])


@cache
def get_shot(shot_id):
    """
    Return shot corresponding to given shot ID.
    """
    return client.fetch_one('shots', shot_id)


@cache
def get_shot_by_name(sequence, shot_name):
    """
    Returns shot corresponding to given sequence and name.
    """
    sequence = normalize_model_parameter(sequence)
    return client.fetch_first("shots/all?parent_id=%s&name=%s" % (
        sequence["id"],
        shot_name
    ))


def new_sequence(
    project,
    episode,
    name
):
    """
    Create a sequence for given episode.
    """
    project = normalize_model_parameter(project)
    episode = normalize_model_parameter(episode)
    data = {
        "name": name,
        "episode_id": episode["id"]
    }

    sequence = get_sequence_by_name(project, name, episode=episode)
    if sequence is None:
        return client.post('data/projects/%s/sequences' % project["id"], data)
    else:
        return sequence


def new_shot(
    project,
    sequence,
    name,
    frame_in=None,
    frame_out=None,
    data={}
):
    """
    Create a shot for given sequence. Add frame in and frame out parameters to
    extra data.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)

    if frame_in is not None:
        data["frame_in"] = frame_in
    if frame_out is not None:
        data["frame_out"] = frame_out

    data = {
        "name": name,
        "data": data,
        "sequence_id": sequence["id"]
    }

    shot = get_shot_by_name(sequence, name)
    if shot is None:
        return client.post("data/projects/%s/shots" % project["id"], data)
    else:
        return shot


def update_shot(shot):
    """
    Save given shot data into the API.
    """
    return client.put('data/entities/%s' % shot["id"], shot)


def update_shot_data(shot, data={}):
    """
    Update the data for the provided shot.
    Keys not provided are not updated while update_shot() delete them
    """
    shot = normalize_model_parameter(shot)
    current_shot = get_shot(shot["id"])
    updated_shot = {'id': current_shot['id'], 'data': current_shot['data']}
    updated_shot['data'].update(data)
    update_shot(updated_shot)


def new_episode(project, name):
    """
    Create an episode for given project.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name
    }
    episode = get_episode_by_name(project, name)
    if episode is None:
        return client.post('data/projects/%s/episodes' % project["id"], data)
    else:
        return episode


@cache
def all_asset_instances_for_shot(shot):
    """
    Return the list of asset instances listed in a shot.
    """
    shot = normalize_model_parameter(shot)
    return client.get("data/shots/%s/asset-instances" % shot["id"])


@cache
def get_asset_instances_for_shot(shot):
    """
    Return the list of asset instances linked to given shot.
    """
    shot = normalize_model_parameter(shot)
    return client.get("data/shots/%s/asset-instances" % shot["id"])


def add_asset_instance_to_shot(shot, asset_instance):
    """
    Link a new asset instance to given shot.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    data = {
        "asset_instance_id": asset_instance["id"]
    }
    return client.post("data/shots/%s/asset-instances" % shot["id"], data)


def remove_asset_instance_from_shot(shot, asset_instance):
    """
    Link a new asset instance to given shot.
    """
    shot = normalize_model_parameter(shot)
    asset_instance = normalize_model_parameter(asset_instance)
    path = "data/shots/%s/asset-instances/%s" % (
        shot["id"],
        asset_instance["id"]
    )
    return client.delete(path)


def update_casting(shot, casting):
    """
    Change casting of given shot with given casting (list of asset ids displayed
    into the shot).
    """
    shot = normalize_model_parameter(shot)
    return client.put("data/shots/%s/casting" % shot["id"], casting)


@deprecated
def all(project=None):
    return all_shots_for_project(project)


@deprecated
def all_for_sequence(project=None):
    return all_shots_for_sequence(project)
