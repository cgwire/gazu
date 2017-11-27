from . import client

from .sorting import sort_by_name


def all(project=None):
    """
    Retrieve all shots from database or for given project.
    """
    if project is not None:
        shots = client.fetch_all("projects/%s/shots" % project["id"])
    else:
        shots = client.fetch_all("shots/all")

    return sort_by_name(shots)


def all_for_sequence(sequence):
    """
    Retrieve all shots which are children from given sequence.
    """
    return sort_by_name(client.fetch_all("sequences/%s/shots" % sequence["id"]))


def all_sequences(project=None):
    """
    Retrieve all sequences from database or for given project.
    """
    if project is not None:
        sequences = client.fetch_all("projects/%s/sequences" % project["id"])
    else:
        sequences = client.fetch_all("sequences")

    return sort_by_name(sequences)


def all_sequences_for_episode(episode):
    """
    Retrieve all sequences which are children of given episode.
    """
    sequences = client.fetch_all("episodes/%s/sequences" % episode["id"])
    return sort_by_name(sequences)


def all_episodes(project=None):
    """
    Retrieve all episodes from database or for given project.
    """
    if project is not None:
        episodes = client.fetch_all("projects/%s/episodes" % project["id"])
    else:
        episodes = client.fetch_all("episodes")

    return sort_by_name(episodes)


def get_sequence_by_name(project, sequence_name):
    """
    Returns sequence corresponding to given name and project.
    """
    result = client.fetch_all("entities?project_id=%s&name=%s" % (
        project["id"],
        sequence_name
    ))
    return next(iter(result or []), None)


def get_shot(shot_id):
    """
    Return shot corresponding to given shot ID.
    """
    return client.fetch_one('entities', shot_id)


def get_shot_by_name(sequence, shot_name):
    """
    Returns shot corresponding to given sequence and name.
    """
    result = client.fetch_all("entities?parent_id=%s&name=%s" % (
        sequence["id"],
        shot_name
    ))
    return next(iter(result or []), None)


def all_scenes(project=None):
    """
    Retrieve all scenes.
    """
    if project is not None:
        scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    else:
        scenes = client.fetch_all("scenes")
    return sort_by_name(scenes)


def all_scenes_for_project(project):
    """
    Retrieve all scenes for given project.
    """
    scenes = client.fetch_all("projects/%s/scenes" % project["id"])
    return sort_by_name(scenes)


def all_scenes_for_sequence(sequence):
    """
    Retrieve all scenes which are children from given sequence.
    """
    return sort_by_name(
        client.fetch_all("sequences/%s/scenes" % sequence["id"])
    )


def get_scene(scene_id):
    """
    Return scene corresponding to given scene ID.
    """
    return client.fetch_one('scenes', scene_id)


def get_scene_by_name(sequence, scene_name):
    """
    Returns scene corresponding to given sequence and name.
    """
    result = client.fetch_all("entities?parent_id=%s&name=%s" % (
        sequence["id"],
        scene_name
    ))
    return next(iter(result or []), None)
