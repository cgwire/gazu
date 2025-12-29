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
    Search for entities matching the given query.

    Args:
        query (str): Search query string.
        project (str / dict): Optional project to limit search to.
        entity_types (list): Optional list of entity type dicts or IDs to filter by.

    Returns:
        dict: Dictionary with entity type keys ("persons", "assets", "shots")
              containing lists of matching entities for each type.
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
