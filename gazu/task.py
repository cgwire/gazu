from deprecated import deprecated

from . import client
from .sorting import sort_by_name
from .helpers import normalize_model_parameter

from .cache import cache


@cache
def all_task_types():
    """
    Return task types
    """
    task_types = client.fetch_all("task-types")
    return sort_by_name(task_types)


@cache
def all_tasks_for_shot(shot):
    """
    Return tasks linked to given shot.
    """
    tasks = client.fetch_all("shots/%s/tasks" % shot['id'])
    return sort_by_name(tasks)


@cache
def all_tasks_for_sequence(sequence):
    """
    Return tasks linked to given sequence.
    """
    tasks = client.fetch_all("sequences/%s/tasks" % sequence['id'])
    return sort_by_name(tasks)


@cache
def all_tasks_for_scene(scene):
    """
    Return tasks linked to given scene.
    """
    tasks = client.fetch_all("scenes/%s/tasks" % scene['id'])
    return sort_by_name(tasks)


@cache
def all_tasks_for_asset(asset):
    """
    Retrieve all tasks directly linked to given asset.
    """
    tasks = client.fetch_all("assets/%s/tasks" % asset["id"])
    return sort_by_name(tasks)


@cache
def all_tasks_for_task_status(project, task_type, task_status):
    """
    Return all tasks set at given status for given project and task type.
    """
    return client.fetch_all(
        "tasks?project_id=%s&task_type_id=%s&task_status_id=%s" % (
            project["id"],
            task_type["id"],
            task_status["id"]
        )
    )


@cache
def all_task_types_for_shot(shot):
    """
    Return task types of task linked to given shot.
    """
    task_types = client.fetch_all("shots/%s/task-types" % shot['id'])
    return sort_by_name(task_types)


@cache
def all_task_types_for_asset(asset):
    """
    Return all task types of tasks related to given asset.
    """
    task_types = client.fetch_all("assets/%s/task-types" % asset['id'])
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(scene):
    """
    Return task types of task linked to given scene.
    """
    task_types = client.fetch_all("scenes/%s/task-types" % scene['id'])
    return sort_by_name(task_types)


@cache
def all_task_types_for_sequence(sequence):
    """
    Return task types of tasks linked directly to given sequence.
    """
    task_types = client.fetch_all("sequences/%s/task-types" % sequence['id'])
    return sort_by_name(task_types)


@cache
def all_tasks_for_entity_and_task_type(entity, task_type):
    """
    Find a task by looking for it through its task type and its entity.
    """
    task_type_id = task_type["id"]
    entity_id = entity["id"]
    return client.fetch_all(
        "entities/%s/task-types/%s/tasks" % (
            entity_id,
            task_type_id
        )
    )


@cache
def get_task_by_name(entity, task_type, name="main"):
    """
    Find a task by looking for it through its name and its entity.
    """
    return client.fetch_first(
        "tasks?name={name}&entity_id={entity_id}&task_type_id={task_type_id}"
        .format(
            name=name,
            task_type_id=task_type["id"],
            entity_id=entity["id"]
        )
    )


@cache
def get_task_type(task_type_id):
    """
    Return task type object for given name.
    """
    return client.fetch_one("task-types", task_type_id)


@cache
def get_task_type_by_name(task_type_name):
    """
    Return task type object for given name.
    """
    return client.fetch_first("task-types?name=%s" % task_type_name)


@cache
def get_task_by_path(project, file_path, entity_type="shot"):
    """
    Retrieve a task from given file path. This function requires context, the
    project related to the given path and the related entity type.
    """
    data = {
        "file_path": file_path,
        "project_id": project["id"],
        "type": entity_type
    }
    return client.post("data/tasks/from-path/", data)


@cache
def get_task_status(task):
    """
    Retrieves status object corresponding to status set on given task.
    """
    return client.fetch_first(
        "task-status?id={task_status_id}".format(
            task_status_id=task['task_status_id']
        )
    )


@cache
def get_task_status_by_name(task_status_name):
    """
    Return task type status for given name.
    """
    return client.fetch_first("task-status?name=%s" % task_status_name)


@cache
def get_task(task_id):
    """
    Return task corresponding to given task ID.
    """
    return client.get('data/tasks/%s/full' % task_id)


def new_task(
    entity,
    task_type,
    name="main",
    task_status=None,
    assigner=None,
    assignees=None
):
    """
    Create a new task for given entity and task type. It requires a task status
    to run properly.
    """
    if task_status is None:
        task_status = get_task_status_by_name("Todo")

    data = {
        "project_id": entity["project_id"],
        "entity_id": entity["id"],
        "task_type_id": task_type["id"],
        "task_status_id": task_status["id"],
        "name": name
    }

    if assigner is not None:
        data["assigner_id"] = assigner["id"]

    if assignees is not None:
        data["assignees"] = [person["id"] for person in assignees]
    else:
        data["assignees"] = []

    task = get_task_by_name(entity, task_type, name)
    if task is None:
        task = client.post("data/tasks", data)
    return task


def start_task(task):
    """
    Change a task status to WIP and set its real start date to now.
    """
    path = "actions/tasks/%s/start" % task["id"]
    return client.put(path, {})


def task_to_review(
    task,
    person,
    comment,
    revision=1,
    change_status=True
):
    """
    Mark given task as pending, waiting for approval.
    """
    path = "actions/tasks/%s/to-review" % task["id"]
    data = {
        "person_id": person["id"],
        "comment": comment,
        "revision": revision,
        "change_status": change_status
    }

    return client.put(path, data)


@cache
def get_time_spent(task, date):
    """
    Get the time spent by CG artists on a task at a given date.
    It returns a dict with person ID as key and time spent object as value.
    A field contains the total time spent.
    Durations must be set in seconds.
    Date format is YYYY-MM-DD.
    """
    path = "actions/tasks/%s/time-spents/%s" % (
        task["id"],
        date
    )
    return client.get(path)


def set_time_spent(task, person, date, duration):
    """
    Set the time spent by a CG artist on a given task at a given date.
    Durations must be set in seconds.
    Date format is YYYY-MM-DD.
    """
    path = "actions/tasks/%s/time-spents/%s/persons/%s" % (
        task["id"],
        date,
        person["id"]
    )
    return client.post(path, {"duration": duration})


def add_time_spent(task, person, date, duration):
    """
    Add given duration to the already logged duration for given task and person
    at a given date.
    Durations must be set in seconds.
    Date format is YYYY-MM-DD.
    """
    path = "actions/tasks/%s/time-spents/%s/persons/%s/add" % (
        task["id"],
        date,
        person["id"]
    )
    return client.post(path, {"duration": duration})


def add_comment(task, task_status, comment=""):
    """
    Add comment to given task. Each comment requires a task_status. Since the
    addition of comment triggers a task status change.
    Comment can be empty.
    """
    task = normalize_model_parameter(task)
    task_status = normalize_model_parameter(task_status)
    data = {
        "task_status_id": task_status["id"],
        "comment": comment
    }
    return client.post("actions/tasks/%s/comment" % task["id"], data)


def add_preview(task, comment, preview_file_path, is_movie=False):
    """
    Add a preview to given comment. It it's a movie, it must be mentioned
    in the option.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    path = "actions/tasks/%s/comments/%s/add-preview" % (
        task["id"],
        comment["id"]
    )
    preview_file = client.post(path, {"is_movie": is_movie})
    path = "pictures/preview-files/%s" % preview_file["id"]
    client.upload(path, preview_file_path)
    return preview_file


def set_main_preview(entity, preview_file):
    """
    Set given preview as thumbnail of given entity.
    """
    entity = normalize_model_parameter(entity)
    preview_file = normalize_model_parameter(preview_file)
    path = "actions/entities/%s/set-main-preview/%s" % (
        entity["id"],
        preview_file["id"]
    )
    return client.put(path, {})


@deprecated
def all_for_shot(shot):
    return all_tasks_for_shot(shot)


@deprecated
def all_for_sequence(sequence):
    return all_tasks_for_sequence(sequence)


@deprecated
def all_for_scene(scene):
    return all_tasks_for_scene(scene)


@deprecated
def all_for_asset(asset):
    return all_tasks_for_asset(asset)
