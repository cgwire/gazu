from . import client

from .cache import cache
from .sorting import sort_by_name


@cache
def all_entities():
    """
    Returns:
        list: Retrieve all entities
    """
    return client.fetch_all("entities")


@cache
def all_entity_types():
    """
    Returns:
        list: Entity types listed in database.
    """
    return sort_by_name(client.fetch_all("entity-types"))


@cache
def all_entities():
    """
    Retrieve all entity types
    """
    return client.fetch_all("entities")


@cache
def all_entity_types():
    """
    Retrieve all entity types
    """
    return client.fetch_all("entity-types")


@cache
def get_entity(entity_id):
    """
    Returns:
        dict: Retrieve entity matching given ID (It can be an entity of any
        kind: asset, shot, sequence or episode).
    """
    return client.fetch_one("entities", entity_id)


@cache
def get_entity_type(entity_type_id):
    """
    Returns:
        Retrieve entity type matching given ID (It can be an entity type of any
        kind).
    """
    return client.fetch_one("entity-types", entity_type_id)


@cache
def get_entity_types():
    """
    Returns:
        list: All entities types available in the API.
    """

    return client.fetch_all("entity-types")


def new_entity_type(name):
    """
    Creates an entity type with the given name.

    Args:
        name (str): The name of the entity type

    Returns:
        dict: The created entity type
    """
    data = {"name": name}
    return client.post("/data/entity-types", data)
