from . import client

from .sorting import sort_by_name

from .cache import cache


@cache
def all(project=None):
    """
    Retrieve all shots from database or for given project.
    """
    if project is not None:
        shots = client.fetch_all("projects/%s/shots" % project["id"])
    else:
        shots = client.fetch_all("shots/all")

    return sort_by_name(shots)


@cache
def all_for_sequence(sequence):
    """
    Retrieve all shots which are children from given sequence.
    """
    return sort_by_name(client.fetch_all("sequences/%s/shots" % sequence["id"]))


@cache
def all_sequences(project=None):
    """
    Retrieve all sequences from database or for given project.
    """
    if project is not None:
        sequences = client.fetch_all("projects/%s/sequences" % project["id"])
    else:
        sequences = client.fetch_all("sequences")

    return sort_by_name(sequences)


@cache
def all_sequences_for_episode(episode):
    """
    Retrieve all sequences which are children of given episode.
    """
    sequences = client.fetch_all("episodes/%s/sequences" % episode["id"])
    return sort_by_name(sequences)


@cache
def all_episodes(project=None):
    """
    Retrieve all episodes from database or for given project.
    """
    if project is not None:
        episodes = client.fetch_all("projects/%s/episodes" % project["id"])
    else:
        episodes = client.fetch_all("episodes")

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
    result = client.fetch_all("entities?project_id=%s&name=%s" % (
        project["id"],
        episode_name
    ))
    return next(iter(result or []), None)


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
    Optionnaly you can specify an episode
    """
    result = client.fetch_all("entities?project_id=%s&name=%s%s" % (
        project["id"],
        sequence_name,
        "&parent_id=%s" % episode['id'] if episode else ""
    ))
    return next(iter(result or []), None)


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
    result = client.fetch_all("entities?parent_id=%s&name=%s" % (
        sequence["id"],
        shot_name
    ))
    return next(iter(result or []), None)


def new_episode(project, name):
    """
    Create an episode for given project.
    """
    shot = {
        "name": name
    }
    return client.post('data/projects/%s/episodes' % project["id"], shot)


def new_sequence(
    project,
    episode,
    name
):
    """
    Create a sequence for given episode.
    """
    sequence = {
        "name": name,
        "episode_id": episode["id"]
    }
    return client.post('data/projects/%s/sequences' % project["id"], sequence)


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
    if frame_in is not None:
        data["frame_in"] = frame_in
    if frame_out is not None:
        data["frame_out"] = frame_out

    shot = {
        "name": name,
        "data": data,
        "sequence_id": sequence["id"]
    }

    return client.post('data/projects/%s/shots' % project["id"], shot)


def update_shot(shot):
    """
    Save given shot data into the API.
    """
    return client.put('data/entities/%s' % shot["id"], shot)


def new_scene(
    project,
    sequence,
    name
):
    """
    Create a scene for given sequence.
    """
    shot = {
        "name": name,
        "sequence_id": sequence["id"]
    }
    return client.post('data/projects/%s/scenes' % project["id"], shot)


@cache
def all_scenes(project=None):
    """
    Retrieve all scenes.
    """
    if project is not None:
        scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    else:
        scenes = client.fetch_all("scenes")
    return sort_by_name(scenes)


@cache
def all_scenes_for_project(project):
    """
    Retrieve all scenes for given project.
    """
    scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    return sort_by_name(scenes)


@cache
def all_scenes_for_sequence(sequence):
    """
    Retrieve all scenes which are children from given sequence.
    """
    return sort_by_name(
        client.fetch_all("sequences/%s/scenes" % sequence["id"])
    )


@cache
def get_scene(scene_id):
    """
    Return scene corresponding to given scene ID.
    """
    return client.fetch_one('scenes', scene_id)


@cache
def get_scene_by_name(sequence, scene_name):
    """
    Returns scene corresponding to given sequence and name.
    """
    result = client.fetch_all("entities?parent_id=%s&name=%s" % (
        sequence["id"],
        scene_name
    ))
    return next(iter(result or []), None)


@cache
def new_asset_instance(shot, asset, description=""):
    """
    Creates a new asset instance on given shot. The instance number is
    automatically generated (increment highest number).
    """
    data = {
        "asset_id": asset["id"],
        "description": description
    }
    result = client.post("data/shots/%s/asset-instances" % shot["id"], data)
    return result
