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
        f"projects/{project['id']}/concepts", client=client
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
        f"concepts/{concept['id']}/preview-files", client=client
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
    path = f"data/concepts/{concept['id']}"
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
    data: dict | None = None,
    entity_concept_links: list[str | dict] | None = None,
    concept_folder: str | dict | None = None,
    client: KitsuClient = default,
) -> dict:
    """
    Create a concept for given project. Allow to set metadata too.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept to create.
        description (str): Description of the concept.
        data (dict): Free field to set metadata of any kind.
        entity_concept_links (list): List of entities to tag, as either
            ID strings or model dicts.
        concept_folder (str / dict): The concept folder dict or ID to create
            the concept in. The concept is created at the root of the
            project when no folder is given.

    Returns:
        Created concept.
    """
    project = normalize_model_parameter(project)
    concept_folder = normalize_model_parameter(concept_folder)
    if data is None:
        data = {}
    if entity_concept_links is None:
        entity_concept_links = []
    data = {
        "name": name,
        "data": data,
        "entity_concept_links": normalize_list_of_models_for_links(
            entity_concept_links
        ),
    }

    if description is not None:
        data["description"] = description

    if concept_folder is not None:
        data["parent_id"] = concept_folder["id"]

    concept = get_concept_by_name(project, name, client=client)
    if concept is None:
        path = f"data/projects/{project['id']}/concepts"
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
    return raw.put(f"data/entities/{concept['id']}", concept, client=client)


@cache
def all_concept_folders_for_project(
    project: str | dict, client: KitsuClient = default
) -> list[dict]:
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: The folders the concepts of given project are sorted in. A
        concept names its folder through its `parent_id`.
    """
    project = normalize_model_parameter(project)
    concept_folders = raw.fetch_all(
        f"projects/{project['id']}/concept-folders", client=client
    )
    return sort_by_name(concept_folders)


@cache
def get_concept_folder_by_name(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict | None:
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): Name of claimed concept folder.

    Returns:
        dict: Concept folder corresponding to given name and project, None
        if there is no such folder.
    """
    concept_folders = all_concept_folders_for_project(project, client=client)
    return next(
        (
            concept_folder
            for concept_folder in concept_folders
            if concept_folder["name"] == name
        ),
        None,
    )


def new_concept_folder(
    project: str | dict, name: str, client: KitsuClient = default
) -> dict:
    """
    Create a concept folder for given project. Reserved to the managers and
    the supervisors of the project. If a folder with this name already
    exists, it is returned as is.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept folder to create.

    Returns:
        dict: Created concept folder.
    """
    project = normalize_model_parameter(project)
    return raw.post(
        f"data/projects/{project['id']}/concept-folders",
        {"name": name},
        client=client,
    )


def update_concept_folder(
    concept_folder: dict, client: KitsuClient = default
) -> dict:
    """
    Save the name of given concept folder into the API. Reserved to the
    managers and the supervisors of the project.

    Args:
        concept_folder (dict): The concept folder dict to update.

    Returns:
        dict: Updated concept folder.
    """
    return raw.put(
        f"data/concept-folders/{concept_folder['id']}",
        {"name": concept_folder["name"]},
        client=client,
    )


def remove_concept_folder(
    concept_folder: str | dict, client: KitsuClient = default
) -> str:
    """
    Remove given concept folder from the database. Its concepts are kept,
    they go back to the root of the project. Reserved to the managers and the
    supervisors of the project.

    Args:
        concept_folder (str / dict): The concept folder dict or ID to remove.
    """
    concept_folder = normalize_model_parameter(concept_folder)
    return raw.delete(
        f"data/concept-folders/{concept_folder['id']}", client=client
    )


def move_concepts(
    project: str | dict,
    concepts: list[str | dict],
    concept_folder: str | dict | None = None,
    client: KitsuClient = default,
) -> list[str]:
    """
    Move given concepts to given concept folder, or back to the root of the
    project when no folder is given. Reserved to the managers and the
    supervisors of the project.

    Args:
        project (str / dict): The project dict or the project ID.
        concepts (list): The concepts to move, as either ID strings or
            model dicts.
        concept_folder (str / dict): The concept folder dict or ID to move
            the concepts to.

    Returns:
        list: IDs of the concepts that were moved. Concepts that do not
        belong to the project are skipped.
    """
    project = normalize_model_parameter(project)
    concept_folder = normalize_model_parameter(concept_folder)
    return raw.post(
        f"actions/projects/{project['id']}/move-concepts",
        {
            "concept_ids": normalize_list_of_models_for_links(concepts),
            "concept_folder_id": (
                concept_folder["id"] if concept_folder is not None else None
            ),
        },
        client=client,
    )
