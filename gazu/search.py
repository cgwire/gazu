from __future__ import annotations

import warnings

from . import client as raw

from .client import KitsuClient
from .helpers import normalize_model_parameter

default = raw.default_client


def search_entities(
    query: str,
    project: str | dict | None = None,
    entity_types: list[str | dict] | None = None,
    client: KitsuClient = default,
    index_names: list[str] | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> dict[str, list]:
    """
    Search for entities that match the given query.

    If the query has less than 3 characters, the API returns an empty dict.

    Args:
        query (str): The search text.
        project (str / dict): The optional project to search in.
        entity_types (list): Do not use. The API ignores this value. Use
            ``index_names``.
        index_names (list): The types of entities to search: "assets", "shots"
            or "persons". By default, the API searches all these types.
        limit (int): The maximum number of entities of each type. By default,
            the API returns 3 entities.
        offset (int): The number of entities to skip.

    Returns:
        dict: The keys are the searched types. The values are the lists of the
            entities that match.
    """
    data = {"query": query}

    if project is not None:
        project = normalize_model_parameter(project)
        data["project_id"] = project["id"]

    if entity_types is not None:
        warnings.warn(
            "search_entities: entity_types is ignored by the API, use "
            "index_names",
            DeprecationWarning,
            stacklevel=2,
        )

    if index_names is not None:
        data["index_names"] = index_names
    if limit is not None:
        data["limit"] = limit
    if offset is not None:
        data["offset"] = offset

    return raw.post("data/search", data, client=client)
