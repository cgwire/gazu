from . import client

from .cache import cache


@cache
def get_entity(entity_id):
    """
    Returns:
        dict: Retrieve entity matching given ID (It can be an entity of any
        kind: asset, shot, sequence or episode).
    """
    return client.fetch_one('entities', entity_id)


@cache
def get_entity_type(entity_type_id):
    """
    Returns:
        Retrieve entity type matching given ID (It can be an entity type of any
        kind).
    """
    return client.fetch_one('entity-types', entity_type_id)
