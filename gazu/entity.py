from __future__ import annotations

from . import client as raw

from .cache import cache
from .client import KitsuClient
from .sorting import sort_by_name
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_entities(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Retrieve all entities
    """
    return raw.fetch_all("entities", client=client)


@cache
def all_entity_types(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: Entity types listed in database.
    """
    return sort_by_name(raw.fetch_all("entity-types", client=client))


@cache
def get_entity(entity_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        entity_id (str): ID of claimed entity.

    Returns:
        dict: Retrieve entity matching given ID (it can be an entity of any
        kind: asset, shot, sequence, episode, etc).
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
        entity_name (str): The name of the claimed entity.
        project (str / dict): Project ID or dict.

    Returns:
        Retrieve entity matching given name (and project if given).
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
        entity_type_id (str): ID of claimed entity type.

    Returns:
        Retrieve entity type matching given ID (It can be an entity type of any
        kind).
    """
    return raw.fetch_one("entity-types", entity_type_id, client=client)


@cache
def get_entity_type_by_name(
    entity_type_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        entity_type_name (str): The name of the claimed entity type

    Returns:
        Retrieve entity type matching given name.
    """
    return raw.fetch_first(
        "entity-types", {"name": entity_type_name}, client=client
    )


@cache
def guess_from_path(project_id: str, path: str, sep: str = "/") -> list[dict]:
    """
    Get list of possible project file tree templates matching a file path
    and data ids corresponding to template tokens.

    Args:
        project_id (str): Project id of given file
        path (str): Path to a file
        sep (str): File path separator, defaults to "/"
    Returns:
        list: dictionaries with the corresponding entities and template name.
    """
    return raw.post(
        "/data/entities/guess_from_path",
        {"project_id": project_id, "file_path": path, "sep": sep},
    )


def new_entity_type(name: str, client: KitsuClient = default) -> dict:
    """
    Creates an entity type with the given name.

    Args:
        name (str): The name of the entity type

    Returns:
        dict: The created entity type

    Raises:
        gazu.exception.ParameterException:
            If an entity type with that name already exists.
    """
    data = {"name": name}
    return raw.create("entity-types", data, client=client)


def remove_entity_type(
    entity_type: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove given entity type from database.

    Args:
        entity_type (str / dict): Entity type to remove.
    """
    entity_type = normalize_model_parameter(entity_type)
    path = "data/entity-types/%s" % entity_type["id"]
    return raw.delete(path, client=client)


def remove_entity(
    entity: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove given entity from database.

    If the Entity has tasks linked to it, this will by default mark the
    Entity as canceled. Deletion can be forced regardless of task links
    with the `force` parameter.

    Args:
        entity (dict): Entity to remove.
        force (bool): Whether to force deletion of the entity regardless of
            whether it has links to tasks.
    """
    entity = normalize_model_parameter(entity)
    path = "data/entities/%s" % entity["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def all_entities_with_tasks_linked_to_entity(
    entity: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        entity (str / dict): Entity to get linked entities.

    Returns:
        list: Retrieve all entities linked to given entity.
    """
    entity = normalize_model_parameter(entity)
    return raw.fetch_all(
        "entities/%s/entities-linked/with-tasks" % entity["id"], client=client
    )
