from . import client

from .sorting import sort_by_name


def all(project=None):
    """
    Retrieve all shots from database or for given project.
    """
    if project is not None:
        shots = client.fetch_all("projects/%s/shots" % project["id"])
    else:
        shots = client.fetch_all("shots")

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


def get_shot(shot_id):
    """
    Return shot corresponding to given shot ID.
    """
    return client.fetch_one('entities', shot_id)
