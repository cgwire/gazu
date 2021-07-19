import datetime

from . import client as raw
from .sorting import sort_by_name
from .helpers import normalize_model_parameter

from .cache import cache

default = raw.default_client


@cache
def all_open_projects(client=default):
    """
    Returns:
        list: Projects for which the user is part of the team. Admins see all
        projects
    """
    projects = raw.fetch_all("user/projects/open", client=client)
    return sort_by_name(projects)


@cache
def all_asset_types_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Asset types for which the user has a task assigned for given
        project.
    """
    project = normalize_model_parameter(project)
    path = "user/projects/%s/asset-types" % project["id"]
    asset_types = raw.fetch_all(path, client=client)
    return sort_by_name(asset_types)


@cache
def all_assets_for_asset_type_and_project(project, asset_type, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        asset_type (str / dict): The asset type dict or ID.

    Returns:
        list: Assets for given project and asset type and for which the user has
        a task assigned.
    """
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    path = "user/projects/%s/asset-types/%s/assets" % (
        project["id"],
        asset_type["id"],
    )
    assets = raw.fetch_all(path, client=client)
    return sort_by_name(assets)


@cache
def all_tasks_for_asset(asset, client=default):
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Tasks for given asset and current user.
    """
    asset = normalize_model_parameter(asset)
    path = "user/assets/%s/tasks" % asset["id"]
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Tasks assigned to current user for given shot.
    """
    shot = normalize_model_parameter(shot)
    path = "user/shots/%s/tasks" % shot["id"]
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_scene(scene, client=default):
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: Tasks assigned to current user for given scene.
    """
    scene = normalize_model_parameter(scene)
    path = "user/scene/%s/tasks" % scene["id"]
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_sequence(sequence, client=default):
    """
    Return the list of tasks for given asset and current user.
    """
    sequence = normalize_model_parameter(sequence)
    path = "user/sequences/%s/tasks" % sequence["id"]
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_task_types_for_asset(asset, client=default):
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Task Types of tasks assigned to current user for given asset.
    """
    asset = normalize_model_parameter(asset)
    path = "user/assets/%s/task-types" % asset["id"]
    tasks = raw.fetch_all(path, client=client)
    return sort_by_name(tasks)


@cache
def all_task_types_for_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Task Types of tasks assigned to current user for given shot.
    """
    shot = normalize_model_parameter(shot)
    path = "user/shots/%s/task-types" % shot["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(scene, client=default):
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: Task Types of tasks assigned to current user for given scene.
    """
    scene = normalize_model_parameter(scene)
    path = "user/scenes/%s/task-types" % scene["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_sequence(sequence, client=default):
    """
    return the list of task_tyes for given asset and current user.
    """
    sequence = normalize_model_parameter(sequence)
    path = "user/sequences/%s/task-types" % sequence["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_sequences_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Sequences for which user has tasks assigned for given project.
    """
    project = normalize_model_parameter(project)
    path = "user/projects/%s/sequences" % project["id"]
    sequences = raw.fetch_all(path, client=client)
    return sort_by_name(sequences)


@cache
def all_episodes_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Episodes for which user has tasks assigned for given project.
    """
    path = "user/projects/%s/episodes" % project["id"]
    asset_types = raw.fetch_all(path, client=client)
    return sort_by_name(asset_types)


@cache
def all_shots_for_sequence(sequence, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Shots for which user has tasks assigned for given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    path = "user/sequences/%s/shots" % sequence["id"]
    shots = raw.fetch_all(path, client=client)
    return sort_by_name(shots)


@cache
def all_scenes_for_sequence(sequence, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Scenes for which user has tasks assigned for given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    path = "user/sequences/%s/scenes" % sequence["id"]
    scenes = raw.fetch_all(path, client=client)
    return sort_by_name(scenes)


@cache
def all_tasks_to_do(client=default):
    """
    Returns:
        list: Tasks assigned to current user which are not complete.
    """
    return raw.fetch_all("user/tasks", client=client)


def log_desktop_session_log_in(client=default):
    """
    Add a log entry to mention that the user logged in his computer.

    Returns:
        dict: Desktop session log entry.
    """
    path = "/data/user/desktop-login-logs"
    data = {"date": datetime.datetime.now().isoformat()}
    return raw.post(path, data, client=client)
