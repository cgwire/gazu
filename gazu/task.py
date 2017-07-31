from . import client
from .sorting import sort_by_name


def all_for_shot(shot):
    """
    Return tasks linked to given shot.
    """
    tasks = client.fetch_all("shots/%s/tasks" % shot['id'])
    return sort_by_name(tasks)


def all_for_asset(asset):
    """
    Retrieve all tasks directly linked to given asset.
    """
    tasks = client.fetch_all("assets/%s/tasks" % asset["id"])
    return sort_by_name(tasks)


def all_task_types_for_shot(shot):
    """
    Return task types of task linked to given shot.
    """
    task_types = client.fetch_all("shots/%s/task_types" % shot['id'])
    return sort_by_name(task_types)


def get_task_by_task_type(task_type, entity):
    """
    Find a task by looking for it through its task type and its entity.
    """
    task_type_id = task_type["id"]
    entity_id = entity["id"]
    tasks = client.fetch_all(
        "tasks?task_type_id={task_type_id}&entity_id={entity_id}".format(
            task_type_id=task_type_id,
            entity_id=entity_id
        )
    )
    return tasks


def get_task_by_name(name, entity):
    """
    Find a task by looking for it through its name and its entity.
    """
    entity_id = entity["id"]
    tasks = client.fetch_all(
        "tasks?name={name}&entity_id={entity_id}".format(
            name=name,
            entity_id=entity_id
        )
    )
    return tasks[0] if tasks else None


def get_task_type(task_type_name):
    """
    Return task type object for given name.
    """
    task_types = client.fetch_all("task_types")
    task_types = [x for x in task_types if x["name"] == task_type_name]
    return task_types[0] if task_types else None


def get_task_from_path(project, file_path, entity_type="shot"):
    """
    Retrieve a task from given file path. This function requires context, the
    project related to the given path and the related entity type.
    """
    data = {
        "file_path": file_path,
        "project_id": project["id"],
        "type": entity_type
    }
    try:
        return client.post("project/tasks/from-path/", data)
    except:
        return None


def get_task_status(task):
    """
    Retrieves status object corresponding to status set on given task.
    """
    task_status = client.fetch_all(
        "task_status?id={task_status_id}".format(
            task_status_id=task['task_status_id']
        )
    )
    return task_status[0] if task_status else None


def start_task(task):
    """
    Change a task status to WIP and set its real start date to now.
    """
    path = client.url_path_join(
        "data", "tasks", task["id"], "start"
    )
    return client.put(path, {})
