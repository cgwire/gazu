from __future__ import annotations

import json
import os
import string

import requests

from gazu.exception import (
    TaskStatusNotFoundException,
    TaskMustBeADictException,
)

from . import client as raw
from .client import KitsuClient
from .sorting import sort_by_name
from .helpers import (
    download_file,
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

from .cache import cache

default = raw.default_client


def _all_tasks_for_entity(
    entity: str | dict,
    collection: str,
    suffix: str = "tasks",
    relations: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Get the tasks at ``<collection>/<entity id>/<suffix>`` and sort them.

    All the ``all_*tasks_for_*`` functions use this function.
    """
    entity = normalize_model_parameter(entity)
    params = {"relations": True} if relations else {}
    tasks = raw.fetch_all(
        f"{collection}/{entity['id']}/{suffix}", params, client=client
    )
    return sort_by_name(tasks)


def _open_comment_files(comments: list[dict]) -> tuple[dict, list]:
    """
    Open the attachment and preview files of a list of comments.

    Returns:
        tuple: The multipart ``files`` dict, with the JSON ``comments`` part,
        and the list of open files. The caller must close these files.
    """
    files = {}
    opened_files = []
    try:
        for x, comment in enumerate(comments):
            for kind in ("attachment_files", "preview_files"):
                for y, file_path in enumerate(comment.get(kind) or []):
                    f = open(file_path, "rb")
                    opened_files.append(f)
                    files[f"{kind[:-1]}-{x}-{y}"] = f
    except Exception:
        for f in opened_files:
            f.close()
        raise
    files["comments"] = (None, json.dumps(comments), "application/json")
    return files, opened_files


@cache
def all_task_statuses(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The task statuses in the database.
    """
    task_statuses = raw.fetch_all("task-status", client=client)
    return sort_by_name(task_statuses)


@cache
def all_task_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The task types in the database.
    """
    task_types = raw.fetch_all("task-types", client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The task types of the given project.
    """
    project = normalize_model_parameter(project)
    task_types = raw.fetch_all(
        f"projects/{project['id']}/task-types", client=client
    )
    return sort_by_name(task_types)


@cache
def all_task_statuses_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The task statuses of the given project.
    """
    project = normalize_model_parameter(project)
    task_statuses = raw.fetch_all(
        f"projects/{project['id']}/settings/task-status", client=client
    )
    return sort_by_name(task_statuses)


@cache
def all_tasks_for_shot(
    shot: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks of the given shot.
    """
    return _all_tasks_for_entity(
        shot, "shots", relations=relations, client=client
    )


@cache
def all_tasks_for_concept(
    concept: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks of the given concept.
    """
    return _all_tasks_for_entity(
        concept, "concepts", relations=relations, client=client
    )


@cache
def all_tasks_for_edit(
    edit: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        edit (str / dict): The edit dict or the edit ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks of the given edit.
    """
    return _all_tasks_for_entity(
        edit, "edits", relations=relations, client=client
    )


@cache
def all_tasks_for_sequence(
    sequence: str | dict,
    relations: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks of the given sequence.
    """
    return _all_tasks_for_entity(
        sequence, "sequences", relations=relations, client=client
    )


@cache
def all_tasks_for_scene(
    scene: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks of the given scene.
    """
    return _all_tasks_for_entity(
        scene, "scenes", relations=relations, client=client
    )


@cache
def all_tasks_for_asset(
    asset: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks directly linked to the given asset.
    """
    return _all_tasks_for_entity(
        asset, "assets", relations=relations, client=client
    )


@cache
def all_tasks_for_episode(
    episode: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Return the tasks directly linked to the given episode.

    Args:
        episode (str / dict): The episode dict or the episode ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks.
    """
    return _all_tasks_for_entity(
        episode, "episodes", relations=relations, client=client
    )


@cache
def all_shot_tasks_for_sequence(
    sequence: str | dict,
    relations: bool = False,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Return the tasks directly linked to all shots of the given sequence.

    Args:
        sequence (str / dict): The sequence dict or the sequence ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks.
    """
    return _all_tasks_for_entity(
        sequence, "sequences", "shot-tasks", relations, client
    )


@cache
def all_shot_tasks_for_episode(
    episode: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Return the tasks directly linked to all shots of the given episode.

    Args:
        episode (str / dict): The episode dict or the episode ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks.
    """
    return _all_tasks_for_entity(
        episode, "episodes", "shot-tasks", relations, client
    )


@cache
def all_assets_tasks_for_episode(
    episode: str | dict, relations: bool = False, client: KitsuClient = default
) -> list[dict]:
    """
    Return the tasks directly linked to all assets of the given episode.

    Args:
        episode (str / dict): The episode dict or the episode ID.
        relations (bool): If True, also get the relations of each task.

    Returns:
        list: The tasks.
    """
    return _all_tasks_for_entity(
        episode, "episodes", "asset-tasks", relations, client
    )


@cache
def all_tasks_for_task_status(
    project: str | dict,
    task_type: str | dict,
    task_status: str | dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        task_type (str / dict): The task type dict or ID.
        task_status (str / dict): The task status dict or ID.

    Returns:
        list: The tasks with the given status, project and task type.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    task_status = normalize_model_parameter(task_status)
    return raw.fetch_all(
        "tasks",
        {
            "project_id": project["id"],
            "task_type_id": task_type["id"],
            "task_status_id": task_status["id"],
        },
        client=client,
    )


@cache
def all_tasks_for_task_type(
    project: str | dict,
    task_type: str | dict,
    episode: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        task_type (str / dict): The task type dict or ID.
        episode (str / dict): The optional episode dict or ID.

    Returns:
        list: The tasks of the given project and task type.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    params = {
        "project_id": project["id"],
        "task_type_id": task_type["id"],
    }
    if episode is not None:
        episode = normalize_model_parameter(episode)
        params["episode_id"] = episode["id"]
    return raw.fetch_all("tasks", params, client=client)


@cache
def all_task_types_for_shot(
    shot: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: The task types of the tasks of the given shot.
    """
    shot = normalize_model_parameter(shot)
    path = f"shots/{shot['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_concept(
    concept: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns:
        list: The task types of the tasks of the given concept.
    """
    concept = normalize_model_parameter(concept)
    path = f"concepts/{concept['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_asset(
    asset: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: The task types of the tasks of the given asset.
    """
    asset = normalize_model_parameter(asset)
    task_types = raw.fetch_all(
        f"assets/{asset['id']}/task-types", client=client
    )
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(
    scene: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: The task types of the tasks of the given scene.
    """
    scene = normalize_model_parameter(scene)
    path = f"scenes/{scene['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_sequence(
    sequence: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: The task types of the tasks directly linked to the sequence.
    """
    sequence = normalize_model_parameter(sequence)
    path = f"sequences/{sequence['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_episode(
    episode: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: The task types of the tasks directly linked to the given episode.
    """
    episode = normalize_model_parameter(episode)
    path = f"episodes/{episode['id']}/task-types"
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_tasks_for_entity_and_task_type(
    entity: str | dict, task_type: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.
        task_type (str / dict): The task type dict or ID.

    Returns:
        list: The tasks of the given entity and task type.
    """
    entity = normalize_model_parameter(entity)
    task_type = normalize_model_parameter(task_type)
    task_type_id = task_type["id"]
    entity_id = entity["id"]
    path = f"entities/{entity_id}/task-types/{task_type_id}/tasks"
    return raw.fetch_all(path, client=client)


@cache
def all_tasks_for_person(
    person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        person (str / dict): The person dict or the person ID.

    Returns:
        list: The tasks of the given person that are not done (only for open
        projects).
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all(f"persons/{person['id']}/tasks", client=client)


@cache
def all_done_tasks_for_person(
    person: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        person (str / dict): The person dict or the person ID.

    Returns:
        list: The tasks of the given person that are done (only for open
        projects).
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all(f"persons/{person['id']}/done-tasks", client=client)


@cache
def get_task_by_entity(
    entity: str | dict,
    task_type: str | dict,
    name: str = "main",
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.
        task_type (str / dict): The task type dict or ID.
        name (str): The name of the task.

    Returns:
        dict: The task with the given entity, task type and name, or None if
        no task matches.
    """
    entity = normalize_model_parameter(entity)
    task_type = normalize_model_parameter(task_type)
    return raw.fetch_first(
        "tasks",
        {
            "name": name,
            "task_type_id": task_type["id"],
            "entity_id": entity["id"],
        },
        client=client,
    )


@cache
def get_task_type(task_type_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        task_type_id (str): The ID of the task type.

    Returns:
        dict: The task type with the given ID.
    """
    return raw.fetch_one("task-types", task_type_id, client=client)


@cache
def get_task_type_by_name(
    task_type_name: str,
    for_entity: str | None = None,
    department: str | dict | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        task_type_name (str): The name of the task type.
        for_entity (str): The entity type of the task type.
        department (str / dict): The department of the task type.

    Returns:
        dict: The task type with the given name, or None if no task type
        matches.
    """
    params = {"name": task_type_name}
    if for_entity is not None:
        params["for_entity"] = for_entity
    if department is not None:
        params["department_id"] = normalize_model_parameter(department)["id"]
    return raw.fetch_first("task-types", params, client=client)


@cache
def get_task_type_by_short_name(
    task_type_short_name: str,
    for_entity: str | None = None,
    department: str | dict | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        task_type_short_name (str): The short name of the task type.
        for_entity (str): The entity type of the task type.
        department (str / dict): The department of the task type.

    Returns:
        dict: The task type with the given short name, or None if no task
        type matches.
    """
    params = {"short_name": task_type_short_name}
    if for_entity is not None:
        params["for_entity"] = for_entity
    if department is not None:
        params["department_id"] = normalize_model_parameter(department)["id"]
    return raw.fetch_first("task-types", params, client=client)


@cache
def get_default_task_status(client: KitsuClient = default) -> dict | None:
    """
    Returns:
        dict: The task status with the `is_default` flag, or None if no status
        has this flag.
    """
    return raw.fetch_first(
        "task-status", params={"is_default": True}, client=client
    )


@cache
def get_task_status(
    task_status_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        task_status_id (str): The ID of the task status.

    Returns:
        dict: The task status with the given ID.
    """
    return raw.fetch_one("task-status", task_status_id, client=client)


@cache
def get_task_status_by_name(
    name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        name (str): The name of the task status.

    Returns:
        dict: The task status with the given name, or None if no status
        matches.
    """
    return raw.fetch_first("task-status", {"name": name}, client=client)


@cache
def get_task_status_by_short_name(
    task_status_short_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        task_status_short_name (str): The short name of the task status.

    Returns:
        dict: The task status with the given short name, or None if no status
        matches.
    """
    return raw.fetch_first(
        "task-status", {"short_name": task_status_short_name}, client=client
    )


def remove_task_type(
    task_type: str | dict,
    force: bool = False,
    client: KitsuClient = default,
) -> str:
    """
    Remove the given task type from the database.

    Args:
        task_type (str / dict): The task type dict or ID.
        force (bool): If True, remove the task type when tasks are linked to
            it. If the task type is linked to a project, first use
            gazu.project.remove_task_type to remove this link.

    Returns:
        str: The response of the API.
    """
    task_type = normalize_model_parameter(task_type)
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(
        f"data/task-types/{task_type['id']}",
        params,
        client=client,
    )


def remove_task_status(
    task_status: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given task status from the database.

    This function always sends the ``force`` parameter to the API.

    Args:
        task_status (str / dict): The task status dict or ID.

    Returns:
        str: The response of the API.
    """
    task_status = normalize_model_parameter(task_status)
    return raw.delete(
        f"data/task-status/{task_status['id']}",
        {"force": True},
        client=client,
    )


def update_task_type(task_type: dict, client: KitsuClient = default) -> dict:
    """
    Update the given task type in the API.

    Args:
        task_type (dict): The task type dict to update.

    Returns:
        dict: The updated task type.
    """
    return raw.put(
        f"data/task-types/{task_type['id']}",
        task_type,
        client=client,
    )


def update_task_status(
    task_status: dict, client: KitsuClient = default
) -> dict:
    """
    Update the given task status in the API.

    Args:
        task_status (dict): The task status dict to update.

    Returns:
        dict: The updated task status.
    """
    return raw.put(
        f"data/task-status/{task_status['id']}",
        task_status,
        client=client,
    )


@cache
def get_task(task_id: str | dict, client: KitsuClient = default) -> dict:
    """
    Args:
        task_id (str / dict): The task dict or the task ID.

    Returns:
        dict: The full task with the given ID.
    """
    task_id = normalize_model_parameter(task_id)
    return raw.get(f"data/tasks/{task_id['id']}/full", client=client)


def new_task(
    entity: str | dict,
    task_type: str | dict,
    name: str = "main",
    task_status: str | dict | None = None,
    assigner: str | dict | None = None,
    assignees: list[str | dict] | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a task for the given entity and task type.

    Args:
        entity (str / dict): The entity dict or ID of the task.
        task_type (str / dict): The task type dict or ID of the task.
        name (str): The name of the task ("main" by default).
        task_status (str / dict): The task status to set. By default, this function
            uses the default task status.
        assigner (dict): The person who assigns the task.
        assignees (list): The persons assigned to the task.

    Returns:
        dict: The created task. A task with the same entity, task type and name
        can exist. In this condition, this function returns this task. It does
        not apply the given task status and assignees.
    """
    entity = normalize_model_parameter(entity)
    if "project_id" not in entity:
        entity = raw.fetch_one("entities", entity["id"], client=client)
    task_type = normalize_model_parameter(task_type)
    if task_status is None:
        task_status = get_default_task_status(client=client)
    task_status = normalize_model_parameter(task_status)

    data = {
        "project_id": entity["project_id"],
        "entity_id": entity["id"],
        "task_type_id": task_type["id"],
        "task_status_id": task_status["id"],
        "assignees": normalize_list_of_models_for_links(
            assignees if assignees is not None else []
        ),
        "name": name,
    }

    if assigner is not None:
        data["assigner_id"] = normalize_model_parameter(assigner)["id"]

    task = get_task_by_entity(entity, task_type, name, client=client)
    if task is None:
        task = raw.post("data/tasks", data, client=client)
    return task


def remove_task(task: str | dict, client: KitsuClient = default) -> str:
    """
    Remove the given task from the database.

    This function always sends the ``force`` parameter to the API.

    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        str: The response of the API.
    """
    task = normalize_model_parameter(task)
    return raw.delete(
        f"data/tasks/{task['id']}", {"force": True}, client=client
    )


def start_task(
    task: str | dict,
    started_task_status: str | dict | None = None,
    person: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a comment that sets the task status to started_task_status.

    The default status is WIP. The real start date of the task becomes the
    current date.

    Args:
        task (str / dict): The task dict or the task ID.
        started_task_status (str / dict): The task status dict or ID.
        person (str / dict): The person dict or the person ID.

    Returns:
        dict: The created comment.

    Raises:
        TaskStatusNotFoundException: If you give no status and the "wip"
            status does not exist.
    """
    if started_task_status is None:
        started_task_status = get_task_status_by_short_name(
            "wip", client=client
        )
        if started_task_status is None:
            raise TaskStatusNotFoundException(
                (
                    "started_task_status is None : 'wip' task status is "
                    "non-existent. You have to create it or to set an other "
                    "task status for started_task_status in the parameters "
                    "of the function."
                )
            )

    return add_comment(task, started_task_status, person=person, client=client)


@cache
def get_time_spent(
    task: str | dict, date: str | None = None, client: KitsuClient = default
) -> dict:
    """
    Get the time that CG artists spent on a task, on the given date if given.

    Durations are in minutes. The date format is YYYY-MM-DD.

    Args:
        task (str / dict): The task dict or the task ID.
        date (str): The optional date of the time spent.

    Returns:
        dict: The keys are person IDs and the values are lists of time spents.
        The "total" key contains the total duration.
    """
    task = normalize_model_parameter(task)
    path = f"actions/tasks/{task['id']}/time-spents"
    if date is not None:
        path += f"/{date}"
    return raw.get(path, client=client)


def set_time_spent(
    task: str | dict,
    person: str | dict,
    date: str,
    duration: int,
    client: KitsuClient = default,
) -> dict:
    """
    Set the time that a CG artist spent on the given task on the given date.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person who spent the time on the task.
        date (str): The date ("YYYY-MM-DD") of the time spent.
        duration (int): The duration of the time spent, in minutes.

    Returns:
        dict: The created time spent entry.
    """
    task = normalize_model_parameter(task)
    person = normalize_model_parameter(person)
    path = (
        f"actions/tasks/{task['id']}/time-spents/{date}/persons/{person['id']}"
    )
    return raw.post(path, {"duration": duration}, client=client)


def add_time_spent(
    task: str | dict,
    person: str | dict,
    date: str,
    duration: int,
    client: KitsuClient = default,
) -> dict:
    """
    Add the given duration to the current duration of a task, person and date.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person who spent the time on the task.
        date (str): The date ("YYYY-MM-DD") of the time spent.
        duration (int): The duration to add, in minutes.

    Returns:
        dict: The updated time spent entry.
    """
    task = normalize_model_parameter(task)
    person = normalize_model_parameter(person)
    path = f"actions/tasks/{task['id']}/time-spents/{date}/persons/{person['id']}/add"
    return raw.post(path, {"duration": duration}, client=client)


def add_comment(
    task: str | dict,
    task_status: str | dict,
    comment: str = "",
    person: str | dict | None = None,
    checklist: list[dict] | None = None,
    attachments: list[str] | None = None,
    created_at: str | None = None,
    links: list[str] | None = None,
    for_client: bool = False,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict:
    """
    Add a comment to the given task.

    Each comment must have a task status, because a new comment can change the
    task status. The comment text can be empty.

    Args:
        task (str / dict): The task dict or the task ID.
        task_status (str / dict): The task status dict or ID.
        comment (str): The comment text.
        person (str / dict): The comment author.
        checklist (list): The comment checklist. For example:
            [{"text": "Item 1", "checked": false}]
        attachments (list[file_path]): The file paths of the attachments.
        created_at (str): The comment date.
        links (list): The URL links to add to the comment.
        for_client (bool): If True, clients can see the comment. Only a
            manager can do this.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload of the attachments.

    Returns:
        dict: The created comment.
    """
    if checklist is None:
        checklist = []
    if attachments is None:
        attachments = []
    if links is None:
        links = []
    task = normalize_model_parameter(task)
    task_status = normalize_model_parameter(task_status)
    data = {
        "task_status_id": task_status["id"],
        "comment": comment,
        "checklist": checklist,
        "links": links,
        "for_client": for_client,
    }

    if person is not None:
        person = normalize_model_parameter(person)
        data["person_id"] = person["id"]

    if created_at is not None:
        data["created_at"] = created_at

    if len(attachments) == 0:
        return raw.post(
            f"actions/tasks/{task['id']}/comment", data, client=client
        )
    else:
        attachments = list(attachments)
        attachment = attachments.pop()
        # Multipart form parts are plain strings. Zou parses "for_client"
        # with bool(str), so "False" would wrongly become True -- drop the
        # field when False (the server defaults it to False). List fields
        # must be JSON-encoded so Zou's json.loads() can decode them.
        if not for_client:
            del data["for_client"]
        data["checklist"] = json.dumps(checklist)
        data["links"] = json.dumps(links)
        return raw.upload(
            f"actions/tasks/{task['id']}/comment",
            attachment,
            data=data,
            extra_files=attachments,
            client=client,
            progress_callback=progress_callback,
        )


def add_attachment_files_to_comment(
    task: str | dict,
    comment: str | dict,
    attachments: str | list[str] = None,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict:
    """
    Add attachment files to the given comment.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment dict or the comment ID.
        attachments (list / str): The path or the paths of the attachments.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: The added attachment files.

    Raises:
        ValueError: If the list of attachments is empty.
    """
    if attachments is None:
        attachments = []
    if isinstance(attachments, str):
        attachments = [attachments]
    if len(attachments) == 0:
        raise ValueError("The attachments list is empty")
    attachments = list(attachments)
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    attachment = attachments.pop()
    return raw.upload(
        f"actions/tasks/{task['id']}/comments/{comment['id']}/add-attachment",
        attachment,
        extra_files=attachments,
        client=client,
        progress_callback=progress_callback,
    )


def get_comment(comment_id: str, client: KitsuClient = default) -> dict:
    """
    Get a comment.

    Args:
        comment_id (str): The comment ID.

    Returns:
        dict: The comment with the given ID.
    """
    return raw.fetch_one("comments", comment_id, client=client)


def remove_comment(comment: str | dict, client: KitsuClient = default) -> str:
    """
    Remove the given comment and its related data from the database.

    The related data are previews, news and notifications.

    Args:
        comment (str / dict): The comment dict or the comment ID.

    Returns:
        str: The response of the API.
    """
    comment = normalize_model_parameter(comment)
    return raw.delete(f"data/comments/{comment['id']}", client=client)


def create_preview(
    task: str | dict,
    comment: str | dict,
    revision: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a preview in the given comment.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        revision (int): The revision number.

    Returns:
        dict: The created preview file.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    path = f"actions/tasks/{task['id']}/comments/{comment['id']}/add-preview"
    data = {}
    if revision is not None:
        data["revision"] = revision
    return raw.post(path, data, client=client)


def create_extra_preview(
    task: str | dict,
    comment: str | dict,
    preview_file: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Create an extra preview file for a comment revision.

    The new preview file has the same revision as the given preview file.
    After this operation, use upload_preview_file to upload the file content.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        preview_file (str / dict): The reference preview file dict or ID.

    Returns:
        dict: The created preview file.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    preview_file = normalize_model_parameter(preview_file)
    path = (
        f"actions/tasks/{task['id']}/comments/{comment['id']}"
        f"/preview-files/{preview_file['id']}"
    )
    return raw.post(path, {}, client=client)


def upload_preview_file(
    preview_file: str | dict,
    file_path: str,
    normalize_movie: bool = True,
    no_job: bool = False,
    client: KitsuClient = default,
    progress_callback=None,
) -> dict:
    """
    Upload the file content of the given preview file.

    The server makes the preview variants in the background. The returned
    preview file has the status "processing". The status becomes "ready"
    when the server has stored the variants. If the script needs the files
    immediately after the upload, set no_job to True. The server then makes
    the variants during the request.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        file_path (str): The path of the file to upload as the preview.
        normalize_movie (bool): If False, the server does not normalize the
            movie.
        no_job (bool): If True, the server makes the variants during the
            request.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        dict: The preview file.
    """
    path = (
        f"pictures/preview-files/"
        f"{normalize_model_parameter(preview_file)['id']}"
    )
    params = []
    if not normalize_movie:
        params.append("normalize=false")
    if no_job:
        params.append("no_job=true")
    if params:
        path += "?" + "&".join(params)
    return raw.upload(
        path, file_path, client=client, progress_callback=progress_callback
    )


def add_preview(
    task: str | dict,
    comment: str | dict,
    preview_file_path: str | None = None,
    preview_file_url: str | None = None,
    normalize_movie: bool = True,
    revision: int | None = None,
    no_job: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Add a preview to the given comment.

    The server makes the preview in the background. The returned preview file
    has the status "processing". If you set no_job to True, the server makes
    the preview during the request.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        preview_file_path (str): The path of the file to upload as the preview.
        preview_file_url (str): The URL of the preview file. If you give this
            value, this function does not use the path.
        normalize_movie (bool): If True, the server normalizes the movie.
        revision (int): The revision number.
        no_job (bool): If True, the server makes the preview during the
            request.

    Returns:
        dict: The created preview file.

    Raises:
        ValueError: If you do not give a path or a URL.
    """
    if preview_file_path is None and preview_file_url is None:
        raise ValueError(
            "add_preview requires either preview_file_path or "
            "preview_file_url."
        )
    downloaded = None
    if preview_file_url is not None:
        preview_file_path = downloaded = download_file(preview_file_url)
    try:
        preview_file = create_preview(
            task, comment, revision=revision, client=client
        )
        return upload_preview_file(
            preview_file,
            preview_file_path,
            normalize_movie=normalize_movie,
            no_job=no_job,
            client=client,
        )
    finally:
        if downloaded is not None and os.path.exists(downloaded):
            os.remove(downloaded)


def add_extra_preview(
    task: str | dict,
    comment: str | dict,
    preview_file: str | dict,
    preview_file_path: str | None = None,
    preview_file_url: str | None = None,
    normalize_movie: bool = True,
    no_job: bool = False,
    client: KitsuClient = default,
) -> dict:
    """
    Add an extra preview to the given comment revision.

    The extra preview has the same revision as the given reference preview
    file. This function then uploads the file content. The server makes the
    preview in the background. The returned preview file has the status
    "processing". If you set no_job to True, the server makes the preview
    during the request.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        preview_file (str / dict): The reference preview file dict or ID. The
            new preview has its revision.
        preview_file_path (str): The path of the file to upload as the preview.
        preview_file_url (str): The URL of the preview file. If you give this
            value, this function does not use the path.
        normalize_movie (bool): If True, the server normalizes the movie.
        no_job (bool): If True, the server makes the preview during the
            request.

    Returns:
        dict: The created preview file.

    Raises:
        ValueError: If you do not give a path or a URL.
    """
    if preview_file_path is None and preview_file_url is None:
        raise ValueError(
            "add_extra_preview requires either preview_file_path or "
            "preview_file_url."
        )
    downloaded = None
    if preview_file_url is not None:
        preview_file_path = downloaded = download_file(preview_file_url)
    try:
        new_preview_file = create_extra_preview(
            task, comment, preview_file, client=client
        )
        return upload_preview_file(
            new_preview_file,
            preview_file_path,
            normalize_movie=normalize_movie,
            no_job=no_job,
            client=client,
        )
    finally:
        if downloaded is not None and os.path.exists(downloaded):
            os.remove(downloaded)


def publish_preview(
    task: str | dict,
    task_status: str | dict,
    comment: str = "",
    person: str | dict | None = None,
    checklist: list[dict] | None = None,
    attachments: list[str] | None = None,
    created_at: str | None = None,
    preview_file_path: str | None = None,
    preview_file_url: str | None = None,
    normalize_movie: bool = True,
    revision: int | None = None,
    set_thumbnail: bool = False,
    links: list[str] | None = None,
    client: KitsuClient = default,
) -> tuple[dict, dict]:
    """
    Publish a comment with the given preview on the given task.

    This function also sets the given task status.

    Args:
        task (str / dict): The task dict or the task ID.
        task_status (str / dict): The task status dict or ID.
        comment (str): The comment text.
        person (str / dict): The comment author.
        checklist (list): The comment checklist.
        attachments (list[file_path]): The file paths of the attachments.
        created_at (str): The comment date.
        preview_file_path (str): The path of the file to upload as the preview.
        preview_file_url (str): The URL of the preview file. If you give this
            value, this function does not use the path.
        normalize_movie (bool): If False, the server does not change the file.
        revision (int): The revision number.
        set_thumbnail (bool): If True, set the preview as the thumbnail of the
            entity.
        links (list): The links to add to the comment.

    Returns:
        tuple(dict, dict): The created comment and the created preview file.
    """
    new_comment = add_comment(
        task,
        task_status,
        comment=comment,
        person=person,
        checklist=checklist,
        attachments=attachments,
        created_at=created_at,
        links=links,
        client=client,
    )
    preview_file = add_preview(
        task,
        new_comment,
        preview_file_path=preview_file_path,
        preview_file_url=preview_file_url,
        normalize_movie=normalize_movie,
        revision=revision,
        client=client,
    )
    if set_thumbnail:
        set_main_preview(preview_file, client=client)
    return new_comment, preview_file


def batch_comments(
    comments: list[dict] | None = None,
    task: str | dict | None = None,
    client: KitsuClient = default,
    progress_callback=None,
) -> list[dict]:
    """
    Publish a list of comments with attachments and previews on the given task.

    Each comment dict must have the "task_status_id" and "text" keys. It can
    have lists of file paths in the "attachment_files" and "preview_files"
    keys. If you do not give a task, each comment must have the "task_id" key.

    Args:
        comments (list): The comments to publish.
        task (str / dict): The task dict or the task ID.
        progress_callback (Callable): The function ``(bytes_read, total)``
            to call during the upload.

    Returns:
        list: The created comments.
    """
    if comments is None:
        comments = []
    if task is not None:
        task = normalize_model_parameter(task)

    files, opened_files = _open_comment_files(comments)
    try:
        return raw.upload(
            f"actions/tasks/{task['id'] + '/' if task else ''}batch-comment",
            file_path=None,
            files=files,
            client=client,
            progress_callback=progress_callback,
        )
    finally:
        for f in opened_files:
            f.close()


def create_multiple_comments(
    project: str | dict,
    comments: list[dict] = None,
    client: KitsuClient = default,
    progress_callback=None,
) -> list[dict]:
    """
    Create more than one comment in one request for the given project.

    Each comment updates the status of its task.

    Zou ignores an entry with no ``object_id``, ``task_status_id`` or
    ``comment``, and does not show an error. This route does not accept files.
    After this operation, use ``add_attachment_files_to_comment`` or
    ``add_preview`` to upload them.

    Args:
        project (str / dict): The project dict or the project ID.
        comments (list): The comments to publish. Each comment must have an
            ``object_id`` (the task ID, or ``task_id``), a ``task_status_id``
            and a ``comment`` text. It can also have a ``links`` list.
        progress_callback: This function does not use this value. The route
            takes no files.

    Returns:
        list: The created comments.
    """
    if comments is None:
        comments = []
    project = normalize_model_parameter(project)

    payload = []
    for comment in comments:
        comment = dict(comment)
        if "task_id" in comment:
            comment.setdefault("object_id", comment.pop("task_id"))
        payload.append(comment)
    return raw.post(
        f"actions/projects/{project['id']}/tasks/comment-many",
        payload,
        client=client,
    )


def copy_last_client_comments(
    project: str | dict,
    tasks: list[str | dict],
    prefix: str = "",
    client: KitsuClient = default,
) -> list[dict]:
    """
    Copy the last client comment of each given task to a new comment.

    The current user is the author of the new comment. Artists cannot see
    client comments, but they can see the new comment. The tasks keep their
    status. This function ignores a task with no client comment. Only a
    project manager can do this.

    Args:
        project (str / dict): The project dict or the project ID.
        tasks (list): The task dicts or task IDs.
        prefix (str): The text before the client text, on its own line.

    Returns:
        list: The created comments.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"actions/projects/{project['id']}/tasks/copy-client-comments",
        {
            "task_ids": [
                normalize_model_parameter(task)["id"] for task in tasks
            ],
            "prefix": prefix,
        },
        client=client,
    )


def add_tasks_batch_comments(
    tasks: list[str | dict],
    comments_data: dict,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Add the same comment to more than one task in one request.

    Args:
        tasks (list): The task dicts or IDs.
        comments_data (dict): The comment fields for all tasks. The dict must
            have the ``text`` and ``task_status_id`` keys. It can have the
            ``person_id`` key.

    Returns:
        list: The created comments.
    """
    # Zou expects a "comments" array, each entry carrying its own task_id.
    comments = [
        {**comments_data, "task_id": normalize_model_parameter(task)["id"]}
        for task in tasks
    ]
    return raw.post(
        "actions/tasks/batch-comment", {"comments": comments}, client=client
    )


def set_main_preview(
    preview_file: str | dict,
    frame_number: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Set the given preview as the thumbnail of its entity.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        frame_number (int): The frame of the movie to use as the main preview.
            Use this value only for a movie preview.

    Returns:
        dict: The updated entity.
    """
    data = {}
    if frame_number is not None:
        data["frame_number"] = frame_number
    preview_file = normalize_model_parameter(preview_file)
    path = f"actions/preview-files/{preview_file['id']}/set-main-preview"
    return raw.put(path, data, client=client)


@cache
def all_comments_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        list: The comments of the given task.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all(f"tasks/{task['id']}/comments", client=client)


@cache
def get_last_comment_for_task(
    task: str | dict, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        dict: The last comment of the given task, or None if the task has no
        comment.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_first(f"tasks/{task['id']}/comments", client=client)


def assign_task(
    task: str | dict, person: str | dict, client: KitsuClient = default
) -> dict:
    """
    Assign one person to a task.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person dict or the person ID.

    Returns:
        list: The updated tasks.
    """
    person = normalize_model_parameter(person)
    task = normalize_model_parameter(task)
    path = f"/actions/persons/{person['id']}/assign"
    return raw.put(path, {"task_ids": [task["id"]]}, client=client)


def clear_assignations(
    tasks: str | dict | list[str | dict],
    person: str | dict | None = None,
    client: KitsuClient = default,
) -> list[str]:
    """
    Remove the assignations of one task or more than one task.

    If you do not give a person, this function removes all assignations.

    Args:
        tasks (list / str / dict): The task dict or the task ID, or a list.
        person (str / dict): The person dict or the person ID.

    Returns:
        list[str]: The IDs of the updated tasks.
    """
    if not isinstance(tasks, list):
        tasks = [tasks]
    if not tasks:
        # Nothing to clear: avoid a pointless 400 from the server.
        return []
    data = {}
    for task in tasks:
        task = normalize_model_parameter(task)
        data.setdefault("task_ids", []).append(task["id"])
    if person is not None:
        person = normalize_model_parameter(person)
        data["person_id"] = person["id"]
    return raw.put(
        "/actions/tasks/clear-assignation", data=data, client=client
    )


def new_task_type(
    name: str,
    color: str = "#000000",
    for_entity: str = "Asset",
    client: KitsuClient = default,
) -> dict:
    """
    Create a task type with the given name.

    If a task type with this name exists in Kitsu, return this task type.

    Args:
        name (str): The name of the task type.
        color (str): The color of the task type as a hexadecimal string. The
            first character is #. For example: #00FF00
        for_entity (str): The entity type of the task type.

    Returns:
        dict: The created or existing task type.
    """
    task_type = get_task_type_by_name(name, for_entity, client=client)
    if task_type is None:
        data = {"name": name, "color": color, "for_entity": for_entity}
        task_type = raw.post("data/task-types", data, client=client)
    return task_type


def new_task_status(
    name: str, short_name: str, color: str, client: KitsuClient = default
) -> dict:
    """
    Create a task status with the given name, short name and color.

    Args:
        name (str): The name of the task status.
        short_name (str): The short name of the task status.
        color (str): The color of the task status as a hexadecimal string. The
            first character is #. For example: #00FF00

    Returns:
        dict: The created task status.

    Raises:
        ValueError: If the color is not a valid hexadecimal string.
    """
    if not color or color[0] != "#":
        raise ValueError("Color must start with '#', e.g. '#00FF00'")
    if not all(c in string.hexdigits for c in color[1:]):
        raise ValueError(
            "Color must be a valid hexadecimal string, e.g. '#00FF00'"
        )

    data = {"name": name, "short_name": short_name, "color": color}
    return raw.post("data/task-status", data, client=client)


def update_task(task: dict, client: KitsuClient = default) -> dict:
    """
    Update the given task in the API.

    The API merges the given metadata with the current metadata. It does not
    remove the other metadata keys.

    Args:
        task (dict): The task dict to update.

    Returns:
        dict: The updated task.
    """
    if "assignees" in task:
        # Copy before normalizing so the caller's dict is left untouched.
        task = {
            **task,
            "assignees": normalize_list_of_models_for_links(task["assignees"]),
        }
    return raw.put(f"data/tasks/{task['id']}", task, client=client)


def update_task_data(
    task: str | dict,
    data: dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Update the metadata of the given task.

    This function does not change the keys that are not in ``data``.

    Args:
        task (str / dict): The task dict or the task ID.
        data (dict): The metadata keys and values to set.

    Returns:
        dict: The updated task.
    """
    if data is None:
        data = {}
    task = normalize_model_parameter(task)
    # Invalidate the cache so the base read (and later reads) reflect the
    # server state; merging onto a stale cached copy reverts concurrent edits.
    get_task.clear_cache()
    current_task = get_task(task["id"], client=client)

    updated_task = {
        "id": current_task["id"],
        "data": {**(current_task["data"] or {}), **data},
    }
    result = update_task(updated_task, client=client)
    get_task.clear_cache()
    return result


_ROUTE_TYPES = {
    "Asset": "assets",
    "Edit": "edits",
    "Sequence": "sequences",
    "Shot": "shots",
}


@cache
def get_task_url(task: dict, client: KitsuClient = default) -> str:
    """
    Args:
        task (dict): The task dict. If it does not contain the task type and
            the project, this function gets the full task.

    Returns:
        url (str): The web URL of the given task. In a TV show, the URL
            contains the episode of the task entity.

    Raises:
        TaskMustBeADictException: If the task is not a dict.
    """
    if not isinstance(task, dict):
        raise TaskMustBeADictException
    if "task_type" not in task or "project" not in task:
        task = get_task(task["id"], client=client)
    host = raw.get_api_url_from_host(client=client)
    base = f"{host}/productions/{task['project_id']}"
    for_entity = task["task_type"].get("for_entity") or "Asset"
    if for_entity == "Episode":
        return f"{base}/episodes/{task['entity_id']}/tasks/{task['id']}/"
    if task["project"].get("production_type") == "tvshow":
        episode_id = _get_task_episode_id(task, for_entity)
        if episode_id:
            base = f"{base}/episodes/{episode_id}"
    route_type = _ROUTE_TYPES.get(for_entity, "assets")
    return f"{base}/{route_type}/tasks/{task['id']}/"


def _get_task_episode_id(task: dict, for_entity: str) -> str | None:
    # The full task gives the episode of a shot or a sequence. An edit
    # belongs to its parent episode. An asset belongs to the episode that
    # created it, or to the "main" pack of Kitsu.
    if task.get("episode"):
        return task["episode"]["id"]
    entity = task.get("entity") or {}
    if for_entity == "Edit":
        return entity.get("parent_id")
    if for_entity == "Asset":
        return entity.get("source_id") or "main"
    return None


def all_tasks_for_project(
    project: str | dict,
    task_type: str | dict | None = None,
    episode: str | dict | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Args:
        project (str / dict): The project or its ID.
        task_type (str / dict): The task type or its ID, to filter the tasks.
        episode (str / dict): The episode or its ID, to filter the tasks.

    Returns:
        list[dict]: The tasks of the given project.
    """
    project = normalize_model_parameter(project)
    path = f"/data/projects/{project['id']}/tasks"
    params = {}
    if task_type is not None:
        task_type = normalize_model_parameter(task_type)
        params["task_type_id"] = task_type["id"]
    if episode is not None:
        episode = normalize_model_parameter(episode)
        params["episode_id"] = episode["id"]
    return raw.get(path, params=params, client=client)


def update_comment(comment: dict, client: KitsuClient = default) -> dict:
    """
    Save the given comment data to the API.

    The metadata of the given comment replace all current metadata.

    Args:
        comment (dict): The comment dict to update.

    Returns:
        dict: The updated comment.
    """
    return raw.put(f"data/comments/{comment['id']}", comment, client=client)


@cache
def all_open_tasks(
    project: str | dict | None = None,
    task_type: str | dict | None = None,
    task_status: str | dict | None = None,
    person: str | dict | list | None = None,
    department: str | dict | None = None,
    studio: str | dict | None = None,
    start_date: str | None = None,
    due_date: str | None = None,
    priority: int | None = None,
    page: int | None = None,
    limit: int | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Get one page of the open tasks, as the Kitsu task list does.

    Args:
        project (str / dict, optional): The project dict or ID.
        task_type (str / dict, optional): The task type dict or ID.
        task_status (str / dict, optional): The task status dict or ID.
        person (str / dict / list, optional): A person, a list of persons,
            or "unassigned" for the tasks with no assignee.
        department (str / dict, optional): The department dict or ID.
        studio (str / dict, optional): The studio dict or ID.
        start_date (str, optional): The tasks that start on or after this date
            (YYYY-MM-DD).
        due_date (str, optional): The tasks with a due date before this date
            (YYYY-MM-DD).
        priority (int, optional): The task priority.
        page (int, optional): The page number. The first page is 1.
        limit (int, optional): The number of tasks on each page (100 by
            default).

    Returns:
        dict: The page, with the "data" (the tasks), "stats", "is_more",
        "limit" and "page" keys.
    """
    params = {}
    for key, model in (
        ("project_id", project),
        ("task_type_id", task_type),
        ("task_status_id", task_status),
        ("department_id", department),
        ("studio_id", studio),
    ):
        if model is not None:
            params[key] = normalize_model_parameter(model)["id"]
    if person == "unassigned":
        params["person_id"] = person
    elif person is not None:
        persons = person if isinstance(person, list) else [person]
        params["person_id"] = ",".join(
            normalize_model_parameter(entry)["id"] for entry in persons
        )
    for key, value in (
        ("start_date", start_date),
        ("due_date", due_date),
        ("priority", priority),
        ("page", page),
        ("limit", limit),
    ):
        if value is not None:
            params[key] = value
    return raw.get("data/tasks/open-tasks", params=params, client=client)


@cache
def get_open_tasks_stats(client: KitsuClient = default) -> dict:
    """
    Get the statistics of the open tasks.

    Returns:
        dict: The statistics of the open tasks.
    """
    return raw.get("data/tasks/open-tasks/stats", client=client)


@cache
def all_previews_for_task(
    task: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all previews of a task.

    Args:
        task (str / dict): The task dict or ID.

    Returns:
        list: The previews of the task.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all(f"tasks/{task['id']}/previews", client=client)


@cache
def all_tasks_for_person_and_type(
    person: str | dict, task_type: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all tasks of a person and a task type.

    Args:
        person (str / dict): The person dict or ID.
        task_type (str / dict): The task type dict or ID.

    Returns:
        list: The tasks of the person and the task type.
    """
    person = normalize_model_parameter(person)
    task_type = normalize_model_parameter(task_type)
    return raw.fetch_all(
        f"persons/{person['id']}/related-tasks/{task_type['id']}",
        client=client,
    )


@cache
def all_comments_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all comments of a project.

    Args:
        project (str / dict): The project dict or ID.

    Returns:
        list: The comments of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(f"projects/{project['id']}/comments", client=client)


@cache
def all_notifications_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all notifications of a project.

    Args:
        project (str / dict): The project dict or ID.

    Returns:
        list: The notifications of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/notifications", client=client
    )


@cache
def all_preview_files_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all preview files of a project.

    Args:
        project (str / dict): The project dict or ID.

    Returns:
        list: The preview files of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/preview-files", client=client
    )


@cache
def all_subscriptions_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Get all subscriptions of a project.

    Args:
        project (str / dict): The project dict or ID.

    Returns:
        list: The subscriptions of the project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        f"projects/{project['id']}/subscriptions", client=client
    )


@cache
def get_persons_tasks_dates(client: KitsuClient = default) -> dict:
    """
    Get the first start date and the last due date of the tasks of each person.

    Returns:
        list: One dict for each person, with the "person_id", "min_date",
        "max_date" and "busy_periods" keys.
    """
    return raw.get("data/persons/task-dates", client=client)


def remove_tasks_for_type(
    project: str | dict, task_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove all tasks of a task type in a project.

    Only an administrator can do this.

    Args:
        project (str / dict): The project dict or ID.
        task_type (str / dict): The task type dict or ID.

    Returns:
        str: The response of the API.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    return raw.delete(
        f"actions/projects/{project['id']}"
        f"/task-types/{task_type['id']}/delete-tasks",
        client=client,
    )


def remove_tasks_batch(
    project: str | dict,
    tasks: list[str | dict],
    client: KitsuClient = default,
) -> requests.Response:
    """
    Remove more than one task of a project in one request.

    Only a project manager can do this.

    Args:
        project (str / dict): The project of the tasks.
        tasks (list): The task dicts or IDs to remove.

    Returns:
        list: The IDs of the removed tasks.
    """
    project = normalize_model_parameter(project)
    task_ids = [normalize_model_parameter(task)["id"] for task in tasks]
    return raw.post(
        f"actions/projects/{project['id']}/delete-tasks",
        task_ids,
        client=client,
    )


def assign_tasks_to_person(
    tasks: list[str | dict], person: str | dict, client: KitsuClient = default
) -> dict:
    """
    Assign more than one task to a person.

    Args:
        tasks (list): The task dicts or IDs.
        person (str / dict): The person dict or ID.

    Returns:
        list: The updated tasks.
    """
    person = normalize_model_parameter(person)
    task_ids = [normalize_model_parameter(task)["id"] for task in tasks]
    return raw.put(
        f"actions/persons/{person['id']}/assign",
        {"task_ids": task_ids},
        client=client,
    )


@cache
def get_task_time_spent_for_date(
    task: str | dict, date: str, client: KitsuClient = default
) -> dict:
    """
    Get the time spent on a task on the given date.

    Args:
        task (str / dict): The task dict or ID.
        date (str): The date with the format YYYY-MM-DD.

    Returns:
        dict: The keys are person IDs and the values are lists of time spents.
        The "total" key contains the total duration.
    """
    task = normalize_model_parameter(task)
    return raw.get(
        f"actions/tasks/{task['id']}/time-spents/{date}",
        client=client,
    )


def remove_time_spent(
    time_spent: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove a time spent entry.

    Args:
        time_spent (str / dict): The time spent dict or ID.

    Returns:
        str: The response of the API.
    """
    time_spent = normalize_model_parameter(time_spent)
    return raw.delete(f"data/time-spents/{time_spent['id']}", client=client)


def remove_preview_from_comment(
    task: str | dict,
    comment: str | dict,
    preview_file: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a preview from a comment.

    Args:
        task (str / dict): The task of the comment.
        comment (str / dict): The comment dict or ID.
        preview_file (str / dict): The preview file dict or ID.

    Returns:
        str: The response of the API.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    preview_file = normalize_model_parameter(preview_file)
    return raw.delete(
        f"actions/tasks/{task['id']}/comments/{comment['id']}"
        f"/preview-files/{preview_file['id']}",
        client=client,
    )


def move_comment_to_task(
    task: str | dict,
    comment: str | dict,
    target_task: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Move a comment to a different task of the same entity.

    Only production managers and studio administrators can do this. The API
    keeps the creation date, text, attachments, mentions and status change of
    the comment. The API makes the notifications and news again for the target
    task, as for a new comment.

    Args:
        task (str / dict): The dict or ID of the current task of the comment.
        comment (str / dict): The comment dict or ID to move.
        target_task (str / dict): The dict or ID of the target task. It must
            have the same entity as the current task.

    Returns:
        dict: The updated comment. Its object_id is the target task ID.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    target_task = normalize_model_parameter(target_task)
    return raw.post(
        f"actions/tasks/{task['id']}/comments/{comment['id']}/move",
        {"target_task_id": target_task["id"]},
        client=client,
    )


def acknowledge_comment(
    task: str | dict,
    comment: str | dict,
    client: KitsuClient = default,
) -> dict:
    """
    Acknowledge a comment.

    If the comment is acknowledged, this function removes the acknowledgment.

    Args:
        task (str / dict): The task dict or ID.
        comment (str / dict): The comment dict or ID.

    Returns:
        dict: The updated comment.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    return raw.post(
        f"data/tasks/{task['id']}/comments/{comment['id']}/ack",
        {},
        client=client,
    )


def reply_to_comment(
    task: str | dict,
    comment: str | dict,
    text: str,
    person: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Reply to an existing comment.

    Args:
        task (str / dict): The task of the comment.
        comment (str / dict): The comment dict or ID.
        text (str): The reply text.
        person (str / dict): The API ignores this value. The current user is
            the author of the reply.

    Returns:
        dict: The new reply.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    data = {"text": text}
    if person is not None:
        person = normalize_model_parameter(person)
        data["person_id"] = person["id"]
    return raw.post(
        f"data/tasks/{task['id']}/comments/{comment['id']}/reply",
        data,
        client=client,
    )


def delete_comment_attachment(
    task: str | dict,
    comment: str | dict,
    attachment_file: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove an attachment from a comment.

    Args:
        task (str / dict): The task of the comment.
        comment (str / dict): The comment dict or ID.
        attachment_file (str / dict): The attachment file dict or ID.

    Returns:
        str: The response of the API.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    attachment_file = normalize_model_parameter(attachment_file)
    return raw.delete(
        f"data/tasks/{task['id']}/comments/{comment['id']}"
        f"/attachments/{attachment_file['id']}",
        client=client,
    )


def delete_comment_reply(
    task: str | dict,
    comment: str | dict,
    reply: str | dict,
    client: KitsuClient = default,
) -> str:
    """
    Remove a reply to a comment.

    Args:
        task (str / dict): The task of the comment.
        comment (str / dict): The comment dict or ID.
        reply (str / dict): The reply dict or ID.

    Returns:
        str: The response of the API.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    reply = normalize_model_parameter(reply)
    return raw.delete(
        f"data/tasks/{task['id']}/comments/{comment['id']}"
        f"/reply/{reply['id']}",
        client=client,
    )


def create_shot_tasks(
    shot: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Create the tasks of a shot.

    Args:
        shot (str / dict): The shot dict or ID.
        task_types (list): The task type dicts or IDs.

    Returns:
        list: The created tasks.
    """
    return create_entity_tasks(shot, task_types, client=client)


def create_asset_tasks(
    asset: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Create the tasks of an asset.

    Args:
        asset (str / dict): The asset dict or ID.
        task_types (list): The task type dicts or IDs.

    Returns:
        list: The created tasks.
    """
    return create_entity_tasks(asset, task_types, client=client)


def create_edit_tasks(
    edit: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Create the tasks of an edit.

    Args:
        edit (str / dict): The edit dict or ID.
        task_types (list): The task type dicts or IDs.

    Returns:
        list: The created tasks.
    """
    return create_entity_tasks(edit, task_types, client=client)


def create_concept_tasks(
    concept: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Create the tasks of a concept.

    Args:
        concept (str / dict): The concept dict or ID.
        task_types (list): The task type dicts or IDs.

    Returns:
        list: The created tasks.
    """
    return create_entity_tasks(concept, task_types, client=client)


def create_entity_tasks(
    entity: str | dict,
    task_types: list[str | dict],
    client: KitsuClient = default,
) -> list[dict]:
    """
    Create the tasks of an entity.

    Args:
        entity (str / dict): The entity dict or ID.
        task_types (list): The task type dicts or IDs.

    Returns:
        list: The created tasks.
    """
    entity = normalize_model_parameter(entity)
    task_type_ids = [
        normalize_model_parameter(task_type)["id"] for task_type in task_types
    ]
    return raw.post(
        f"data/entities/{entity['id']}/tasks",
        {"task_type_ids": task_type_ids},
        client=client,
    )
