from __future__ import annotations

from . import client as raw

from .cache import cache
from .client import KitsuClient
from .sorting import sort_by_name
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
    warn_ignored_force,
)

default = raw.default_client


@cache
def all_entities(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: All entities in the database.
    """
    return raw.fetch_all("entities", by_cursor=True, client=client)


@cache
def all_entity_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: The entity types in the database.
    """
    return sort_by_name(raw.fetch_all("entity-types", client=client))


@cache
def get_entity(entity_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        entity_id (str): The ID of the entity.

    Returns:
        dict: The entity with the given ID. The entity can be of all types:
        asset, shot, sequence, episode and more.
    """
    return raw.fetch_one("entities", entity_id, client=client)


@cache
def get_entity_by_name(
    entity_name: str,
    project: str | dict | None = None,
    client: KitsuClient = default,
) -> dict | None:
    """
    Args:
        entity_name (str): The name of the entity.
        project (str / dict): The project ID or dict.

    Returns:
        dict: The entity with the given name and, if given, in the given
        project. None if no entity matches.
    """
    params = {"name": entity_name}
    if project is not None:
        project = normalize_model_parameter(project)
        params["project_id"] = project["id"]
    return raw.fetch_first("entities", params, client=client)


@cache
def get_entity_type(
    entity_type_id: str, client: KitsuClient = default
) -> dict:
    """
    Args:
        entity_type_id (str): The ID of the entity type.

    Returns:
        dict: The entity type with the given ID. The entity type can be of
        all kinds.
    """
    return raw.fetch_one("entity-types", entity_type_id, client=client)


@cache
def get_entity_type_by_name(
    entity_type_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        entity_type_name (str): The name of the entity type.

    Returns:
        dict: The entity type with the given name, or None if no entity type
        matches.
    """
    return raw.fetch_first(
        "entity-types", {"name": entity_type_name}, client=client
    )


@cache
def guess_from_path(
    project_id: str,
    path: str,
    sep: str = "/",
    client: KitsuClient = default,
) -> list[dict]:
    """
    Get the project file tree templates that match a file path.

    The result also gives the data IDs of the template tokens.

    Args:
        project_id (str): The project ID of the file.
        path (str): The path of the file.
        sep (str): The file path separator ("/" by default).
        client (KitsuClient): The client to use for the request.

    Returns:
        list: The dicts with the related entities and the template name.
    """
    return raw.post(
        "/data/entities/guess_from_path",
        {"project_id": project_id, "file_path": path, "sep": sep},
        client=client,
    )


def new_entity_type(name: str, client: KitsuClient = default) -> dict:
    """
    Create an entity type with the given name.

    Args:
        name (str): The name of the entity type.

    Returns:
        dict: The created entity type.

    Raises:
        gazu.exception.ParameterException:
            If an entity type with this name exists. The API ignores the
            letter case of the name.
    """
    data = {"name": name}
    return raw.create("entity-types", data, client=client)


def remove_entity_type(
    entity_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove the given entity type from the database.

    Args:
        entity_type (str / dict): The entity type to remove.

    Returns:
        str: The response of the API.
    """
    entity_type = normalize_model_parameter(entity_type)
    path = f"data/entity-types/{entity_type['id']}"
    return raw.delete(path, client=client)


def remove_entity(
    entity: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given entity from the database.

    If the entity has tasks, versions or child entities, the database refuses
    the deletion. The API returns an error and does not cancel the entity.
    To cancel an entity or to remove its tasks, use the function for its
    type (for example, ``gazu.asset.remove_asset``) or ``remove_entities``.

    Args:
        entity (str / dict): The entity to remove.
        force (bool): Do not use. The API ignores this value on this route.

    Returns:
        str: The response of the API.

    Raises:
        gazu.exception.ParameterException: If the database refuses the
            deletion.
    """
    if force:
        warn_ignored_force("remove_entity")
    entity = normalize_model_parameter(entity)
    return raw.delete(f"data/entities/{entity['id']}", client=client)


def remove_entities(
    project: str | dict,
    entities: list[str | dict],
    force: bool = False,
    client: KitsuClient = default,
) -> list[str]:
    """
    Remove more than one entity of the given project in one request.

    The entities can be assets, shots, edits and concepts.

    If ``force`` is False, the first call sets an entity with tasks to
    canceled. The second call removes the entity. The API always removes
    concepts. If ``force`` is True, the API removes each entity and its tasks
    immediately.

    Only the creator of an entity or a project manager can remove it.

    The API ignores an entity in these conditions: the entity does not exist,
    it is in a different project, or it is not an asset, a shot, an edit or a
    concept. The returned list does not contain this entity, and the request
    does not fail.

    For a user who is not a manager, one entity from a different creator
    causes the request to fail. The API then removes no entity.

    The API removes the entities one by one. If an error occurs during the
    request, the removed entities stay removed and the API returns no list.

    Args:
        project (str / dict): The project of the entities.
        entities (list): The entities to remove, as IDs or dicts. Each ID
            must be a valid UUID. If not, the API refuses the full request.
        force (bool): If True, remove the entities and their tasks.

    Returns:
        list: The IDs of the entities that the API processed.
    """
    project = normalize_model_parameter(project)
    entity_ids = normalize_list_of_models_for_links(entities)
    path = f"actions/projects/{project['id']}/delete-entities"
    if force:
        path += "?force=true"
    return raw.post(path, entity_ids, client=client)


def all_entities_with_tasks_linked_to_entity(
    entity: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.

    Returns:
        list: The entities with tasks that are linked to the given entity.
    """
    entity = normalize_model_parameter(entity)
    return raw.fetch_all(
        f"entities/{entity['id']}/entities-linked/with-tasks", client=client
    )
