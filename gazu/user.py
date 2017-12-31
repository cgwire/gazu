from . import client
from .sorting import sort_by_name

from .cache import cache


@cache
def all_open_projects():
    """
    Return the list of projects for which the user has a task.
    """
    projects = client.fetch_all("user/projects/open")
    return sort_by_name(projects)


@cache
def all_asset_types_for_project(project):
    """
    Return the list of asset types for which the user has a task.
    """
    path = "user/projects/%s/asset-types" % project["id"]
    asset_types = client.fetch_all(path)
    return sort_by_name(asset_types)


@cache
def all_assets_for_asset_type_and_project(project, asset_type):
    """
    Return the list of assets for given project and asset_type and for which
    the user has a task.
    """
    path = "user/projects/%s/asset-types/%s/assets" % (
        project["id"],
        asset_type["id"]
    )
    assets = client.fetch_all(path)
    return sort_by_name(assets)


@cache
def all_tasks_for_asset(asset):
    """
    Return the list of tasks for given asset and current user.
    """
    path = "user/assets/%s/tasks" % asset["id"]
    tasks = client.fetch_all(path)
    return sort_by_name(tasks)


@cache
def all_tasks_for_shot(shot):
    """
    Return the list of tasks for given asset and current user.
    """
    path = "user/shots/%s/tasks" % shot["id"]
    tasks = client.fetch_all(path)
    return sort_by_name(tasks)


@cache
def all_tasks_for_scene(scene):
    """
    Return the list of tasks for given asset and current user.
    """
    path = "user/scene/%s/tasks" % scene["id"]
    tasks = client.fetch_all(path)
    return sort_by_name(tasks)


@cache
def all_task_types_for_asset(asset):
    """
    Return the list of task types for given asset and current user.
    """
    path = "user/assets/%s/task-types" % asset["id"]
    tasks = client.fetch_all(path)
    return sort_by_name(tasks)


@cache
def all_task_types_for_shot(shot):
    """
    return the list of task_tyes for given asset and current user.
    """
    path = "user/shots/%s/task-types" % shot["id"]
    task_types = client.fetch_all(path)
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(scene):
    """
    return the list of task_tyes for given asset and current user.
    """
    path = "user/scenes/%s/task-types" % scene["id"]
    task_types = client.fetch_all(path)
    return sort_by_name(task_types)


@cache
def all_sequences_for_project(project):
    """
    Return the list of sequences for given project and current user.
    """
    path = "user/projects/%s/sequences" % project["id"]
    sequences = client.fetch_all(path)
    return sort_by_name(sequences)


@cache
def all_shots_for_sequence(sequence):
    """
    Return the list of shots for given sequence and current user.
    """
    path = "user/sequences/%s/shots" % sequence["id"]
    shots = client.fetch_all(path)
    return sort_by_name(shots)


@cache
def all_scenes_for_sequence(sequence):
    """
    Return the list of scenes for given sequence and current user.
    """
    path = "user/sequences/%s/scenes" % sequence["id"]
    scenes = client.fetch_all(path)
    return sort_by_name(scenes)
