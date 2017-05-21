import client
from sorting import sort_by_name


def all(project=None):
    if project is not None:
        shots = client.fetch_all("projects/%s/shots" % project["id"])
    else:
        shots = client.fetch_all("shots")

    return sort_by_name(shots)


def all_for_sequence(sequence):
    return sort_by_name(client.fetch_all("sequences/%s/shots" % sequence["id"]))


def all_sequences(project=None):

    if project is not None:
        sequences = client.fetch_all("projects/%s/sequences" % project["id"])
    else:
        sequences = client.fetch_all("sequences")

    return sort_by_name(sequences)


def all_episodes(project=None):

    if project is not None:
        episodes = client.fetch_all("projects/%s/episodes" % project["id"])
    else:
        episodes = client.fetch_all("episodes")

    return sort_by_name(episodes)


def all_sequences_for_episode(episode):
    sequences = client.fetch_all("episodes/%s/sequences" % episode["id"])
    return sort_by_name(sequences)


def task_types_for_shot(shot):
    task_types = client.fetch_all("shots/%s/task_types" % shot['id'])
    return sort_by_name(task_types)


def tasks_for_shot(shot):
    tasks = client.fetch_all("shots/%s/tasks" % shot['id'])
    return sort_by_name(tasks)
