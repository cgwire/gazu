from __future__ import annotations

from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .client import KitsuClient
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

default = raw.default_client


@cache
def all_concepts(client: KitsuClient = default) -> list[dict]:
    """
    Returns:
        list: All concepts from database.
    """
    concepts = raw.fetch_all("concepts", client=client)
    return sort_by_name(concepts)


@cache
def all_concepts_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Concepts from database for the given project.
    """
    project = normalize_model_parameter(project)
    concepts = raw.fetch_all(
        "projects/%s/concepts" % project["id"], client=client
    )
    return sort_by_name(concepts)


@cache
def all_previews_for_concept(
    concept: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns:
        list: Previews from database for given concept.
    """
    concept = normalize_model_parameter(concept)
    return raw.fetch_all(
        "concepts/%s/preview-files" % concept["id"], client=client
    )


def remove_concept(
    concept: str | dict, force: bool = False, client: KitsuClient = default
) -> str:
    """
    Remove the given Concept from the database.

    If the Concept has tasks linked to it, this will by default mark the
    Concept as canceled. Deletion can be forced regardless of task links
    with the `force` parameter.

    Args:
        concept (dict / str): Concept to remove.
        force (bool): Whether to force the deletion of the concept.
    """
    concept = normalize_model_parameter(concept)
    path = "data/concepts/%s" % concept["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


@cache
def get_concept(concept_id: str, client: KitsuClient = default) -> dict:
    """
    Args:
        concept_id (str): ID of claimed concept.

    Returns:
        dict: Concept corresponding to given concept ID.
    """
    return raw.fetch_one("concepts", concept_id, client=client)


@cache
def get_concept_by_name(
    project: str | dict, concept_name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        concept_name (str): Name of claimed concept.

    Returns:
        dict: Concept corresponding to given name and project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "concepts",
        {"project_id": project["id"], "name": concept_name},
        client=client,
    )


def new_concept(
    project: str | dict,
    name: str,
    description: str | None = None,
    data: dict = {},
    entity_concept_links: list[str | dict] = [],
    client: KitsuClient = default,
) -> dict:
    """
    Create a concept for given project. Allow to set metadata too.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept to create.
        data (dict): Free field to set metadata of any kind.
        entity_concept_links (list): List of entities to tag, as either
            ID strings or model dicts.

    Returns:
        Created concept.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "data": data,
        "entity_concept_links": normalize_list_of_models_for_links(
            entity_concept_links
        ),
    }

    if description is not None:
        data["description"] = description

    concept = get_concept_by_name(project, name, client=client)
    if concept is None:
        path = "data/projects/%s/concepts" % project["id"]
        return raw.post(path, data, client=client)
    else:
        return concept


def update_concept(concept: dict, client: KitsuClient = default) -> dict:
    """
    Save given concept data into the API. Metadata are fully replaced by the ones
    set on given concept.

    Args:
        concept (dict): The concept dict to update.

    Returns:
        dict: Updated concept.
    """
    return raw.put("data/entities/%s" % concept["id"], concept, client=client)
