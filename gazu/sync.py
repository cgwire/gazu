from . import client as raw

from .helpers import normalize_model_parameter

default = raw.default_client


def get_last_events(
    page_size=20000, project=None, after=None, before=None, client=default
):
    """
    Get last events that occured on the machine.

    Args:
        page_size (int): Number of events to retrieve.
        project (dict/id): Get only events related to this project.
        after (dict/id): Get only events occuring after given date.
        before (dict/id): Get only events occuring before given date.


    Returns:
        dict: Last events matching criterions.
    """
    path = "/data/events/last"
    params = {"page_size": page_size}
    if project is not None:
        project = normalize_model_parameter(project)
        params["project_id"] = project["id"]
    if after is not None:
        params["after"] = after
    if before is not None:
        params["before"] = before
    return raw.get(path, params=params, client=client)


def import_entities(entities, client=default):
    """
    Import entities from another instance to target instance (keep id and audit
    dates).
    Args:
        entities (list): Entities to import.

    Returns:
        dict: Entities created.
    """
    return raw.post("import/kitsu/entities", entities, client=client)


def import_tasks(tasks, client=default):
    """
    Import tasks from another instance to target instance (keep id and audit
    dates).
    Args:
        tasks (list): Tasks to import.

    Returns:
        dict: Tasks created.
    """
    return raw.post("import/kitsu/tasks", tasks, client=client)


def import_entity_links(links, client=default):
    """
    Import enitity links from another instance to target instance (keep id and
    audit dates).
    Args:
        links (list): Entity links to import.

    Returns:
        dict: Entity links created.
    """
    return raw.post("import/kitsu/entity-links", links, client=client)


def get_model_list_diff(source_list, target_list):
    """
    Args:
        source_list (list): List of models to compare.
        target_list (list): List of models for which we want a diff.

    Returns:
        tuple: Two lists, one containing the missing models in the target list
        and one containing the models that should not be in the target list.
    """
    missing = []
    source_ids = {m["id"]: True for m in source_list}
    target_ids = {m["id"]: True for m in target_list}
    for model in source_list:
        if model["id"] not in target_ids:
            missing.append(model)
    unexpected = [model for model in target_list if model["id"] not in source_ids]
    return (missing, unexpected)


def get_link_list_diff(source_list, target_list):
    """
    Args:
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        tuple: Two lists, one containing the missing links in the target list
        and one containing the links that should not be in the target list.
        Links are identified by their in ID and their out ID.
    """
    def get_link_key(l): return l["entity_in_id"] + "-" + l["entity_out_id"]
    missing = []
    unexpected = []
    source_ids = {get_link_key(m): True for m in source_list}
    target_ids = {get_link_key(m): True for m in target_list}
    for link in source_list:
        if get_link_key(link) not in target_ids:
            missing.append(link)
    for link in target_list:
        if get_link_key(link) not in source_ids:
            unexpected.append(link)
    return (missing, unexpected)


def get_id_map_by_name(source_list, target_list):
    """
    Args:
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        dict: A dict where keys are the source model names and the values are
        the IDs of the target models with same name.
        It's useful to match a model from the source list to its relative in
        the target list based on its name.
    """
    link_map = {}
    name_map = {}
    for model in target_list:
        name_map[model["name"].lower()] = model["id"]
    for model in source_list:
        if model["name"].lower() in name_map:
            link_map[model["id"]] = name_map[model["name"].lower()]
    return link_map


def is_changed(source_model, target_model):
    source_date = source_model["updated_at"]
    target_date = target_model["updated_at"]
    return source_date > target_date
