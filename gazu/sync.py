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
    Get last events that occured on the machine.

    Args:
        limit (int): Number of events to retrieve.
        project (str / dict): Get only events related to this project.
        after (str): Get only events occuring after given date.
        before (str): Get only events occuring before given date.
        only_files (bool): Get only events related to files.

    Returns:
        list[dict]: Last events matching criterions.
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
    Import entities from another instance to target instance (keep id and audit
    dates).

    Args:
        entities (list): Entities to import.

    Returns:
        list[dict]: Entities created.
    """
    return raw.post("import/kitsu/entities", entities, client=client)


def import_tasks(
    tasks: list[dict], client: KitsuClient = default
) -> list[dict]:
    """
    Import tasks from another instance to target instance (keep id and audit
    dates).

    Args:
        tasks (list): Tasks to import.

    Returns:
        list[dict]: Tasks created.
    """
    return raw.post("import/kitsu/tasks", tasks, client=client)


def import_entity_links(
    links: list[dict], client: KitsuClient = default
) -> list[dict]:
    """
    Import enitity links from another instance to target instance (keep id and
    audit dates).

    Args:
        links (list): Entity links to import.

    Returns:
        list: Entity links created.
    """
    return raw.post("import/kitsu/entity-links", links, client=client)


def get_model_list_diff(
    source_list: list[dict], target_list: list[dict], id_field: str = "id"
) -> tuple[list[dict], list[dict]]:
    """
    Args:
        source_list (list): List of models to compare.
        target_list (list): List of models for which we want a diff.
        id_field (str): the model field to use as an ID for comparison.

    Returns:
        tuple: Two lists, one containing the missing models in the target list
        and one containing the models that should not be in the target list.
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
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        tuple: Two lists, one containing the missing links in the target list
        and one containing the links that should not be in the target list.
        Links are identified by their in ID and their out ID.
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
        source_list (list): Source models to map.
        target_list (list): Target models to match against by name.

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
            link_map[model["name"]] = name_map[model["name"].lower()]
    return link_map


def get_id_map_by_id(
    source_list: list[dict], target_list: list[dict], field: str = "name"
) -> dict:
    """
    Args:
        source_list (list): Source models to map from.
        target_list (list): Target models to map to.
        field (str): Field used to match models across lists (default "name").

    Returns:
        dict: A dict where keys are the source model IDs and values are the
        IDs of the target models matched on the given field. Useful to match a
        model from the source list to its counterpart in the target list.
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
        source_model (dict): Model from the source API.
        target_model (dict): Matching model from the target API.

    Returns:
        bool: True if the source model is more recent than the target model
        (based on the `updated_at` field)
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
    Build an id map between two instances for a given model.

    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API
        fetch_all (Callable): function returning all models for a client.
        field (str): field used to match models (default "name").

    Returns:
        dict: A dict matching source model ids with target model ids.
    """
    source = fetch_all(client=source_client)
    target = fetch_all(client=target_client)
    return get_id_map_by_id(source, target, field=field)


def get_sync_department_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source departments ids with target department ids
    """
    return _get_sync_id_map(
        source_client, target_client, person_module.all_departments
    )


def get_sync_asset_type_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source asset type ids with target asset type ids
    """
    return _get_sync_id_map(
        source_client, target_client, asset_module.all_asset_types
    )


def get_sync_project_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source project ids with target project ids
    """
    return _get_sync_id_map(
        source_client, target_client, project_module.all_projects
    )


def get_sync_task_type_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source task type ids with target task type ids
    """
    return _get_sync_id_map(
        source_client, target_client, task_module.all_task_types
    )


def get_sync_task_status_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source task status ids with target task status
              ids
    """
    return _get_sync_id_map(
        source_client, target_client, task_module.all_task_statuses
    )


def get_sync_person_id_map(
    source_client: KitsuClient, target_client: KitsuClient
) -> dict:
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source person ids with target person ids
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
    Point the `created_by` field of given entities to the matching target
    person, or to nobody: the source person IDs do not exist on the target.
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
    Copy assets from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed assets
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
    Copy episodes from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)

    Args:
        project_source (dict): The project to get episodes from
        project_target (dict): The project to push episodes to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed episodes
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
    Copy sequences from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)

    Args:
        project_source (dict): The project to get sequences from
        project_target (dict): The project to push sequences to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed sequences
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
    Copy shots from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get shots from
        project_target (dict): The project to push shots to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed shots
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
    Copy edits from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get edits from
        project_target (dict): The project to push edits to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed edits
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
    Copy concept folders and concepts from source to target and preserve
    audit fields (`id`, `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get concepts from
        project_target (dict): The project to push concepts to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed concept folders and concepts
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
    Copy entity links (breakdown, concepts) from source to target and preserve
    audit fields (`id`, `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed entity links
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
    links from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        dict: Pushed data
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
    Copy tasks from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        default_status (str / dict): The default status for the pushed tasks
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API

    Returns:
        list: Pushed tasks
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
    Create a new comment into target api for each comment in source project
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API
        normalize_movie (bool): Whether the target normalizes the pushed
            movie previews. Turn it off for previews already normalized
            by the source.

    Returns:
        list: Source tasks whose comments were pushed
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
    Create a new comment into target api for each comment in source task
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        task_status_map (dict): A mapping of source TaskStatus IDs to target IDs.
        person_map (dict): A mapping of source Person IDs to target IDs.
        task (str / dict): The task to push comments for
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API
        normalize_movie (bool): Whether the target normalizes the pushed
            movie previews.

    Returns:
        list: Created comments
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
    Create a new comment into target api for each comment in source task
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        task_status_map (dict): A mapping of source TaskStatus IDs to target IDs.
        person_map (dict): A mapping of source Person IDs to target IDs.
        task (str / dict): The task to push the comment for.
        comment (dict): The comment to push.
        client_source (KitsuClient): client to get data from source API
        client_target (KitsuClient): client to push data to target API
        author_id (str): The ID of the Person to set as the comment author.
        tmp_path (str): The local path on disk to download the attachment files
            for syncing.
        normalize_movie (bool): Whether the target normalizes the pushed
            movie previews.

    Returns:
        dict: The source comment.
    """
    if tmp_path is None:
        tmp_path = tempfile.mkdtemp(prefix="zou_sync_")
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
    Return a path for a downloaded file in a folder of its own: two files
    of a comment can share the same name.
    """
    # Sanitize the server-provided values so they can't escape tmp_path.
    folder = os.path.join(tmp_path, sanitize_filename(file_id))
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, sanitize_filename(name))


def _remove_sync_file(file_path: str) -> None:
    try:
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))
    except OSError:
        pass


def convert_id_list(ids: list[str], model_map: dict) -> list:
    """
    Args:
        ids (list): Ids to convert.
        model_map (dict): Map matching ids to another value.

    Returns:
        list: Ids converted through given model map.
    """
    return [model_map[id] for id in ids]
