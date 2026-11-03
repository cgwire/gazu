from __future__ import annotations

from . import client as raw

from .client import KitsuClient
from .helpers import normalize_model_parameter

default = raw.default_client


def search_entities(
    query: str,
    project: str | dict | None = None,
    entity_types: list[str | dict] | None = None,
    client: KitsuClient = default,
) -> dict[str, list]:
    """
    Search for entities that match the given query.

    If the query has less than 3 characters, the API returns an empty dict.
    The API returns a maximum of 3 entities of each type.

    Args:
        query (str): The search text.
        project (str / dict): The optional project to search in.
        entity_types (list): The API ignores this value.

    Returns:
        dict: The keys are "persons", "assets" and "shots". The values are the
            lists of the entities that match.
    """
    data = {"query": query}

    if project is not None:
        project = normalize_model_parameter(project)
        data["project_id"] = project["id"]

    if entity_types is not None:
        entity_type_ids = [
            normalize_model_parameter(entity_type)["id"]
            for entity_type in entity_types
        ]
        data["entity_types"] = entity_type_ids

    return raw.post("data/search", data, client=client)
