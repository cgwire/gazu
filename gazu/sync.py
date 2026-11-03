"""
Compare the data of two Kitsu instances and copy data between them.
"""

from __future__ import annotations

import logging
import os
import tempfile

from typing import Callable

from . import client as raw
from . import asset as asset_module
from . import casting as casting_module
from . import concept as concept_module
from . import edit as edit_module
from . import entity as entity_module
from . import person as person_module
from . import project as project_module
from . import files as files_module
from . import shot as shot_module
from . import task as task_module

from .client import KitsuClient
from .helpers import (
    normalize_model_parameter,
    sanitize_filename,
    validate_date_format,
)

logger = logging.getLogger("gazu.sync")

default = raw.default_client


def get_last_events(
    limit: int = 20000,
    project: str | dict | None = None,
    after: str | None = None,
    before: str | None = None,
    only_files: bool = False,
    name: str | None = None,
    client: KitsuClient = default,
) -> list[dict]:
    """
    Get the last events of the instance.

    Only a manager can do this.

    Args:
        limit (int): The number of events to get.
        project (str / dict): Get only the events of this project.
        after (str): Get only the events after the given date.
        before (str): Get only the events before the given date.
        only_files (bool): Get only the events of files.
        name (str): Get only the events with this name.

    Returns:
        list[dict]: The last events that match the criteria.
    """
    path = "/data/events/last"
    params = {"limit": limit, "only_files": only_files}
    if project is not None:
        project = normalize_model_parameter(project)
        params["project_id"] = project["id"]
    if after is not None:
        params["after"] = validate_date_format(after)
    if before is not None:
        params["before"] = validate_date_format(before)
    if name is not None:
        params["name"] = name
    return raw.get(path, params=params, client=client)


def import_entities(
    entities: list[dict], client: KitsuClient = default
) -> list[dict]:
    """
    Import entities from a different instance to the target instance.

    The API keeps the IDs and the audit dates. If an entity exists, the API
    updates it.

    Args:
        entities (list): The entities to import.

    Returns:
        list[dict]: The imported entities.
    """
    return raw.post("import/kitsu/entities", entities, client=client)


def import_tasks(
    tasks: list[dict], client: KitsuClient = default
) -> list[dict]:
    """
    Import tasks from a different instance to the target instance.

    The API keeps the IDs and the audit dates. If a task exists, the API
    updates it.

    Args:
        tasks (list): The tasks to import.

    Returns:
        list[dict]: The imported tasks.
    """
    return raw.post("import/kitsu/tasks", tasks, client=client)


def import_entity_links(
    links: list[dict], client: KitsuClient = default
) -> list[dict]:
    """
    Import entity links from a different instance to the target instance.

    The API keeps the IDs and the audit dates. If a link exists, the API
    updates it.

    Args:
        links (list): The entity links to import.

    Returns:
        list: The imported entity links.
    """
    return raw.post("import/kitsu/entity-links", links, client=client)


def get_model_list_diff(
    source_list: list[dict], target_list: list[dict], id_field: str = "id"
) -> tuple[list[dict], list[dict]]:
    """
    Args:
        source_list (list): The models to compare.
        target_list (list): The models to examine.
        id_field (str): The model field to use as the ID for the comparison.

    Returns:
        tuple: Two lists. The first list has the models that are missing in
        the target list. The second list has the models of the target list
        that are not in the source list.
    """
    source_ids = {m[id_field]: True for m in source_list}
    target_ids = {m[id_field]: True for m in target_list}
    missing = [
        model
        for model in source_list
        if not target_ids.get(model[id_field], False)
    ]
    unexpected = [
        model
        for model in target_list
        if not source_ids.get(model[id_field], False)
    ]
    return (missing, unexpected)


def get_link_list_diff(
    source_list: list[dict], target_list: list[dict]
) -> tuple[list[dict], list[dict]]:
    """
    Args:
        source_list (list): The links to compare.
        target_list (list): The links to examine.

    Returns:
        tuple: Two lists. The first list has the links that are missing in
        the target list. The second list has the links of the target list
        that are not in the source list. The "in" ID and the "out" ID
        identify a link.
    """

    def get_link_key(l: dict) -> str:
        return l["entity_in_id"] + "-" + l["entity_out_id"]

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


def get_id_map_by_name(
    source_list: list[dict], target_list: list[dict]
) -> dict:
    """
    Args:
        source_list (list): The source models to map.
        target_list (list): The target models to compare by name.

    Returns:
        dict: The keys are the source model names. The values are the IDs of
        the target models with the same name. The letter case has no effect.
        Use this dict to find the target model of a source model.
    """
    link_map = {}
    name_map = {}
    for model in target_list:
        name_map[model["name"].lower()] = model["id"]
    for model in source_list:
        if model["name"].lower() in name_map:
            link_map[model["name"]] = name_map[model["name"].lower()]
    return link_map


def get_id_map_by_id(
    source_list: list[dict], target_list: list[dict], field: str = "name"
) -> dict:
    """
    Args:
        source_list (list): The source models to map.
        target_list (list): The target models.
        field (str): The field to compare in the two lists ("name" by default).
            The letter case has no effect.

    Returns:
        dict: The keys are the source model IDs. The values are the IDs of
        the target models with the same field value. Use this dict to find
        the target model of a source model.
    """
    link_map = {}
    name_map = {}
    for model in target_list:
        name_map[model[field].lower()] = model["id"]
    for model in source_list:
        if model[field].lower() in name_map:
            link_map[model["id"]] = name_map[model[field].lower()]
    return link_map


def is_changed(source_model: dict, target_model: dict) -> bool:
    """
    Args:
        source_model (dict): The model from the source API.
        target_model (dict): The related model from the target API.

    Returns:
        bool: True if the source model is more recent than the target model.
        This function compares the `updated_at` fields.
    """
    source_date = source_model["updated_at"]
    target_date = target_model["updated_at"]
    return source_date > target_date


def _get_sync_id_map(
    source_client: KitsuClient,
    target_client: KitsuClient,
    fetch_all: Callable,
    field: str = "name",
) -> dict:
    """
    Make an ID map between two instances for the given model.

    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.
        fetch_all (Callable): The function that returns all models of a client.
        field (str): The field to compare ("name" by default).

    Returns:
        dict: The keys are source model IDs. The values are target
        model IDs.
    """
    source = fetch_all(client=source_client)
    target = fetch_all(client=target_client)
    return get_id_map_by_id(source, target, field=field)


def get_sync_department_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source department IDs. The values are target
        department IDs.
    """
    return _get_sync_id_map(
        source_client, target_client, person_module.all_departments
    )


def get_sync_asset_type_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source asset type IDs. The values are target
        asset type IDs.
    """
    return _get_sync_id_map(
        source_client, target_client, asset_module.all_asset_types
    )


def get_sync_project_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source project IDs. The values are target
        project IDs.
    """
    return _get_sync_id_map(
        source_client, target_client, project_module.all_projects
    )


def get_sync_task_type_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source task type IDs. The values are target
        task type IDs.
    """
    return _get_sync_id_map(
        source_client, target_client, task_module.all_task_types
    )


def get_sync_task_status_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source task status IDs. The values are target
        task status IDs.
    """
    return _get_sync_id_map(
        source_client, target_client, task_module.all_task_statuses
    )


def get_sync_person_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): The client of the source API.
        target_client (KitsuClient): The client of the target API.

    Returns:
        dict: The keys are source person IDs. The values are target
        person IDs.
    """
    return _get_sync_id_map(
        source_client,
        target_client,
        person_module.all_persons,
        field="email",
    )


def _map_created_by(
    entities: list[dict],
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Set the `created_by` field of the given entities to the target person.

    If no target person matches, the value is None. The source person IDs do
    not exist on the target.
    """
    person_map = get_sync_person_id_map(client_source, client_target)
    for entity in entities:
        entity["created_by"] = person_map.get(entity.get("created_by"))
    return entities


def push_assets(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy assets from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).
    This function does not copy an asset if its asset type is not mapped.

    Args:
        project_source (dict): The source project of the assets.
        project_target (dict): The target project of the assets.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed assets.
    """
    asset_types_map = get_sync_asset_type_id_map(client_source, client_target)
    task_types_map = get_sync_task_type_id_map(client_source, client_target)
    assets = asset_module.all_assets_for_project(
        project_source, client=client_source
    )
    mapped_assets = []
    for asset in assets:
        entity_type_id = asset["entity_type_id"]
        if entity_type_id not in asset_types_map:
            logger.warning(
                "Skipping asset %s: asset type %s is not mapped to the "
                "target.",
                asset.get("id"),
                entity_type_id,
            )
            continue
        asset["entity_type_id"] = asset_types_map[entity_type_id]
        if asset["ready_for"] is not None:
            if asset["ready_for"] not in task_types_map:
                logger.warning(
                    "Asset %s: ready_for task type %s is not mapped to the "
                    "target, importing without it.",
                    asset.get("id"),
                    asset["ready_for"],
                )
                asset["ready_for"] = None
            else:
                asset["ready_for"] = task_types_map[asset["ready_for"]]
        asset["project_id"] = project_target["id"]
        mapped_assets.append(asset)
    _map_created_by(mapped_assets, client_source, client_target)
    return import_entities(mapped_assets, client=client_target)


def push_episodes(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy episodes from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the episodes.
        project_target (dict): The target project of the episodes.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed episodes.
    """
    episodes = shot_module.all_episodes_for_project(
        project_source, client=client_source
    )
    for episode in episodes:
        episode["project_id"] = project_target["id"]
    _map_created_by(episodes, client_source, client_target)
    return import_entities(episodes, client=client_target)


def push_sequences(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy sequences from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the sequences.
        project_target (dict): The target project of the sequences.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed sequences.
    """
    sequences = shot_module.all_sequences_for_project(
        project_source, client=client_source
    )
    for sequence in sequences:
        sequence["project_id"] = project_target["id"]
    _map_created_by(sequences, client_source, client_target)
    return import_entities(sequences, client=client_target)


def push_shots(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy shots from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the shots.
        project_target (dict): The target project of the shots.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed shots.
    """
    shots = shot_module.all_shots_for_project(
        project_source, client=client_source
    )
    for shot in shots:
        shot["project_id"] = project_target["id"]
    _map_created_by(shots, client_source, client_target)
    return import_entities(shots, client=client_target)


def push_edits(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy edits from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the edits.
        project_target (dict): The target project of the edits.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed edits.
    """
    edits = edit_module.all_edits_for_project(
        project_source, client=client_source
    )
    for edit in edits:
        edit["project_id"] = project_target["id"]
    _map_created_by(edits, client_source, client_target)
    return import_entities(edits, client=client_target)


def push_concepts(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy concept folders and concepts from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the concepts.
        project_target (dict): The target project of the concepts.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed concept folders and concepts.
    """
    entity_type_map = _get_sync_id_map(
        client_source, client_target, entity_module.all_entity_types
    )
    # A concept or a folder points to its folder through parent_id: the
    # folders are pushed first, each parent before its children.
    folders = concept_module.all_concept_folders_for_project(
        project_source, client=client_source
    )
    ordered_folders = []
    while folders:
        pushed_ids = {folder["id"] for folder in ordered_folders}
        ready = [
            folder
            for folder in folders
            if folder.get("parent_id") is None
            or folder["parent_id"] in pushed_ids
        ]
        if not ready:
            ready = folders
        ordered_folders += ready
        folders = [folder for folder in folders if folder not in ready]
    concepts = concept_module.all_concepts_for_project(
        project_source, client=client_source
    )

    mapped_entities = []
    for entity in ordered_folders + concepts:
        entity_type_id = entity["entity_type_id"]
        if entity_type_id not in entity_type_map:
            logger.warning(
                "Skipping concept %s: entity type %s is not mapped to the "
                "target.",
                entity.get("id"),
                entity_type_id,
            )
            continue
        entity["entity_type_id"] = entity_type_map[entity_type_id]
        entity["project_id"] = project_target["id"]
        mapped_entities.append(entity)
    _map_created_by(mapped_entities, client_source, client_target)
    return import_entities(mapped_entities, client=client_target)


def push_entity_links(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy entity links (breakdown, concepts) from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    Args:
        project_source (dict): The source project of the entity links.
        project_target (dict): This function does not use this value.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed entity links.
    """
    links = casting_module.all_entity_links_for_project(
        project_source, client=client_source
    )
    return import_entity_links(links, client=client_target)


def push_project_entities(
    project_source: dict,
    project_target: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> dict:
    """
    Copy assets, episodes, sequences, shots, edits, concepts and entity
    links from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    This function copies the episodes only for a TV show.

    Args:
        project_source (dict): The source project.
        project_target (dict): The target project.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        dict: The pushed data. The keys are "assets", "episodes", "sequences",
        "shots", "edits", "concepts" and "entity_links".
    """
    assets = push_assets(
        project_source, project_target, client_source, client_target
    )
    episodes = []
    if project_source["production_type"] == "tvshow":
        episodes = push_episodes(
            project_source, project_target, client_source, client_target
        )
    sequences = push_sequences(
        project_source, project_target, client_source, client_target
    )
    shots = push_shots(
        project_source, project_target, client_source, client_target
    )
    edits = push_edits(
        project_source, project_target, client_source, client_target
    )
    concepts = push_concepts(
        project_source, project_target, client_source, client_target
    )
    entity_links = push_entity_links(
        project_source, project_target, client_source, client_target
    )
    return {
        "assets": assets,
        "episodes": episodes,
        "sequences": sequences,
        "shots": shots,
        "edits": edits,
        "concepts": concepts,
        "entity_links": entity_links,
    }


def push_tasks(
    project_source: dict,
    project_target: dict,
    default_status: str | dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
) -> list[dict]:
    """
    Copy tasks from the source to the target.

    This function keeps the audit fields (`id`, `created_at` and `updated_at`).

    This function sets all pushed tasks to the default status. It does not
    copy attachments or previews. Use ``push_tasks_comments`` for these.
    It does not copy a task if its task type is not mapped.

    Args:
        project_source (dict): The source project of the tasks.
        project_target (dict): The target project of the tasks.
        default_status (str / dict): The status of the pushed tasks.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.

    Returns:
        list: The pushed tasks.
    """
    default_status_id = normalize_model_parameter(default_status)["id"]
    task_type_map = get_sync_task_type_id_map(client_source, client_target)
    person_map = get_sync_person_id_map(client_source, client_target)

    tasks = task_module.all_tasks_for_project(
        project_source, client=client_source
    )
    mapped_tasks = []
    for task in tasks:
        if task["task_type_id"] not in task_type_map:
            logger.warning(
                "Skipping task %s: task type %s is not mapped to the target.",
                task.get("id"),
                task["task_type_id"],
            )
            continue
        task["task_type_id"] = task_type_map[task["task_type_id"]]
        task["task_status_id"] = default_status_id
        assigner_id = task["assigner_id"]
        if assigner_id is not None and assigner_id not in person_map:
            logger.warning(
                "Task %s: assigner %s is not mapped to the target, "
                "importing the task without an assigner.",
                task.get("id"),
                assigner_id,
            )
        task["assigner_id"] = person_map.get(assigner_id)
        task["project_id"] = project_target["id"]
        task["assignees"] = [
            person_map[person_id]
            for person_id in task["assignees"]
            if person_id in person_map
        ]
        mapped_tasks.append(task)
    return import_tasks(mapped_tasks, client=client_target)


def push_tasks_comments(
    project_source: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
    normalize_movie: bool = True,
) -> list[dict]:
    """
    Create a comment in the target API for each comment of the source project.

    This function keeps only the `created_at` field of the audit fields.
    It also creates the attachments and the previews.

    Args:
        project_source (dict): The source project of the comments.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.
        normalize_movie (bool): If True, the target normalizes the pushed
            movie previews. Set it to False for previews that the source
            normalized.

    Returns:
        list: The source tasks of the pushed comments.
    """
    task_status_map = get_sync_task_status_id_map(client_source, client_target)
    person_map = get_sync_person_id_map(client_source, client_target)
    tasks = task_module.all_tasks_for_project(
        project_source, client=client_source
    )
    for task in tasks:
        push_task_comments(
            task_status_map,
            person_map,
            task,
            client_source,
            client_target,
            normalize_movie=normalize_movie,
        )
    return tasks


def push_task_comments(
    task_status_map: dict,
    person_map: dict,
    task: str | dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
    normalize_movie: bool = True,
) -> list[dict]:
    """
    Create a comment in the target API for each comment of the source task.

    This function keeps only the `created_at` field of the audit fields.
    It also creates the attachments and the previews.

    Args:
        task_status_map (dict): The map of source status IDs to target IDs.
        person_map (dict): The map of source person IDs to target IDs.
        task (str / dict): The task of the comments.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.
        normalize_movie (bool): If True, the target normalizes the pushed
            movie previews.

    Returns:
        list: The source comments that this function pushed.
    """
    comments = task_module.all_comments_for_task(task, client=client_source)
    comments.reverse()
    comments_target = []
    for comment in comments:
        comment_target = push_task_comment(
            task_status_map,
            person_map,
            task,
            comment,
            client_source,
            client_target,
            normalize_movie=normalize_movie,
        )
        if comment_target is not None:
            comments_target.append(comment_target)
    return comments_target


def push_task_comment(
    task_status_map: dict,
    person_map: dict,
    task: str | dict,
    comment: dict,
    client_source: KitsuClient,
    client_target: KitsuClient,
    author_id: str | None = None,
    tmp_path: str | None = None,
    normalize_movie: bool = True,
) -> dict:
    """
    Create a comment in the target API from the given source comment.

    This function keeps only the `created_at` field of the audit fields.
    It also creates the attachments and the previews. If the task status of
    the comment is not mapped, this function does not push the comment.

    Args:
        task_status_map (dict): The map of source status IDs to target IDs.
        person_map (dict): The map of source person IDs to target IDs.
        task (str / dict): The task of the comment.
        comment (dict): The comment to push.
        client_source (KitsuClient): The client of the source API.
        client_target (KitsuClient): The client of the target API.
        author_id (str): The ID of the person to set as the comment author.
        tmp_path (str): The local folder for the downloaded files. If the value
            is None, this function uses a temporary folder and removes it.
        normalize_movie (bool): If True, the target normalizes the pushed
            movie previews.

    Returns:
        dict: The source comment, or None if this function did not push it.
    """
    if tmp_path is None:
        with tempfile.TemporaryDirectory(prefix="zou_sync_") as tmp_path:
            return push_task_comment(
                task_status_map,
                person_map,
                task,
                comment,
                client_source,
                client_target,
                author_id=author_id,
                tmp_path=tmp_path,
                normalize_movie=normalize_movie,
            )
    attachments = []
    for attachment_id in comment["attachment_files"]:
        if isinstance(attachment_id, dict):
            attachment_id = attachment_id["id"]
        attachment_file = files_module.get_attachment_file(
            attachment_id, client=client_source
        )
        file_path = _get_sync_file_path(
            tmp_path, attachment_id, attachment_file["name"]
        )
        files_module.download_attachment_file(
            attachment_file, file_path, client=client_source
        )
        attachments.append(file_path)

    previews = []
    for preview_file in comment["previews"]:
        if isinstance(preview_file, str):
            preview_file_id = preview_file
        else:
            preview_file_id = preview_file["id"]
        preview_file = files_module.get_preview_file(
            preview_file_id, client=client_source
        )
        if (
            preview_file["original_name"] is not None
            and preview_file["extension"] is not None
        ):
            file_path = _get_sync_file_path(
                tmp_path,
                preview_file_id,
                preview_file["original_name"]
                + "."
                + preview_file["extension"],
            )
            files_module.download_preview_file(
                preview_file, file_path, client=client_source
            )
            previews.append(
                {
                    "file_path": file_path,
                    "annotations": preview_file["annotations"],
                }
            )
        else:
            logger.warning(
                "Skipping preview %s: missing original_name or extension.",
                preview_file.get("id"),
            )

    if comment["task_status_id"] not in task_status_map:
        logger.warning(
            "Skipping comment %s: task status %s is not mapped to the target.",
            comment.get("id"),
            comment["task_status_id"],
        )
        return
    task_status = {"id": task_status_map[comment["task_status_id"]]}
    if author_id is None:
        author_id = person_map.get(comment["person_id"])
        if author_id is None:
            logger.warning(
                "Comment %s: author %s is not mapped to the target, "
                "the comment will be attributed to the current user.",
                comment.get("id"),
                comment["person_id"],
            )
    person = {"id": author_id} if author_id is not None else None

    comment_target = task_module.add_comment(
        task,
        task_status,
        attachments=attachments,
        comment=comment["text"],
        created_at=comment["created_at"],
        person=person,
        checklist=comment["checklist"] or [],
        client=client_target,
    )

    for preview in previews:
        new_preview_file = task_module.add_preview(
            task,
            comment_target,
            preview["file_path"],
            normalize_movie=normalize_movie,
            client=client_target,
        )
        files_module.update_preview(
            new_preview_file,
            {"annotations": preview["annotations"]},
            client=client_target,
        )
        _remove_sync_file(preview["file_path"])

    for attachment_path in attachments:
        _remove_sync_file(attachment_path)

    return comment


def _get_sync_file_path(tmp_path: str, file_id: str, name: str) -> str:
    """
    Return the path of a downloaded file. Each file has its own folder.

    Two files of a comment can have the same name.
    """
    # Sanitize the server-provided values so they can't escape tmp_path.
    folder = os.path.join(tmp_path, sanitize_filename(file_id))
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, sanitize_filename(name))


def _remove_sync_file(file_path: str) -> None:
    """
    Remove a downloaded file and its folder. Ignore the system errors.
    """
    try:
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))
    except OSError:
        pass


def convert_id_list(ids: list[str], model_map: dict) -> list:
    """
    Args:
        ids (list): The IDs to convert.
        model_map (dict): The map of IDs to their new values.

    Returns:
        list: The values of the given IDs in the map.
    """
    return [model_map[id] for id in ids]
